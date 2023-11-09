import os, sys
import multiprocessing as mp
import time
import numpy as np
import cupy as cp

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = f"{FILE_DIR}/../"
sys.path.insert(0, ROOT_DIR)

from helper_functions.uhd_interface import SDR
from tools.plot_signal import plot_signal

class Stream:
    # TODO: Add parameter to add a signal to the queue to stop the process
    def __init__(self, sdr: SDR, stream_q: mp.Queue, max_loops:int):
        """Monitors the airwaves for a target frequency

        Arguments:
            sdr (SDR): A SDR class to interface with the SDR.

            stream_q (mp.Queue): A shared queue to feed packet_detect signals.
        """
        self.sdr = sdr
        self.stream_q = stream_q
        self.max_loops = max_loops

    def start(self) -> None:
        """Streams signals captured from the SDR"""
        count = 0
        while True:
            self.stream_q.put(self.sdr.rx_data())
            count += 1
            if count > self.max_loops:
                print("EXIT")
                self.stream_q.put(" ")
                break

if __name__ == "__main__":
    sdr = SDR(15000000.0, 2400000000.0, 70, 74)
    q = mp.Queue()
    stream = Stream(sdr, q, 500)
    stream.start()
    signal: cp.ndarray = cp.zeros(1)
    while True:
        data = q.get()
        if type(data) == str:
            break
        else:
            data = cp.asarray(data)
            data = data.ravel()
            data = cp.trim_zeros(data)
            signal = cp.concatenate((signal, data))
    signal = cp.asnumpy(signal)
    plot_signal(signal, 15000000.0, 1.5)