def target_detected_action(detection, rvec, tvec):
    """
    Placeholder action executed when the target AprilTag is detected.
    
    Parameters:
      detection: The detected tag object.
      rvec: Rotation vector (Rodrigues form).
      tvec: Translation vector (in meters).
    """
    print("==== TARGET DETECTED ====")
    print(f"Tag ID: {detection.getId()}")
    print(f"Translation (meters): {tvec.ravel()}")
    print(f"Rotation vector: {rvec.ravel()}")
    #TODO: insert code here
