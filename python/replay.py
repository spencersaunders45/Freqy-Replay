#!/bin/python3

from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
import multiprocessing as mp
import numpy as np
import argparse, traceback
import sys, os

_HOME = os.path.isdir("HOME")
if os.path.isdir(f"{_HOME}/uhd/install/lib/python3.8/site-packages"):
    PYTHON_DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, PYTHON_DIR)
    UHD = f"{_HOME}/uhd/install/lib/python3.8/site-packages"
    sys.path.insert(0, UHD)

from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler

from monitor.monitor import Monitor
from attack.attack import Attack


class FreqyReplay:
    streaming_q: mp.Queue = mp.Queue()
    hdf5: HDF5Handler = HDF5Handler()
    settings: TOMLDocument = TOMLFile("config.toml").read()
    all_processes = list()

    def __init__(self):
        """The main class that controls the processes and threads of the application.

        Arguments:
            mode (str): Defines if the radio will be in Attack or Monitor mode.
        """
        self._monitor = Monitor()
        self._attack = Attack()
        # Get TOML key value pairs
        self.toml_filter: dict = self.settings.get("FILTER")
        # FILTER
        self.byte_size: str = self.toml_filter["byte_size"]
        self.seconds: str = self.toml_filter["seconds"]
        self.center_freq_filter: int = self.toml_filter["center_freq"]
        self.sample_rate_filter: float = self.toml_filter["sample_rate"]

    def attack(self):
        """Starts a replay attack."""
        self._attack.replay()

    def monitor(self):
        """Starts monitoring airwaves."""
        self._monitor.launch()

    def display_all_files(self):
        self.hdf5.display_all_files()

    def view_file_meta_data(self, file_name: str):
        if self.center_freq_filter:
            center_freq = self.center_freq_filter
        else:
            center_freq = None
        if self.sample_rate_filter:
            sample_rate = self.sample_rate_filter
        else:
            sample_rate = None
        if self.seconds:
            seconds = self.seconds
        else:
            seconds = None
        if self.byte_size:
            bytes_size = self.byte_size
        else:
            bytes_size = None
        self.hdf5.display_metadata(
            file_name, bytes_size, seconds, center_freq, sample_rate
        )

    def plot_signal(self, file_name: str, dataset: str):
        self.hdf5.plot_signal(file_name, dataset)


if __name__ == "__main__":
    # freqy_replay = FreqyReplay()
    parser = argparse.ArgumentParser()
    # Add required arguments
    parser.add_argument(
        "mode",
        default=None,
        choices=["a", "m", "n"],
        help="a: attack mode, m: monitor mode, n: neither",
    )
    # Add args
    parser.add_argument(
        "-v",
        "--view-files",
        default=None,
        help="View all signal files.",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--meta-data",
        default=None,
        help="View the meta data for a specific signal file.",
    )
    parser.add_argument(
        "-p",
        "--plot-signal",
        default=None,
        help="Plots a saved packet.",
        nargs=2
    )
    # TODO: Add feature to delete signals that are less than the passed parameters
    args = parser.parse_args()

    if args.mode == "a":
        FreqyReplay().attack()
    elif args.mode == "m":
        FreqyReplay().monitor()

    if args.view_files:
        FreqyReplay().display_all_files()

    if args.meta_data:
        FreqyReplay().view_file_meta_data(args.meta_data)

    if args.plot_signal:
        FreqyReplay().plot_signal(args.plot_signal[0], args.plot_signal[1])
