"""
Tests if setup was successful.
"""

import os, sys
import numpy as np

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = f'{FILE_DIR}/../../'
sys.path.insert(0,ROOT)

from python.helper_functions.uhd_interface import SDR

center_frequency = 915000000.0
sample_rate = 15000000.0
rx_gain = 74
tx_gain = 70

sdr = SDR(sample_rate, center_frequency, tx_gain, rx_gain)

signal = sdr.rx_data()

print(signal)
