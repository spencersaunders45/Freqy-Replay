"""
TODO: Give option to name a file
TODO: If name already exists add a num to the end of the file
TODO: Ability to add metadata: *name *size *sample_rate *center_frequency
"""

import multiprocessing as mp
import numpy as np
import os, sys

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f'{FILE_DIR}/../'
sys.path.insert(0,PYTHON_DIR)

from helper_functions.hdf5_handler import HDF5Handler

class PacketSaver:
    def __init__(self, file_name:str, packet_q:mp.Queue):
        """Saves off packets into HDF5 files.
        
        Arguments:
            file_name (str): The name of the HDF5 file to be saved.

            packet_q (mp.Queue): A shared queue that holds the completed packets to be saved.
        """
        self.file_name = file_name
        self.packet_q = packet_q

    def start(self):
        while True:
            packet = self.packet_q.get()
