#!/usr/bin/env python3
'''
Host implementation. Communicates with the BASIC controller (which drives the LairdCP)
through a serial connection. 

Both this program and the controller itself are relatively dumb pipes-- they take very 
little notice of whats going on with the data passing through them, and intentionally 
only expose a pair of channels (in and out) on each of their interfaces. The controller
has in/out endpoints on its BLE channel with Mobile, and in/out endpoints on the serial 
connection with the host. This program may have a few more. 
'''

import serial
import threading

# Constant
SERIAL_PORT = '/dev/ttyAMA0'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 0.1
SERIAL_RTSCTS = 1


class SerialConnection(object):
    '''
    Simple wrapper around a serial connection that is threadsafe
    '''

    def __init__(self, port):
        super(SerialConnection, self).__init__()
        self._serial = serial.Serial(port=port,
                                     baudrate=SERIAL_BAUDRATE,
                                     timeout=SERIAL_TIMEOUT,
                                     rtscts=SERIAL_RTSCTS)

        self._lock = threading.Lock()

    def read(self):
        '''
        Reads a line from the serial connection. Blocks if another 
        read() or write() is in progress
        '''
        with self._lock:
            return self._serial.readline()

    def write(self, msg):
        ''' Write a message to the serial connection '''
        msg += '\r'

        with self._lock:
            self._serial.write(msg.encode())

    def waiting(self):
        return self._serial.in_waiting


conn = SerialConnection(SERIAL_PORT)


def main():
    first = True

    while True:
        beb = conn._serial.in_waiting

        while beb > 0:
            print(f"Waiting with bytes: {beb}")
            x = conn.read()
            x = x.decode()
            print(x)

        if first:
            print("First....")
            conn.write("txpower\r")
            first = False


if __name__ == '__main__':
    main()
