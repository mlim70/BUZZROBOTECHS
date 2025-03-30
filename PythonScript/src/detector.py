import cv2
import numpy as np
from robotpy_apriltag import AprilTagDetector

def create_detector(tag_family="tag36h11"):
    """
    Create and configure a robotpy-apriltag detector.
    """
    detector = AprilTagDetector()
    detector.addFamily(tag_family)
    return detector

def detect_tags(frame, detector):
    """
    Convert the input frame to grayscale and detect AprilTags.
    
    Parameters:
      frame (numpy.ndarray): Input BGR frame.
      detector: An instance of AprilTagDetector.
      
    Returns:
      list: Detected AprilTag objects.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray)
    return detections

def get_detection_corners(detection):
    """
    Retrieve the corner points from a detection.
    robotpy-apriltag expects a dummy buffer tuple as argument.
    
    Returns:
      np.ndarray: 4x2 array of corner points as floats.
    """
    # Supply a dummy buffer tuple of eight floats.
    corners_tuple = detection.getCorners((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    corners = np.array(corners_tuple, dtype=np.float32).reshape((4, 2))
    return corners

def estimate_pose(detection, camera_matrix, dist_coeffs, tag_size):
    """
    Estimate the 3D pose (rotation and translation) of the detected tag.
    
    Parameters:
      detection: A detected AprilTag object.
      camera_matrix (np.ndarray): The 3x3 camera intrinsic matrix.
      dist_coeffs (np.ndarray): Distortion coefficients.
      tag_size (float): Real-world side length of the tag in meters.
      
    Returns:
      (rvec, tvec) if successful, or (None, None).
    """
    half_size = tag_size / 2.0
    # Define the object points of the tag corners in the tag's coordinate system.
    obj_points = np.array([
        [-half_size, -half_size, 0.0],
        [ half_size, -half_size, 0.0],
        [ half_size,  half_size, 0.0],
        [-half_size,  half_size, 0.0]
    ], dtype=np.float32)
    
    img_points = get_detection_corners(detection)
    success, rvec, tvec = cv2.solvePnP(obj_points, img_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    if not success:
        return None, None
    return rvec, tvec

def draw_detections(frame, detections, target_id=None):
    """
    Draw detected tag outlines, centers, and IDs on the frame.
    
    Parameters:
      frame (np.ndarray): The image frame.
      detections (list): List of detected tag objects.
      target_id (int): ID of the target tag to highlight in green.
      
    Returns:
      np.ndarray: The annotated frame.
    """
    for detection in detections:
        corners = get_detection_corners(detection).astype(int)
        tag_id = detection.getId()
        
        # Use green for target tag, blue for others
        color = (0, 255, 0) if tag_id == target_id else (255, 0, 0)
        
        cv2.polylines(frame, [corners.reshape((-1, 1, 2))], isClosed=True, color=color, thickness=2)
        center = detection.getCenter()
        cX, cY = int(center.x), int(center.y)
        cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"ID: {tag_id}", (cX - 10, cY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
