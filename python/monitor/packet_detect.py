import numpy as np
import multiprocessing as mp
from numba import njit, jit
from time import sleep

@njit(cache=True)
def remove_zeros(signal:np.ndarray) -> np.ndarray:
    """Uses jit to quickly remove the block of zeros at the end of the array.
    
    Arguments:
        signal (np.ndarray): The numpy array that carries the IQ packets of the signal data.

    Returns:
        np.ndarray: The numpy array with the zeros removed.
    """
    return np.trim_zeros(signal, trim='b')

@njit(cache=True)
def process_signal(signal:np.ndarray, threshold:float, cutoff:int) -> bool:
    """Decides if the signal is part of a packet
    
    Arguments:
        signal (np.ndarray): The numpy array that carries the IQ packets of the signal data.
        threshold (float): The minimum value that a signal must exceed to be considered part of a packet.
        cutoff (int): The number of IQ values that are allowed to be under the threshold and still be considered part of a packet.

    Returns:
        bool: A bool indicating if the signal is part of a packet.
    """

class PacketDetect:

    def __init__(self, stream_q:mp.Queue, packet_counter:mp.Value, threshold:float, cutoff:int, bouncer:int, packet_q:mp.Queue, max_int:int):
        self.stream_q = stream_q
        self.packet_q = packet_q
        self.packet_counter = packet_counter
        self.threshold = threshold
        self.cutoff = cutoff
        self.bouncer = bouncer
        self.max_int = max_int

    def start(self):
        while True:
            signal, order_num = self.stream_q.get()
            signal = remove_zeros(signal)
            is_packet = process_signal(signal, self.threshold, self.cutoff)
            while True:
                # TODO: Add a watchdog here to prevent infinite loop
                if self.bouncer == order_num:
                    self.packet_q.put((signal,is_packet))
                    self.packet_counter.value += 1
                    if self.packet_counter >= self.max_int:
                        self.packet_counter.value = 0
                else:
                    sleep(.0001)