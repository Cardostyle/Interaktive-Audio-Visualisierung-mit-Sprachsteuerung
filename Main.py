import pyaudio
import numpy as np
import pygame
import speech_recognition as sr

# Own functions
from Ui import (
    render_text,
    draw_waveform,
    draw_spectrum
)
from SoundChanger import (
    filter_quiet_sounds,
    change_pitch,
    lowpass_filter,
    highpass_filter,
    robot_voice,
    chorus
)

# Audio Stream Configuration
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
GAIN = 5.0  # Increase the input volume

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


# Visualization Modes
MODES = ["waveform", "spectrum"]
mode_index = 0
# Colors
background_color = (0, 0, 0)
diagram_color = (0, 255, 0)
# Font and Color for Text
font = pygame.font.Font(None, 36)  # Default font with size 36
text_color = (255, 255, 255)  # White color
text_is_white = True

# Different output Modes
mic_output_enabled = False
reverb_enabled = False
robot_enabled = False
highpass_enabled = False
lowpass_enabled = False
chorus_enabled = False
pitch_mode = 0  # 0 = Normal, 1 = High, 2 = Low
pitch_modes_text = ["Normal", "Chipmunk", "Deep"]#


# Speech Recognition Initialization
recognizer = sr.Recognizer()
mic = sr.Microphone()
voice_active = False


# Function for Speech Recognition
def process_voice_commands():
    global background_color, diagram_color, mode_index, mic_output_enabled, reverb_enabled, pitch_mode, text_is_white, highpass_enabled, lowpass_enabled,robot_enabled, chorus_enabled
    try:
        with mic as source:
            audio = recognizer.listen(source,timeout=3, phrase_time_limit=3)
        command = recognizer.recognize_google(audio).lower()

        if "background red" in command:
            background_color = (255, 0, 0)
        elif "background blue" in command:
            background_color = (0, 0, 255)
        elif "background green" in command:
            background_color = (0, 255, 0)
        elif "background yellow" in command:
            background_color = (255, 255, 0)
        elif "background white" in command:
            background_color = (255, 255, 255)
        elif "diagram red" in command:
            diagram_color = (255, 0, 0)
        elif "diagram blue" in command:
            diagram_color = (0, 0, 255)
        elif "diagram green" in command:
            diagram_color = (0, 255, 0)
        elif "diagram yellow" in command:
            diagram_color = (255, 255, 0)
        elif "diagram white" in command:
            diagram_color = (255, 255, 255)
        elif "diagram black" in command:
            diagram_color = (0, 0, 0)
        elif "toggle diagram" in command:
            mode_index = (mode_index + 1) % len(MODES)
        elif "pitch" in command:
            pitch_mode = (pitch_mode + 1) % 3
        elif "microphone" in command:
            mic_output_enabled = not mic_output_enabled
        elif "text" in command:
             text_is_white = not text_is_white
        elif "highpass" in command:
            highpass_enabled = not highpass_enabled
        elif "lowpass" in command:
            lowpass_enabled = not lowpass_enabled
        elif "chorus" or "double" in command:
            chorus_enabled = not chorus_enabled
        elif "robot" in command:
            robot_enabled = not robot_enabled
        else:
            print("not recognized \nYou Said: " + command)
    except sr.UnknownValueError:
        pass  # Ignore unrecognized commands -> Shouldn't be a problem
    except sr.WaitTimeoutError:
        print("No speech detected within the timeout period.")
        return  # End the function
    except sr.RequestError:
        print("Speech recognition service is unavailable.")




# Main Loop
running = True
while running:
    try:
        # Capture Audio
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16) / 32768.0
        data *= GAIN

        # Filter out quiet sounds
        data = filter_quiet_sounds(data, threshold=0.001)

        # handle Chorus
        if chorus_enabled:
            data=chorus(data)

        # Handle Pitch Change
        if pitch_mode != 0:
            data = change_pitch(data, pitch_mode)

        #handle Lowpass
        if highpass_enabled:
            data=highpass_filter(data)

        #handle Highpass
        if lowpass_enabled:
            data=lowpass_filter(data)
        #handle Robot Voice
        if robot_enabled:
            data=robot_voice(data,RATE)

        # Handle Microphone Output
        if mic_output_enabled:
            stream.write((data * 32768).astype(np.int16).tobytes())

        # Event Handling with Keyboard
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
                        text_is_white = not text_is_white
                    case pygame.K_2:
                        mic_output_enabled = not mic_output_enabled
                    case pygame.K_4:
                        pitch_mode = (pitch_mode + 1 // 1) % 3  # Cycle through pitch modes
                    case pygame.K_5:
                        voice_active = True
                    case pygame.K_6:
                        robot_enabled = not robot_enabled
                    case pygame.K_7:
                        highpass_enabled = not highpass_enabled
                    case pygame.K_8:
                        lowpass_enabled = not lowpass_enabled
                    case pygame.K_9:
                        chorus_enabled = not chorus_enabled
                    case pygame.K_q:
                        background_color = (255, 0, 0)  # Red
                    case pygame.K_w:
                        background_color = (0, 255, 0)  # Green
                    case pygame.K_e:
                        background_color = (0, 0, 255)  # Blue
                    case pygame.K_r:
                        background_color = (255, 255, 0)  # Yellow
                    case pygame.K_t:
                        background_color = (255, 255, 255)  # White
                    case pygame.K_z:
                        background_color = (0, 0, 0)  # Black
                    case pygame.K_a:
                        diagram_color = (255, 0, 0)  # Red
                    case pygame.K_s:
                        diagram_color = (0, 255, 0)  # Green
                    case pygame.K_d:
                        diagram_color = (0, 0, 255)  # Blue
                    case pygame.K_f:
                        diagram_color = (255, 255, 0)  # Yellow
                    case pygame.K_g:
                        diagram_color = (255, 255, 255)  # White
                    case pygame.K_h:
                        diagram_color = (0, 0, 0)  # Black

        # Visualization
        if MODES[mode_index] == "waveform":
            draw_waveform(screen, data, background_color, diagram_color)
        elif MODES[mode_index] == "spectrum":
            draw_spectrum(screen, data, background_color, diagram_color)

        if text_is_white:
            text_color = (255, 255, 255)
        else:
            text_color = (0, 0, 0)

        render_text(screen, font,f"Visualization Mode: {MODES[mode_index]}", 10, 10,text_color)
        render_text(screen, font, f"Mic Output Enabled: {mic_output_enabled}", 10, 50,text_color)
        render_text(screen, font, f"Pitch Mode: {pitch_modes_text[pitch_mode]}", 10, 130,text_color)
        render_text(screen, font, f"Voice Input: {voice_active}", 10, 90,text_color)

        effects = ""
        if highpass_enabled:
            effects+="Highpass "
        if lowpass_enabled:
            effects+="Lowpass "
        if robot_enabled:
            effects+="Robot "
        if chorus_enabled:
            effects+="Chorus "

        render_text(screen, font, f"Effects Enabled: {effects}", 10, 170,text_color)

        pygame.display.flip()
        clock.tick(20)

        # handle Voice_commands
        if voice_active:
            process_voice_commands()
            voice_active = False

    except KeyboardInterrupt:
        running = False

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
