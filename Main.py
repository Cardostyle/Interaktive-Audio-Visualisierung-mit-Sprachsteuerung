import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import pygame
from collections import deque

# Audio Stream Configuration
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
GAIN = 5.0  # Increase the input volume
reverb_buffer = deque(maxlen=CHUNK * 2)  # Buffer für 10 Chunks

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

# Initialize Pygame for Visualization
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Audio Visualizer")
clock = pygame.time.Clock()

# Font and Color for Text
font = pygame.font.Font(None, 36)  # Default font with size 36
text_color = (255, 255, 255)  # White color
black_white = ["white", "black"]
text_index = 0

# Colors
BACKGROUND_COLOR = (0, 0, 0)
WAVE_COLOR = (0, 255, 0)

# Visualization Modes
MODES = ["waveform", "spectrum"]
mode_index = 0

# Different output Modes
mic_output_enabled = False
reverb_enabled = False
pitch_mode = 0  # 0 = Normal, 1 = High, 2 = Low
pitch_modes_text = ["Normal", "Chipmunk", "Deep"]

# Reverb Buffer
reverb_buffer = deque(maxlen=CHUNK * 2)  # Buffer for 10 chunks

# Function to Render Text
def render_text(text, x, y):
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x, y))

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

    # Calculate FFT
    spectrum = np.abs(fft(data))[:CHUNK // 2]  # Use only the first half

    # Normalize spectrum values
    spectrum /= np.max(spectrum) if np.max(spectrum) > 0 else 1

    max_height = screen.get_height()
    bar_width = max(1, screen.get_width() // len(spectrum))
    for i, value in enumerate(spectrum):
        height = int(value * max_height)  # Scale height to screen
        pygame.draw.rect(screen, WAVE_COLOR,
                         (i * bar_width, max_height - height, bar_width, height))

# Funktion für Hall mit Puffer
def apply_reverb_with_feedback(data, buffer, delay_samples=12000, decay=0.8):
    buffer.extend(data)  # Neuen Chunk in den Puffer einfügen
    if len(buffer) > delay_samples:
        delayed_signal = np.array(list(buffer)[-delay_samples:]) * decay
    else:
        delayed_signal = np.zeros_like(data)

    # Feedback hinzufügen
    feedback_signal = delayed_signal * decay
    output = data + delayed_signal + feedback_signal

    return np.clip(output, -1.0, 1.0)  # Normalisieren, um Clipping zu vermeiden

# Function to Filter Quiet Noises
def filter_quiet_sounds(data, threshold=0.02):
    return np.where(np.abs(data) > threshold, data, 0.0)

# Function to Change Pitch
def change_pitch(data, mode):
    if mode == 1:  # High pitch (Chipmunk)
        data = np.interp(np.arange(0, len(data), 1.2), np.arange(0, len(data)), data)
    if mode == 2:  # Low pitch (Deep)
        data = np.interp(np.arange(0, len(data), 0.8), np.arange(0, len(data)), data)
    return data

# Main Loop
running = True
while running:
    try:
        # Capture Audio
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16) / 32768.0
        data *= GAIN

        # Filter out quiet sounds
        data = filter_quiet_sounds(data, threshold=0.001)

        # Apply Pitch Change
        data = change_pitch(data, pitch_mode)

        # Handle Reverb
        if reverb_enabled:
            data = apply_reverb_with_feedback(data, reverb_buffer)

        # Handle Microphone Output
        if mic_output_enabled:
            stream.write((data * 32768).astype(np.int16).tobytes())

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        mode_index = (mode_index + 1) % len(MODES)
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_1:
                        text_index = (text_index + 1) % len(black_white)
                    case pygame.K_2:
                        mic_output_enabled = not mic_output_enabled
                    case pygame.K_3:
                        reverb_enabled = not reverb_enabled
                    case pygame.K_4:
                        pitch_mode = (pitch_mode + 1 // 1) % 3  # Cycle through pitch modes
                    case pygame.K_q:
                        BACKGROUND_COLOR = (255, 0, 0)  # Red
                    case pygame.K_w:
                        BACKGROUND_COLOR = (0, 255, 0)  # Green
                    case pygame.K_e:
                        BACKGROUND_COLOR = (0, 0, 255)  # Blue
                    case pygame.K_r:
                        BACKGROUND_COLOR = (255, 255, 0)  # Yellow
                    case pygame.K_t:
                        BACKGROUND_COLOR = (255, 255, 255)  # White
                    case pygame.K_z:
                        BACKGROUND_COLOR = (0, 0, 0)  # Black
                    case pygame.K_a:
                        WAVE_COLOR = (255, 0, 0)  # Red
                    case pygame.K_s:
                        WAVE_COLOR = (0, 255, 0)  # Green
                    case pygame.K_d:
                        WAVE_COLOR = (0, 0, 255)  # Blue
                    case pygame.K_f:
                        WAVE_COLOR = (255, 255, 0)  # Yellow
                    case pygame.K_g:
                        WAVE_COLOR = (255, 255, 255)  # White
                    case pygame.K_h:
                        WAVE_COLOR = (0, 0, 0)  # Black

        # Visualization
        if MODES[mode_index] == "waveform":
            draw_waveform(data)
        elif MODES[mode_index] == "spectrum":
            draw_spectrum(data)

        if black_white[text_index] == "white":
            text_color = (255, 255, 255)
        elif black_white[text_index] == "black":
            text_color = (0, 0, 0)

        render_text(f"Visualization Mode: {MODES[mode_index]}", 10, 10)
        render_text(f"Mic Output Enabled: {mic_output_enabled}", 10, 50)
        render_text(f"Reverb Enabled: {reverb_enabled}", 10, 90)
        render_text(f"Pitch Mode: {pitch_modes_text[pitch_mode]}", 10, 130)

        pygame.display.flip()
        clock.tick(30)

    except KeyboardInterrupt:
        running = False

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
