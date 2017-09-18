#!/usr/bin/env python3
import serial

ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=115200,
    timeout=0.1,
    rtscts=1
)


def main():
    first = True

    while True:
        while ser.in_waiting:
            x = ser.readline()
            x = x.decode()
            print (x)

        if first:
            ser.write("txpower\r")
            first = False

    ser.close()


if __name__ == '__main__':
    main()
