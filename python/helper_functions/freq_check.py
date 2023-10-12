import numpy as np
# from numba import jit
# from time import time
# import matplotlib.pyplot as plt

""" 
view the real part of an imaginary number with `.real`
view the complex part of an imaginary number with `.imag`
"""

def dominant_frequency(signal_data:np.ndarray, sample_rate:float, center_freq:float) -> float:
    """Computes the dominant frequency of provided signal.

    Arguments:
        signal_data (np.ndarray): The data representing the captured signal.
        sample_rate (float): The sample rate set on the SDR.
        center_freq (float): The center frequency set on the SDR.

    Returns:

    """
    # Remove the DC component from the signal_data
    signal_data:np.ndarray = signal_data - np.mean(signal_data)
    # Gets the magnitude and phase angle of the signal
    fft_result:np.ndarray = np.fft.fft(signal_data)
    # 
    freqs:np.ndarray = np.fft.fftfreq(len(signal_data), 1/sample_rate)
    dom_freq:float = freqs[np.argmax(np.abs(fft_result))]
    return center_freq + dom_freq
