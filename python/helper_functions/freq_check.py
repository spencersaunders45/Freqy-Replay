import numpy as np
from time import time

from hdf5_handler import HDF5Handler
""" 
view the real part of an imaginary number with `.real`
view the complex part of an imaginary number with `.imag`
"""

class AnalyzeFrequency:

    def __init__(self):
        """ """
        pass

    def remove_zeros(self, signal_data:np.ndarray) -> np.ndarray:
        """ Removes zeros that follow the main signal_dat
        
        Arguments:
            signal_data (np.ndarray): The data representing the captured signal.
        """

    def dominant_frequency(self, signal_data:np.ndarray, sample_rate:float, center_freq:float) -> float:
        """Computes the dominant frequency of provided signal.

        Arguments:
            signal_data (np.ndarray): The data representing the captured signal.
            sample_rate (float): The sample rate set on the SDR.
            center_freq (float): The center frequency set on the SDR.

        Returns:
            (int) The frequency of the captured signal.
        """
        # Remove the zeros at the end of the array
        last_nonzero:int = np.max(np.where(signal_data != 0j))
        signal_data = signal_data[:last_nonzero+1]
        # Remove the DC component from the signal_data
        signal_data:np.ndarray = signal_data - np.mean(signal_data)
        # Gets the magnitude and phase angle of the signal
        fft_result:np.ndarray = np.fft.fft(signal_data)
        # Creates an array of frequencies that corresponds to each value in fft_result.
        freqs:np.ndarray = np.fft.fftfreq(len(signal_data), 1/sample_rate)
        # returns the frequency with the highest magnitude.
        dom_freq:float = freqs[np.argmax(np.abs(fft_result))]
        # Add the center frequency to the offset frequency to get the absolute frequency
        return center_freq + dom_freq

if __name__ == '__main__':
    hdf5_handler = HDF5Handler()
    af = AnalyzeFrequency()
    signal = hdf5_handler.get_signal('capture1')
    print(f'{signal}\n')
    start_time = time()
    freq = af.dominant_frequency(signal[0], 15000000.0, 2400000000.0)
    print(f'TIME: {time() - start_time}')
    print(freq)