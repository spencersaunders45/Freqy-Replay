import os, sys
import subprocess
import grp
import re

USER = os.environ["USER"]
SUDO_USER = os.environ["SUDO_USER"]
USER_HOME = f"/home/{SUDO_USER}"
CORE_COUNT = os.cpu_count()
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
PACKAGES = {
    "autoconf",
    "automake",
    "build-essential",
    "ccache",
    "cmake",
    "cpufrequtils",
    "doxygen",
    "ethtool",
    "g++",
    "git",
    "inetutils-tools",
    "libboost-all-dev",
    "libncurses5",
    "libncurses5-dev",
    "libusb-1.0-0",
    "libusb-1.0-0-dev",
    "libusb-dev",
    "python3-dev",
    "python3-mako",
    "python3-numpy",
    "python3-requests",
    "python3-scipy",
    "python3-setuptools",
    "python3-ruamel.yaml",
}
PYTHON_VERSION = "3.11"
UHD_VERSION = "v4.3.0.0"
SETUP_ENV_FILE = f"""
LOCALPREFIX={USER_HOME}/uhd/install
export PATH=$LOCALPREFIX/bin:$PATH
export LD_LOAD_LIBRARY=$LOCALPREFIX/lib:$LD_LOAD_LIBRARY
export LD_LIBRARY_PATH=$LOCALPREFIX/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$LOCALPREFIX/lib/python{PYTHON_VERSION}/site-packages:$PYTHONPATH
export PKG_CONFIG_PATH$=LOCALPREFIX/lib/pkgconfig:$PKG_CONFIG_PATH
export UHD_RFNOC_DIR=$LOCALPREFIX/share/uhd/rfnoc/
export UHD_IMAGES_DIR=$LOCALPREFIX/share/uhd/images
"""


def run_as_root(cmd: list, working_dir: str = None) -> None:
    """Runs a command as root.

    Arguments:
        cmd (list): A list of str's that make up the command to be ran.
        working_dir (str): A path to a dir where the command should be ran. If None then the command will run in the directory where this file is located.
    """
    command: list = " ".join(["sudo"] + cmd).split(" ")
    if working_dir:
        subprocess.run(command, cwd=working_dir)
    else:
        subprocess.run(command)


def run_as_user(cmd: list, working_dir: str = None) -> None:
    """Runs a command under the SUDO_USER.

    Arguments:
        cmd (list): A list of str's that make up the command to be ran.
        working_dir (str): A path to a dir where the command should be ran. If None then the command will run in the directory where this file is located.
    """
    command: str = " ".join(["sudo", "-u", SUDO_USER] + cmd).split(" ")
    print(command)
    if working_dir:
        subprocess.run(command, cwd=working_dir)
    else:
        subprocess.run(command)


def check_for_sudo() -> None:
    """Checks if the script is being ran as a root user."""

    if USER != "root":
        print("Must run setup.py as root.")
        exit(1)


# update apt and install packages
def install_packages() -> None:
    """Installs the packages required for the project"""

    print("\nINSTALLING PACKAGES\n")

    # Update packages list
    run_as_root(["apt-get", "update"])
    # Install packages
    for package in PACKAGES:
        run_as_root(["apt-get", "install", "-y", package])


def clone_uhd() -> None:
    """Clones the UHD repo"""

    print("\nCLONING UHD\n")

    UHD_REPO = f"{FILE_PATH}/../../uhd"
    # Check if uhd repo is there
    if not os.path.isdir(f"{FILE_PATH}/../../uhd"):
        # Clone the repo
        run_as_user(
            ["git", "clone", "https://github.com/EttusResearch/uhd.git"],
            f"{FILE_PATH}/../../",
        )
    # Checkout correct version of UHD
    run_as_user(["git", "checkout", UHD_VERSION], UHD_REPO)
    # Update submodules
    run_as_user(["git", "submodule", "update"], UHD_REPO)
    # Check for build dir
    if not os.path.isdir(f"{FILE_PATH}/../../uhd/host/build"):
        run_as_user(["mkdir", f"{FILE_PATH}/../../uhd/host/build"])
    print("\n\tBUILDING UHD\n")
    # run Make file
    working_dir: str = f"{FILE_PATH}/../../uhd/host/build/"
    run_as_user(
        [
            "cmake",
            "-DCMAKE_INSTALL_PREFIX=~/uhd/install",
            f"DPYTHON_EECUTABLE=/usr/bin/python{PYTHON_VERSION}",
            f"-DRUNTIME_PYTHON_EXECUTABLE=/usr/bin/python{PYTHON_VERSION}",
            "../",
        ],
        working_dir,
    )
    run_as_user(["make", f"--jobs={CORE_COUNT - 1}"], working_dir)
    run_as_user(["make", "test"], working_dir)
    run_as_user(["make install"], working_dir)
    run_as_root(
        ["ln", "-sf", f"{FILE_PATH}/uhd/host/build/lib/libuhd.so.4.3.0", "/lib"]
    )
    run_as_root(
        ["ln", "-sf", f"{FILE_PATH}/uhd/host/build/lib/libuhd.so.4.3.0", "/usr/lib"]
    )


