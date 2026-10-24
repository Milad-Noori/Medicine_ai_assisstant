import cv2
import numpy as np

from pipeline.input_handler import ImageInputError, _limit_size

WINDOW_NAME = "Medicine Reader"


def capture_from_webcam(camera_index: int = 0) -> np.ndarray:
    backend = cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") and _is_windows() else cv2.CAP_ANY
    cap = cv2.VideoCapture(camera_index, backend)
    if not cap.isOpened():
        raise ImageInputError(
            f"وبکم با شماره {camera_index} باز نشد. شماره‌ی دیگری را امتحان کنید "
            "یا مطمئن شوید برنامه‌ی دیگری از دوربین استفاده نمی‌کند."
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    captured = None
    try:
        _warm_up(cap)
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                raise ImageInputError("خواندن تصویر از وبکم ناموفق بود.")

            preview = frame.copy()
            cv2.putText(
                preview, "SPACE: ضبط | ESC/Q: کنلل", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA,
            )
            cv2.imshow(WINDOW_NAME, preview)

            key = cv2.waitKey(1) & 0xFF
            if key == 32:
                captured = frame
                break
            if key in (27, ord("q"), ord("Q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if captured is None:
        raise ImageInputError("گرفتن عکس توسط کاربر لغو شد.")
    return _limit_size(captured)


def _warm_up(cap: cv2.VideoCapture, frames: int = 15) -> None:
    for _ in range(frames):
        cap.read()


def _is_windows() -> bool:
    import sys
    return sys.platform.startswith("win")


import cv2
from pipeline.webcam import capture_from_webcam
from pipeline.preprocess import preprocess_for_ocr

img = capture_from_webcam(0)
cv2.imwrite("captured.jpg", img)
cv2.imwrite("preprocessed.png", preprocess_for_ocr(img))