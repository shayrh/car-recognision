# 🚗 Car Recognition Toolkit

A compact set of Python utilities for experimenting with **vehicle detection**, **license plate recognition**, and **media upload workflows**, powered by [Ultralytics YOLOv8](https://docs.ultralytics.com/) and **PyTorch**.  
Supports both **command-line** and **graphical** interfaces with optional **GPU acceleration (CUDA / WSL2)**.

---

## 🎥 Demo

![Demo Video](https://github.com/shayrh/car-recognision/raw/main/car_example.mp4)

---

## 📁 Project Structure

| File | Description |
| --- | --- |
| `detect.py` | Minimal example using YOLOv8n to detect vehicles in a single image (`car.jpg`) and save the annotated result. |
| `detect_cars_gui.py` | Tkinter desktop app that lets you pick an image or URL, runs YOLOv8x, and shows detections with icons. |
| `detect_square.py` | Scrollable image gallery with upload functionality to a backend endpoint. |
| `carparts_gui_server.py` | Combined Flask + Tkinter app — Flask handles uploads while the GUI manages local/remote images. |
| `used-car-dealership-artesia.html` | Static HTML demo page for a used-car dealership. |

---

## ⚙️ Requirements

Python 3.9+ and the following packages:

```bash
pip install ultralytics torch torchvision torchaudio opencv-python pillow requests flask easyocr
