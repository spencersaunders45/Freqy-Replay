import numpy as np
import matplotlib.pyplot as plt

# Let's assume your captured signal is stored in a variable named `captured_signal`
# And your sample rate is stored in a variable named `sample_rate`


def plot_signal(captured_signal, sample_rate, threshold=None):
    # Generate a time axis based on the length of your signal and the sample rate
    time_axis = np.arange(len(captured_signal)) / sample_rate

    # Plot the signal
    plt.figure(figsize=(15, 5))
    plt.plot(time_axis, np.abs(captured_signal), label="Captured Signal")

    # Optionally, plot a threshold line
    if threshold:
        plt.axhline(y=threshold, color="r", linestyle="--", label="Threshold")

    # Highlighting the above-threshold data points
    # above_threshold = np.abs(captured_signal) > threshold
    # plt.plot(time_axis[above_threshold], np.abs(captured_signal)[above_threshold], 'ro', label='Potential Packets')

    plt.title("Captured Signal with Potential Packets Highlighted")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
