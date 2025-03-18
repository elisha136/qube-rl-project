import time
import csv
import control

def collect_data(duration=5.0, dt=0.02, filename="my_data1.csv", motor_voltage=1.0):
    """
    Collect data for 'duration' seconds at intervals of 'dt'.
    Set a motor voltage, read angles, rpm, current, and save to CSV.
    """
    control.init_serial_connection()
    control.reset_encoders()

    start_time = time.time()
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "motor_angle", "pendulum_angle", "rpm", "current"])

        while (time.time() - start_time) < duration:
            # set_motor_voltage() returns (motor_angle, pendulum_angle, rpm, current)
            motor_angle, pendulum_angle, rpm, current = control.set_motor_voltage(motor_voltage)
            t = time.time() - start_time
            writer.writerow([f"{t:.3f}", f"{motor_angle:.3f}",
                             f"{pendulum_angle:.3f}", f"{rpm:.3f}", f"{current:.3f}"])
            time.sleep(dt)

    # Stop the motor at the end
    control.set_motor_voltage(0.0)
    control.close_serial_connection()
    print(f"Data collection complete. Saved to {filename}")

if __name__ == "__main__":
    collect_data(duration=5.0, dt=0.02, filename="my_data1.csv", motor_voltage=1.0)
