import serial
import time
import threading
from datetime import datetime

# Global serial connection
ser = None
debug_thread = None
should_stop = False

def read_debug_messages():
    """
    Continuously read and print debug messages from the Arduino.
    """
    global ser, should_stop
    while not should_stop and ser is not None and ser.is_open:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8').strip()
                # Print all messages from Arduino with timestamp
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"[{timestamp}] Arduino: {line}")
            except Exception as e:
                print(f"Error reading debug message: {e}")
        time.sleep(0.01)  # Small delay to prevent CPU overuse

def initialize_serial():
    """
    Initialize the serial connection.
    Returns True if successful, False otherwise.
    """
    global ser, debug_thread, should_stop
    try:
        # Try different common port names
        ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        for port in ports:
            try:
                ser = serial.Serial(port, 115200, timeout=1)
                print(f"Successfully connected to {port}")
                time.sleep(2)  # Give time for the connection to establish
                
                # Start debug message reading thread
                should_stop = False
                debug_thread = threading.Thread(target=read_debug_messages)
                debug_thread.daemon = True
                debug_thread.start()
                
                return True
            except serial.SerialException:
                continue
        
        raise Exception("Could not find Arduino on any common ports")
    except Exception as e:
        print(f"Error establishing serial connection: {e}")
        return False

def target_detected_action(detection, rvec, tvec):
    """
    Action executed when the target AprilTag is detected.
    Sends the tag's position and orientation data over serial.
    
    Parameters:
      detection: The detected tag object.
      rvec: Rotation vector (Rodrigues form).
      tvec: Translation vector (in meters).
    """
    global ser
    
    print("\n==== TARGET DETECTED ====")
    print(f"Tag ID: {detection.getId()}")
    print(f"Translation (meters): {tvec.ravel()}")
    print(f"Rotation vector: {rvec.ravel()}")
    
    if ser is None or not ser.is_open:
        if not initialize_serial():
            print("Failed to send data: No serial connection")
            return
    
    try:
        # Get x, y, z coordinates and rotation vector components
        x, y, z = tvec.flatten()
        rx, ry, rz = rvec.flatten()
        
        # Format the message as a comma-separated string ending with a newline
        # Format: x,y,z,rx,ry,rz
        message = f"{x:.3f},{y:.3f},{z:.3f},{rx:.3f},{ry:.3f},{rz:.3f}\n"
        ser.write(message.encode('utf-8'))
        print(f"Sent data: {message.strip()}")
    except Exception as e:
        print(f"Error sending data: {e}")

def cleanup_serial():
    """
    Clean up the serial connection.
    """
    global ser, debug_thread, should_stop
    should_stop = True
    if debug_thread is not None:
        debug_thread.join(timeout=1.0)
    if ser is not None and ser.is_open:
        ser.close()
        print("Serial connection closed") 