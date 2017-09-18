#!/usr/bin/env python3

import pydbus

try:
    from gi.repository import GObject
    from gi.repository import GLib
except ImportError:
    import gobject as GObject


class Advertisement(object):
    """
      <node>
        <interface name="org.bluez.LEAdvertisement1">
          <method name="Release">
            <annotation name="org.freedesktop.DBus.Method.NoReply" value="true"/>
          </method>
          <annotation name="org.freedesktop.DBus.Properties.PropertiesChanged" value="const"/>
          <property name="Type" type="s" access="read"/>
          <property name="ServiceUUIDs" type="as" access="read"/>
          <property name="ManufacturerData" type="a{sv}" access="read"/>
          <property name="SolicitUUIDs" type="as" access="read"/>
          <property name="ServiceData" type="a{sv}" access="read"/>
          <property name="IncludeTxPower" type="b" access="read"/>
        </interface>
      </node>
    """

    def __init__(self, bus):
        self.Type = 'peripheral'
        self.ServiceUUIDs = []
        self.ManufacturerData = {}
        self.SolicitUUIDs = []
        self.ServiceData = {}
        self.IncludeTxPower = False
        bus.register_object('/nic/twigpilot', self, None)

    def Release(self):
        print('{}: Advertisement Released!'.format(self))


def main():
    bus = pydbus.SystemBus()
    adaptor = bus.get('org.bluez', '/org/bluez/hci0')
    adaptor.Powered = True
    adaptor.Alias = 'SeeMe'

    advertisement = Advertisement(bus)
    advertisement.IncludeTxPower = True

    adaptor.RegisterAdvertisement('/nic/twigpilot', {})

    loop = GLib.MainLoop()

    try:
        print("Starting advertisement")
        loop.run()
    except KeyboardInterrupt:
        loop.quit()


if __name__ == '__main__':
    main()
