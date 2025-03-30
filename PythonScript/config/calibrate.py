import numpy as np
import cv2
import glob
import os

def calibrate_camera():
    # Chessboard dimensions
    CHECKERBOARD = (6, 8)  # Number of inner corners per a chessboard row and column (7x9 squares)
    SQUARE_SIZE = 0.018  # Size of each square in meters (18mm)

    # Prepare object points
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * SQUARE_SIZE

    # Arrays to store object points and image points
    objpoints = []  # 3D points in real world space
    imgpoints = []  # 2D points in image plane

    # Get list of calibration images
    images = glob.glob('calib_images/*.jpg')
    print(f"Found {len(images)} calibration images")

    if len(images) == 0:
        print("Error: No images found in calib_images directory!")
        return

    for fname in images:
        print(f"\nProcessing {fname}...")
        img = cv2.imread(fname)
        if img is None:
            print(f"Error: Could not read image {fname}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Try different flags for corner detection
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, flags=flags)

        if ret:
            print(f"Successfully found corners in {fname}")
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                      (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
            cv2.imshow('Corners', img)
            cv2.waitKey(500)  # Show each image for 500ms
        else:
            print(f"Failed to find corners in {fname}")
            # Show the image that failed
            cv2.imshow('Failed Image', img)
            cv2.waitKey(1000)  # Show for 1 second

    cv2.destroyAllWindows()

    if len(objpoints) == 0:
        print("\nNo calibration images were successfully processed!")
        print("Common issues:")
        print("1. Check if your calibration pattern is 6x8 inner corners (7x9 squares)")
        print("2. Ensure the pattern is well-lit and clearly visible")
        print("3. Make sure the pattern is flat (not curved)")
        print("4. Try capturing images at different angles and distances")
        print("5. Verify that the pattern is not blurry")
        return

    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # Save calibration parameters
    np.savez('calibration.npz', mtx=mtx, dist=dist)
    print("\nCalibration completed and saved to calibration.npz")

    # Print calibration results
    print("\nCamera Matrix:")
    print(mtx)
    print("\nDistortion Coefficients:")
    print(dist)

if __name__ == "__main__":
    calibrate_camera() 