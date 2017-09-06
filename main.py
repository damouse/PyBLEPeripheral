import sys
import array
from random import randint

import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import advertisement
import service
import constants

# Global main loop
mainloop = None


class ServiceAdvertisement(advertisement.Advertisement):

    def __init__(self, bus, index, gatt):
        advertisement.Advertisement.__init__(self, bus, index, 'peripheral')

        for service in gatt.services:
            print "Adding service UUID: ", service.uuid
            self.add_service_uuid(service.uuid)

        # self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
        # self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.include_tx_power = True


#
# Handler Callbacks
#
def register_ad_cb():
    print 'Advertisement registered'


def register_ad_error_cb(error):
    print 'Failed to register advertisement: ' + str(error)
    mainloop.quit()


def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = service.find_adapter(bus)

    if not adapter:
        print('GattManager1 interface not found')
        return

    adapter_obj = bus.get_object(advertisement.BLUEZ_SERVICE_NAME, adapter)
    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_obj = bus.get_object(advertisement.BLUEZ_SERVICE_NAME, adapter)
    ad_manager = dbus.Interface(ad_obj, advertisement.LE_ADVERTISING_MANAGER_IFACE)

    service_obj = bus.get_object(constants.BLUEZ_SERVICE_NAME, adapter)
    service_manager = dbus.Interface(service_obj, constants.GATT_MANAGER_IFACE)

    app = service.Application(bus)
    ad = ServiceAdvertisement(bus, 0, app)

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    print("Registering Advertisement...")
    ad_manager.RegisterAdvertisement(ad.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    mainloop.run()


if __name__ == '__main__':
    main()
