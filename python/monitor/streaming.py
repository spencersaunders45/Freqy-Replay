import os, sys
from helper_functions.uhd_interface import SDR
import multiprocessing as mp

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = f'{FILE_DIR}/../'
sys.path.insert(0, ROOT_DIR)

class Stream:
    #TODO: Add parameter to add a signal to the queue to stop the process
    def __init__(self, target_freq:float, listen_time:float, sdr:SDR, stream_q:mp.Queue, max_count:int):
        """ Monitors the airwaves for a target frequency
        
        Arguments:
            target_freq (float): The target frequency to listen for in MHz.
            listen_time (float): The total time (in seconds) to determine what frequency the signal is at. 
            sdr (SDR): A SDR class to interface with the SDR.
        """
        self.target_freq = target_freq
        self.listen_time = listen_time
        self.sdr = sdr
        self.stream_q = stream_q
        self.max_count = max_count
        self.packet_order = 0

    def start(self):
        """ Streams signals captured from the SDR """
        while True:
            self.stream_q.put(self.sdr.rx_data())