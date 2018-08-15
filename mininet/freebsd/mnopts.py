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

CONTROLLERS = { #'ref': Controller,
                #'ovsc': OVSController,
                #'nox': NOX,
                'remote': RemoteController,
                'ryu': Ryu,
                #'swd': Switchd,
                'default': DefaultController,
                'none': NullController }

SWITCHES = { #'user': UserSwitch,
             'ovs': OVSSwitch,
             'ovsbr' : OVSBridge,
             # Keep ovsk for compatibility with 2.0
             #'ovsk': OVSSwitch,
             #'ivs': IVSSwitch,
             #'ifsw': IfSwitch,
             'sysbr': ClassicBridge,
             'default': DefaultSwitch }

HOSTS = { #'rt': specialClass( CPULimitedHost, defaults=dict( sched='rt' ) ),
          #'cfs': specialClass( CPULimitedHost, defaults=dict( sched='cfs' ) )
          'proc': Host }

LINKS = { #'tc': TCLink,
          #'tcu': TCULink,
          'ovs': OVSLink,
          'default': Link }
