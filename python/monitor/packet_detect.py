import numpy as np
import multiprocessing as mp
from numba import njit, jit
from time import sleep, time
import os, sys

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f'{FILE_DIR}/../'
sys.path.insert(0, PYTHON_DIR)

from helper_functions.hdf5_handler import HDF5Handler
from tools.plot_signal import plot_signal


@njit(cache=True, fastmath=True)
def process_signal(
    signal: np.ndarray,
    threshold: float,
    cutoff: int,
    packet: np.ndarray,
    carryover: int,
    packet_slack: float
) -> tuple:
    """Decides if the signal is part of a packet

    Arguments:
        signal (np.ndarray): The numpy array that carries the IQ packets of the
            signal data.

        threshold (float): The minimum value that a signal must exceed to be
            considered part of a packet.

        cutoff (int): The number of IQ values that are allowed to be under the
            threshold and still be considered part of a packet.

        packet (np.ndarray): Holds the pieces of collected signals that  contain
            the packet information.

        carryover (int): If a packet is not finished being created then this
        will contain the value of the number of index's that were below the
        threshold when the signal ended (if any).

        packet_slack (int): The amount of indexes that will be added to the discoverd
            packet to ensure the whole packet is captured.

    Returns:
        tuple (list[np.ndarray], bool, int, bool):
        - list[np.ndarray]: A list containing all captured signals
        - bool: Indicates if the last packet in the list was completely captured.
        - int: Indicates how many indexes where below the threshold on the continuing packet
        - bool: Indicates if the first two packets in the list need to be concatenated.
    """
    # print("here")
    # Skips if signal is None
    if signal == None:
        return (None, True, 0)
    # Skips if the array is empty
    if not signal.any():
        return (None, True, 0)
    # Ensures array is 1D
    signal = signal.ravel()
    signal: np.ndarray = np.trim_zeros(signal)
    abs_signal: np.ndarray = np.absolute(signal)
    # Check if the max value is above the threshold
    max_value_in_signal = np.max(abs_signal)
    if max_value_in_signal < threshold:
        return (None, True, 0)
    # Each value maps to a index in abs_signal where the value is above the
    # threshold
    threshold_list: np.ndarray = np.where(abs_signal > threshold)[0]
    # Each value represents the difference between index i and i+1 in
    # threshold_list.
    threshold_diff: np.ndarray = np.diff(threshold_list)
    # Each value represents the
    cutoff_list: np.ndarray = np.where(threshold_diff > cutoff)[0]

    all_packets: list = list()
    new_carryover: int = signal.size - threshold_list[-1]
    end_of_packet_reached: bool = False
    # Checks if the current last packet does not carry over into the next signal
    if new_carryover > cutoff:
        end_of_packet_reached = True
        new_carryover = 0

    # If there is no packet and there is no cutoff found
    if packet == None:
        if cutoff_list.size == 0:
            # print("A")
            return (
                [signal[threshold_list[0] : threshold_list[-1]]],
                end_of_packet_reached,
                new_carryover,
            )
        for i in range(cutoff_list.size + 1):
            cutoff_list_value: int = cutoff_list[i]
            # Find the first packet
            if i == 0:
                # print("B") #! WORKING
                all_packets.append(
                    signal[threshold_list[0] : threshold_list[cutoff_list_value]]
                )
            # Find the last packet
            elif i == cutoff_list.size:
                # print("C") #! WORKING
                all_packets.append(
                    signal[threshold_list[cutoff_list[-1]] : threshold_list[-1]+1]
                )
            # Find all other packets
            else:
                # print("D") #! WORKING
                last_cutoff_list_value: int = cutoff_list[i - 1]
                all_packets.append(
                    signal[
                        threshold_list[last_cutoff_list_value + 1] : threshold_list[
                            cutoff_list_value
                        ]
                    ]
                )
        return (all_packets, end_of_packet_reached, new_carryover)
    else:
        if cutoff_list.size == 0 and end_of_packet_reached:
            # print("E")
            return (
                [signal[threshold_list[0] : threshold_list[-1]]],
                end_of_packet_reached,
                new_carryover
            )
        elif cutoff_list.size == 0 and not end_of_packet_reached:
            # print("F") #! WORKING
            joined_signal: np.ndarray = np.concatenate((packet, signal))
            return (
                [joined_signal],
                end_of_packet_reached,
                new_carryover
            )
        # Check if the carryover packet ended or if it continues into this signal
        packet_finished: bool = False
        if (threshold_list[0] + carryover) > cutoff:
            # print("G")
            all_packets.append(packet)
            packet_finished = True
        # Find all packets
        for i in range(cutoff_list.size + 1):
            if not cutoff_list.size > 0:
                break
            cutoff_list_value: int = cutoff_list[i]
            # Find the first packet
            if i == 0 and not packet_finished:
                # print("H")
                all_packets.append(np.concatenate((packet, signal[: threshold_list[cutoff_list_value]])))
            elif i == 0 and packet_finished:
                # print("I")
                # print(cutoff_list)
                # print(cutoff_list_value)
                all_packets.append(
                    signal[threshold_list[0] : threshold_list[cutoff_list_value]]
                )
            # Find the last packet
            elif i == cutoff_list.size:
                # print("J")
                all_packets.append(
                    signal[threshold_list[cutoff_list[-1]] : threshold_list[-1]+1]
                )
            # Find all other packets
            else:
                # print("K")
                last_cutoff_list_value: int = cutoff_list[i - 1]
                all_packets.append(
                    signal[
                        threshold_list[last_cutoff_list_value + 1] : threshold_list[
                            cutoff_list_value
                        ]
                    ]
                )
        return (all_packets, end_of_packet_reached, new_carryover)


