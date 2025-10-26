from ultralytics import YOLO
import cv2

# Load YOLOv8 nano model
model = YOLO("yolov8n.pt")

# Read image
img = "car.jpg"
frame = cv2.imread(img)

# Detect cars
results = model(frame, device=0)  # device=0 => GPU

# Draw boxes
annotated = results[0].plot()

# Show result
cv2.imshow("Car Detection 🚗", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
