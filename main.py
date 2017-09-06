import advertisement
import gatt

import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import sys
import array
from random import randint

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject


mainloop = None


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = gatt.find_adapter(bus)

    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(bus.get_object(gatt.BLUEZ_SERVICE_NAME, adapter), gatt.GATT_MANAGER_IFACE)

    app = gatt.Application(bus)
    mainloop = GObject.MainLoop()
    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=gatt.register_app_cb, error_handler=gatt.register_app_error_cb)
    mainloop.run()


if __name__ == '__main__':
    main()
