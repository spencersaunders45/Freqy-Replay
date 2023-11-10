#!/home/dev/git/Freqy-Replay/.venv/bin/python

from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
import multiprocessing as mp
import threading as th
from time import sleep
import numpy as np
import argparse, traceback
import sys, os
import signal

_HOME = os.path.isdir('HOME')
if os.path.isdir(f'{_HOME}/uhd/install/lib/python3.8/site-packages'):
    PYTHON_DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0,PYTHON_DIR)
    UHD = f'{_HOME}/uhd/install/lib/python3.8/site-packages'
    sys.path.insert(0, UHD)

from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
# from helper_functions.freq_check import dominant_frequency
from monitor.streaming import Stream
from monitor.packet_saver import PacketSaver
from monitor.packet_detect import PacketDetect
from attack import Attack

# sdr = SDR(15000000.0, 2400000000.0, 70, 74, None)


class FreqyReplay:
    streaming_q: mp.Queue = mp.Queue()
    hdf5: HDF5Handler = HDF5Handler()
    settings: TOMLDocument = TOMLFile("config.toml").read()
    all_processes = list()

    def __init__(self, mode: str, file_name:str = None):
        """The main class that controls the processes and threads of the application.

        Arguments:
            mode (str): Defines if the radio will be in Attack or Monitor mode.
        """
        self.file_name =  file_name
        # Get TOML key value pairs
        self.toml_radio: dict = self.settings.get("RADIO")
        self.toml_attack: dict = self.settings.get("ATTACK")
        self.toml_monitor: dict = self.settings.get("MONITOR")
        # RADIO
        self.center_freq: float = self.toml_radio["center_freq"]
        self.sample_rate: float = self.toml_radio["sample_rate"]
        self.rx_gain: int = self.toml_radio["rx_gain"]
        self.tx_gain: int = self.toml_radio["tx_gain"]
        self.uhd_id: str = self.toml_radio["uhd_id"]
        # ATTACK
        self.file: str = self.toml_attack["file"]
        self.dataset: str = self.toml_attack["dataset"]
        self.repeat: int = self.toml_attack["repeat"]
        self.interval: float = self.toml_attack["interval"]
        # MONITOR
        self.threshold: float = self.toml_monitor["threshold"]
        self.cutoff: float = self.toml_monitor["cutoff"]
        self.packet_slack: int = self.toml_monitor["packet_slack"]
        # Call the mode
        if mode == "attack":
            self.sdr = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
            self.freqy_attack()
        elif mode == "monitor":
            self.sdr = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
            self.freqy_monitor()
        elif mode == 'n':
            pass
        else:
            print("Something when wrong. Mode was not found")
            print(traceback.format_exc())

    def freqy_attack(self):
        """Starts a replay attack."""
        packet:np.ndarray = self.hdf5.get_signal(self.file, self.dataset)
        attack_p = mp.Process(target=Attack(self.interval, packet, self.sdr).replay)
        attack_p.start()
        attack_p.join()

    def freqy_monitor(self):
        """Starts monitoring airwaves."""
        streaming_q = mp.Queue(10)
        packet_q = mp.Queue(10)
        stream_p = Stream(self.sdr, streaming_q)
        packet_detect_p = PacketDetect(streaming_q, self.threshold, self.cutoff, packet_q)
        packet_saver_p = PacketSaver(self.file, packet_q, self.hdf5, self.center_freq)
        # Processes
        self.all_processes.append(mp.Process(target=stream_p.start))
        self.all_processes.append(mp.Process(target=packet_detect_p.start))
        self.all_processes.append(mp.Process(target=packet_saver_p.start))
        for process in self.all_processes:
            process.start()


    def display_all_files(self):
        self.hdf5.display_all_files()

    def view_file_meta_data(self):
        self.hdf5.display_metadata(self.file_name)


if __name__ == "__main__":
    # freqy_replay = FreqyReplay()
    parser = argparse.ArgumentParser()
    # Add required arguments
    parser.add_argument("mode", default=None, choices=['a', 'm', 'n'], help="a: attack mode, m: monitor mode, n: neither")
    # Add args
    parser.add_argument('-f', '--view-files', default=None, help="View all signal files.", action="store_true")
    parser.add_argument('-m', '--meta-data', default=None, help="View the meta data for a specific signal file.")
    args = parser.parse_args()
    
    if args.mode == 'a':
        FreqyReplay('attack')
    elif args.mode == 'm':
        FreqyReplay('monitor')

    if args.view_files:
        FreqyReplay('n').display_all_files()

    if args.meta_data:
        FreqyReplay('n', args.meta_data).view_file_meta_data()