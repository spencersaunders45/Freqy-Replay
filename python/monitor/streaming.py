import os, sys
from helper_functions.uhd_interface import SDR
import multiprocessing as mp

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = f"{FILE_DIR}/../"
sys.path.insert(0, ROOT_DIR)


class Stream:
    # TODO: Add parameter to add a signal to the queue to stop the process
    def __init__(self, sdr: SDR, stream_q: mp.Queue):
        """Monitors the airwaves for a target frequency

        Arguments:
            sdr (SDR): A SDR class to interface with the SDR.

            stream_q (mp.Queue): A shared queue to feed packet_detect signals.
        """
        self.sdr = sdr
        self.stream_q = stream_q

    def start(self) -> None:
        """Streams signals captured from the SDR"""
        while True:
            self.stream_q.put(self.sdr.rx_data())