def setup_uhd_env() -> None:
    """Preps the setup environment for UHD"""

    print("\nSETTING UP UHD ENVIRONMENT\n")

    # Create setup.env file
    with open((f"{USER_HOME}/uhd/install/setup.env"), "w", encoding="ascii") as f:
        f.write(SETUP_ENV_FILE)
    # Transfer file ownership from root to user
    run_as_root(["chown", "-R", f"{USER}:{USER}", f"{USER_HOME}/uhd"])
    # make setup.env file executable
    run_as_user(["chmod", "-x", f"{USER_HOME}/uhd/install/setup.env"])
    # execute setup.env file
    run_as_user([f"{USER_HOME}/uhd/install/setup.env"])
    # Run uhd_images_downloader.py script
    if os.path.exists(f"{USER_HOME}/uhd/install/lib/uhd/utils"):
        run_as_root(
            [
                f"python{PYTHON_VERSION}",
                f"{USER_HOME}/uhd/install/lib/uhd/utils/uhd_images_downloader.py",
            ]
        )
    else:
        run_as_root(
            [
                f"python{PYTHON_VERSION}",
                f"{FILE_PATH}/../../uhd/host/build/utils/uhd_images_downloader.py",
            ]
        )


def configure_for_b200() -> None:
    """setup UHD to use the B200 SDR"""

    print("\nSETUP UHD FOR B200 SDR\n")

    working_dir: str = f"{FILE_PATH}/../../uhd/host/utils"
    run_as_root(["cp", "uhd-usrp.rules", "/etc/udev/rules.d/"], working_dir)
    run_as_root(["udevadm", "control", "--reload-rules"])
    run_as_root(["udevadm", "trigger"])


def configure_usergroups():
    """add USRP to usergroups and to the /etc/security/limits.conf file"""

    print("\nCONFIGURE USERGROUPS\n")
    # create a list of all group names
    all_groups: list = list()
    for group in grp.getgrall():
        all_groups.append(group.gr_name)
    # check if usrp is in the groups list
    if "usrp" not in all_groups:
        run_as_root(["groupadd", "usrp"])
    # ...
    run_as_root(["usermod", "-aG", "usrp", SUDO_USER])
    # add usrp to limits.conf file
    with open("/etc/security/limits.conf", "r") as f:
        limits = f.read()

    limits = re.sub(r"(?=\# End of file)", "@usrp - rtprio 99\n", limits)

    with open("/etc/security/limits.conf", "w") as f:
        f.write(limits)


def verify_python3_uhd_install():
    """Ensures that python3-uhd was installed"""
    print("\nVERIFY PYTHON3-UHD INSTALL\n")
    run_as_root(["apt-get", "install", "-y", "python3-uhd"])


def install_gqrx():
    """Install gqrx for debugging purposes"""
    print("\nINSTALL GQRX\n")
    run_as_root(["apt-get", "install", "-y", "gqrx-sdr"])
    if os.path.exists("/usr/lib/uhd/utils/"):
        run_as_root(["/usr/lib/uhd/utils/uhd_images_downloader.py", "-y"])
    else:
        run_as_root(
            [
                f"python{PYTHON_VERSION}",
                f"{FILE_PATH}/../../uhd/host/utils/uhd_images_downloader.py.in",
            ]
        )


if __name__ == "__main__":
    check_for_sudo()
    # Install packages
    install_packages()
    # Setup and install UHD
    clone_uhd()
    setup_uhd_env()
    configure_usergroups()
    verify_python3_uhd_install()
    install_gqrx()
