import h5py #python3 -m pip install pytest pytest-mpi h5py
import numpy as np
import os, sys, traceback

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SIGNALS_DIR = f'{FILE_DIR}/../captured_signals/'

"""
//TODO: Save numpy arrays into HDF5 files
TODO: Add name and size metadata to datasets
TODO: Create new files based off the frequency the SDR is at
    TODO: Every first dataset will be a counter (int) for naming files. Incremented every time a new dataset is added
TODO: Add methods that allow you to update the metadata
TODO: Add method that allow you to view all the dataset names in a file.
TODO: Add method that allows you to see all the hdf5 files
"""

class HDF5Handler:
    """ Handles the saving and retrieving of captured signals """
    def __init__(self):
        pass

    def save_signal(self, signal:np.ndarray, file_name:str) -> None:
        """ Saves captured signals into a hdf5 file.
        
        Arguments:
            signal (np.ndarray): The captured signal. (There is no need to include the file extension)
            file_name (str): The name of the file.
        """
        try:
            f = h5py.File(f'{SIGNALS_DIR}{file_name}.hdf5', 'w')
            f.create_dataset('signal', data=signal)
            f.close()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def get_signal(self, file_name:str) -> np.ndarray:
        """ Gets the contents of the given hdf5 file and returns it.
        
        Arguments:
            file_name (str): The name of the hdf5 file. (There is no need to include the file extension)

        Returns:
            A numpy array containing the data for a signal.
        """
        try:
            f = h5py.File(f'{SIGNALS_DIR}{file_name}.hdf5', 'r')
            signal = f['signal'][:]
            f.close()
            return signal
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise


if __name__ == '__main__':
    hdf5_handler = HDF5Handler()
    signal = np.zeros(256)
    hdf5_handler.save_signal(signal, 'test')
    extracted_signal = hdf5_handler.get_signal('test')
    print(extracted_signal)