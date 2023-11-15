import numpy as np
import matplotlib.pyplot as plt
from helper_functions.hdf5_handler import HDF5Handler

# Parameters for the dummy signal
sample_rate = 15000000.0  # Sample rate in samples per second (Hz)
duration = 1  # Signal duration in seconds
frequency = 2.4e9  # Signal frequency in Hz (for a 2.4 GHz signal, you'd use 2.4e9)

packet_durations = [1e-4, 1e-3, 1e-2, 1e-1]

for i in range(len(packet_durations)):
    # Time vector for the signal
    t = np.arange(0, duration, 1 / sample_rate)

    # Create a dummy signal (e.g., a sine wave)
    signal = np.sin(2 * np.pi * frequency * t)

    all_packet_positions = [
        [
            int(0.1 * len(signal)),
            int(0.2 * len(signal)),
            int(0.3 * len(signal)),
            int(0.4 * len(signal)),
            int(0.5 * len(signal)),
            int(0.6 * len(signal)),
        ],
        [
            int(0.1 * len(signal)),
            int(0.2 * len(signal)),
            int(0.3 * len(signal)),
            int(0.4 * len(signal)),
            int(0.5 * len(signal)),
        ],
        [
            int(0.1 * len(signal)),
            int(0.3 * len(signal)),
            int(0.5 * len(signal)),
            int(0.7 * len(signal)),
        ],
        [int(0.1 * len(signal)), int(0.4 * len(signal)), int(0.7 * len(signal))],
    ]

    # Parameters for the dummy packet
    packet_duration = packet_durations[i]  # Duration of the packet in seconds (1e-4)
    packet_length = int(
        packet_duration * sample_rate
    )  # Number of samples in the packet
    packet = np.ones(packet_length)  # Create a square pulse for the dummy packet

    # Positions where packets will be inserted
    packet_positions = all_packet_positions[i]

    # Insert packets into the signal
    for pos in packet_positions:
        signal[pos : pos + packet_length] += packet

    # Add Gaussian noise to the entire signal (signal + packets)
    noise_variance = 0.1
    noisy_signal = signal + np.random.normal(0, np.sqrt(noise_variance), signal.shape)
    noisy_signal = np.abs(noisy_signal)

    # time_axis = np.arange(len(captured_signal)) / sample_rate

    # Save the noisy_signal
    # hdf5 = HDF5Handler()
    # hdf5.save_signal(noisy_signal, noisy_signal.size, frequency, 999.9, 1.5, sample_rate, "priming_signals")

    # Plot the noisy signal with the packets
    plt.figure(figsize=(15, 5))
    plt.plot(t, noisy_signal)
    plt.title("Noisy Signal with Packets")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
