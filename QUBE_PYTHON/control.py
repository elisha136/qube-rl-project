from PID import *
import serial
import time
import csv

# Arduino COM port (or QUBE’s USB/serial port)
COM_PORT = "COM4"

# Using mac?
USING_MAC = False

# Target values (not strictly needed for data collection, but kept for reference)
MOTOR_TARGET_ANGLE = 0  # degrees
PENDULUM_TARGET_ANGLE = 0  # degrees
MOTOR_TARGET_RPM = 0     # rpm (max 3500)

pid = PID()

# --------------------------------------------
# STEP 1: PLACEHOLDER SERIAL OBJECT & FUNCTIONS
# --------------------------------------------
SER = None

def init_serial_connection():
    """
    Initialize the serial connection if not already open.
    Adjust baudrate, timeout, etc. to match your QUBE’s settings.
    """
    global SER
    if SER is None:
        baud_rates = [9600, 19200, 38400, 57600, 115200]  # Common baud rates
        for baud_rate in baud_rates:
            try:
                SER = serial.Serial(
                    port=COM_PORT,
                    baudrate=baud_rate,
                    timeout=1
                )
                time.sleep(2)  # Short delay to let the serial port initialize
                print(f"Connected with baud rate: {baud_rate}")
                break
            except serial.SerialException:
                print(f"Failed to connect with baud rate: {baud_rate}")
                SER = None
        if SER is None:
            raise Exception("Failed to connect to the QUBE with any common baud rate.")

def set_motor_voltage(voltage):
    """
    Send a command to set motor voltage.
    Replace this with the correct protocol/format for your QUBE.
    """
    init_serial_connection()
    # Convert to string with a command label recognized by your QUBE
    cmd = f"V {voltage:.3f}\n"
    SER.write(cmd.encode())

def get_pendulum_angle():
    """
    Query the QUBE for the pendulum angle (in degrees or radians).
    Replace with the correct serial command and parsing logic.
    """
    init_serial_connection()
    # Send request for pendulum angle
    SER.write(b"A_PEND\n")
    # Read line
    response = SER.readline()
    print(f"Raw pendulum angle response: {response}")  # Debugging output
    try:
        response = response.decode('utf-8').strip()
    except UnicodeDecodeError:
        response = response.decode('latin-1').strip()
    try:
        angle = float(response)
    except ValueError:
        print(f"Failed to parse pendulum angle: {response}")
        angle = 0.0
    return angle

def get_motor_angle():
    """
    Query the QUBE for the motor shaft angle (in degrees or radians).
    """
    init_serial_connection()
    # Send request for motor angle
    SER.write(b"A_MOTOR\n")
    # Read line
    response = SER.readline()
    print(f"Raw motor angle response: {response}")  # Debugging output
    try:
        response = response.decode('utf-8').strip()
    except UnicodeDecodeError:
        response = response.decode('latin-1').strip()
    try:
        angle = float(response)
    except ValueError:
        print(f"Failed to parse motor angle: {response}")
        angle = 0.0
    return angle

def get_rpm():
    """
    Query the QUBE for the motor speed in RPM.
    """
    init_serial_connection()
    # Send request for RPM
    SER.write(b"RPM\n")
    # Read line
    response = SER.readline()
    print(f"Raw RPM response: {response}")  # Debugging output
    try:
        response = response.decode('utf-8').strip()
    except UnicodeDecodeError:
        response = response.decode('latin-1').strip()
    try:
        rpm = float(response)
    except ValueError:
        print(f"Failed to parse RPM: {response}")
        rpm = 0.0
    return rpm

# -------------------------------------------------
# Data collection
# -------------------------------------------------
def collect_data(samples=1000, filename="dataset.csv"):
    """
    Collect data from the QUBE and save it to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "motor_angle", "pendulum_angle", "rpm"])

        for _ in range(samples):
            timestamp = time.time()
            motor_angle = get_motor_angle()
            pendulum_angle = get_pendulum_angle()
            rpm = get_rpm()
            writer.writerow([timestamp, motor_angle, pendulum_angle, rpm])
            time.sleep(0.01)  # Adjust the delay as needed

if __name__ == "__main__":
    collect_data()
