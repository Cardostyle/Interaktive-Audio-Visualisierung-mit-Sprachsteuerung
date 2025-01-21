import numpy as np
from scipy.signal import butter, lfilter

# Function to filter quiet noises
def filter_quiet_sounds(data, threshold=0.02):
    return np.where(np.abs(data) > threshold, data, 0.0)

# Function to change pitch
def change_pitch(data, mode):
    if mode == 1:  # High pitch (Chipmunk effect)
        data = np.interp(np.arange(0, len(data), 1.2), np.arange(0, len(data)), data)
    if mode == 2:  # Low pitch (Deep voice effect)
        data = np.interp(np.arange(0, len(data), 0.8), np.arange(0, len(data)), data)
    return data

# Lowpass filter function
def lowpass_filter(signal, rate=44100, cutoff=1000):
    nyquist = rate / 2
    b, a = butter(4, cutoff / nyquist, btype='low')
    return lfilter(b, a, signal)

# Highpass filter function
def highpass_filter(signal, rate=44100, cutoff=500):
    nyquist = rate / 2
    b, a = butter(4, cutoff / nyquist, btype='high')
    return lfilter(b, a, signal)

# Function to apply a robotic voice effect
def robot_voice(signal, rate):
    t = np.arange(len(signal))
    modulation = np.sign(np.sin(2 * np.pi * 60 * t / rate))  # Square wave at 60 Hz
    modulated_signal = signal * modulation
    return modulated_signal

# Chorus effect function
def chorus(signal, rate=44100, detune=0.03, delay_ms=20):
    delay_samples = int(rate * delay_ms / 1000)

    # Generate a detuned signal
    detuned_signal = np.interp(
        np.arange(0, len(signal), 1 + detune),
        np.arange(len(signal)),
        signal
    )

    # Trim detuned_signal to match the length of the original signal
    detuned_signal = detuned_signal[:len(signal)]

    # Initialize the chorus signal
    chorus_signal = np.zeros(len(signal))
    chorus_signal[:len(signal)] += signal

    # Calculate the maximum length for the target range
    max_length = len(signal) - delay_samples

    # Add the detuned signal with delay
    chorus_signal[delay_samples:delay_samples + max_length] += detuned_signal[:max_length]

    return chorus_signal
