import time
import csv
import random

import control

def collect_data(
    filename="data.csv",
    duration=10.0,   # total time in seconds
    dt=0.01,         # time step in seconds
    voltage_range=1.0
):
    """
    Collect data from the QUBE by sending random motor voltages in
    [-voltage_range, +voltage_range], logging sensor data to a CSV file.
    """
    # Ensure serial is initialized
    control.init_serial_connection()

    start_time = time.time()

    # Open the CSV file for writing
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header row
        writer.writerow(["time", "voltage", 
                         "motor_angle", "pendulum_angle", "rpm"])

        # Loop until duration is exceeded
        while (time.time() - start_time) < duration:
            # 1) Generate a random motor voltage within [-voltage_range, voltage_range]
            voltage = random.uniform(-voltage_range, voltage_range)

            # 2) Send the motor voltage
            control.set_motor_voltage(voltage)

            # 3) Wait for dt
            time.sleep(dt)

            # 4) Read sensor data
            motor_angle = control.get_motor_angle()
            pendulum_angle = control.get_pendulum_angle()
            rpm = control.get_rpm()

            # 5) Write row to CSV
            t = time.time() - start_time
            writer.writerow([f"{t:.3f}", f"{voltage:.3f}", 
                             f"{motor_angle:.3f}", f"{pendulum_angle:.3f}", 
                             f"{rpm:.3f}"])

    # After data collection, set motor voltage to 0 for safety
    control.set_motor_voltage(0.0)

    print(f"Data collection complete. File saved to: {filename}")

if __name__ == "__main__":
    # Example usage:
    collect_data(
        filename="data.csv",
        duration=10.0,
        dt=0.02,
        voltage_range=1.0
    )
