import array
from random import randint
import sys

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import constants

mainloop = None


class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(HeartRateService(bus, 0))
        # self.add_service(BatteryService(bus, 1))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(constants.DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()

            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()

                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            constants.GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(constants.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != constants.GATT_SERVICE_IFACE:
            raise constants.InvalidArgsException()

        return self.get_properties()[constants.GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):

    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            constants.GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(
                    self.get_descriptor_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(constants.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != constants.GATT_CHRC_IFACE:
            raise constants.InvalidArgsException()

        return self.get_properties()[constants.GATT_CHRC_IFACE]

    @dbus.service.method(constants.GATT_CHRC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise constants.NotSupportedException()

    @dbus.service.method(constants.GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise constants.NotSupportedException()

    @dbus.service.method(constants.GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise constants.NotSupportedException()

    @dbus.service.method(constants.GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise constants.NotSupportedException()

    @dbus.service.signal(constants.DBUS_PROP_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            constants.GATT_DESC_IFACE: {
                'Characteristic': self.chrc.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != constants.GATT_DESC_IFACE:
            raise constants.InvalidArgsException()

        return self.get_properties()[constants.GATT_DESC_IFACE]

    @dbus.service.method(constants.GATT_DESC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise constants.NotSupportedException()

    @dbus.service.method(constants.GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise constants.NotSupportedException()


class HeartRateService(Service):
    HR_UUID = '180D'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
        self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
        self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
        self.energy_expended = 0


class HeartRateMeasurementChrc(Characteristic):
    HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.HR_MSRMT_UUID,
            ['notify'],
            service)
        self.notifying = False
        self.hr_ee_count = 0

    def hr_msrmt_cb(self):
        value = []
        value.append(dbus.Byte(0x06))

        value.append(dbus.Byte(randint(90, 130)))

        if self.hr_ee_count % 10 == 0:
            value[0] = dbus.Byte(value[0] | 0x08)
            value.append(dbus.Byte(self.service.energy_expended & 0xff))
            value.append(dbus.Byte((self.service.energy_expended >> 8) & 0xff))

        self.service.energy_expended = min(0xffff, self.service.energy_expended + 1)
        self.hr_ee_count += 1

        print('Updating value: ' + repr(value))

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {'Value': value}, [])
        return self.notifying

    def _update_hr_msrmt_simulation(self):
        print('Update HR Measurement Simulation')

        if not self.notifying:
            return

        GObject.timeout_add(1000, self.hr_msrmt_cb)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_hr_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_hr_msrmt_simulation()


class BodySensorLocationChrc(Characteristic):
    BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.BODY_SNSR_LOC_UUID,
            ['read'],
            service)

    def ReadValue(self, options):
        # Return 'Chest' as the sensor location.
        return [0x01]


class HeartRateControlPointChrc(Characteristic):
    HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.HR_CTRL_PT_UUID,
            ['write'],
            service)

    def WriteValue(self, value, options):
        print('Heart Rate Control Point WriteValue called', value)
        text = ''.join([chr(character) for value in ssid])
        print('Have text: ' + str(text))

        if len(value) != 1:
            raise constants.InvalidValueLengthException()

        byte = value[0]
        print('Control Point value: ' + repr(byte))

        if byte != 1:
            raise constants.FailedException("0x80")

        print('Energy Expended field reset!')
        self.service.energy_expended = 0


class BatteryService(Service):
    BATTERY_UUID = '180f'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))


class BatteryLevelCharacteristic(Characteristic):
    BATTERY_LVL_UUID = '2a19'

    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, self.BATTERY_LVL_UUID, ['read', 'notify'], service)
        self.notifying = False
        self.battery_lvl = 100
        GObject.timeout_add(5000, self.drain_battery)

    def notify_battery_level(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
            constants.GATT_CHRC_IFACE,
            {'Value': [dbus.Byte(self.battery_lvl)]}, [])

    def drain_battery(self):
        if self.battery_lvl > 0:
            self.battery_lvl -= 2
            if self.battery_lvl < 0:
                self.battery_lvl = 0
        print('Battery Level drained: ' + repr(self.battery_lvl))
        self.notify_battery_level()
        return True

    def ReadValue(self, options):
        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False


class CharacteristicUserDescriptionDescriptor(Descriptor):
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        Descriptor.__init__(
            self, bus, index,
            self.CUD_UUID,
            ['read', 'write'],
            characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise constants.NotPermittedException()
        self.value = value


def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'), constants.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if constants.GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(bus.get_object(constants.BLUEZ_SERVICE_NAME, adapter), constants.GATT_MANAGER_IFACE)

    app = Application(bus)
    mainloop = GObject.MainLoop()
    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
    mainloop.run()


if __name__ == '__main__':
    main()
