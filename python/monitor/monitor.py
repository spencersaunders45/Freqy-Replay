from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
import multiprocessing as mp
import threading as th
from time import sleep
import numpy as np
import argparse, traceback
import sys, os
import signal
import queue

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f"{FILE_DIR}/../"
sys.path.insert(0, PYTHON_DIR)
TOML_FILE = f'{PYTHON_DIR}/config.toml'

from helper_functions.uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
from monitor.packet_saver import PacketSaver
from monitor.packet_detect import PacketDetect
from helper_functions.plot_signal import plot_signal


class Monitor:
    # TODO: Add parameter to add a signal to the queue to stop the process
    def __init__(self):
        """Monitors the airwaves for a target frequency

        Arguments:
            sdr (SDR): A SDR class to interface with the SDR.

            stream_q (mp.Queue): A shared queue to feed packet_detect signals.
        """
        self.hdf5: HDF5Handler = HDF5Handler()
        self.settings: TOMLDocument = TOMLFile(TOML_FILE).read()
        # TOML settings
        self.toml_radio: dict = self.settings.get("RADIO")
        self.toml_monitor: dict = self.settings.get("MONITOR")
        # RADIO
        self.center_freq: float = self.toml_radio["center_freq"]
        self.sample_rate: float = self.toml_radio["sample_rate"]
        self.rx_gain: int = self.toml_radio["rx_gain"]
        self.tx_gain: int = self.toml_radio["tx_gain"]
        self.uhd_id: str = self.toml_radio["uhd_id"]
        # MONITOR
        self.view_sample: float = self.toml_monitor["view_sample"]
        self.samples_to_collect: float = self.toml_monitor["samples_to_collect"]
        self.threshold: float = self.toml_monitor["threshold"]
        self.cutoff: float = self.toml_monitor["cutoff"]
        self.packet_slack: int = self.toml_monitor["packet_slack"]
        self.queue_size: int = self.toml_monitor["queue_size"]
        self.file_name: int = self.toml_monitor["file_name"]
        self.max_loops: int = self.toml_monitor["max_loops"]

        # Queues
        self.stream_q = mp.Queue(self.queue_size)
        self.packet_queue = mp.Queue(self.queue_size)
        # Signal done
        self.keep_going: bool = True

    def __empty_q(self) -> None:
        while True:
            try:
                self.stream_q.get(timeout=0.1)
            except queue.Empty:
                break

    def __sigint_handler(self, sig_num, frame):
        self.keep_going = False
        sleep(.05)
        self.__empty_q()
        self.stream_q.put("DONE", timeout=.05)
        self.packet_detect_p.kill()
        self.packet_saver_p.kill()
        exit(0)

    def launch(self) -> None:
        signal.signal(signal.SIGINT, self.__sigint_handler)
        if self.view_sample:
            self.view_signals()
            exit(0)
        packet_detect = PacketDetect(
            self.stream_q,
            self.threshold,
            self.cutoff,
            self.packet_queue,
            self.packet_slack,
        )
        packet_saver = PacketSaver(
            self.file_name,
            self.packet_queue,
            self.hdf5,
            self.center_freq,
            self.sample_rate,
            self.threshold,
        )
        self.packet_detect_p = mp.Process(target=packet_detect.start_packet_detect)
        self.packet_saver_p = mp.Process(target=packet_saver.start)
        self.packet_detect_p.start()
        self.packet_saver_p.start()
        self.__stream_rx_data()

    def view_signals(self) -> None:
        self.sdr = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
        signals = list()
        for _ in range(self.samples_to_collect):
            data = self.sdr.rx_data()
            signals.append(data)
        # Put the signal together
        big_signal = np.zeros(10)
        for signal in signals:
            signal = signal.ravel()
            signal = np.trim_zeros(signal)
            if big_signal.all():
                big_signal = signal
            else:
                big_signal = np.concatenate((big_signal, signal))
        plot_signal(big_signal, self.sample_rate, self.threshold)

    def __stream_rx_data(self) -> None:
        """Streams signals captured from the SDR"""
        self.sdr = SDR(self.sample_rate, self.center_freq, self.tx_gain, self.rx_gain)
        print("SDR finished setup")
        heartbeat = 0
        kill_count: int = 0
        while self.keep_going:
            data = self.sdr.rx_data()
            # Waits for queue to empty if it fills
            if self.stream_q.full():
                print("stream_q full")
                while self.stream_q.qsize() != 0:
                    sleep(0.001)
                print("stream_q empty")
                continue
            self.stream_q.put(data)
            heartbeat += 1
            # Displays a heartbeat
            if heartbeat > 5000:
                heartbeat = 0
                print("SDR still alive")
            # Kills if max_loop is set
            if self.max_loops:
                kill_count += 1
                if kill_count > self.max_loops:
                    self.stream_q.put("DONE")
                    break
        print("EXITED STREAMER")

