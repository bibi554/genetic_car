import src.other.variables as var  # Import the variables
import random  # Used to generate random numbers

"""
This file contains the Genetic class used to store the genetic parameters of a car
"""


class Genetic:
    """
    The class is used to represent a genetic algorithm and store the genetic parameters of a car
    """
    def __init__(self, list_parameters=None):
        """
        Initialization of the genetic algorithm

        Args:
            list_parameters (list(int)): list of the parameters of the genetic algorithm in this order : (height_slow, height_medium, height_fast, width_slow, width_medium, width_fast)
        """
        if list_parameters is not None:        # If we have the parameters of the genetic algorithm
            self.height_slow = list_parameters[0] * var.HEIGHT_CONE  # Height of the detection cone when the car is going slow
            self.height_medium = list_parameters[1] * var.HEIGHT_CONE  # Height of the detection cone when the car is going at medium speed
            self.height_fast = list_parameters[2] * var.HEIGHT_CONE  # Height of the detection cone when the car is going fast

            self.width_slow = list_parameters[3] * var.WIDTH_CONE  # Width of the detection cone when the car is going slow
            self.width_medium = list_parameters[4] * var.WIDTH_CONE  # Width of the detection cone when the car is going at medium speed
            self.width_fast = list_parameters[5] * var.WIDTH_CONE  # Width of the detection cone when the car is going fast

        else:                                  # If we don't have the parameters we randomize them
            self.height_slow = var.HEIGHT_CONE * random.randint(1, 6)  # Height of the detection cone when the car is going slow
            self.height_medium = var.HEIGHT_CONE * random.randint(1, 6)  # Height of the detection cone when the car is going at medium speed
            self.height_fast = var.HEIGHT_CONE * random.randint(1, 6)  # Height of the detection cone when the car is going fast

            self.width_slow = var.WIDTH_CONE * random.randint(1, 6)  # Width of the detection cone when the car is going slow
            self.width_medium = var.WIDTH_CONE * random.randint(1, 6)  # Width of the detection cone when the car is going at medium speed
            self.width_fast = var.WIDTH_CONE * random.randint(1, 6)  # Width of the detection cone when the car is going fast

    def __str__(self):
        """
        String representation of the genetic algorithm

        Returns:
            str: string representation of the genetic algorithm
        """
        return f' {self.height_slow // var.HEIGHT_CONE} {self.height_medium // var.HEIGHT_CONE} {self.height_fast // var.HEIGHT_CONE} ' \
               f'{self.width_slow // var.WIDTH_CONE} {self.width_medium // var.WIDTH_CONE} {self.width_fast // var.WIDTH_CONE}'

    def __eq__(self, other):
        """
        Check if two genetic algorithms are equals, two genetic algorithms are equals if they have the same parameters

        Args:
            other (Genetic): genetic algorithm to compare with

        Returns:
            bool: True if the two genetic algorithms are equals, False otherwise
        """
        return self.width_fast == other.width_fast and self.height_fast == other.height_fast and \
            self.width_medium == other.width_medium and self.height_medium == other.height_medium and \
            self.width_slow == other.width_slow and self.height_slow == other.height_slow

    def copy(self):
        """
        Copy the genetic algorithm

        Returns:
            Genetic: copy of the genetic algorithm
        """
        return Genetic(self.get_list())

    def get_list(self):
        """
        Get the list of the genetic parameters

        Returns:
            list: list of the genetic parameters
        """
        return [self.height_slow // var.HEIGHT_CONE, self.height_medium // var.HEIGHT_CONE, self.height_fast // var.HEIGHT_CONE,
                self.width_slow // var.WIDTH_CONE, self.width_medium // var.WIDTH_CONE, self.width_fast // var.WIDTH_CONE]
