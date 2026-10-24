import cv2
from pipeline.input_handler import load_image_from_path
from pipeline.preprocess import preprocess_for_ocr
from pipeline.ocr import extract_text

img = load_image_from_path("captured.jpg")
processed = preprocess_for_ocr(img)
result = extract_text(processed)

print("متن:", result.text)
print("میانگین اطمینان:", result.average_confidence)
print("کلمات مشکوک:", [(w.text, w.confidence) for w in result.low_confidence_words])