Mininet - FreeBSD Edition (A platform port)
-------------------------------------------

Based on Mininet 2.3.0d1

This is an experimental port of [Mininet](https://github.com/mininet)
to FreeBSD. This is very much a work-in-progress so don't be
surprised if things are unsupported and/or broken!

### What is Mininet?

Shamelessly repurposing the Mininet README as an intro/recap:

Mininet emulates a complete network of hosts, links, and switches
on a single machine. To create a sample two-host, one-switch network,
just run:

  `sudo mn --controller=ryu`

Mininet is useful for interactive development, testing, and demos,
especially those using OpenFlow and SDN.  OpenFlow-based network
controllers prototyped in Mininet can usually be transferred to
hardware with minimal changes for full line-rate execution.

### Features

This port currently supports:

* [Ryu](https://osrg.github.io/ryu/) as the stock controller (i.e.,
  installable from the supplied install script)

* OpenvSwitch as the (currently only) OpenFlow-capable Switch node

* The Mininet command-line launcher (`mn`), and a subset of its
  features:

  * Launching of parameterized topologies e.g. `mn --topo=tree,2,3`

  * Cleanup though `mn -c`

  * `pingall` and `ping` tests

* The Mininet CLI, and a subset of its built-in features:

  * Running commands on nodes e.g. `h1 ifconfig -a`

  * Python and shell commands with `py` and `sh`

  * `ping`* tests (`pingpair`, `pingall`, etc.)

  * Listing of network links, nodes, etc (`nodes`, `intfs`, etc.)

* Connecting of topologies to external controllers using
  `RemoteController` (Or `mn --controller=remote ...`)

* Installation of Mininet core files, Open vSwitch, and Ryu via
  install script

### Installation

See `INSTALL.FreeBSD` for installation instructions and details.

### Documentation

Information on Mininet itself, along with a walkthrough and an
introduction to its Python API, can be found on the
[Mininet Web Site](http://mininet.org).

Information specific to this Mininet port can be found here:

<https://wiki.freebsd.org/Mininet>
