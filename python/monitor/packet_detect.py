import numpy as np
import multiprocessing as mp
from numba import njit, jit
from time import sleep

@njit(cache=True, fastmath=True)
def process_signal(signal:np.ndarray, threshold:float, cutoff:int, packet:np.ndarray) -> tuple:
    """Decides if the signal is part of a packet
    
    Arguments:
        signal (np.ndarray): The numpy array that carries the IQ packets
            of the signal data.

        threshold (float): The minimum value that a signal must exceed to
            be considered part of a packet.

        cutoff (int): The number of IQ values that are allowed to be under
            the threshold and still be considered part of a packet.

    Returns:
        tuple (np.ndarray, bool): A tuple containing the packet and a bool
            indicating if the packet was completed.
    """
    # TODO: Check if they want to keep scanning after end of packet is found
    signal:np.ndarray = np.trim_zeros(signal, trim='b')
    abs_signal:np.ndarray = np.absolute(signal)
    # Check if the max value is above the threshold
    max_value_in_signal = np.max(abs_signal)
    if max_value_in_signal < threshold:
        return (packet, True)
    # If there is no packet then create start of packet
    if packet == None:
        max_value_index:int = np.argmax(abs_signal)
        packet = signal[max_value_index:]
    # Scan rest of packet to find end of packet
    cutoff_counter:int = cutoff
    last_index_above_threshold = None
    for index in range(abs_signal.size-1):
        # Stop when end of packet is found
        if cutoff_counter <= 0:
            packet = np.concatenate(packet, signal[:last_index_above_threshold])
            return (packet, True)
        # Continue scanning for end of packet
        if abs_signal[index] > threshold:
            cutoff_counter:int = cutoff
            last_index_above_threshold:int = index
        # Decrement the cutoff_counter
        else:
            cutoff_counter -= 1
    # Entire signal is part of the packet
    packet = np.concatenate(packet, signal)
    return (packet, False)



class PacketDetect:

    def __init__(self, stream_q:mp.Queue, packet_counter:mp.Value, threshold:float, cutoff:int, bouncer:mp.Value, packet_q:mp.Queue, max_int:int):
        """A class that handles detecting when a signal is part of a packet.
        
        Arguments:
            stream_q (mp.Queue): A queue holding iq samples and the order in which they
                were added.

            packet_counter (mp.Value): A shared value that keeps track of which packet 
                has been processed to maintain packet order.
            
            threshold (float): The value that signifies when a signal should start to
                considered a packet.
            
            cutoff (int): The number of iq values that need to be below the threshold
                for the signal to be considered ended.
            
            bouncer (mp.Value): A shared value that controls the order in which
                signals are placed onto the packet_q.
            
            packet_q (mp.Queue): A queue holding iq samples and a bool identifying if
                they are part of a packet.
            
            max_int (int): The maximum value 
        """
        self.stream_q:mp.Queue = stream_q
        self.packet_q:mp.Queue = packet_q
        self.packet_counter:mp.Value = packet_counter
        self.threshold:float = threshold
        self.cutoff:int = cutoff
        self.packet:np.ndarray = None
        # self.bouncer:mp.Value = bouncer #! may not need
        # self.max_int:int = max_int      #! may not need

    def start(self) -> None:
        """ Decides when a signal is part of a packet. """
        while True:
            signal = self.stream_q.get()
            self.packet, end_of_packet = process_signal(signal, self.threshold, self.cutoff, self.packet)
            if self.packet and end_of_packet:
                self.packet_q.put(self.packet)
                self.packet = None



"""
signal = np.trim_zeros(signal, trim='b')
abs_signal:np.ndarray = np.abs(signal)
max_signal_value = np.max(abs_signal)
# If there is currently no packet detected then find if
# there are any signals that go above the threshold.
# TODO: Check if there are any values above the threshold before looping. If continuing a packet check to see if the index is larger than the cutoff point.
if packet == None:
    if max_signal_value > threshold:                           #* No packet exists and there is a value above the threshold
        max_value_index:int = np.argmax(abs_signal)
        signal = signal[max_value_index:]
    else:                                                      #* No packet exists and no value above the threshold
        return (packet, True)
# Find the cutoff point of the packet in the signal
#! TODO: Make sure packet is not None
signal_cutoff:int = cutoff
index_above_threshold:int = None
for i in range(len(abs_signal)):
    if signal_cutoff == 0 and packet == None:                  #* cutoff reached and packet has not been created yet
        packet = signal[:index_above_threshold+1]
        return (packet, True)
    if signal_cutoff == 0 and index_above_threshold == None:   #* cutoff reached, packet exists, and end of signal is not found
        return (packet, True)
    elif signal_cutoff == 0 and index_above_threshold:         #* cutoff reached, packet exists, 
        signal = signal[:index_above_threshold+1]
        packet = np.concatenate(packet, signal)
        return (packet, True)
    elif signal_cutoff > 0 and abs_signal[i] > threshold:
        index_above_threshold = i
        signal_cutoff = cutoff
    elif signal_cutoff > 0 and abs_signal[i] < threshold:
        signal_cutoff -= 1
if packet:
    packet = np.concatenate(packet, signal)
    return (packet, False)
else:
    return (signal, False)
"""