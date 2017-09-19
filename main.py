#!/usr/bin/env python3
'''
Host implementation. Communicates with the BASIC controller (which drives the LairdCP)
through a serial connection. 

Both this program and the controller itself are relatively dumb pipes-- they take very 
little notice of whats going on with the data passing through them, and intentionally 
only expose a pair of channels (in and out) on each of their interfaces. The controller
has in/out endpoints on its BLE channel with Mobile, and in/out endpoints on the serial 
connection with the host. This program may have a few more. 

You know, I don't think we need a heavily multithreaded implementation here. Its more correct, 
but the technical risk is limited by the bandwidth that the 6 channels are using, which
is both light and limited by the concurrent design of the communication patterns.

Then again, because the serial connection blocks, maybe the threading implementation is safer.
'''

import serial
from threading import Thread
from queue import Queue

# Constants
SERIAL_PORT = '/dev/ttyAMA0'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 0.1
SERIAL_RTSCTS = 1


class SerialConnection(object):
    '''
    Manages the serial connection on its own internal thread, using a 
    queue to batch up messages that arrive from the controller. 
    '''

    def __init__(self, port):
        super(SerialConnection, self).__init__()
        self._serial = serial.Serial(port=port, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT, rtscts=SERIAL_RTSCTS)

        self.queue = Queue()
        self.thread = None
        self.is_open = False

    def open(self):
        ''' This doesen't open the serial connection, it starts the thread that listens to it '''
        self.is_open = True
        self.thread = Thread(target=self.read)
        self.thread.start()

    def close(self):
        ''' Kill the outbound thread, if it exists '''
        if not self.is_open:
            return

        self.is_open = False
        self.thread.join()

    def write(self, msg):
        ''' Write a message to the serial connection '''
        msg += '\r'
        self._serial.write(msg.encode())

    def spinwait(self):
        ''' Spins on the inbound queue, returning messages as they arrive '''
        while self.is_open:
            msg = self.queue.get()
            print("Have message: ", msg)

    def _read(self):
        ''' Starts the internal read loop '''
        while self.is_open:
            while self._serial.in_waiting:
                x = self._serial.readline()
                x = x.decode()
                print(x)
                self.queue.put(x)


class ControllerManager(object):
    '''
    Manages the smartBASIC controller using the SerialConnection class above
    for communication
    '''

    def __init__(self):
        super(ControllerManager, self).__init__()

    def send(self, status, error):
        ''' 
        Send a response through to the controller. 

        :param status:
        '''
        pass


def main():
    conn = SerialConnection(SERIAL_PORT)
    conn.open()
    conn.write("txpower")
    conn.spinwait()


if __name__ == '__main__':
    main()









































