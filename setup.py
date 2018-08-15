#!/usr/bin/env python

"Setuptools params"

from setuptools import setup, find_packages
from os.path import join

# Get version number from source tree
import sys
sys.path.append( '.' )
from mininet.net import VERSION

scripts = [ join( 'bin', filename ) for filename in [ 'mn' ] ]

modname = distname = 'mininet'

def sys_package():
    if sys.platform.startswith('freebsd'):
        return ['mininet.freebsd']
    elif sys.platform.startswith('linux'):
        return ['mininet.linux']
    elif sys.platform.startswith('openbsd'):
        return ['mininet.openbsd']
    return []

setup(
    name=distname,
    version=VERSION,
    description='Process-based OpenFlow emulator',
    author='Bob Lantz',
    author_email='rlantz@cs.stanford.edu',
    packages=[
        'mininet',
        'mininet.examples',
    ] + sys_package(),
    py_modules=[
        'mininet.examples.cluster',
        'mininet.examples.clustercli'
    ],
    long_description="""
        Mininet is a network emulator which uses lightweight
        virtualization to create virtual networks for rapid
        prototyping of Software-Defined Network (SDN) designs
        using OpenFlow. http://mininet.org
        """,
    classifiers=[
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: System :: Emulators",
    ],
    keywords='networking emulator protocol Internet OpenFlow SDN',
    license='BSD',
    install_requires=[
        'setuptools'
    ],
    scripts=scripts,
)
