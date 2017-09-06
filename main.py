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

    adapter_obj = bus.get_object(advertisement.BLUEZ_SERVICE_NAME, adapter)
    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_obj = bus.get_object(advertisement.BLUEZ_SERVICE_NAME, adapter)
    ad_manager = dbus.Interface(ad_obj, advertisement.LE_ADVERTISING_MANAGER_IFACE)

    service_obj = bus.get_object(gatt.BLUEZ_SERVICE_NAME, adapter)
    service_manager = dbus.Interface(service_obj, gatt.GATT_MANAGER_IFACE)

    app = gatt.Application(bus)
    mainloop = GObject.MainLoop()
    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=gatt.register_app_cb,
                                        error_handler=gatt.register_app_error_cb)

    mainloop.run()


if __name__ == '__main__':
    main()
