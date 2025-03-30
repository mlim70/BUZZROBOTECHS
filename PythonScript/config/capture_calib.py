# capture_calib.py
from picamera2 import Picamera2
import cv2
import time
import os

# Create directory for calibration images if it doesn't exist.
os.makedirs("calib_images", exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()
time.sleep(2)  # Let the camera adjust

# Capture 15 images
for i in range(1, 16):
    frame = picam2.capture_array()
    filename = f"calib_images/image{i:02d}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")
    time.sleep(1)  # Pause between shots

picam2.stop()
