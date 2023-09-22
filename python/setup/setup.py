import os, sys
import subprocess

USER = os.environ['USER']
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
print(FILE_PATH)

PACKAGES = {
    "autoconf"
    "automake"
    "build-essential"
    "ccache"
    "cmake"
    "cpufrequtils"
    "doxygen"
    "ethtool"
    "g++"
    "git"
    "inetutils-tools"
    "libboost-all-dev"
    "libncurses5"
    "libncurses5-dev"
    "libusb-1.0-0"
    "libusb-1.0-0-dev"
    "libusb-dev"
    "python3-dev"
    "python3-mako"
    "python3-numpy"
    "python3-requests"
    "python3-scipy"
    "python3-setuptools"
    "python3-ruamel.yaml"
}

# check if they are running as sudo
def check_for_sudo():
    if USER != 'root':
        print("Must run setup.py as root.")
        exit(1)

# update apt and install packages
def clone_uhd():
    out = subprocess.run(['pwd'], capture_output=True, cwd=f'{FILE_PATH}/../..')
    print(out.stdout.decode().strip())

# install python

# install UHD

# add UHD to path

# install gqrx

#? install py_aff3ct

if __name__ == "__main__":
    check_for_sudo()
    clone_uhd()