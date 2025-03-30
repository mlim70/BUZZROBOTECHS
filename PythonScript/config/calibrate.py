import numpy as np
import cv2
import glob
import os

def calibrate_camera():
    # Chessboard dimensions
    CHECKERBOARD = (6, 9)  # Number of inner corners per a chessboard row and column
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

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

        if ret:
            print(f"Found corners in {fname}")
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                      (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
            cv2.imshow('Corners', img)
            cv2.waitKey(500)  # Show each image for 500ms

    cv2.destroyAllWindows()

    if len(objpoints) == 0:
        print("No calibration images were successfully processed!")
        return

    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # Save calibration parameters
    np.savez('calibration.npz', mtx=mtx, dist=dist)
    print("Calibration completed and saved to calibration.npz")

    # Print calibration results
    print("\nCamera Matrix:")
    print(mtx)
    print("\nDistortion Coefficients:")
    print(dist)

if __name__ == "__main__":
    calibrate_camera() 