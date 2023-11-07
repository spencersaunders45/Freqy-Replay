import os, sys
from time import sleep
import numpy as np

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,FILE_DIR)

from helper_functions.uhd_interface import SDR

class Attack:

    def __init__(self, interval:float, packet:np.ndarray, sdr:SDR):
        """Controls the replay attack.
        
        Parameters:
            interval (float): The time to wait between each TX
            
            packet (np.ndarray): The packet to be replayed.
            
            sdr (SDR): The interface with the SDR.
        """
        self.interval = interval
        self.packet = packet
        self.sdr = sdr

    def replay(self):
        """Replays a captured packet."""
        while True:
            self.sdr.tx_data(self.packet)
            sleep(self.interval)
