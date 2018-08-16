"""
Options used by mn that differ wildly with OS.
"""
from mininet.link import Link, OVSLink
from mininet.node import ( Host, Ryu, RemoteController, NullController,
                           DefaultController, OVSSwitch, OVSBridge )
from mininet.nodelib import IfBridge

ClassicBridge = IfBridge
DefaultControllers = ( Ryu, )
DefaultSwitch = OVSSwitch

CONTROLLERS = { 'remote': RemoteController,
                'ryu': Ryu,
                'default': DefaultController,
                'none': NullController }

SWITCHES = { 'ovs': OVSSwitch,
             'ovsbr' : OVSBridge,
             'sysbr': ClassicBridge,
             'default': DefaultSwitch }

HOSTS = { 'proc': Host }

LINKS = { 'ovs': OVSLink,
          'default': Link }
