from pathlib import Path

import cv2
import numpy as np

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_SIDE = 3000


class ImageInputError(Exception):
    """خطای مربوط به ورودی تصویر."""


def load_image_from_bytes(data: bytes) -> np.ndarray:
    if not data:
        raise ImageInputError("فایل تصویر خالی است.")
    buffer = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ImageInputError("فرمت تصویر معتبر نیست یا فایل خراب است.")
    return _limit_size(image)


def load_image_from_path(path: str) -> np.ndarray:
    file_path = Path(path)
    if not file_path.is_file():
        raise ImageInputError(f"فایل پیدا نشد: {path}")
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ImageInputError(f"پسوند پشتیبانی نمی‌شود: {file_path.suffix}")
    return load_image_from_bytes(file_path.read_bytes())


def _limit_size(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= MAX_SIDE:
        return image
    scale = MAX_SIDE / longest
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)