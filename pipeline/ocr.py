import os
import re
from dataclasses import dataclass, field

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OCR_LANGUAGES = "eng+fas"
MIN_CONFIDENCE = 40
LOW_CONFIDENCE_LIMIT = 70


class OCRError(Exception):
    """خطای مربوط به OCR."""


@dataclass
class OCRWord:
    text: str
    confidence: float
    box: tuple


@dataclass
class OCRResult:
    text: str
    words: list = field(default_factory=list)
    low_confidence_words: list = field(default_factory=list)
    average_confidence: float = 0.0


def _setup_tesseract() -> None:
    if os.path.isfile(DEFAULT_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError as exc:
        raise OCRError(
            "Tesseract پیدا نشد. آن را نصب کنید یا مسیرش را در DEFAULT_TESSERACT_PATH بگذارید."
        ) from exc


def extract_text(image: np.ndarray) -> OCRResult:
    _setup_tesseract()
    if image is None or image.size == 0:
        raise OCRError("تصویر ورودی OCR خالی است.")

    rgb = _to_rgb(image)
    data = pytesseract.image_to_data(
        rgb, lang=OCR_LANGUAGES, config="--oem 3 --psm 6", output_type=Output.DICT
    )

    words = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue
        try:
            confidence = float(data["conf"][i])
        except ValueError:
            continue
        if confidence < MIN_CONFIDENCE:
            continue
        box = (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
        words.append(OCRWord(text=text, confidence=confidence, box=box))

    if not words:
        return OCRResult(text="")

    full_text = _clean_text(" ".join(w.text for w in words))
    low = [w for w in words if w.confidence < LOW_CONFIDENCE_LIMIT]
    average = sum(w.confidence for w in words) / len(words)
    return OCRResult(
        text=full_text,
        words=words,
        low_confidence_words=low,
        average_confidence=round(average, 1),
    )


def _to_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _clean_text(text: str) -> str:
    text = re.sub(r"[|_~`]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()