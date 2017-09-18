#!/usr/bin/env python
import serial
import kbhit

ser = serial.Serial(
  port='/dev/ttyAMA0',
  baudrate = 115200,
  #parity=serial.PARITY_NONE,
  #topbits=serial.STOPBITS_ONE,
  #bytesize=serial.EIGHTBITS,
  timeout=0.1,
  rtscts=1
)

while 1:
    while ser.in_waiting:
        #x = ser.read()
        x = ser.readline()
        x = x.decode()
        print (x)

    while kbhit.kbhit():
        r = input()
        print(r)
        ser.write(bytes(r, 'UTF-8'))
        
ser.close()
