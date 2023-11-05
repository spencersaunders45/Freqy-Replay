"""
TODO: Give option to name a file
TODO: If name already exists add a num to the end of the file
TODO: Ability to add metadata: *name *size *sample_rate *center_frequency
"""

import multiprocessing as mp
import numpy as np
import os, sys
from datetime import date

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f"{FILE_DIR}/../"
sys.path.insert(0, PYTHON_DIR)

from helper_functions.hdf5_handler import HDF5Handler


class PacketSaver:
    def __init__(self, file_name: str, packet_q: mp.Queue, hdf5:HDF5Handler, center_frequency:float):
        """Saves off packets into HDF5 files.

        Arguments:
            file_name (str): The name of the HDF5 file to be saved.

            packet_q (mp.Queue): A shared queue that holds the completed packets to be saved.
        """
        self.file_name = file_name
        self.packet_q = packet_q
        self.hdf5 = hdf5
        self.center_frequency = center_frequency
        self.dataset_count = 0

    def start(self):
        while True:
            all_packets = self.packet_q.get()
            for packet in all_packets:
                self.hdf5.save_signal(packet, self.file_name, packet.size, self.center_frequency)
