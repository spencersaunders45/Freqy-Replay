import os, sys
from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
import multiprocessing as mp

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = f'{FILE_DIR}/../'
sys.path.insert(0, ROOT_DIR)

class Monitor:
    
    def __init__(self, target_freq:float, listen_time:float, sdr:SDR, captured_signals_q:mp.Queue):
        """ Monitors the airwaves for a target frequency
        
        Arguments:
            target_freq (float): The target frequncy to listen for in MHz.
            listen_time (float): The total time (in seconds) to determine what frequncy the signal is at. 
            sdr (SDR): A SDR class to interface with the SDR.
        """
        self.target_freq = target_freq
        self.listen_time = listen_time
        self.sdr = sdr
        self.captured_signals_q = captured_signals_q

    def start(self):
        """Listens for a target frequncy"""
        # TODO: loops through data streamed from USRP and averages out the freq.
        # Once the average matches the target frequency that section is saved as a hdf5.
        while True:
            pass