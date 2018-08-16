"""
Options used by mn that differ wildly with OS.
"""
from mininet.link import Link
from mininet.node import ( Host, RemoteController,  NullController,
                           DefaultController, Switchd, IfSwitch )
from mininet.nodelib import Bridge4


ClassicBridge = Bridge4
DefaultControllers = ( Switchd, )
DefaultSwitch = IfSwitch

CONTROLLERS = { 'remote': RemoteController,
                'swd': Switchd,
                'default': DefaultController,
                'none': NullController }

SWITCHES = { 'ifsw': IfSwitch,
             'sysbr': ClassicBridge,
             'default': DefaultSwitch }

HOSTS = { 'proc': Host }

LINKS = { 'default': Link }
