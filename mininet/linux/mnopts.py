"""
Options used by mn that differ wildly with OS.
"""
from mininet.link import Link, TCLink, TCULink, OVSLink
from mininet.node import ( Host, CPULimitedHost, Controller, OVSController,
                           Ryu, NOX, RemoteController, findController,
                           DefaultController, NullController,
                           UserSwitch, OVSSwitch, OVSBridge, IVSSwitch,
                           DefaultSwitch )
from mininet.nodelib import LinuxBridge
from mininet.util import specialClass

ClassicBridge = LinuxBridge
DefaultControllers = ( Controller, OVSController )
DefaultSwitch = OVSSwitch

CONTROLLERS = { 'ref': Controller,
                'ovsc': OVSController,
                'nox': NOX,
                'remote': RemoteController,
                'ryu': Ryu,
                'default': DefaultController,
                'none': NullController }

SWITCHES = { 'user': UserSwitch,
             'ovs': OVSSwitch,
             'ovsbr' : OVSBridge,
             # Keep ovsk for compatibility with 2.0
             'ovsk': OVSSwitch,
             'ivs': IVSSwitch,
             'sysbr': ClassicBridge,
             'default': DefaultSwitch }

HOSTS = { 'proc': Host,
          'rt': specialClass( CPULimitedHost, defaults=dict( sched='rt' ) ),
          'cfs': specialClass( CPULimitedHost, defaults=dict( sched='cfs' ) ) }

LINKS = { 'tc': TCLink,
          'tcu': TCULink,
          'ovs': OVSLink,
          'default': Link }
