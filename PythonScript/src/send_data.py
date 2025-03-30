import serial
import time
import threading
from datetime import datetime

# Global serial connection
ser = None
debug_thread = None
should_stop = False
last_error_time = 0
error_cooldown = 5  # seconds to wait between retries
thread_lock = threading.Lock()
last_send_time = 0
min_send_interval = 0.05  # 50ms between sends (20Hz)

def read_debug_messages():
    """
    Continuously read and print debug messages from the Arduino.
    """
    global ser, should_stop
    while not should_stop:
        try:
            with thread_lock:
                if ser is None or not ser.is_open:
                    time.sleep(0.1)  # Wait a bit before retrying
                    continue
                
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        # Print all messages from Arduino with timestamp
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[{timestamp}] Arduino: {line}")
                    except Exception as e:
                        print(f"Error reading message: {e}")
                        time.sleep(0.1)  # Wait before retrying
                        continue
                
            time.sleep(0.01)  # Small delay to prevent CPU overuse
            
        except Exception as e:
            print(f"Error in debug thread: {e}")
            time.sleep(0.1)  # Wait before retrying
            continue

def initialize_serial():
    """
    Initialize the serial connection.
    Returns True if successful, False otherwise.
    """
    global ser, debug_thread, should_stop, last_error_time
    try:
        # Try different common port names
        ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        for port in ports:
            try:
                with thread_lock:
                    if ser is not None and ser.is_open:
                        ser.close()
                    ser = serial.Serial(port, 115200, timeout=0.1)  # Reduced timeout
                    print(f"Successfully connected to {port}")
                    time.sleep(2)  # Give time for the connection to establish
                    
                    # Start debug message reading thread
                    should_stop = False
                    if debug_thread is None or not debug_thread.is_alive():
                        debug_thread = threading.Thread(target=read_debug_messages)
                        debug_thread.daemon = True
                        debug_thread.start()
                    
                    return True
            except serial.SerialException as e:
                print(f"Failed to connect to {port}: {e}")
                continue
        
        raise Exception("Could not find Arduino on any common ports")
    except Exception as e:
        print(f"Error establishing serial connection: {e}")
        return False

def target_detected_action(detection, rvec, tvec):
    """
    Action executed when the target AprilTag is detected.
    Sends the tag's position and orientation data over serial.
    """
    global ser, last_error_time, last_send_time
    
    current_time = time.time()
    
    # Rate limit the sending of data
    if current_time - last_send_time < min_send_interval:
        return
    
    print("\n==== TARGET DETECTED ====")
    print(f"Tag ID: {detection.getId()}")
    print(f"Translation (meters): {tvec.ravel()}")
    print(f"Rotation vector: {rvec.ravel()}")
    
    # Check if we need to retry connection
    if ser is None or not ser.is_open or (current_time - last_error_time) > error_cooldown:
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
        
        with thread_lock:
            if ser is not None and ser.is_open:
                ser.write(message.encode('utf-8'))
                ser.flush()  # Ensure the data is sent
                last_send_time = current_time
                print(f"Sent data: {message.strip()}")
            else:
                raise Exception("Serial connection not available")
                
    except Exception as e:
        print(f"Error sending data: {e}")
        last_error_time = current_time
        with thread_lock:
            if ser is not None and ser.is_open:
                try:
                    ser.close()
                except:
                    pass
                ser = None

def cleanup_serial():
    """
    Clean up the serial connection.
    """
    global ser, debug_thread, should_stop
    should_stop = True
    if debug_thread is not None:
        debug_thread.join(timeout=1.0)
    with thread_lock:
        if ser is not None and ser.is_open:
            try:
                ser.close()
            except:
                pass
            print("Serial connection closed") 