import cv2
import argparse
from config.calibration import load_calibration
from .detector import create_detector, detect_tags, estimate_pose, draw_detections
from .actions import target_detected_action

def main():
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
    
    try:
        source = int(args.source)
    except ValueError:
        source = args.source

    # Load camera calibration parameters.
    camera_matrix, dist_coeffs = load_calibration(args.calib)
    print("Loaded calibration data.")

    # Create the AprilTag detector.
    detector = create_detector(args.families)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Error: Unable to open video source.")
        return

    print("Starting continuous detection. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        if args.upscale != 1.0:
            frame = cv2.resize(frame, None, fx=args.upscale, fy=args.upscale, interpolation=cv2.INTER_LINEAR)
        
        detections = detect_tags(frame, detector)
        for detection in detections:
            if detection.getId() == args.target:
                rvec, tvec = estimate_pose(detection, camera_matrix, dist_coeffs, args.tag_size)
                if rvec is not None and tvec is not None:
                    target_detected_action(detection, rvec, tvec)
        
        annotated = draw_detections(frame.copy(), detections)
        cv2.imshow("AprilTag Pose Estimation", annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
