"Module dependency utility functions for Mininet."

from mininet.util import quietRun
from mininet.log import info, error, debug
from os import environ, uname

if uname()[ 0 ] == 'FreeBSD':
    from mininet.util_freebsd import ( lsmod, rmmod, modprobe )
else:
    from mininet.util_linux import ( lsmod, rmmod, modprobe )

OF_KMOD = 'ofdatapath'
OVS_KMOD = 'openvswitch_mod'  # Renamed 'openvswitch' in OVS 1.7+/Linux 3.5+
TUN = 'tun'

def moduleDeps( subtract=None, add=None ):
    """Handle module dependencies.
       subtract: string or list of module names to remove, if already loaded
       add: string or list of module names to add, if not already loaded"""
    subtract = subtract if subtract is not None else []
    add = add if add is not None else []
    if isinstance( subtract, basestring ):
        subtract = [ subtract ]
    if isinstance( add, basestring ):
        add = [ add ]
    for mod in subtract:
        if mod in lsmod():
            info( '*** Removing ' + mod + '\n' )
            rmmodOutput = rmmod( mod )
            if rmmodOutput:
                error( 'Error removing ' + mod + ': "%s">\n' % rmmodOutput )
                exit( 1 )
            if mod in lsmod():
                error( 'Failed to remove ' + mod + '; still there!\n' )
                exit( 1 )
    for mod in add:
        if mod not in lsmod():
            info( '*** Loading ' + mod + '\n' )
            modprobeOutput = modprobe( mod )
            if modprobeOutput:
                error( 'Error inserting ' + mod +
                       ' - is it installed and available via modprobe?\n' +
                       'Error was: "%s"\n' % modprobeOutput )
            if mod not in lsmod():
                error( 'Failed to insert ' + mod + ' - quitting.\n' )
                exit( 1 )
        else:
            debug( '*** ' + mod + ' already loaded\n' )


def pathCheck( *args, **kwargs ):
    "Make sure each program in *args can be found in $PATH."
    moduleName = kwargs.get( 'moduleName', 'it' )
    for arg in args:
        if not quietRun( 'which ' + arg ):
            error( 'Cannot find required executable %s.\n' % arg +
                   'Please make sure that %s is installed ' % moduleName +
                   'and available in your $PATH:\n(%s)\n' % environ[ 'PATH' ] )
            exit( 1 )
