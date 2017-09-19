# Bluetooth Client

Sample BLE peripheral implementation written in two parts: controller in smartBASIC and host written in Python 3. This software is meant to run on a LairdCP BL652. 

The BASIC controller implements a GATT server with custom UUIDs that exposes LHR-specifc characteristics as endpoints to communicate with a mobile app. Its largely a dumb tunnel with one inbound and one outbound interface both on the bluetooth side and the host side.

The Python3 host interacts with the controller through the aforementioned 2 endpoints over a serial connection.

## Setup

Setting up the Pi with LairdCP is not covered here, mostly because @damouse is not the one who set it up.

Install required python packages:

```
pip3 install pyserial
```

To run the controller, open `UwTerminalX`, establish a connection with the breakout board, then rightclick the screen and select `Compile and Load`, choosing `gatt_program.sb`

To start the host, make sure the program is started, `UwTerminalX` is off, and then run `main.py`.

## Interacting with LaircCP BL625

This is the breakout board that houses our bluetooth chip. 

Some common commands: 

- Reset the device: `at`
- Erase memory: `at&f 1`
