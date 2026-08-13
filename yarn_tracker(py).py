# ============================================================
# Yarn Length Tracker
# ============================================================
# Author:       Ethan DeMoss
# Updated:      8/11/2026
#
# Description:
#   Real-time yarn length tracker using an Arduino Nano and
#   rotary encoder. Displays live length, logs completed balls,
#   generates a time vs length chart, and saves session data.
#
# Requirements:
#   pip install pyserial matplotlib
# ============================================================

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime
import sys
import msvcrt  

def check_keyboard():
    if msvcrt.kbhit():
        key = msvcrt.getwch()
        if key.lower() == 'r':
            return "reset"
    return None

# ---- SESSION STATE ----
session_start_time = None
time_points = []
length_points = []
balls = []
current_length_yd = 0.0

# ---- SERIAL CONNECTION ----

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "CH340" in port.description or "Arduino" in port.description:
            return port.device
    return None


def connect_to_arduino():
    print("\n  Searching for Arduino...")
    port = find_arduino_port()

    if port:
        print(f"  Found Arduino on {port}")
    else:
        print("  Could not auto-detect Arduino.")
        ports = serial.tools.list_ports.comports()
        for i, p in enumerate(ports):
            print(f"  [{i+1}] {p.device} — {p.description}")
        choice = input("\n  Select port number: ")
        try:
            port = serial.tools.list_ports.comports()[int(choice) - 1].device
        except (ValueError, IndexError):
            print("  Invalid selection.")
            return None

    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)
        print(f"  Connected to {port}")
        return ser
    except serial.SerialException as e:
        print(f"  Could not connect: {e}")
        return None


def send_diameter(ser, diameter_cm):
    command = f"D:{diameter_cm}\n"
    ser.write(command.encode("utf-8"))
    time.sleep(0.5)
    # Read confirmation
    while ser.in_waiting > 0:
        response = ser.readline().decode("utf-8").strip()
        if "DIAMETER_SET" in response:
            print(f"  Arduino confirmed diameter: {diameter_cm} cm")


# ---- SERIAL PARSING ----

def parse_serial_line(line):
    try:
        if line.startswith("Length:") and line.endswith("yd"):
            value = float(line.replace("Length:", "").replace("yd", "").strip())
            return ("length", value)
        elif line == "RESET":
            return ("reset", None)
        elif line == "READY":
            return ("ready", None)
        else:
            return None
    except ValueError:
        return None


# ---- MAIN SESSION ----

