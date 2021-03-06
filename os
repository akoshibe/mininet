#!/bin/sh

# Emit OS-specific parameters

OS=`uname`
case $OS in
    *Linux*)
        prefix='/usr'
        mandir='/usr/share'
        inst=$(pwd)/util/install-linux.sh
        python=python
        mnexec=$(pwd)/mnexec_linux.c
        ;;
    *FreeBSD*)
        prefix='/usr/local'
        mandir=$prefix
        inst=$(pwd)/util/install-freebsd.sh
        python=python
        mnexec=$(pwd)/mnexec_bsd.c
        ;;
    *OpenBSD*)
        prefix='/usr/local'
        mandir='/usr/share'
        inst=$(pwd)/util/install-openbsd.sh
        # could just link 'python2.7' to 'python'
        python=python2.7
        mnexec=$(pwd)/mnexec_bsd.c
        ;;
    *)
        echo "Unknown platform: $OS"
        exit 1
        ;;
esac

[ "$1" = bindir ] && echo $prefix/bin
[ "$1" = mandir ] && echo $mandir/man/man1
[ "$1" = pkgdir ] && echo $prefix/lib/python2.7/site-packages
[ "$1" = python ] && echo $python
[ "$1" = mnxdep ] && echo $mnexec
