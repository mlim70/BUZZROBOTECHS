#python PythonScript/src/ReadApril.py --mode static --image [image in root].png
import cv2
import numpy as np
from robotpy_apriltag import AprilTagDetector
import argparse

def detect_tags(image, detector: AprilTagDetector):
    """
    Convert the input image to grayscale and detect AprilTags.
    
    Parameters:
      image (numpy.ndarray): Input BGR image.
      detector (AprilTagDetector): An instance of the AprilTag detector.
    
    Returns:
      list: A list of detected tag objects.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray)
    return detections

def draw_detections(image, detections):
    """
    Draw bounding boxes, centers, and tag IDs on the image for each detected AprilTag.
    
    Parameters:
      image (numpy.ndarray): Input image.
      detections (list): List of detected tag objects.
    
    Returns:
      numpy.ndarray: The annotated image.
    """
    for tag in detections:
        # Supply a dummy buffer tuple (8 zeros) to receive the corner coordinates.
        corners_tuple = tag.getCorners((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        # Reshape the returned flat tuple into a 4x2 array (four corners, each with x and y)
        corners = np.array(corners_tuple, dtype=np.int32).reshape((4, 2))
        cv2.polylines(image, [corners.reshape((-1, 1, 2))], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Draw the center of the tag.
        center = tag.getCenter()
        cX, cY = int(center.x), int(center.y)
        cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
        
        # Annotate with the tag ID.
        tag_id = tag.getId()
        cv2.putText(image, f"ID: {tag_id}", (cX - 10, cY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return image

def process_static_image(image_path):
    """
    Load an image from disk, detect AprilTags, print their info, and display the annotated image.
    
    Parameters:
      image_path (str): Path to the test image.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return

    # Create the detector and add the appropriate tag family (adjust if your tag uses a different family)
    detector = AprilTagDetector()
    detector.addFamily("tag36h11")
    
    detections = detect_tags(image, detector)
    
    print(f"Detected {len(detections)} tag(s).")
    for tag in detections:
        print(f"Tag ID: {tag.getId()}, Center: {tag.getCenter()}")
    
    annotated = draw_detections(image, detections)
    cv2.imshow("AprilTag Detection - Static Image", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_live_video():
    """
    Open a video capture stream, continuously detect AprilTags, display detections, and print tag info.
    
    Press 'q' to quit the live video display.
    """
    cap = cv2.VideoCapture(0)  # Change index if needed
    if not cap.isOpened():
        print("Error: Could not open video capture device.")
        return

    detector = AprilTagDetector()
    detector.addFamily("tag36h11")
    
    print("Starting live video. Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        detections = detect_tags(frame, detector)
        for tag in detections:
            print(f"Tag ID: {tag.getId()}, Center: {tag.getCenter()}")
        
        annotated = draw_detections(frame, detections)
        cv2.imshow("AprilTag Detection - Live Video", annotated)
        
        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AprilTag detection using robotpy-apriltag.")
    parser.add_argument('--mode', choices=['static', 'live'], default='static',
                        help="Choose 'static' to process an image file or 'live' for video capture.")
    parser.add_argument('--image', type=str, default='test_image.png',
                        help="Path to the test image (used in static mode).")
    
    args = parser.parse_args()
    
    if args.mode == 'static':
        process_static_image(args.image)
    elif args.mode == 'live':
        process_live_video()
