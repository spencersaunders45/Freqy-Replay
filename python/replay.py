from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
import multiprocessing as mp
import threading as th
from time import sleep
import numpy as np
import argparse, traceback

from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
from helper_functions.freq_check import dominant_frequency
from monitor.streaming import Stream
from monitor.packet_saver import PacketSaver
from monitor.packet_detect import PacketDetect
from attack import Attack

# sdr = SDR(15000000.0, 2400000000.0, 70, 74, None)


class FreqyReplay:
    streaming_q: mp.Queue = mp.Queue()
    hdf5: HDF5Handler = HDF5Handler()
    settings: TOMLDocument = TOMLFile("config.toml").read()

    def __init__(self, mode: str):
        """The main class that controls the processes and threads of the application.

        Arguments:
            mode (str): Defines if the radio will be in Attack or Monitor mode.
        """
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
        self.target_freq: float = self.toml_monitor["target_freq"]
        self.listen_time: float = self.toml_monitor["listen_time"]
        self.pool_size: int = self.toml_monitor["pool_size"]
        # SDR
        self.sdr = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
        # Call the mode
        if mode == "attack":
            self.freqy_attack()
        elif mode == "monitor":
            self.freqy_monitor()
        else:
            print("Something when wrong. Mode was not found")
            print(traceback.format_exc())

    def freqy_attack(self):
        """Starts a replay attack."""
        # attack_p = mp.Process(target=Attack(self.file, self.dataset, self.repeat, self.interval).start)
        # attack_p.start()
        # attack_p.join()
        pass

    def freqy_monitor(self):
        """Starts monitoring airwaves."""
        streaming_q = mp.Queue(10)
        packet_q = mp.Queue(10)
        # Processes
        streaming = mp.Process(target=Stream().start)
        packet_detect = mp.Process(target=PacketDetect().start)
        packet_saver = mp.Process(target=PacketSaver().start)
        packet_saver.start()
        packet_detect.start()
        streaming.start()
        packet_saver.join()
        packet_detect.join()
        streaming.join()


if __name__ == "__main__":
    FreqyReplay()
