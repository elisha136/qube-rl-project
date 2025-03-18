import serial
import time
import struct

# Teensy / QUBE connection settings
COM_PORT = "COM10"   # Update if needed
BAUD_RATE = 115200

SER = None

def init_serial_connection():
    """Initialize the serial connection if not already open."""
    global SER
    if SER is None:
        SER = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=1)
        time.sleep(2)  # give the port time to initialize
        print(f"Connected to {COM_PORT} at {BAUD_RATE} baud.")

def close_serial_connection():
    """Close the serial connection if needed."""
    global SER
    if SER is not None and SER.is_open:
        SER.close()
        SER = None

def parse_encoder_data(data4: bytes) -> float:
    """
    Decode the 4-byte format used in sendEncoderData():
      - 2 bytes for revolutions (with sign bit in bit 15),
      - 2 bytes for angle (top 9 bits = integer, lower 7 bits = decimal .xx).
    """
    rev = (data4[0] << 8) | data4[1]   # 16 bits
    ang = (data4[2] << 8) | data4[3]   # 16 bits

    negative = bool(rev & 0x8000)
    revCount = rev & 0x7FFF  # lower 15 bits are the absolute revolution count

    angle_int = ang >> 7         # shift down 7 bits
    angle_dec = ang & 0x7F       # bottom 7 bits
    angle_float = angle_int + (angle_dec / 100.0)

    if negative:
        angle_float = -((revCount * 360.0) + angle_float)
    else:
        angle_float = (revCount * 360.0) + angle_float

    return angle_float

def parse_rpm_data(data2: bytes) -> float:
    """
    Decode 2 bytes for RPM. 
    The code sets bit 15 if negative, bits 14-0 store the absolute RPM.
    """
    val = (data2[0] << 8) | data2[1]
    negative = bool(val & 0x8000)
    rpm = val & 0x7FFF
    if negative:
        rpm = -rpm
    return float(rpm)

def parse_current_data(data2: bytes) -> float:
    """
    Decode 2 bytes for motor current (absolute value in the firmware).
    """
    val = (data2[0] << 8) | data2[1]
    return float(val)

def send_command_and_read_data(
    resetMotor=0,
    resetPendulum=0,
    r=999,
    g=999,
    b=999,
    motorCmd=0
):
    """
    Sends 10 bytes to the Teensy:
      Byte 0: resetMotor (bool)
      Byte 1: resetPendulum (bool)
      Bytes 2-3: R (0-999)
      Bytes 4-5: G (0-999)
      Bytes 6-7: B (0-999)
      Bytes 8-9: motorCommand + 999
    Then reads 12 bytes in response:
      4 bytes: motor angle
      4 bytes: pendulum angle
      2 bytes: RPM
      2 bytes: current
    Returns (motor_angle, pendulum_angle, rpm, current).
    """
    init_serial_connection()

    out_bytes = bytearray(10)
    out_bytes[0] = int(resetMotor)       # 0 or 1
    out_bytes[1] = int(resetPendulum)    # 0 or 1

    out_bytes[2] = (r >> 8) & 0xFF
    out_bytes[3] = r & 0xFF
    out_bytes[4] = (g >> 8) & 0xFF
    out_bytes[5] = g & 0xFF
    out_bytes[6] = (b >> 8) & 0xFF
    out_bytes[7] = b & 0xFF

    cmd_offset = motorCmd + 999
    out_bytes[8] = (cmd_offset >> 8) & 0xFF
    out_bytes[9] = cmd_offset & 0xFF

    SER.write(out_bytes)

    resp = SER.read(12)
    if len(resp) < 12:
        print(f"Warning: expected 12 bytes, got {len(resp)}. Data={resp}")
        return None, None, None, None

    motor_angle = parse_encoder_data(resp[0:4])
    pendulum_angle = parse_encoder_data(resp[4:8])
    rpm = parse_rpm_data(resp[8:10])
    current = parse_current_data(resp[10:12])

    return motor_angle, pendulum_angle, rpm, current

def set_motor_voltage(voltage):
    """
    Example function if you want to interpret 'voltage' as a motor command.
    The QUBE library uses 'setMotorSpeed' which might be in range [-999, 999].
    You can map voltage to a command if you know the ratio (e.g. 3 V => ~999).
    """
    scaling_factor = 333.0
    motorCmd = int(voltage * scaling_factor)
    return send_command_and_read_data(
        resetMotor=0,
        resetPendulum=0,
        r=999,
        g=999,
        b=999,
        motorCmd=motorCmd
    )

def reset_encoders():
    """ Reset both motor and pendulum encoders. """
    return send_command_and_read_data(
        resetMotor=1,
        resetPendulum=1,
        r=999,
        g=999,
        b=999,
        motorCmd=0
    )

def get_data():
    """
    Just read data without changing motor command or resetting encoders.
    Returns (motor_angle, pendulum_angle, rpm, current).
    """
    return send_command_and_read_data(
        resetMotor=0,
        resetPendulum=0,
        r=999,
        g=999,
        b=999,
        motorCmd=0
    )

def collect_data(samples=1000, filename="dataset.csv"):
    """
    Collect data from the QUBE and save it to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "motor_angle", "pendulum_angle", "rpm", "current"])

        for _ in range(samples):
            timestamp = time.time()
            motor_angle, pendulum_angle, rpm, current = get_data()
            writer.writerow([timestamp, motor_angle, pendulum_angle, rpm, current])
            time.sleep(0.01)  # Adjust the delay as needed

if __name__ == "__main__":
    collect_data()
