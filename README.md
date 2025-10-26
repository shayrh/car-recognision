# Car Recognition Toolkit

This repository collects a set of small utilities for experimenting with vehicle detection and media upload workflows. The tools are built around the [Ultralytics YOLOv8](https://docs.ultralytics.com/) models and a handful of lightweight graphical interfaces for image selection and processing.

## Project structure

| File | Description |
| --- | --- |
| `detect.py` | Minimal example that runs the YOLOv8 nano model on a single image (`car.jpg`) and displays the detections in an OpenCV preview window. |
| `detect_cars_gui.py` | Tkinter desktop application that lets you pick an image from disk or a URL, runs YOLOv8x to detect vehicles, and shows the annotated result. |
| `detect_square.py` | Scrollable Tkinter gallery for selecting multiple images and uploading them to a backend endpoint. |
| `carparts_gui_server.py` | Combined Flask + Tkinter app. The Flask server accepts uploads while the GUI can browse local files or download images from a URL before uploading them. |
| `used-car-dealership-artesia.html` | Static HTML landing page mockup for a used car dealership. |

## Requirements

The scripts target Python 3.9+ and rely on the following packages:

- `ultralytics` (provides YOLOv8 models)
- `torch` (PyTorch backend for YOLO)
- `opencv-python`
- `pillow`
- `requests`
- `flask`

Tkinter ships with most desktop Python distributions. GPU acceleration is optional but supported when CUDA-enabled PyTorch is installed.

Install dependencies with pip:

```bash
pip install ultralytics torch torchvision torchaudio opencv-python pillow requests flask
```

## Running the examples

### Simple detection

1. Place an input image at the repository root named `car.jpg`.
2. Run the script:

    ```bash
    python detect.py
    ```

The script loads the YOLOv8 nano model and opens a window with bounding boxes drawn around detected vehicles.

### GUI vehicle detector

The `detect_cars_gui.py` application provides a richer interface with icon-based buttons, URL downloads, and GPU support if available.

```bash
python detect_cars_gui.py
```

- **Browse** to choose an image from disk.
- Paste a link and click **From URL** to download an online image asynchronously.
- Click **Detect Vehicles** to annotate the image with numbered detections (cars, trucks, buses, motorbikes).

Annotated images are saved to the `uploads/` directory alongside the source file.

### Image gallery uploader

`detect_square.py` focuses on selecting multiple files and uploading them to a HTTP endpoint. By default it targets `http://127.0.0.1:5000/upload`.

```bash
python detect_square.py
```

- Use **📂 Browse Images** to add files to the scrollable gallery.
- Click **⬆️ Upload Selected** to send each image via POST.
- The status bar reports successes and failures.

To change the upload destination, edit the `UPLOAD_URL` constant near the top of the script.

### All-in-one uploader with backend

`carparts_gui_server.py` bundles a Flask server and Tkinter client. The server stores uploads under `uploads/`, while the GUI handles browsing, previewing, downloading by URL, and submitting files to the server.

Run the application with:

```bash
python carparts_gui_server.py
```

The Flask server listens on `http://127.0.0.1:5000`. Uploaded files can be retrieved at `/uploads/<filename>`.

## Model weights

The YOLO scripts expect the corresponding model weights (`yolov8n.pt` for the simple demo and `yolov8x.pt` for the GUI). Download them from the [Ultralytics releases](https://github.com/ultralytics/assets/releases) and place them in the project directory before running the scripts.

## License

No license information was provided with the original project files. Add your preferred license here if you plan to publish or distribute this code.

