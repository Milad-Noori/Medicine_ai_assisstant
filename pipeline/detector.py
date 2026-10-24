import numpy as np
from ultralytics import YOLO

MODEL_PATH = "model/yolo8n.pt"
CONFIDENCE = 0.4
PADDING = 15

_model = None


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(MODEL_PATH)
    return _model


def crop_medicine(image: np.ndarray) -> np.ndarray:
    results = _get_model()(image, conf=CONFIDENCE, verbose=False)
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return image

    best = int(boxes.conf.argmax())
    x1, y1, x2, y2 = boxes.xyxy[best].cpu().numpy().astype(int)

    height, width = image.shape[:2]
    x1 = max(0, x1 - PADDING)
    y1 = max(0, y1 - PADDING)
    x2 = min(width, x2 + PADDING)
    y2 = min(height, y2 + PADDING)
    return image[y1:y2, x1:x2]