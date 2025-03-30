import cv2
import argparse
import numpy as np
import time
from picamera2 import Picamera2
from config.calibration import load_calibration
from .detector import create_detector, detect_tags, estimate_pose, draw_detections
from .actions import target_detected_action

def draw_info_overlay(frame, target_detected, tag_id, x, y, z, distance):
    """
    Draw a clean, organized information overlay on the frame.
    """
    # Create a semi-transparent overlay for the info panel
    overlay = frame.copy()
    height, width = frame.shape[:2]
    
    # Define panel dimensions and position
    panel_width = 300
    panel_height = 200
    panel_x = 10
    panel_y = 10
    
    # Draw semi-transparent background for the panel
    cv2.rectangle(overlay, 
                 (panel_x, panel_y), 
                 (panel_x + panel_width, panel_y + panel_height),
                 (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Define colors
    success_color = (0, 255, 0)  # Green
    error_color = (0, 0, 255)    # Red
    text_color = (255, 255, 255) # White
    
    # Draw status
    status_text = "TARGET DETECTED" if target_detected else "TARGET NOT DETECTED"
    status_color = success_color if target_detected else error_color
    cv2.putText(frame, status_text, (panel_x + 10, panel_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
    if target_detected:
        # Draw tag ID
        cv2.putText(frame, f"Tag ID: {tag_id}", (panel_x + 10, panel_y + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        
        # Draw coordinates with labels
        cv2.putText(frame, f"X: {x:.3f}m", (panel_x + 10, panel_y + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        cv2.putText(frame, f"Y: {y:.3f}m", (panel_x + 10, panel_y + 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        cv2.putText(frame, f"Z: {z:.3f}m", (panel_x + 10, panel_y + 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        
        # Draw distance in bottom right
        cv2.putText(frame, f"Distance: {distance:.3f}m", 
                    (width - 200, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
    
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
        print(f"Camera matrix shape: {camera_matrix.shape}")
        print(f"Distortion coefficients shape: {dist_coeffs.shape}")
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
        
        print("Creating preview configuration...")
        config = picam2.create_preview_configuration()
        print("Configuring camera...")
        picam2.configure(config)
        print("Starting camera...")
        picam2.start()
        print("Waiting for camera to adjust...")
        time.sleep(2)
        print("Camera initialization complete")
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return

    print("Starting continuous detection. Press 'q' to quit.")
    frame_count = 0
    
    while True:
        try:
            frame_count += 1
            print(f"\nProcessing frame {frame_count}")
            
            print("Capturing frame...")
            frame = picam2.capture_array()
            print(f"Frame captured, shape: {frame.shape}")
            
            print("Converting color space...")
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            if args.upscale != 1.0:
                print(f"Upscaling frame by factor {args.upscale}")
                frame = cv2.resize(frame, None, fx=args.upscale, fy=args.upscale, interpolation=cv2.INTER_LINEAR)
            
            print("Detecting AprilTags...")
            detections = detect_tags(frame, detector)
            print(f"Found {len(detections)} tags")
            
            target_detected = False
            x, y, z = 0, 0, 0
            distance = 0
            
            for detection in detections:
                print(f"Processing tag ID: {detection.getId()}")
                if detection.getId() == args.target:
                    print("Target tag found, estimating pose...")
                    rvec, tvec = estimate_pose(detection, camera_matrix, dist_coeffs, args.tag_size)
                    if rvec is not None and tvec is not None:
                        print("Pose estimated successfully")
                        target_detected = True
                        target_detected_action(detection, rvec, tvec)
                        
                        # Get coordinate information
                        x, y, z = tvec.flatten()
                        distance = np.linalg.norm(tvec)
                        
                        # Print coordinates to console
                        print(f"\n=== COORDINATES TO TARGET TAG {args.target} ===")
                        print(f"X: {x:.3f}m")
                        print(f"Y: {y:.3f}m")
                        print(f"Z: {z:.3f}m")
                        print(f"Distance: {distance:.3f}m")
                        print("==========================================\n")
                    else:
                        print("Failed to estimate pose")
            
            # Draw detections
            print("Drawing detections...")
            annotated = draw_detections(frame.copy(), detections)
            
            # Draw information overlay
            print("Drawing information overlay...")
            annotated = draw_info_overlay(annotated, target_detected, args.target, x, y, z, distance)
            
            print("Displaying frame...")
            cv2.imshow("AprilTag Pose Estimation", annotated)
            
            print("Waiting for key press...")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit command received")
                break
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            break

    print("Cleaning up...")
    try:
        picam2.stop()
        cv2.destroyAllWindows()
        print("Cleanup complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
