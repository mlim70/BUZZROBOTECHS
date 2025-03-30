# capture_calib.py
from picamera2 import Picamera2
import cv2
import time
import os
import numpy as np

# Create directory for calibration images if it doesn't exist.
os.makedirs("calib_images", exist_ok=True)

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()
time.sleep(2)  # Let the camera adjust

print("Starting calibration capture...")
print("Press SPACE to capture an image")
print("Press Q to quit")

image_count = 1
while True:
    # Capture frame
    frame = picam2.capture_array()
    
    # Convert from RGB to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Display the frame
    cv2.imshow('Calibration Capture (Press SPACE to capture, Q to quit)', frame)
    
    # Wait for key press
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):  # Quit
        break
    elif key == ord(' '):  # Space bar to capture
        filename = f"calib_images/image{image_count:02d}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        image_count += 1
        time.sleep(0.5)  # Small delay between captures

picam2.stop()
cv2.destroyAllWindows()
print(f"\nCalibration capture complete. Saved {image_count-1} images.")
