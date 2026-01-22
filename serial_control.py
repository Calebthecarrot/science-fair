import serial
import time

arduino = serial.Serial("COM3", 9600, timeout=1)
time.sleep(2)

def send_angle(angle):
    msg = f"ANGLE:{angle:.1f}\n"
    arduino.write(msg.encode())
    print("Sent:", msg.strip())
