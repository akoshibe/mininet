"""
Node Library for Mininet

This contains additional Node types which you may find to be useful.
"""
from os import uname

from mininet.node import Node, Switch
from mininet.log import info, warn
from mininet.moduledeps import pathCheck
from mininet.util import quietRun


class LinuxBridge( Switch ):
    "Linux Bridge (with optional spanning tree)"

    nextPrio = 100  # next bridge priority for spanning tree

    def __init__( self, name, stp=False, prio=None, **kwargs ):
        """stp: use spanning tree protocol? (default False)
           prio: optional explicit bridge priority for STP"""
        self.stp = stp
        if prio:
            self.prio = prio
        else:
            self.prio = LinuxBridge.nextPrio
            LinuxBridge.nextPrio += 1
        Switch.__init__( self, name, **kwargs )

    def connected( self ):
        "Are we forwarding yet?"
        if self.stp:
            return 'forwarding' in self.cmd( 'brctl showstp', self )
        else:
            return True

    def start( self, _controllers ):
        "Start Linux bridge"
        self.cmd( 'ifconfig', self, 'down' )
        self.cmd( 'brctl delbr', self )
        self.cmd( 'brctl addbr', self )
        if self.stp:
            self.cmd( 'brctl setbridgeprio', self.prio )
            self.cmd( 'brctl stp', self, 'on' )
        for i in self.intfList():
            if self.name in i.name:
                self.cmd( 'brctl addif', self, i )
        self.cmd( 'ifconfig', self, 'up' )

    def stop( self, deleteIntfs=True ):
        """Stop Linux bridge
           deleteIntfs: delete interfaces? (True)"""
        self.cmd( 'ifconfig', self, 'down' )
        self.cmd( 'brctl delbr', self )
        super( LinuxBridge, self ).stop( deleteIntfs )

    def dpctl( self, *args ):
        "Run brctl command"
        return self.cmd( 'brctl', *args )

    @classmethod
    def setup( cls ):
        "Check dependencies and warn about firewalling"
        pathCheck( 'brctl', moduleName='bridge-utils' )
        # Disable Linux bridge firewalling so that traffic can flow!
        for table in 'arp', 'ip', 'ip6':
            cmd = 'sysctl net.bridge.bridge-nf-call-%stables' % table
            out = quietRun( cmd ).strip()
            if out.endswith( '1' ):
                warn( 'Warning: Linux bridge may not work with', out, '\n' )


class IfBridge( Switch ):
    "FreeBSD if_bridge(4) Node (with optional spanning tree)."

    nextPrio = 100  # next bridge priority for spanning tree

    def __init__( self, name, stp=False, prio=None, **kwargs ):
        """stp: use spanning tree protocol? (default False)
           prio: optional explicit bridge priority for STP"""
        self.stp = stp
        if prio:
            self.prio = prio
        else:
            self.prio = IfBridge.nextPrio
            IfBridge.nextPrio += 1
        Switch.__init__( self, name, **kwargs )

    def connected( self ):
        "Are we forwarding yet?"
        if self.stp:
            return 'UP' in self.cmd( 'ifconfig', self.bname )
        else:
            return True

    def start( self, _controllers ):
        "Start bridge. Retain the bridge's name to save on ifconfig calls"
        res = quietRun( 'ifconfig bridge create' )[:-1]
        self.bname = res
        quietRun( 'ifconfig %s vnet %s' % ( res, self ) )
        addcmd, stpcmd = '', ''
        for i in self.intfList():
            if self.name in i.name or 'epair' in i.name:
                addcmd += ' addm ' + i.name
                if self.stp:
                    # STP settings are per-port. perhaps enable that as an option.
                    stpcmd += ' stp ' + i.name
                self.cmd( 'ifconfig', i.name, 'up' )
        self.cmd( 'ifconfig', res, addcmd )
        if self.stp:
            # ifconfig 'stp' and 'priority' latter default 32768
            self.cmd( 'ifconfig', res, 'priority', self.prio )
            self.cmd( 'ifconfig', res, stpcmd )
        self.cmd( 'ifconfig', res, 'up' )

    def stop( self, deleteIntfs=True ):
        """Stop bridge
           deleteIntfs: delete interfaces? (True)"""
        self.cmd( 'ifconfig %s destroy' % self.bname )
        super( IfBridge, self ).stop( deleteIntfs )

    def dpctl( self, *args ):
        "Run brctl command"
        # actually ifconfig
        return self.cmd( 'ifconfig', self.bname, *args )

    @classmethod
    def setup( cls ):
        "Check dependencies"
        if 'if_bridge' not in lsmod():
            modprobe( 'if_bridge' )


NAT = IpfwNAT if uname()[ 0 ] == 'FreeBSD' else IptablesNAT

