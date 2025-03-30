#python3 -m src.main --source 0 --target 27 --upscale 1 --tag_size 0.018
# camera device index, target id, zoom factor, tag size in meters

import cv2
import argparse
import numpy as np
import time
from picamera2 import Picamera2
from config.calibration import load_calibration
from .detector import create_detector, detect_tags, estimate_pose, draw_detections
from .send_data import target_detected_action

def draw_info_overlay(frame, target_detected, tag_id, x, y, z, distance):
    """
    Draw a clean, organized information overlay on the frame.
    """
    height, width = frame.shape[:2]
    
    # Define colors
    success_color = (0, 255, 0)  # Green
    error_color = (0, 0, 255)    # Red
    text_color = (255, 255, 255) # White
    
    if target_detected:
        # Draw status
        cv2.putText(frame, "TARGET DETECTED", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, success_color, 1)
        
        # Draw tag ID
        cv2.putText(frame, f"Tag ID: {tag_id}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        # Draw coordinates with labels
        cv2.putText(frame, f"X: {x:.3f}m", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        cv2.putText(frame, f"Y: {y:.3f}m", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        cv2.putText(frame, f"Z: {z:.3f}m", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        # Draw distance in bottom right with smaller text
        cv2.putText(frame, f"Distance: {distance:.3f}m", 
                    (width - 150, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
    else:
        # Draw a subtle "not detected" message
        cv2.putText(frame, "TARGET NOT DETECTED", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, error_color, 1)
    
    return frame

def main():
    print("Starting program initialization...")
    parser = argparse.ArgumentParser(description="Continuous AprilTag 3D Pose Estimation using robotpy-apriltag")
    parser.add_argument('--source', type=str, default="0",
                        help="Video source: device index (e.g., 0) or URL for your Camo feed.")
    parser.add_argument('--upscale', type=float, default=1.0,
                        help="Upscale factor for frames (e.g., 1.5) to help detect small tags.")
    parser.add_argument('--target', type=int, required=True,
                        help="Desired AprilTag ID that triggers the action.")
    parser.add_argument('--tag_size', type=float, default=0.0508,
                        help="Real-world tag size in meters (default ~2 inches = 0.0508 m).")
    parser.add_argument('--calib', type=str, default="calibration.npz",
                        help="Path to calibration file containing 'mtx' and 'dist'.")
    parser.add_argument('--families', type=str, default="tag36h11",
                        help="AprilTag families to detect (default: tag36h11).")
    args = parser.parse_args()
    print(f"Arguments parsed: {args}")

    try:
        print("Loading calibration data...")
        camera_matrix, dist_coeffs = load_calibration(args.calib)
        print("Calibration data loaded successfully")
    except Exception as e:
        print(f"Error loading calibration data: {e}")
        return

    try:
        print("Creating AprilTag detector...")
        detector = create_detector(args.families)
        print("AprilTag detector created successfully")
    except Exception as e:
        print(f"Error creating detector: {e}")
        return

    try:
        print("Initializing Pi Camera...")
        picam2 = Picamera2()
        print("Camera object created")
        
        print("\nCreating preview configuration...")
        config = picam2.create_preview_configuration(
            main={"size": (1280, 720)},
            controls={
                "FrameDurationLimits": (33333, 33333),
                "ExposureTime": 10000,
                "AeEnable": True,
                "AwbEnable": True,
                "Contrast": 1.5,
                "Sharpness": 1.5,
                "Brightness": 0.1
            }
        )
        
        print("Configuring camera...")
        picam2.configure(config)
        print("Starting camera...")
        picam2.start()
        print("Camera initialization complete")
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if the camera is properly connected")
        print("2. Run 'vcgencmd get_camera' to check camera status")
        print("3. Check if camera is enabled in raspi-config")
        print("4. Try rebooting the Raspberry Pi")
        return

    print("Starting continuous detection. Press 'q' to quit.")
    frame_count = 0
    last_print_time = time.time()
    print_interval = 1.0  # Print status every 1 second
    
    while True:
        try:
            frame_count += 1
            current_time = time.time()
            
            # Only print status every print_interval seconds
            if current_time - last_print_time >= print_interval:
                print(f"\nFrame {frame_count} - Processing...")
                last_print_time = current_time
            
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            if args.upscale != 1.0:
                frame = cv2.resize(frame, None, fx=args.upscale, fy=args.upscale, interpolation=cv2.INTER_LINEAR)
            
            detections = detect_tags(frame, detector)
            target_detected = False
            x, y, z = 0, 0, 0
            distance = 0
            
            for detection in detections:
                if detection.getId() == args.target:
                    rvec, tvec = estimate_pose(detection, camera_matrix, dist_coeffs, args.tag_size)
                    if rvec is not None and tvec is not None:
                        target_detected = True
                        target_detected_action(detection, rvec, tvec)
                        x, y, z = tvec.flatten()
                        distance = np.linalg.norm(tvec)
                        
                        # Only print coordinates when target is detected
                        if current_time - last_print_time >= print_interval:
                            print(f"\n=== TARGET TAG {args.target} DETECTED ===")
                            print(f"X: {x:.3f}m | Y: {y:.3f}m | Z: {z:.3f}m")
                            print(f"Distance: {distance:.3f}m")
                            print("==========================================\n")
            
            annotated = draw_detections(frame.copy(), detections, args.target)
            annotated = draw_info_overlay(annotated, target_detected, args.target, x, y, z, distance)
            
            cv2.imshow("AprilTag Pose Estimation", annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit command received")
                break
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)
            continue

    print("Cleaning up...")
    try:
        picam2.stop()
        cv2.destroyAllWindows()
        from .send_data import cleanup_serial
        cleanup_serial()
        print("Cleanup complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
