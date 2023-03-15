import h5py  # python3 -m pip install pytest pytest-mpi h5py
from h5py import Group, Dataset
import numpy as np
import os, sys, traceback
from random import randint
from datetime import date, datetime

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SIGNALS_DIR = f"{FILE_DIR}/../captured_signals/"
PYTHON_DIR = f"{FILE_DIR}/../"
sys.path.insert(0, PYTHON_DIR)

from helper_functions.plot_signal import plot_signal

"""
TODO: Add methods that allow you to update the metadata
"""


class HDF5Handler:
    def __init__(self) -> None:
        """Handles the saving and retrieving of captured signals"""
        pass

    def save_signal(
        self,
        signal: np.ndarray,
        signal_size: float,
        frequency: float,
        packet_length_of_time: float,
        threshold: float,
        sample_rate: float,
        file_name: str = "default",
    ) -> None:
        """Saves captured signals into a hdf5 file.

        Arguments:
            signal (np.ndarray): The captured signal.
            
            signal_size (float): The size of the signal in bytes.
            
            frequency (float): The center frequency the SDR is running.
            
            packet_length_of_time (float): The size of the packet in time (seconds).
            
            threshold (float): The threshold the packet was captured on.
            
            sample_rate (float): The sample_rate the SDR is running.
            
            file_name (str): The name of the file the packet should be saved to.
        """
        try:
            create_counter: bool = False
            if not os.path.isfile(f"{SIGNALS_DIR}{file_name}.hdf5"):
                create_counter = True
                h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "w")
            f: Group = h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "r+")
            # Add a counter to the file
            if create_counter:
                temp = f.create_dataset("counter", (1,), dtype="i")
                temp[0] = 0
            # Create a dataset and add it to the HDF5 file
            counter: Dataset = f["counter"]
            dataset: Dataset = f.create_dataset(f"signal{counter[0]}", data=signal)
            counter[0]: int = counter[0] + 1
            # Add metadata to the dataset
            dataset.attrs.create("date_captured", date.today().strftime("%d-%b-%Y"))
            dataset.attrs.create(
                "time_captured", datetime.now().time().strftime("%H:%M:%S")
            )
            dataset.attrs.create("signal_size_bytes", signal_size)
            dataset.attrs.create("signal_length_seconds", packet_length_of_time)
            dataset.attrs.create("threshold", threshold)
            dataset.attrs.create("center_frequency", frequency),
            dataset.attrs.create("sample_rate", sample_rate)
            f.close()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def get_signal(self, file_name: str, dataset: str) -> np.ndarray:
        """Gets the contents of the given hdf5 file and returns it.

        Arguments:
            file_name (str): The name of the hdf5 file. (There is no need to include the file extension)

            dataset (str): The name of the dataset in the hdf5 file.

        Returns:
            A numpy array containing the data for a signal.
        """
        try:
            f: Group = h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "r")
            signal: np.ndarray = f[dataset][:]
            f.close()
            return signal
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def plot_signal(self, file_name: str, dataset: str) -> None:
        """ Plots a captured signal """
        f: Group = h5py.File(f"{SIGNALS_DIR}{file_name}", "r")
        file_data: Dataset = f[dataset]
        signal: np.ndarray = file_data[:]
        threshold: float = file_data.attrs["threshold"]
        sample_rate: float = file_data.attrs["sample_rate"]
        f.close()
        plot_signal(signal, sample_rate, threshold)

    def __filter_signals(
        self,
        dataset: dict,
        byte_size: int,
        seconds: float,
        center_freq: float,
        sample_rate: float,
    ) -> bool:
        """ Indicates if a packet should be filtered out or not.
        
        Arguments:
            dataset (dict): The dict containing the metadata of the packet.
            
            byte_size (int): The minimum size the bytes should be.
            
            seconds (float): The minimum time the packet should be.
            
            center_frequency (float): The required center_frequency of the packet.
            
            sample_rate (float): The required sample_rate of the packet.
            
        Returns:
            bool: Indicates if the packet should be kept.
        """
        if byte_size:
            if dataset["signal_size_bytes"] >= byte_size:
                return True
        if seconds:
            if dataset["signal_length_seconds"] >= seconds:
                return True
        if center_freq:
            if dataset["center_frequency"] >= center_freq:
                return True
        if sample_rate:
            if dataset["sample_rate"] >= sample_rate:
                return True
        return False

    def display_metadata(
        self,
        file_name: str,
        byte_size: int = None,
        seconds: float = None,
        center_freq: float = None,
        sample_rate: float = None,
    ) -> None:
        """Gets the metadata of a file.

        Arguments:
            file_name (str): The name of the HDF5 file.
            
            byte_size (int): The minimum size the bytes should be.
            
            seconds (float): The minimum time the packet should be.
            
            center_frequency (float): The required center_frequency of the packet.
            
            sample_rate (float): The required sample_rate of the packet.
        """
        # Get all the dataset data from the file
        f: Group = h5py.File(f"{SIGNALS_DIR}{file_name}", "r")
        dict_dataset: dict = dict()
        for key in f.keys():
            dataset: Dataset = f[key]
            if key == "counter":
                continue
            dict_dataset[key]: dict = dict()
            for name, value in dataset.attrs.items():
                dict_dataset[key][name] = value
        f.close()
        # Filter and print the dataset data
        if byte_size or seconds or center_freq or sample_rate:
            for key in dict_dataset.keys():
                if self.__filter_signals(
                    dict_dataset[key], byte_size, seconds, center_freq, sample_rate
                ):
                    print(f"\t{key}")
                    for attribute in dict_dataset[key].keys():
                        print(f"\t\t{attribute}: {dict_dataset[key][attribute]}")
                    print()
        else:
            for key in dict_dataset.keys():
                print(f"\t{key}")
                for attribute in dict_dataset[key].keys():
                    print(f"\t\t{attribute}: {dict_dataset[key][attribute]}")
                print()

    def display_all_files(self) -> None:
        """Displays all HDF5 files and their metadata"""
        path: str = f"{PYTHON_DIR}/captured_signals/"
        file_list: list = os.listdir(path)
        for file in file_list:
            if not (".hdf5" in file):
                continue
            else:
                print(file)

    def view_datasets(self, file_name: str) -> None:
        """View all the datasets from a single file.

        Arguments:
            file_name (str): The name of the file to be examined.
        """
        f: h5py.File = h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "r")
        print(f"{file_name}.hdf5")
        for key in f.keys():
            print(f"\t{key}")

    def get_all_files(self) -> list:
        """ Gets a list of all .hdf5 file in the captured_signals dir
        
        Returns:
            list[str]: A list of file names.
        """
        all_files: list = os.listdir(f"{SIGNALS_DIR}")
        file_names: list = list()
        for file in all_files:
            if ".hdf5" in file:
                file_names.append(file)
        return all_files