class IptablesNAT( Node ):
    "NAT: Provides connectivity to external network"

    def __init__( self, name, subnet='10.0/8',
                  localIntf=None, flush=False, **params):
        """Start NAT/forwarding between Mininet and external network
           subnet: Mininet subnet (default 10.0/8)
           flush: flush iptables before installing NAT rules"""
        super( NAT, self ).__init__( name, **params )

        self.subnet = subnet
        self.localIntf = localIntf
        self.flush = flush
        self.forwardState = self.cmd( 'sysctl -n net.ipv4.ip_forward' ).strip()

    def config( self, **params ):
        """Configure the NAT and iptables"""
        super( NAT, self).config( **params )

        if not self.localIntf:
            self.localIntf = self.defaultIntf()

        if self.flush:
            self.cmd( 'sysctl net.ipv4.ip_forward=0' )
            self.cmd( 'iptables -F' )
            self.cmd( 'iptables -t nat -F' )
            # Create default entries for unmatched traffic
            self.cmd( 'iptables -P INPUT ACCEPT' )
            self.cmd( 'iptables -P OUTPUT ACCEPT' )
            self.cmd( 'iptables -P FORWARD DROP' )

        # Install NAT rules
        self.cmd( 'iptables -I FORWARD',
                  '-i', self.localIntf, '-d', self.subnet, '-j DROP' )
        self.cmd( 'iptables -A FORWARD',
                  '-i', self.localIntf, '-s', self.subnet, '-j ACCEPT' )
        self.cmd( 'iptables -A FORWARD',
                  '-o', self.localIntf, '-d', self.subnet, '-j ACCEPT' )
        self.cmd( 'iptables -t nat -A POSTROUTING',
                  '-s', self.subnet, "'!'", '-d', self.subnet,
                  '-j MASQUERADE' )

        # Instruct the kernel to perform forwarding
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

        # Prevent network-manager from messing with our interface
        # by specifying manual configuration in /etc/network/interfaces
        intf = self.localIntf
        cfile = '/etc/network/interfaces'
        line = '\niface %s inet manual\n' % intf
        config = open( cfile ).read()
        if ( line ) not in config:
            info( '*** Adding "' + line.strip() + '" to ' + cfile + '\n' )
            with open( cfile, 'a' ) as f:
                f.write( line )
        # Probably need to restart network-manager to be safe -
        # hopefully this won't disconnect you
        self.cmd( 'service network-manager restart' )

    def terminate( self ):
        "Stop NAT/forwarding between Mininet and external network"
        # Remote NAT rules
        self.cmd( 'iptables -D FORWARD',
                   '-i', self.localIntf, '-d', self.subnet, '-j DROP' )
        self.cmd( 'iptables -D FORWARD',
                  '-i', self.localIntf, '-s', self.subnet, '-j ACCEPT' )
        self.cmd( 'iptables -D FORWARD',
                  '-o', self.localIntf, '-d', self.subnet, '-j ACCEPT' )
        self.cmd( 'iptables -t nat -D POSTROUTING',
                  '-s', self.subnet, '\'!\'', '-d', self.subnet,
                  '-j MASQUERADE' )
        # Put the forwarding state back to what it was
        self.cmd( 'sysctl net.ipv4.ip_forward=%s' % self.forwardState )
        super( NAT, self ).terminate()


class IpfwNAT( Node ):
    """NAT: Provides connectivity to external network using ipfw. NOTE: This
       *will* mangle IPFW rules that are already present on the host!"""

    nextId = 100 # unique NAT instance number
    ruleBase = 10 # rule number to start from

    def __init__( self, name, subnet='10.0/8',
                  localIntf=None, flush=False,
                  natid=None, rulenr=None, **params):
        """Start NAT/forwarding between Mininet and external network
           subnet: Mininet subnet (default 10.0/8)
           flush: flush existing rules before installing NAT rules"""
        super( NAT, self ).__init__( name, **params )

        self.subnet = subnet
        self.localIntf = localIntf
        self.flush = flush
        if natid:
            self.natId = str( natid )
        else:
            self.natId = str( NAT.nextId )
            NAT.nextId += 1
        if rulenr:
            self.ruleNr = str( rulenr )
        else:
            self.ruleNr = str( NAT.ruleBase )
            NAT.ruleBase += 10 # rule numbers 10 apart for each for readability
        self.forwardState = self.cmd( 'sysctl -n net.inet.ip.forwarding' ).strip()

    def ipfw( self, *args ):
        """ invoke ipfw, -q for quiet """
        return self.cmd( 'ipfw -q', *args )

    def config( self, **params ):
        """Configure the NAT and iptables"""
        super( NAT, self).config( **params )

        if not self.localIntf:
            self.localIntf = self.defaultIntf()

        if self.flush:
            self.cmd( 'sysctl net.inet.ip.forwarding=0' )
            self.ipfw( 'flush' )

        # Install NAT rules
        self.ipfw( 'nat', self.natId, 'config if', self.localIntf, 'reset' )
        self.ipfw( 'add', self.ruleNr, 'nat', self.natId,
                   'all from', self.subnet, 'to any out' )
        self.ipfw( 'add', self.ruleNr, 'nat', self.natId,
                   'all from any to any in' )

        # Instruct the kernel to perform forwarding
        self.cmd( 'sysctl net.inet.ip.forwarding=1' )

    def terminate( self ):
        "Stop NAT/forwarding between Mininet and external network"
        # Remove NAT rules
        self.ipfw( 'delete', self.ruleNr )
        self.ipfw( 'delete 32000' )

        # Put the forwarding state back to what it was
        self.cmd( 'sysctl net.inet.ip.forwarding=%s' % self.forwardState )
        super( NAT, self ).terminate()

    @classmethod
    def setup( cls ):
        """ check for dependencies, then configure and load them """
        klds = lsmod()
        kenv = quietRun( 'kenv net.inet.ip.fw.default_to_accept' ).strip()
        deny = True if kenv == '0' else False
        # if the default rule is deny all, change to allow all so hosts can
        # still pass traffic. Also reload ipfw so that it is reconfigured
        if deny:
            quietRun( 'kenv net.inet.ip.fw.default_to_accept=1' )
        if deny and 'ipfw.ko' in klds:
            rmmod( 'ipfw' )
            modprobe( 'ipfw' )
        if 'ipfw_nat.ko' not in klds:
            modprobe( 'ipfw_nat' )
