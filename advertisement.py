'''
Implementatino of DBus Advertisement class. This class is light on comments-- its 
lifted from the bluez examples almost wholesale.
'''

import array
from random import randint

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import constants


class Advertisement(dbus.service.Object):
    '''
    Base Advertisement object, used to broadcast LHR services.
    '''
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type

        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids, signature='s')

        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids, signature='s')

        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(self.manufacturer_data, signature='qv')

        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data, signature='sv')

        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)

        return {constants.LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    @dbus.service.method(constants.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        print 'GetAll'
        if interface != constants.LE_ADVERTISEMENT_IFACE:
            raise constants.InvalidArgsException()

        print 'returning props'
        return self.get_properties()[constants.LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(constants.LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print '%s: Released!' % self.path


class ServiceAdvertisement(advertisement.Advertisement):
    '''
    Our (LHR) application specific advertisement. Uses the UUIDs of services registered
    in the passed 'gatt' object's services UUIDs
    '''

    def __init__(self, bus, index, gatt):
        advertisement.Advertisement.__init__(self, bus, index, 'peripheral')

        # Expose services
        for service in gatt.services:
            self.add_service_uuid(service.uuid)


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'), constants.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if constants.GATT_MANAGER_IFACE in props.keys():
            return o

    return None









