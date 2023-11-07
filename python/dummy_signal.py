import numpy as np
import matplotlib.pyplot as plt

# Parameters for the dummy signal
sample_rate = 1e6  # Sample rate in samples per second (Hz)
duration = 1       # Signal duration in seconds
frequency = 2.4e3  # Signal frequency in Hz (for a 2.4 GHz signal, you'd use 2.4e9)

# Time vector for the signal
t = np.arange(0, duration, 1/sample_rate)

# Create a dummy signal (e.g., a sine wave)
signal = np.sin(2 * np.pi * frequency * t)

# Parameters for the dummy packet
packet_duration = 1e-2      # Duration of the packet in seconds (1e-4)
packet_length = int(packet_duration * sample_rate)  # Number of samples in the packet
packet = np.ones(packet_length)  # Create a square pulse for the dummy packet

# Positions where packets will be inserted
packet_positions = [
    int(0.1 * len(signal)),
    int(0.3 * len(signal)),
    int(0.5 * len(signal)),
    int(0.7 * len(signal)),
    int(0.9 * len(signal))
]

# Insert packets into the signal
for pos in packet_positions:
    signal[pos:pos + packet_length] += packet

# Add Gaussian noise to the entire signal (signal + packets)
noise_variance = 0.1
noisy_signal = signal + np.random.normal(0, np.sqrt(noise_variance), signal.shape)

# Plot the noisy signal with the packets
plt.figure(figsize=(15, 5))
plt.plot(t, noisy_signal)
# plt.plot(t, test)
plt.title("Noisy Signal with Packets")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()


