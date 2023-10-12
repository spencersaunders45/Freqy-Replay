import numpy as np

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
    # Creates an array of frequencies that corresponds to each value in fft_result.
    freqs:np.ndarray = np.fft.fftfreq(len(signal_data), 1/sample_rate)
    # returns the frequency with the highest magnitude.
    dom_freq:float = freqs[np.argmax(np.abs(fft_result))]
    # Add the center frequency to the offset frequency to get the absolute frequency
    return center_freq + dom_freq
