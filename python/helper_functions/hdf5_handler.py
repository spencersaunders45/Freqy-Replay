import h5py  # python3 -m pip install pytest pytest-mpi h5py
from h5py import Group, Dataset
import numpy as np
import os, sys, traceback
from random import randint
from datetime import date, datetime

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SIGNALS_DIR = f"{FILE_DIR}/../captured_signals/"
PYTHON_DIR = f"{FILE_DIR}/../"

"""
TODO: Add name and size metadata to datasets
TODO: Create new files based off the frequency the SDR is at
    TODO: Every first dataset will be a counter (int) for naming files. Incremented every time a new dataset is added
TODO: Add methods that allow you to update the metadata
TODO: Add method that allow you to view all the dataset names in a file.
TODO: Add method that allows you to see all the hdf5 files
"""


class HDF5Handler:

    def __init__(self):
        """Handles the saving and retrieving of captured signals"""
        pass

    def save_signal(
        self,
        signal: np.ndarray,
        file_name: str,
        signal_size: float,
        frequency: float,
    ) -> None:
        """Saves captured signals into a hdf5 file.
        
        IMPORTANT: make sure to open file first with open_file method.

        Arguments:
            signal (np.ndarray): The captured signal.

            file_name (str): The name of the file. (There is no need to include the file extension)

            signal_size (float):

            frequency (float):
        """
        try:
            create_counter:bool = False
            if not os.path.isdir(f'{SIGNALS_DIR}{file_name}.hdf5'):
                create_counter = True
            f:Group = h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "w")
            # Add a counter to the file
            if create_counter:
                f.create_dataset('counter', 0)
                self.counter = 0
            # Create a dataset and add it to the HDF5 file
            dataset: Dataset = f.create_dataset(f"signal_{f['counter'][:]+1}", data=signal)
            f['counter'][...] += 1
            # Add metadata to the dataset
            dataset.attrs.create("date_captured", date.today().strftime("%d-%b-%Y"))
            dataset.attrs.create("time_captured", datetime.now().time().strftime('%H:%M:%S'))
            dataset.attrs.create("signal_size_bytes", signal_size)
            dataset.attrs.create("center_frequency", frequency)
            f.close()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def get_signal(self, file_name: str) -> np.ndarray:
        """Gets the contents of the given hdf5 file and returns it.

        Arguments:
            file_name (str): The name of the hdf5 file. (There is no need to include the file extension)

        Returns:
            A numpy array containing the data for a signal.
        """
        try:
            f: Group = h5py.File(f"{SIGNALS_DIR}{file_name}.hdf5", "r")
            signal = f["signal"][:]
            f.close()
            return signal
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def __display_metadata(self, file_name: str) -> None:
        """Gets the metadata of a file.

        Arguments:
            file_name (str): The name of the HDF5 file.
        """
        f: Group = h5py.File(f"{file_name}", "r")
        dataset: Dataset = f["signal"]
        for name, value in dataset.attrs.items():
            print(f"\t{name}: {value}")
        print()
        f.close()

    def display_file_info(self) -> None:
        """Displays all HDF5 files and their metadata"""
        path = f"{PYTHON_DIR}/captured_signals/"
        file_list = os.listdir(path)
        for file in file_list:
            if not (".hdf5" in file):
                continue
            else:
                print(file)
                self.__display_metadata(f"{path}{file}")


if __name__ == "__main__":
    hdf5_handler = HDF5Handler()
    random_words = list()
    f = open(f"{PYTHON_DIR}/testing/random_words.txt")
    for line in f:
        random_words.append(line.strip())
    f.close()
    for _ in range(5):
        list_size = randint(100, 500)
        signal = np.random.randint(-7, 7, list_size)
        word1 = random_words[randint(0, len(random_words) - 1)]
        word2 = random_words[randint(0, len(random_words) - 1)]
        file_name = f"{word1}-{word2}"
        hdf5_handler.save_signal(
            signal, file_name, date.today(), signal.nbytes, 915000000.0
        )
    hdf5_handler.display_file_info()
