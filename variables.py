import pygame  # To use pygame
from constants import WIDTH_SCREEN, HEIGHT_SCREEN, CAR_SIZES  # Import the screen size
from utils import scale_image  # Import the scale_image function

DEBUG = False  # True for debug mode, False for normal mode
KEYBOARD_CONTROL = False  # True to control the car with the keyboard
SEE_CURSOR = False  # True to see the cursor position and color when clicking
SEED = None  # Seed of the random (None to not use a seed)

RECT_BLIT_CAR = pygame.rect.Rect(0, 0, 0, 0)  # Coordinates of the rect used to erase the cars of the screen
RECTS_BLIT_UI = []  # Coordinates of the rects used to erase the ui of the screen

START = False  # Start the game (True or False)
PLAY = False  # Stop the game (True or False)

PAUSE = False  # Pause the game (True or False)
DURATION_PAUSES = 0  # Duration of all the pauses
START_TIME_PAUSE = 0  # Time when the game has been paused
TIME_REMAINING_PAUSE = 0  # Time remaining when the game has been paused

CHANGE_CHECKPOINT = False  # Change the checkpoint for the actual map
SEE_CHECKPOINTS = False  # See the checkpoints
CHECKPOINTS = None  # List of checkpoints

# We open the file parameters to read the number of the map and the number of cars
with open("data/parameters", "r") as file_parameters_read:
    num_map, nb_cars = file_parameters_read.readlines()
    NUM_MAP = int(num_map)  # Map number
    NB_CARS = int(nb_cars)  # Number of cars

CHANGE_NB_CARS = False  # Change the number of cars
STR_NB_CARS = str(NB_CARS)  # Text of the number of cars

BACKGROUND = None  # Image of the background
BACKGROUND_MASK = None    # Mask of the black pixels of the background (used to detect collisions)
CAR_IMAGE = None  # Image of the car

USE_GENETIC = True  # True to use the genetic algorithm, False to just play
GENERATION = 1  # Number of the generation
NB_CARS_ALIVE = 0  # Number of cars alive

TIME_REMAINING = 0  # Time remaining for the genetic algorithm
START_TIME = 0  # Start time of the genetic algorithm


def change_map(num):
    """
    Change the map and all the variables associated

    Args:
        num (int): number of the new map
    """
    global NUM_MAP, BACKGROUND, BACKGROUND_MASK, CAR_IMAGE, CHECKPOINTS
    NUM_MAP = num  # New map number
    # We change the variable in the file parameters
    with open("data/parameters", "w") as file_parameters_write:
        file_parameters_write.write(str(NUM_MAP) + "\n" + str(NB_CARS))

    BACKGROUND = pygame.transform.scale(pygame.image.load("images/background_" + str(NUM_MAP) + ".png"), (WIDTH_SCREEN, HEIGHT_SCREEN))  # Image of the background
    BACKGROUND_MASK = pygame.mask.from_threshold(BACKGROUND, (0, 0, 0, 255), threshold=(1, 1, 1, 1))  # Mask of the black pixels of the background (used to detect collisions)
    CAR_IMAGE = scale_image(pygame.image.load("images/car.bmp"), CAR_SIZES[NUM_MAP])    # Image of the car

    CHECKPOINTS = []  # List of checkpoints
    with open("data/checkpoints_" + str(NUM_MAP), "r") as file_checkpoint_read:
        checkpoints = file_checkpoint_read.readlines()
        for checkpoint in checkpoints:
            a, b = checkpoint.split(" ")
            CHECKPOINTS.append((int(a), int(b)))
