from tomlkit.toml_file import TOMLFile
import multiprocessing as mp
import threading as th
from time import time

from uhd_interface import SDR
from helper_functions.hdf5_handler import HDF5Handler
from helper_functions.freq_check import dominant_frequency

import numpy as np

settings = TOMLFile('config.toml').read()

""" 
TODO: add arguments to view all saved frequencies
TODO: add argument to select saved frequency
"""

# sdr = SDR(15000000.0, 2400000000.0, 70, 74, None)
hdf5 = HDF5Handler()

# signal = sdr.rx_data()
signal = hdf5.get_signal('capture1').tolist()
clean_signal = list()

for i in signal:
    for j in i:
        if j.real == 0.0 or j.imag == 0.0:
            continue
        clean_signal.append(j)

# clean_signal = np.array(clean_signal)
start_time = time()
print(dominant_frequency(clean_signal, 15000000.0, 2400000000.0))
print(time() - start_time)