def run_session(ser):
    global current_length_yd, session_start_time
    global time_points, length_points, balls

    while True:
        try:
            diameter = float(input("\n  Enter swift diameter tip-to-tip (cm): "))
            if diameter > 0:
                break
            print("  Please enter a positive number.")
        except ValueError:
            print("  Invalid input.")

    send_diameter(ser, diameter)
    session_start_time = time.time()

    print("\n============================================================")
    print("                   YARN LENGTH TRACKER")
    print("============================================================")
    print("  Wind yarn on the swift to begin tracking.")
    print("  Press the encoder button to log a completed ball.")
    print("  Press Ctrl+C to end the session.")
    print("  Press R to log a completed ball (or use arduino button).")
    print("============================================================\n")

    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_title("Yarn Length Over Time")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Cumulative Length (yards)")
    ax.grid(True, alpha=0.3)
    line_plot, = ax.plot([], [], "b-", linewidth=2)
    plt.tight_layout()
    plt.show()

    last_chart_update = time.time()

    try:
        while True:
            if ser.in_waiting > 50:
                ser.reset_input_buffer()
            if ser.in_waiting > 0:
                raw = ser.readline().decode("utf-8").strip()
                result = parse_serial_line(raw)

                if result is None:
                    pass

                elif result[0] == "reset":
                    if current_length_yd > 0:
                        ball_num = len(balls) + 1
                        balls.append(current_length_yd)
                        print(f"\n  ✓ Ball {ball_num} logged: {current_length_yd:.2f} yd")
                        print(f"  Session total: {sum(balls):.2f} yd across {len(balls)} ball(s)\n")
                        ax.axvline(
                            x=time.time() - session_start_time,
                            color="red",
                            linestyle="--",
                            alpha=0.5
                        )
                        ax.text(
                            time.time() - session_start_time,
                            max(length_points) if length_points else 0,
                            f" Ball {ball_num}",
                            color="red",
                            fontsize=8
                        )
                    current_length_yd = 0.0
                    ser.write(b"RESET\n")

                elif result[0] == "length":
                    current_length_yd = result[1]
                    elapsed = time.time() - session_start_time
                    cumulative = current_length_yd + sum(balls)
                    time_points.append(elapsed)
                    length_points.append(cumulative)
                    print(
                        f"  Current ball: {current_length_yd:.2f} yd  |  "
                        f"Session total: {cumulative:.2f} yd",
                        end="\r"
                    )
            keyboard = check_keyboard()
            if keyboard == "reset":
                if current_length_yd > 0:
                    ball_num = len(balls) + 1
                    balls.append(current_length_yd)
                    print(f"\n  ✓ Ball {ball_num} logged: {current_length_yd:.2f} yd")
                    print(f"  Session total: {sum(balls):.2f} yd across {len(balls)} ball(s)\n")
                    ax.axvline(
                        x=time.time() - session_start_time,
                        color="red",
                        linestyle="--",
                        alpha=0.5
                 )
                    ax.text(
                        time.time() - session_start_time,
                        max(length_points) if length_points else 0,
                        f" Ball {ball_num}",
                        color="red",
                        fontsize=8
        )
                current_length_yd = 0.0

            # Update chart every 2 seconds instead of every loop
            if time.time() - last_chart_update > 2.0:
                if len(time_points) > 1:
                    line_plot.set_data(time_points, length_points)
                    ax.relim()
                    ax.autoscale_view()
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                last_chart_update = time.time()
        

    except KeyboardInterrupt:
        print("\n\n  Session ended.")

    # Final chart update and pause
    if len(time_points) > 1:
        line_plot.set_data(time_points, length_points)
        ax.relim()
        ax.autoscale_view()
        ax.set_title("Yarn Length Over Time — Session Complete")
        fig.canvas.draw()

    plt.ioff()
    print("\n  Close the chart window to see session summary.")
    plt.show(block=True)


# ---- SUMMARY AND LOGGING ----

def show_summary():
    global balls, current_length_yd, session_start_time

    if current_length_yd > 0:
        save = input("\n  Log final ball before summary? (y/n): ")
        if save.lower() == "y":
            balls.append(current_length_yd)

    if not balls:
        print("\n  No balls logged this session.")
        return

    total = sum(balls)
    count = len(balls)
    average = total / count
    total_seconds = int(time.time() - session_start_time)
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    print("\n============================================================")
    print("                    SESSION SUMMARY")
    print("============================================================")
    for i, length in enumerate(balls):
        print(f"  Ball {i+1}: {length:.2f} yd  ({length * 0.9144:.2f} m)")
    print(f"\n  Total yarn:    {total:.2f} yd  ({total * 0.9144:.2f} m)")
    print(f"  Balls wound:   {count}")
    print(f"  Average ball:  {average:.2f} yd")
    print(f"  Total time:    {minutes}m {seconds}s")
    print("============================================================")

    save_log = input("\n  Save session log to file? (y/n): ")
    if save_log.lower() == "y":
        save_session_log(total, count, average, minutes, seconds)


def save_session_log(total, count, average, minutes, seconds):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"yarn_session_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("YARN LENGTH TRACKER — SESSION LOG\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 40 + "\n\n")
        for i, length in enumerate(balls):
            f.write(f"Ball {i+1}: {length:.2f} yd  ({length * 0.9144:.2f} m)\n")
        f.write(f"\nTotal:   {total:.2f} yd  ({total * 0.9144:.2f} m)\n")
        f.write(f"Balls:   {count}\n")
        f.write(f"Average: {average:.2f} yd\n")
        f.write(f"Time:    {minutes}m {seconds}s\n")

    print(f"\n  Session saved to {filename}")

# ---- ENTRY POINT ----

def main():
    ser = connect_to_arduino()
    if ser is None:
        print("  Could not connect to Arduino. Exiting.")
        return

    try:
        run_session(ser)
        show_summary()
    finally:
        ser.close()
        print("  Serial connection closed.")


main()