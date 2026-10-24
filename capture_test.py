import cv2
from pipeline.webcam import capture_from_webcam

img = capture_from_webcam(0)
cv2.imwrite("captured.jpg", img)
print("عکس ذخیره شد: captured.jpg")