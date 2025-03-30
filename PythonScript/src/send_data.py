import serial
import time

# Global serial connection
ser = None

def initialize_serial():
    """
    Initialize the serial connection.
    Returns True if successful, False otherwise.
    """
    global ser
    try:
        # Open the serial port (update '/dev/ttyUSB0' or '/dev/ttyACM0' as needed)
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        time.sleep(2)  # Give time for the connection to establish
        print("Serial connection established successfully")
        return True
    except Exception as e:
        print(f"Error establishing serial connection: {e}")
        return False

def target_detected_action(detection, rvec, tvec):
    """
    Action executed when the target AprilTag is detected.
    Sends the tag's position data over serial.
    
    Parameters:
      detection: The detected tag object.
      rvec: Rotation vector (Rodrigues form).
      tvec: Translation vector (in meters).
    """
    global ser
    
    print("==== TARGET DETECTED ====")
    print(f"Tag ID: {detection.getId()}")
    print(f"Translation (meters): {tvec.ravel()}")
    print(f"Rotation vector: {rvec.ravel()}")
    
    if ser is None or not ser.is_open:
        if not initialize_serial():
            print("Failed to send data: No serial connection")
            return
    
    try:
        # Get x, y, z coordinates
        x, y, z = tvec.flatten()
        
        # Format the message as a comma-separated string ending with a newline
        message = f"{x:.3f},{y:.3f},{z:.3f}\n"
        ser.write(message.encode('utf-8'))
        print(f"Sent data: {message.strip()}")
    except Exception as e:
        print(f"Error sending data: {e}")

def cleanup_serial():
    """
    Clean up the serial connection.
    """
    global ser
    if ser is not None and ser.is_open:
        ser.close()
        print("Serial connection closed") 