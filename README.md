# Bluetooth Client

Sample BLE peripheral implementation written in Python. Its mostly a mix of existing sources. 

This is a Python 2.7 project that uses `pipenv`. It was tested on a Raspberry Pi 3 with `bluez` version 5.46.

Note: this project doesn't appear to work with Python 3-- could not install `python-dbus` on 3.

## Setup

This section details how to configure a Raspberry Pi to run this code. The first section is setup just for this program, while the second contains system configuration instructions. 

### Client Setup

Install `pipenv` with:

```
pip install pipenv
```

Install dependencies:

```
pipenv install
```

Activate `virtualenv` (you must do this every time before running the project):

```
pipenv shell
```

Run the project: 

```
python main.py
```

Add a new dependency:

```
pipenv install [packageName]
```

### System Setup

Follow the guide [here](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation) to install the `bluez` stack on your RPi. The Pi I worked with to write these instructions already had a `bluez` stack installed, so I can't guarantee the instructions will get you all the way there. You'll at least need the following additional packages:

```
sudo apt-get install libdbus-glib-1-dev
```
