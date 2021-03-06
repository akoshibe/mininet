"""
A interface object that relies on ifconfig(8) and ip(8) to manipulate
network interfaces and devices.
"""
from mininet.baseintf import BaseIntf

class Intf( BaseIntf ):
    """Interface objects that use 'ip' and 'ifconfig' to configure the
    underlying interface that it represents"""

    def setMAC( self, macstr ):
        self.mac = macstr
        return ( self.ifconfig( 'down' ) +
                 self.ifconfig( 'hw', 'ether', macstr ) +
                 self.ifconfig( 'up' ) )

    def rename( self, newname ):
        "Rename interface"
        self.ifconfig( 'down' )
        result = self.cmd( 'ip link set', self.name, 'name', newname )
        self.name = newname
        self.ifconfig( 'up' )

    def delete( self ):
        "Delete interface"
        self.cmd( 'ip link del ' + self.name )
        # We used to do this, but it slows us down:
        # if self.node.inNamespace:
        # Link may have been dumped into root NS
        # quietRun( 'ip link del ' + self.name )
        self.node.delIntf( self )
        self.link = None

    def status( self ):
        "Return intf status as a string"
        links, _err, _result = self.node.pexec( 'ip link show' )
        if self.name in links:
            return "OK"
        else:
            return "MISSING"
