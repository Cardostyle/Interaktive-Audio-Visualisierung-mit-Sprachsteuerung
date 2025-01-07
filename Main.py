import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import pygame

# Audio Stream Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize Pygame for Visualization
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Audio Visualizer")
clock = pygame.time.Clock()

# Colors
BACKGROUND_COLOR = (0, 0, 0)
WAVE_COLOR = (0, 255, 0)
SPECTRUM_COLOR = (255, 0, 0)

# Visualization Modes
MODES = ["waveform", "spectrum"]
mode_index = 0

# Function to Draw Waveform
def draw_waveform(data):
    screen.fill(BACKGROUND_COLOR)
    center_y = screen.get_height() // 2
    step = len(data) // screen.get_width()
    points = [(x, center_y - int(data[x * step] * center_y)) for x in range(screen.get_width())]
    pygame.draw.lines(screen, WAVE_COLOR, False, points, 2)

# Function to Draw Spectrum
def draw_spectrum(data):
    screen.fill(BACKGROUND_COLOR)
    spectrum = np.abs(fft(data))[:CHUNK // 2]
    max_height = screen.get_height()
    bar_width = screen.get_width() // len(spectrum)
    for i, value in enumerate(spectrum):
        height = int(value / max(spectrum) * max_height)
        pygame.draw.rect(screen, SPECTRUM_COLOR, (i * bar_width, max_height - height, bar_width, height))

# Main Loop
running = True
while running:
    try:
        # Capture Audio
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16) / 32768.0

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mode_index = (mode_index + 1) % len(MODES)

        # Visualization
        if MODES[mode_index] == "waveform":
            draw_waveform(data)
        elif MODES[mode_index] == "spectrum":
            draw_spectrum(data)

        pygame.display.flip()
        clock.tick(30)

    except KeyboardInterrupt:
        running = False

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
