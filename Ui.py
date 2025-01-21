import pygame
import numpy as np

# Function to Render Text
def render_text(screen, font, text, x, y, text_color):
    """
    Renders text onto the Pygame screen.

    Parameters:
        screen (pygame.Surface): The Pygame screen to render text onto.
        font (pygame.Font): The font to use for rendering.
        text (str): The text to render.
        x (int): The x-coordinate of the text.
        y (int): The y-coordinate of the text.
        text_color (tuple): The RGB color of the text.
    """
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x, y))


# Function to Draw Waveform
def draw_waveform(screen, data, background_color, graph_color):
    """
    Draws a waveform visualization on the Pygame screen.

    Parameters:
        screen (pygame.Surface): The Pygame screen to draw on.
        data (numpy.ndarray): The audio data to visualize.
        background_color (tuple): The RGB background color of the screen.
        graph_color (tuple): The RGB color of the waveform.
    """
    screen.fill(background_color)
    center_y = screen.get_height() // 2
    step = len(data) // screen.get_width()
    points = [(x, center_y - int(data[x * step] * center_y)) for x in range(screen.get_width())]
    pygame.draw.lines(screen, graph_color, False, points, 2)


# Function to Draw Spectrum
def draw_spectrum(screen, data, background_color, graph_color):
    """
    Draws a spectrum visualization on the Pygame screen.

    Parameters:
        screen (pygame.Surface): The Pygame screen to draw on.
        data (numpy.ndarray): The audio data to visualize (frequency spectrum).
        background_color (tuple): The RGB background color of the screen.
        graph_color (tuple): The RGB color of the spectrum bars.
    """
    screen.fill(background_color)

    # Calculate FFT
    spectrum = data[:len(data) // 2]

    # Normalize spectrum values
    spectrum /= max(np.max(spectrum), 1e-6)

    max_height = screen.get_height()
    bar_width = max(1, screen.get_width() // len(spectrum))
    for i, value in enumerate(spectrum):
        height = int(value * max_height)  # Scale height to screen
        pygame.draw.rect(screen, graph_color,
                         (i * bar_width, max_height - height, bar_width, height))
