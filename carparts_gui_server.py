# carparts_gui_server.py
# Flask + Tkinter GUI that uploads local files or downloads images directly from a URL.

import os, threading, uuid, requests
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from tkinter import Tk, Frame, Button, Label, Entry, filedialog, StringVar, Canvas, Scrollbar, NW, BOTH, RIGHT, Y, LEFT, X, TOP, BOTTOM
from PIL import Image, ImageTk

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {"png", "jpg", "jpeg", "webp"}
PORT = 5000

# ------------------ Flask backend ------------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "no file field"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        return jsonify({"error": "unsupported type"}), 415
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = os.path.join(UPLOAD_DIR, filename)
    f.save(path)
    return jsonify({"url": f"/uploads/{filename}", "filename": filename})

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

def run_flask():
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

# ------------------ Tkinter GUI ------------------
class ImageUploader(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Car Parts Image Uploader")
        self.pack(fill=BOTH, expand=True)

        self.images = []
        self.tk_images = []
        self.status = StringVar(value=f"Server: http://127.0.0.1:{PORT}/upload")

        # Top bar
        top = Frame(self)
        top.pack(side=TOP, fill=X, padx=6, pady=6)
        Label(top, textvariable=self.status).pack(side=LEFT)
        Button(top, text="📂 Browse", command=self.choose).pack(side=RIGHT, padx=4)
        Button(top, text="⬆ Upload", command=self.upload_all).pack(side=RIGHT, padx=4)
        Button(top, text="🗑 Clear", command=self.clear).pack(side=RIGHT, padx=4)

        # Gallery
        cont = Frame(self)
        cont.pack(fill=BOTH, expand=True, padx=8, pady=8)
        self.canvas = Canvas(cont, highlightthickness=0)
        self.scroll = Scrollbar(cont, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.gallery = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.gallery, anchor=NW)
        self.gallery.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self.scroll_y)

        # URL input
        url_frame = Frame(self)
        url_frame.pack(side=BOTTOM, fill=X, padx=8, pady=6)
        Label(url_frame, text="Image URL:").pack(side=LEFT)
        self.url_entry = Entry(url_frame, width=50)
        self.url_entry.pack(side=LEFT, padx=6)
        Button(url_frame, text="🌐 Download from URL", command=self.download_url).pack(side=LEFT)

    def scroll_y(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def choose(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if not paths:
            return
        for p in paths:
            if p not in self.images:
                self.images.append(p)
        self.refresh()

    def clear(self):
        self.images = []
        for w in self.gallery.winfo_children():
            w.destroy()
        self.tk_images.clear()

    def refresh(self):
        for w in self.gallery.winfo_children():
            w.destroy()
        self.tk_images.clear()
        for idx, p in enumerate(self.images):
            try:
                im = Image.open(p)
                im.thumbnail((200, 200))
                img = ImageTk.PhotoImage(im)
                self.tk_images.append(img)
                tile = Frame(self.gallery, bd=1, relief="solid")
                tile.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
                Label(tile, image=img).pack()
                Label(tile, text=os.path.basename(p)).pack()
            except Exception as e:
                print("Error:", e)

    def upload_all(self):
        if not self.images:
            self.status.set("No images selected.")
            return
        self.status.set("Uploading...")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        ok, fail = 0, []
        for path in self.images:
            try:
                with open(path, "rb") as f:
                    files = {"file": (os.path.basename(path), f, "image/jpeg")}
                    r = requests.post(f"http://127.0.0.1:{PORT}/upload", files=files, timeout=10)
                if r.ok:
                    ok += 1
                else:
                    fail.append(os.path.basename(path))
            except Exception:
                fail.append(os.path.basename(path))
        self.status.set(f"Uploaded {ok}, failed {len(fail)}")

    def download_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status.set("Please enter an image URL.")
            return
        self.status.set("Downloading...")
        threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()

    def _download_worker(self, url):
        try:
            resp = requests.get(url, stream=True, timeout=10)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            ext = ".jpg" if "jpeg" in content_type else ".png"
            filename = os.path.join(UPLOAD_DIR, secure_filename(f"{uuid.uuid4().hex}{ext}"))
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            self.images.append(filename)
            self.refresh()
            self.status.set(f"Downloaded: {os.path.basename(filename)}")
        except Exception as e:
            self.status.set(f"Download failed: {e}")

# ------------------ Run both ------------------
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    root = Tk()
    root.geometry("900x700")
    app = ImageUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
