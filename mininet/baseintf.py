"""
The base network interface object that Links and Nodes understand, and other
interface objects are based upon.
"""

from mininet.log import error
import re

class BaseIntf( object ):
    """Basic interface object that can configure itself."""

    def __init__( self, name, node, port=None, link=None,
                  mac=None, **params ):
        """name: interface name (e.g. h1-eth0)
           node: owning node (where this intf most likely lives)
           link: parent link if we're part of a link
           other arguments are passed to config()"""
        self.node = node
        self.name = name
        self.link = link
        self.mac = mac
        self.ip, self.prefixLen = None, None

        # if interface is lo/lo0, we know the ip is 127.0.0.1.
        # This saves an ifconfig command per node
        if self.name == 'lo' or self.name == 'lo0':
            self.ip = '127.0.0.1'
            self.prefixLen = 8
        # Add to node (and move ourselves if necessary )
        moveIntfFn = params.pop( 'moveIntfFn', None )
        if moveIntfFn:
            node.addIntf( self, port=port, moveIntfFn=moveIntfFn )
        else:
            node.addIntf( self, port=port )
        # Save params for future reference
        self.params = params
        self.config( **params )

    def cmd( self, *args, **kwargs ):
        "Run a command in our owning node"
        return self.node.cmd( *args, **kwargs )

    def ifconfig( self, *args ):
        "Configure ourselves using ifconfig"
        return self.cmd( 'ifconfig', self.name, *args )

    def setIP( self, ipstr, prefixLen=None ):
        """Set our IP address"""
        # This is a sign that we should perhaps rethink our prefix
        # mechanism and/or the way we specify IP addresses
        if '/' in ipstr:
            self.ip, self.prefixLen = ipstr.split( '/' )
            return self.ifconfig( ipstr, 'up' )
        else:
            if prefixLen is None:
                raise Exception( 'No prefix length set for IP address %s'
                                 % ( ipstr, ) )
            self.ip, self.prefixLen = ipstr, prefixLen
            return self.ifconfig( '%s/%s' % ( ipstr, prefixLen ) )

    def setMAC( self, macstr ):
        """Set the MAC address for an interface.
           macstr: MAC address as string"""
        pass

    _ipMatchRegex = re.compile( r'\d+\.\d+\.\d+\.\d+' )
    _macMatchRegex = re.compile( r'..:..:..:..:..:..' )

    def updateIP( self ):
        "Return updated IP address based on ifconfig"
        # use pexec instead of node.cmd so that we dont read
        # backgrounded output from the cli.
        ifconfig, _err, _exitCode = self.node.pexec(
            'ifconfig %s' % self.name )
        ips = self._ipMatchRegex.findall( ifconfig )
        self.ip = ips[ 0 ] if ips else None
        return self.ip

    def updateMAC( self ):
        "Return updated MAC address based on ifconfig"
        ifconfig = self.ifconfig()
        macs = self._macMatchRegex.findall( ifconfig )
        self.mac = macs[ 0 ] if macs else None
        return self.mac

    # Instead of updating ip and mac separately,
    # use one ifconfig call to do it simultaneously.
    # This saves an ifconfig command, which improves performance.

    def updateAddr( self ):
        "Return IP address and MAC address based on ifconfig."
        ifconfig = self.ifconfig()
        ips = self._ipMatchRegex.findall( ifconfig )
        macs = self._macMatchRegex.findall( ifconfig )
        self.ip = ips[ 0 ] if ips else None
        self.mac = macs[ 0 ] if macs else None
        return self.ip, self.mac

    def IP( self ):
        "Return IP address"
        return self.ip

    def MAC( self ):
        "Return MAC address"
        return self.mac

    def isUp( self, setUp=False ):
        "Return whether interface is up"
        if setUp:
            cmdOutput = self.ifconfig( 'up' )
            # no output indicates success
            if cmdOutput:
                error( "Error setting %s up: %s " % ( self.name, cmdOutput ) )
                return False
            else:
                return True
        else:
            return "UP" in self.ifconfig()

    def rename( self, newname ):
        """Rename interface"""
        pass

    # The reason why we configure things in this way is so
    # That the parameters can be listed and documented in
    # the config method.
    # Dealing with subclasses and superclasses is slightly
    # annoying, but at least the information is there!

    def setParam( self, results, method, **param ):
        """Internal method: configure a *single* parameter
           results: dict of results to update
           method: config method name
           param: arg=value (ignore if value=None)
           value may also be list or dict"""
        name, value = param.items()[ 0 ]
        f = getattr( self, method, None )
        if not f or value is None:
            return
        if isinstance( value, list ):
            result = f( *value )
        elif isinstance( value, dict ):
            result = f( **value )
        else:
            result = f( value )
        results[ name ] = result
        return result

    def config( self, mac=None, ip=None, ifconfig=None,
                up=True, **_params ):
        """Configure Node according to (optional) parameters:
           mac: MAC address
           ip: IP address
           ifconfig: arbitrary interface configuration
           Subclasses should override this method and call
           the parent class's config(**params)"""
        # If we were overriding this method, we would call
        # the superclass config method here as follows:
        # r = Parent.config( **params )
        r = {}
        self.setParam( r, 'setMAC', mac=mac )
        self.setParam( r, 'setIP', ip=ip )
        self.setParam( r, 'isUp', up=up )
        self.setParam( r, 'ifconfig', ifconfig=ifconfig )
        return r

    def delete( self ):
        "Delete interface"
        pass

    def status( self ):
        "Return intf status as a string"
        pass

    def __repr__( self ):
        return '<%s %s>' % ( self.__class__.__name__, self.name )

    def __str__( self ):
        return self.name
