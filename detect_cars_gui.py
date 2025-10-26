# detect_cars_gui.py – GUI with real icons instead of emojis
import os, threading, uuid, requests, cv2
from tkinter import Tk, Frame, Button, Label, filedialog, StringVar, Entry, BOTH, X, LEFT, PhotoImage
from PIL import Image, ImageTk
from ultralytics import YOLO
import torch

# 🔥 Load YOLO model
model = YOLO("yolov8x.pt")

# 🚀 Use CUDA if available
if torch.cuda.is_available():
    model.to("cuda")
    print("✅ Using GPU (CUDA)")
else:
    print("⚠️ CUDA not available, running on CPU")

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ICON_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(UPLOAD_DIR, exist_ok=True)

BTN_STYLE = {
    "font": ("Arial", 13, "bold"),
    "bg": "#0078D7",
    "fg": "white",
    "padx": 10,
    "pady": 6,
    "compound": LEFT
}

class CarDetector(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("🚗 Car Detector with Icons")
        self.pack(fill=BOTH, expand=True)
        self.status = StringVar(value="Choose image or URL")
        self.panel = Label(self)
        self.panel.pack(padx=10, pady=10)

        # Load icons
        self.icon_browse = self.load_icon("browse.png")
        self.icon_url = self.load_icon("url.png")
        self.icon_detect = self.load_icon("detect.png")

        # Top bar
        top = Frame(self)
        top.pack(fill=X, padx=10, pady=10)

        Button(top, text="Browse", image=self.icon_browse,
               command=self.choose_file, **BTN_STYLE).pack(side=LEFT, padx=5)

        self.url_entry = Entry(top, width=45, font=("Arial", 12))
        self.url_entry.pack(side=LEFT, padx=6)

        # 🩵 Enable paste (Ctrl+V or right-click)
        def paste_clipboard(event=None):
            try:
                text = self.master.clipboard_get()
                self.url_entry.insert("insert", text)
            except Exception:
                pass
            return "break"

        self.url_entry.bind("<Control-v>", paste_clipboard)
        self.url_entry.bind("<Button-3>", lambda e: self.url_entry.event_generate("<<Paste>>"))

        Button(top, text="From URL", image=self.icon_url,
               command=self.load_from_url, **BTN_STYLE).pack(side=LEFT, padx=5)

        Button(top, text="Detect Vehicles", image=self.icon_detect,
               command=self.detect_cars, **BTN_STYLE).pack(side=LEFT, padx=5)

        Label(
    self,
    textvariable=self.status,
    font=("Arial", 16, "bold"),
    fg="#000000",
    bg="#f0f0f0",
    wraplength=900,
    justify="center"
).pack(pady=12)
        self.image_path = None
        self.tk_img = None

    def load_icon(self, name):
        path = os.path.join(ICON_DIR, name)
        if os.path.exists(path):
            return PhotoImage(file=path)
        return PhotoImage(width=1, height=1)  # fallback

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if path:
            self.image_path = path
            self.display_image(path)
            self.status.set("✅ Image loaded.")

    def load_from_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status.set("Enter image URL.")
            return
        self.status.set("Downloading...")
        threading.Thread(target=self._download_image, args=(url,), daemon=True).start()

    def _download_image(self, url):
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0 Safari/537.36"
                )
            }
            r = requests.get(url, stream=True, timeout=10, headers=headers, allow_redirects=True)
            r.raise_for_status()

            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise ValueError(f"URL is not an image (content-type: {content_type})")

            fname = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.jpg")
            with open(fname, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            self.image_path = fname
            self.display_image(fname)
            self.status.set("✅ Image downloaded successfully.")
        except Exception as e:
            self.status.set(f"❌ Failed: {e}")

    def display_image(self, path):
        img = Image.open(path)
        img.thumbnail((850, 600))
        self.tk_img = ImageTk.PhotoImage(img)
        self.panel.config(image=self.tk_img)

    def detect_cars(self):
        if not self.image_path:
            self.status.set("No image selected.")
            return
        self.status.set("Detecting...")
        threading.Thread(target=self._detect_worker, daemon=True).start()

    def _detect_worker(self):
        try:
            results = model.predict(
                self.image_path,
                conf=0.20,       # detect small cars
                iou=0.5,         # less merging
                imgsz=1920,      # high resolution
                device=0
            )

            img = cv2.imread(self.image_path)
            count = 0
            for r in results:
                for b in r.boxes:
                    cls = int(b.cls[0])
                    label = r.names[cls]
                    if label.lower() in ["car", "truck", "bus", "motorbike"]:
                        count += 1
                        x1, y1, x2, y2 = map(int, b.xyxy[0])
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(img, f"{count}", (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            out = os.path.join(UPLOAD_DIR, f"detected_{os.path.basename(self.image_path)}")
            cv2.imwrite(out, img)
            self.display_image(out)
            self.status.set(f"✅ Detected {count} vehicles (conf=0.2, res=1920).")
        except Exception as e:
            self.status.set(f"Error: {e}")

def main():
    r = Tk()
    r.geometry("1000x750")
    r.configure(bg="#f0f0f0")
    CarDetector(r)
    r.mainloop()

if __name__ == "__main__":
    main()
