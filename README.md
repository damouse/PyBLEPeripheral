# Bluetooth Client

Sample BLE peripheral implementation written in Python. Its mostly a mix of existing sources. 

This is a Python 2.7 project because I couldn't get the `dbus` libraries installed and working on Python 3.4. It was tested on a Raspberry Pi 3 with `bluez` version 5.46.

## Setup

This section details how to configure a Raspberry Pi to run this code. The first section is setup just for this program, while the second contains system configuration instructions. 

### Client Setup

Install dependencies:

```
pip install 
```


### System Setup

Follow the guide [here](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation) to install the `bluez` stack on your RPi. The Pi I worked with to write these instructions already had a `bluez` stack installed, so I can't guarantee the instructions will get you all the way there. You'll at least need the following additional packages:

```
sudo apt-get install libdbus-glib-1-dev
```

If you still encounter issues, check out this [helpful gist](https://gist.github.com/larsblumberg/2335c0ba97f805a2b996f1a7c3ac9571) for other missing packages. 