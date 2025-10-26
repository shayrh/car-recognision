# image_uploader_gui.py
# Desktop GUI (Tkinter) to select images (Browse), preview them, and optionally upload to a Flask /upload endpoint.
# No placeholders; default upload URL points to local Flask app at http://127.0.0.1:5000/upload

import os
import io
import threading
import requests
from tkinter import Tk, Frame, Button, Label, filedialog, StringVar, Scrollbar, Canvas, NW, BOTH, RIGHT, Y, LEFT, X, TOP, BOTTOM
from PIL import Image, ImageTk

UPLOAD_URL = "http://127.0.0.1:5000/upload"  # Flask endpoint

class ImagePreviewer(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Image Picker & Uploader")
        self.pack(fill=BOTH, expand=True)

        # State
        self.images_paths = []          # Selected file paths
        self.photo_thumbs = []          # Keep references to Tk images

        # Top controls
        top_bar = Frame(self)
        top_bar.pack(side=TOP, fill=X, padx=8, pady=8)

        self.status = StringVar(value="Ready")
        Label(top_bar, textvariable=self.status).pack(side=LEFT)

        Button(top_bar, text="📂 Browse Images", command=self.choose_files).pack(side=RIGHT, padx=4)
        Button(top_bar, text="⬆️ Upload Selected", command=self.upload_selected).pack(side=RIGHT, padx=4)
        Button(top_bar, text="🗑 Clear", command=self.clear_all).pack(side=RIGHT, padx=4)

        # Scrollable preview area
        container = Frame(self)
        container.pack(fill=BOTH, expand=True, padx=8, pady=8)

        self.canvas = Canvas(container, highlightthickness=0)
        self.scrollbar = Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.gallery = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.gallery, anchor=NW)
        self.gallery.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Footer
        footer = Frame(self)
        footer.pack(side=BOTTOM, fill=X, padx=8, pady=6)
        Label(footer, text=f"Upload URL: {UPLOAD_URL}").pack(side=LEFT)

        # Allow mousewheel scrolling (Windows/Mac/Linux)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)   # Linux up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)   # Linux down

    # ----- UI actions -----
    def choose_files(self):
        filetypes = [("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(title="Choose images", filetypes=filetypes)
        if not paths:
            self.status.set("No files selected")
            return
        new = [p for p in paths if p not in self.images_paths]
        self.images_paths.extend(new)
        self._refresh_gallery()
        self.status.set(f"Selected {len(self.images_paths)} file(s)")

    def clear_all(self):
        self.images_paths = []
        self.photo_thumbs = []
        for w in list(self.gallery.children.values()):
            w.destroy()
        self.status.set("Cleared")

    def upload_selected(self):
        if not self.images_paths:
            self.status.set("Nothing to upload")
            return
        self.status.set("Uploading...")
        threading.Thread(target=self._upload_worker, daemon=True).start()

    # ----- Workers -----
    def _upload_worker(self):
        ok_count = 0
        fail = []
        for p in self.images_paths:
            try:
                with open(p, "rb") as f:
                    files = {"file": (os.path.basename(p), f, self._guess_mime(p))}
                    r = requests.post(UPLOAD_URL, files=files, timeout=20)
                if r.ok and isinstance(r.json(), dict) and r.json().get("url"):
                    ok_count += 1
                else:
                    fail.append(os.path.basename(p))
            except Exception:
                fail.append(os.path.basename(p))
        if fail:
            self.status.set(f"Uploaded {ok_count}, failed {len(fail)}: {', '.join(fail[:3])}{'...' if len(fail)>3 else ''}")
        else:
            self.status.set(f"Uploaded {ok_count} file(s) successfully")

    # ----- Helpers -----
    def _refresh_gallery(self):
        # Clear previous thumbs
        for w in list(self.gallery.children.values()):
            w.destroy()
        self.photo_thumbs = []
        # Create tiles
        max_w, max_h = 220, 220
        pad = 8
        cols = 3
        for idx, path in enumerate(self.images_paths):
            try:
                im = Image.open(path)
                im.thumbnail((max_w, max_h))
                tk_im = ImageTk.PhotoImage(im)
                self.photo_thumbs.append(tk_im)  # keep reference

                tile = Frame(self.gallery, bd=1, relief="solid")
                row, col = divmod(idx, cols)
                tile.grid(row=row, column=col, padx=pad, pady=pad, sticky="nsew")

                lbl = Label(tile, image=tk_im)
                lbl.pack(side=TOP, padx=4, pady=4)

                base = os.path.basename(path)
                caption = Label(tile, text=base, wraplength=max_w, justify="center")
                caption.pack(side=TOP, padx=4, pady=4)
            except Exception:
                # Skip unreadable files
                continue

        # Make columns stretch evenly
        for c in range(3):
            self.gallery.grid_columnconfigure(c, weight=1)

        # Resize canvas width to fit
        self.after(50, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _guess_mime(self, path):
        ext = os.path.splitext(path)[1].lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(ext, "application/octet-stream")

    def _on_mousewheel(self, event):
        # Windows/Mac use event.delta; Linux uses Button-4/5
        delta = 0
        if event.num == 4:   # Linux scroll up
            delta = -120
        elif event.num == 5: # Linux scroll down
            delta = 120
        else:
            delta = -1 * int(event.delta)
        self.canvas.yview_scroll(int(delta/120), "units")

def main():
    root = Tk()
    root.geometry("980x680")
    app = ImagePreviewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
