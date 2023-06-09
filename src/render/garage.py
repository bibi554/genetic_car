from src.other.utils import convert_to_new_window  # To convert the position if we resize the window
from src.render.rect_garage import RectGarage, reset_dict_check  # Import the rectangle garage
from src.data.constants import PATH_IMAGE  # To get the path of the image
from src.render.button import Button  # Import the button
import src.data.variables as var  # Import the variable
import pygame  # To use pygame


"""
This function contains the Garage class and all the functions related to it. The garage is the place where the cars are stored.
"""


class Garage:
    """
    This class is used to represent the garage, used to store the cars
    """
    def __init__(self):
        """
        Initialize the garage
        """
        self.rect = None  # Rectangle of the garage
        self.nb_rectangle = None  # Number of rectangle in the garage
        self.rectangles = None  # List of the rectangles in the garage
        self.actual_x = None  # Actual x position to write the rectangles
        self.actual_y = None  # Actual y position to write the rectangles
        self.change_y = None  # True if the y position has to change in the next rectangle (it means we are at the right of the garage)
        self.actual_page = None  # Actual page of the garage
        self.reload_page = None  # True if we have to change the page of the garage (for example at the beginning)
        self.time_since_last_delete = None  # Time since the last delete of a car
        self.trash_button = None  # Button to delete all cars
        self.next_button = None  # Button to go to the next page
        self.previous_button = None  # Button to go to the previous page

    def __str__(self):
        """
        Return the string to display with the print function

        Returns:
            str: string of the garage
        """
        string = f'Garage : {self.nb_rectangle} rectangles :'
        for rect in self.rectangles:
            string += f'\n{rect}'
        return string

    def init(self):
        """
        Initialize the garage during the game
        """
        pos_rect = convert_to_new_window((500, 125))  # Position of the rectangle of the garage
        self.rect = pygame.Rect(pos_rect[0], pos_rect[1], var.SCALE_RESIZE_X * 500, var.SCALE_RESIZE_Y * 550)  # Rectangle of the garage
        self.nb_rectangle = 0  # Number of rectangle in the garage
        self.rectangles = []  # List of the rectangles in the garage
        self.actual_x = 0  # Actual x position to write the rectangles
        self.actual_y = 0  # Actual y position to write the rectangles
        self.change_y = False  # True if the y position has to change in the next rectangle (it means we are at the right of the garage)
        self.actual_page = 0  # Actual page of the garage
        self.reload_page = True  # True if we have to change the page of the garage (for example at the beginning)
        self.time_since_last_delete = 0  # Time since the last delete of a car
        self.trash_button = Button(930, 135, pygame.image.load(PATH_IMAGE + '/trash_button_1.png'),
                                   pygame.image.load(PATH_IMAGE + '/trash_button_2.png'),
                                   pygame.image.load(PATH_IMAGE + '/trash_button_3.png'), scale=0.2)
        self.next_button = Button(940, 623, pygame.image.load(PATH_IMAGE + '/next_page_button_1.png'),
                                  pygame.image.load(PATH_IMAGE + '/next_page_button_2.png'),
                                  pygame.image.load(PATH_IMAGE + '/next_page_button_3.png'), scale=0.2)
        self.previous_button = Button(520, 623, pygame.transform.flip(pygame.image.load(PATH_IMAGE + '/next_page_button_1.png'), True, False),
                                      pygame.transform.flip(pygame.image.load(PATH_IMAGE + '/next_page_button_2.png'), True, False),
                                      pygame.transform.flip(pygame.image.load(PATH_IMAGE + '/next_page_button_3.png'), True, False), scale=0.2)

    def display_garage(self):
        """
        Display the garage
        """
        # Create rectangles for the garage
        pygame.draw.rect(var.WINDOW, (128, 128, 128), self.rect, 0)
        pygame.draw.rect(var.WINDOW, (1, 1, 1), self.rect, 2)
        var.WINDOW.blit(var.LARGE_FONT.render('Voitures sauvegardées', True, (0, 0, 0), (128, 128, 128)), convert_to_new_window((595, 135)))

        for rect_garage in self.rectangles:  # For each rectangle in the garage
            if rect_garage.draw_rect_garage(self.time_since_last_delete):  # If the rectangle is deleted we reset the page of the garage
                self.reload_page = True  # We have to change the page of the garage
                self.time_since_last_delete = pygame.time.get_ticks()  # We reset the time since the last delete of a car (to avoid deleting all in one long click)

        self.trash_button.draw()  # We draw the trash button
        if self.trash_button.activated:
            var.MEMORY_CARS = {'dice': [], 'genetic': []}  # We reset the memory of the cars
            self.reload_page = True  # We have to change the page of the garage
            reset_dict_check()  # We reset the state of the check buttons


        if self.reload_page:  # If we have to change the page of the garage
            # Reset the data
            self.reset_variables()

            id_rect = 0  # The number to identify the id of the rectangle
            for key in var.MEMORY_CARS.keys():
                for memory_car in var.MEMORY_CARS.get(key):
                    # If the rectangle is in the good page
                    if 10 * self.actual_page <= self.nb_rectangle < 10 * (self.actual_page + 1):
                        self.rectangles.append(RectGarage(id_car=memory_car[0], name=memory_car[1], type_car=key, genetic=memory_car[2],
                                                          id_rect=id_rect, pos=(self.actual_x, self.actual_y), color=memory_car[3], scores=memory_car[4]))  # We create the rectangles
                        id_rect += 1  # We add one to the number to identify the id of the rectangle
                        self.update_variables()  # We change the values of the data
                    self.nb_rectangle += 1  # We add one to the number of rectangle in the garage

            self.reload_page = False  # We don't have to change the page of the garage anymore


        # Change of pages
        if (self.actual_page + 1) * 10 < self.nb_rectangle:  # If we are not at the last page
            self.next_button.draw()  # We draw the next button
            if self.next_button.just_clicked:
                self.actual_page += 1
                self.reload_page = True  # We have to change the page of the garage

        if self.actual_page > 0:  # If we are not at the first page
            self.previous_button.draw()  # We draw the previous button
            if self.previous_button.just_clicked:
                self.actual_page -= 1
                self.reload_page = True  # We have to change the page of the garage

    def update_variables(self):
        """
        Update the data to draw the next rectangle in the garage
        """
        if self.change_y:  # If we have to change the y position (it means we are at the right of the garage)
            self.actual_y += 90
            self.actual_x -= 240
        else:
            self.actual_x += 240
        self.change_y = not self.change_y  # At the next rectangle, we are going to change of axis

    def reset_variables(self):
        """
        Reset the data
        """
        var.CARS_FROM_GARAGE = []  # We reset the list of the cars from the garage
        self.rectangles = []  # We reset the list of the rectangle in the garage
        self.nb_rectangle = 0  # Number of rectangle in the garage
        self.actual_x = 515  # Actual x position to write the rectangles
        self.actual_y = 185  # Actual y position to write the rectangles
        self.change_y = False  # True if the y position has to change in the next rectangle


    def erase_garage(self):
        """
        Erase the garage
        """
        rect = pygame.Rect(self.rect)  # We create a rectangle with the position of the garage
        var.WINDOW.blit(var.BACKGROUND, rect, rect)  # We erase the garage


def add_garage_cars(cars):
    """
    Add the cars from the garage to the list of cars
    """
    index = 0

    if var.CARS_FROM_GARAGE:  # If we have a car from the garage
        for car in var.CARS_FROM_GARAGE:
            car.reset()
            cars.append(car)  # Add cars from the garage to the list
            index += 1
    return cars


GARAGE = Garage()  # We create the garage
