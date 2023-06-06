import pygame  # To use pygame
import variables  # Import the variables
from constants import WINDOW, RADIUS_CHECKPOINT, FONT, RECT_GARAGE, LARGE_FONT  # Import the constants
from utils import text_rec  # Import the text_rec function


def edit_background():
    """
    Add elements to the background for the rest of the game
    """
    # Add a text for the debug mode
    variables.BACKGROUND.blit(FONT.render("Activer debug :", True, (255, 255, 255), (0, 0, 0)), (1290, 640))  # Add the debug text
    variables.BACKGROUND.blit(FONT.render("Nombre de voitures", True, (0, 0, 0), (128, 128, 128)), (1060, 25))  # Add the yes text
    pygame.draw.line(variables.BACKGROUND, (0, 0, 0), (1280, 120), (1280, 0), 2)  # Line at the right
    pygame.draw.line(variables.BACKGROUND, (0, 0, 0), (325, 120), (325, 0), 2)  # Line at the left


def display_checkpoints():
    for checkpoint in variables.CHECKPOINTS:
        pygame.draw.circle(WINDOW, (255, 0, 0), checkpoint, RADIUS_CHECKPOINT, 1)


def display_text_ui(caption, pos):
    """
    Display a text with a variable

    Args:
        caption (str): caption of the text
        pos (tuple): position of the text
    """
    text = FONT.render(caption, True, (0, 0, 0), (128, 128, 128))  # Create the text
    WINDOW.blit(text, pos)  # Draw the text
    variables.RECTS_BLIT_UI.append(text_rec(text, pos))  # Add the rectangle of the text to the list of rectangles to blit


def display_garage():
    """
    Display the garage
    """
    # Create rectangles for the garage
    pygame.draw.rect(WINDOW, (128, 128, 128), RECT_GARAGE, 0)
    pygame.draw.rect(WINDOW, (115, 205, 255), RECT_GARAGE, 2)
    WINDOW.blit(LARGE_FONT.render("Super garage", True, (0, 0, 0), (128, 128, 128)), (RECT_GARAGE[0] + 165, RECT_GARAGE[1] + 10))


def erase_garage():
    """
    Erase the garage
    """
    rect = pygame.Rect(RECT_GARAGE)  # We create a rectangle with the position of the garage
    WINDOW.blit(variables.BACKGROUND, rect, rect)  # We erase the garage
    variables.DISPLAY_GARAGE = False  # We stop the display of the garage
