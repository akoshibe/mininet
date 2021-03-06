"""
OS-specific utility functions for Linux, counterpart to util.py.
"""

from resource import getrlimit, setrlimit, RLIMIT_NPROC, RLIMIT_NOFILE
from mininet.log import error, warn, debug
from mininet.util import ( errRun, quietRun, retry )


LO='lo'                   # loopback name.
DP_MODE='kernel'          # OVS mode - 'user' or 'kernel'.

# Interface management
#
# Interfaces are managed as strings which are simply the
# interface names, of the form 'nodeN-ethM'.
#
# To connect nodes, we create a pair of veth interfaces, and then place them
# in the pair of nodes that we want to communicate. We then update the node's
# list of interfaces and connectivity map.
#
# For the kernel datapath, switch interfaces
# live in the root namespace and thus do not have to be
# explicitly moved.

def makeIntfPair( intf1, intf2, addr1=None, addr2=None, node1=None, node2=None,
                  deleteIntfs=True, runCmd=None ):
    """Make a veth pair connnecting new interfaces intf1 and intf2
       intf1: name for interface 1
       intf2: name for interface 2
       addr1: MAC address for interface 1 (optional)
       addr2: MAC address for interface 2 (optional)
       node1: home node for interface 1 (optional)
       node2: home node for interface 2 (optional)
       deleteIntfs: delete intfs before creating them
       runCmd: function to run shell commands (quietRun)
       raises Exception on failure"""
    if not runCmd:
        runCmd = quietRun if not node1 else node1.cmd
        runCmd2 = quietRun if not node2 else node2.cmd
    if deleteIntfs:
        # Delete any old interfaces with the same names
        runCmd( deleteCmd( intf1 ) )
        runCmd2( deleteCmd( intf2 ) )
    # Create new pair
    netns = 1 if not node2 else node2.pid
    if addr1 is None and addr2 is None:
        cmdOutput = runCmd( 'ip link add name %s '
                            'type veth peer name %s '
                            'netns %s' % ( intf1, intf2, netns ) )
    else:
        cmdOutput = runCmd( 'ip link add name %s '
                            'address %s '
                            'type veth peer name %s '
                            'address %s '
                            'netns %s' %
                            (  intf1, addr1, intf2, addr2, netns ) )
    if cmdOutput:
        raise Exception( "Error creating interface pair (%s,%s): %s " %
                         ( intf1, intf2, cmdOutput ) )

    return intf1, intf2


def deleteCmd( intf, node=None ):
    """Command to destroy an interface."""
    return 'ip link del ' + intf

def moveIntfNoRetry( intf, dstNode, printError=False ):
    """Move interface to node, without retrying.
       intf: string, interface
        dstNode: destination Node
        printError: if true, print error"""
    intf = str( intf )
    cmd = 'ip link set %s netns %s' % ( intf, dstNode.pid )
    cmdOutput = quietRun( cmd )
    # If ip link set does not produce any output, then we can assume
    # that the link has been moved successfully.
    if cmdOutput:
        if printError:
            error( '*** Error: moveIntf: ' + intf +
                   ' not successfully moved to ' + dstNode.name + ':\n',
                   cmdOutput )
        return False
    return True

# duplicate in util_freebsd
def moveIntf( intf, dstNode, printError=True,
              retries=3, delaySecs=0.001 ):
    """Move interface to node, retrying on failure.
       intf: string, interface
       dstNode: destination Node
       printError: if true, print error"""
    retry( retries, delaySecs, moveIntfNoRetry, intf, dstNode,
           printError=printError )

# Other stuff we use
def sysctlTestAndSet( name, limit ):
    "Helper function to set sysctl limits"
    #convert non-directory names into directory names
    if '/' not in name:
        name = '/proc/sys/' + name.replace( '.', '/' )
    #read limit
    with open( name, 'r' ) as readFile:
        oldLimit = readFile.readline()
        if isinstance( limit, int ):
            #compare integer limits before overriding
            if int( oldLimit ) < limit:
                with open( name, 'w' ) as writeFile:
                    writeFile.write( "%d" % limit )
        else:
            #overwrite non-integer limits
            with open( name, 'w' ) as writeFile:
                writeFile.write( limit )

def rlimitTestAndSet( name, limit ):
    "Helper function to set rlimits"
    soft, hard = getrlimit( name )
    if soft < limit:
        hardLimit = hard if limit < hard else limit
        setrlimit( name, ( limit, hardLimit ) )

def fixLimits():
    "Fix ridiculously small resource limits."
    debug( "*** Setting resource limits\n" )
    try:
        rlimitTestAndSet( RLIMIT_NPROC, 8192 )
        rlimitTestAndSet( RLIMIT_NOFILE, 16384 )
        #Increase open file limit
        sysctlTestAndSet( 'fs.file-max', 10000 )
        #Increase network buffer space
        sysctlTestAndSet( 'net.core.wmem_max', 16777216 )
        sysctlTestAndSet( 'net.core.rmem_max', 16777216 )
        sysctlTestAndSet( 'net.ipv4.tcp_rmem', '10240 87380 16777216' )
        sysctlTestAndSet( 'net.ipv4.tcp_wmem', '10240 87380 16777216' )
        sysctlTestAndSet( 'net.core.netdev_max_backlog', 5000 )
        #Increase arp cache size
        sysctlTestAndSet( 'net.ipv4.neigh.default.gc_thresh1', 4096 )
        sysctlTestAndSet( 'net.ipv4.neigh.default.gc_thresh2', 8192 )
        sysctlTestAndSet( 'net.ipv4.neigh.default.gc_thresh3', 16384 )
        #Increase routing table size
        sysctlTestAndSet( 'net.ipv4.route.max_size', 32768 )
        #Increase number of PTYs for nodes
        sysctlTestAndSet( 'kernel.pty.max', 20000 )
    # pylint: disable=broad-except
    except Exception:
        warn( "*** Error setting resource limits. "
              "Mininet's performance may be affected.\n" )
    # pylint: enable=broad-except


def mountCgroups():
    "Make sure cgroups file system is mounted"
    mounts = quietRun( 'cat /proc/mounts' )
    cgdir = '/sys/fs/cgroup'
    csdir = cgdir + '/cpuset'
    if ('cgroup %s' % cgdir not in mounts and
            'cgroups %s' % cgdir not in mounts):
        raise Exception( "cgroups not mounted on " + cgdir )
    if 'cpuset %s' % csdir not in mounts:
        errRun( 'mkdir -p ' + csdir )
        errRun( 'mount -t cgroup -ocpuset cpuset ' + csdir )

def numCores():
    "Returns number of CPU cores based on /proc/cpuinfo"
    if hasattr( numCores, 'ncores' ):
        return numCores.ncores
    try:
        numCores.ncores = int( quietRun('grep -c processor /proc/cpuinfo') )
    except ValueError:
        return 0
    return numCores.ncores

# Kernel module manipulation

def lsmod():
    "Return output of lsmod."
    return quietRun( 'lsmod' )

def rmmod( mod ):
    """Return output of lsmod.
       mod: module string"""
    return quietRun( [ 'rmmod', mod ] )

def modprobe( mod ):
    """Return output of modprobe
       mod: module string"""
    return quietRun( [ 'modprobe', mod ] )
