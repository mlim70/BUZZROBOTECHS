import numpy as np

def load_calibration(filepath="calibration.npz"):
    """
    Load calibration parameters from a .npz file.
    The file should contain 'mtx' (camera matrix) and 'dist' (distortion coefficients).
    """
    data = np.load(filepath)
    mtx = data['mtx']
    dist = data['dist']
    return mtx, dist