class PacketDetect:
    def __init__(
        self, stream_q: mp.Queue, threshold: float, cutoff: int, packet_q: mp.Queue, packet_slack: int
    ):
        """A class that handles detecting when a signal is part of a packet.

        Arguments:
            stream_q (mp.Queue): A queue holding iq samples and the order in
                which they were added.

            threshold (float): The value that signifies when a signal should
                start to considered a packet.

            cutoff (int): The number of iq values that need to be below the
                threshold for the signal to be considered ended.

            packet_q (mp.Queue): A queue holding iq samples and a bool
                identifying if they are part of a packet.

            packet_slack (int): The amount of indexes that will be added to the
                discovered packet to ensure the whole packet is captured.
        """
        self.stream_q: mp.Queue = stream_q
        self.packet_q: mp.Queue = packet_q
        self.threshold: float = threshold
        self.cutoff: int = cutoff
        self.packet_slack: int = packet_slack
        self.packet: np.ndarray = None
        self.carryover: int = None
        self.run = True

    def __prime_packet_detect(self) -> None:
        print("Preparing packet_detect")
        hdf5 = HDF5Handler()
        primer_signals = list()
        primer_signals.append(hdf5.get_signal('priming_signals', 'signal1'))
        primer_signals.append(hdf5.get_signal('priming_signals', 'signal2'))
        primer_signals.append(hdf5.get_signal('priming_signals', 'signal3'))
        # Runs the jit function with dummy data to compile it before running
        # real data through it
        for signal in primer_signals:
            signal_chunks = np.array_split(signal, 40)
            for chunk in signal_chunks:
                self.stream_q.put(chunk)
        self.stream_q.put("DONE")
        self.__find_packets()
        # Clean out packet_q of dummy data
        timeout = 0
        while True:
            print("AAAA")
            data = self.packet_q.get()
            if type(data) == str:
                if data == "DONE":
                    break
        print("packet_detect preped")

    def __find_packets(self) -> None:
        """Decides when a signal is part of a packet."""
        count = 0
        while self.run:
            count += 1
            if count > 5000:
                print("packet_detect still alive")
                count = 0
            signal = self.stream_q.get()
            start_time = time()
            if type(signal) == str:
                self.packet_q.put("DONE")
                break
            all_packets, end_of_packet_reached, self.carryover = process_signal(
                signal, self.threshold, self.cutoff, self.packet, self.carryover, self.packet_slack
            )
            if not all_packets:
                continue
            if len(all_packets) > 0 and end_of_packet_reached:
                self.packet = None
                self.carryover = 0
                self.packet_q.put(all_packets)
            elif len(all_packets) > 0 and not end_of_packet_reached:
                self.packet = all_packets.pop()
                self.packet_q.put(all_packets)
            # print(f'TIME: {time() - start_time}')
        print("EXITED PACKET_DETECT")

    def start_packet_detect(self) -> None:
        self.__prime_packet_detect()
        self.__find_packets()

if __name__ == '__main__':
    
    q_1 = mp.Queue()
    q_2 = mp.Queue()
    packet_d = PacketDetect(q_1, 1.6, 500, q_2, 100.0)
    packet_d.start_packet_detect()
