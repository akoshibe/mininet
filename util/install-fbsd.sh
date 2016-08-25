#!/bin/sh

# Mininet install script with just the bits that are currently supported.
# It follows the logic/contents of `install.sh`. 

dist=$(uname -s)
ver=$(uname -K)
arch=$(uname -m)

if [ "${dist}" = "FreeBSD" ]; then
    install='sudo pkg install'
    remove='sudo pkg remove'
    pkginst='sudo pkg add'
    #install='sudo pkg -o ASSUME_ALWAYS_YES=true install'
    #remove='sudo pkg -o ASSUME_ALWAYS_YES=true remove'
    #pkginst='sudo pkg -o ASSUME_ALWAYS_YES=true add'
else
    printf '%s\n' "This script is for FreeBSD, but you are using ${dist}" \
                  "Try install.sh instead"
    exit 1
fi 

# Get directory containing mininet folder
MININET_DIR=$( CDPATH= cd -- "$( dirname -- "$0" )/../.." && pwd -P )
echo ***directory is: $MININET_DIR

# install/do everything
all () {
    mn_deps
}

# base (non-OpenFlow) bits - Mininet Python bits, dependencies 
mn_deps () {
    # check for VIMAGE support - how correlated is uname -K to -r?
    if [ ${ver} -lt 1100000 ]; then
        if [ ! "$(sysctl kern.conftxt | grep 'VIMAGE\|DUMMYNET')" ]; then
            printf '%s\n' "VIMAGE and DUMMYNET are required but seem missing" \
                          "Retry after rebuilding your kernel with these options"
            exit 1
	fi 
    fi

    $install socat psmisc xterm openssh-portable iperf help2man bash\
        py27-setuptools py27-pyflakes pylint-py27 py27-pep8 py27-pexpect #\
        # gcc gmake

    echo "Installing Mininet core"
    cur=$(pwd -P) 
    cd ${MININET_DIR}/mininet
    ln -F mnexec-fbsd.c mnexec.c
    sudo make install
    cd ${cur} 
}

usage () {
    printf '%s\n' \
        "" \
        "Usage: $(basename $0) [-anh]" \
        "" \
        "options:" \
        " -a: (default) install (A)ll packages" \
        " -h: print this (H)elp message" \
        " -n: install Mini(N)et dependencies + core files"
    exit 2
}

if [ $# -eq 0 ]; then
    all
else
    while getopts 'ahn' OPTION; do
        case $OPTION in
            a)    all ;;
            h)    usage ;;
            n)    mn_deps ;;
            ?)    usage ;;
        esac
    done
    shift $(($OPTIND - 1))
fi
