import src.data.variables as var  # Variables of the game
import random  # Used to generate random numbers
from src.game.car import Car  # Import the car

"""
This file contains all the functions used to apply the genetic algorithm to the cars (selection, mutation, crossover)
"""


def apply_genetic(cars):
    """
    Apply the genetic algorithm to the cars

    Args:
        cars (list): list of cars

    Returns:
        list: list of cars with the genetic algorithm applied
    """
    cars = [car for car in cars if not car.view_only]  # We remove the cars that are only here for the visuals

    if cars:
        cars = sorted(cars, key=lambda c: c.scores, reverse=True)  # Sort the cars by score
        cars_to_keep = find_cars_to_keep(cars)  # We find the cars to keep (the best cars)
        cars = init_cars(cars_to_keep, var.NB_CARS - len(cars_to_keep))  # Select the best cars
        cars = mutate(cars)  # Mutate the cars
        cars = crossover(cars)  # Crossover the cars
        cars = add_cars_to_keep(cars, cars_to_keep)  # We add the best cars to the list
    else:
        cars = [Car() for _ in range(var.NB_CARS)]  # If there is no car, we add random cars

    return cars


def find_cars_to_keep(cars):
    """
    Find the cars to keep (the best cars) and add the best car to the memory

    Args:
        cars (list): list of cars

    Returns:
        list: list of cars to keep
    """
    number_to_keep = min(int(var.PROPORTION_CARS_KEPT * len(cars)), var.NB_CARS)  # Number of cars to keep
    cars_to_keep = cars[:number_to_keep]  # Select the best cars

    best_car = cars[0]  # We get the best car
    var.MEMORY_CARS.get('genetic').append([var.NUM_GENERATION, 'Génération_' + str(var.NUM_GENERATION), best_car.genetic, 'gray', best_car.best_scores])  # Add the best car to the memory

    if len(cars_to_keep) == 0:
        cars_to_keep.append(best_car)

    return cars_to_keep


def init_cars(cars_to_keep, number_cars):
    """
    Initialize the cars we will mutate and crossover

    Args:
        cars_to_keep (list): list of cars we will copy
        number_cars (int): number of cars we will mutate and crossover

    Returns:
        list: list of the cars we will mutate and crossover
    """
    # Calculate the weights based on the car scores
    weights = [car.scores for car in cars_to_keep]
    total_weight = sum(weights)
    if total_weight == 0:  # To avoid division by 0
        total_weight = 1
    probabilities = [weight / total_weight for weight in weights]

    selected_cars = random.choices(cars_to_keep, probabilities, k=number_cars)  # We choose the cars based on their probabilities
    cars = [Car(car.genetic) for car in selected_cars]

    return cars


def mutate(cars):
    """
    Mutate the cars

    Args:
        cars (list): list of cars

    Returns:
        list: list of cars mutated
    """
    new_cars = []  # List of new cars

    for car in cars:
        added = False
        count = 0  # Number of times we tried to add the car
        while not added:
            car = mutate_one_car(car)  # Mutate the car
            count += 1
            if car not in new_cars or count > 150:  # If the car is not already in the list or if we have tried too many times
                added = True
                new_cars.append(car)  # We add the car to the list

    return new_cars


def mutate_one_car(car):
    """
    Mutate one car

    Args:
        car (Car): the car to mutate

    Returns:
        Car: the mutated car
    """
    for attribute_name, attribute_value in vars(car.genetic).items():
        if random.random() < var.ACTUAL_CROSSOVER_CHANCE:
            # See if it is a width or a length
            if attribute_name.startswith('width'):
                multiplier = var.WIDTH_CONE
            else:
                multiplier = var.LENGTH_CONE
            actual_value = int(getattr(car.genetic, attribute_name) / multiplier)  # Get the actual value of the attribute
            setattr(car.genetic, attribute_name, multiplier * random_attribution(actual_value))

    return car


def crossover(cars):
    """
    Crossover the cars (exchange some attributes between two cars)

    Args:
        cars (list): list of cars

    Returns:
        list: list of cars crossed
    """
    for i in range(len(cars)):
        for j in range(len(cars)):  # We search for all pairs of cars
            if random.random() < var.ACTUAL_CROSSOVER_CHANCE and i != j:  # If we do a crossover
                car1, car2 = (cars[i], cars[j])
                id_changed_attribute = random.randint(0, 5)  # We choose a random attribute to exchange
                for k, (attribute_name, attribute_value) in enumerate(vars(car1.genetic).items()):
                    if k == id_changed_attribute:
                        setattr(car1.genetic, attribute_name, getattr(car2.genetic, attribute_name))
                        setattr(car2.genetic, attribute_name, attribute_value)
                        break
    return cars


def add_cars_to_keep(cars, cars_to_keep):
    """
    Add the best cars to the list

    Args:
        cars (list): list of cars that have been mutated and crossed
        cars_to_keep (list): list of cars to keep (the best cars)

    Returns:
        list: list of cars
    """
    for car in cars_to_keep[1:]:
        cars.append(Car(genetic=car.genetic, best_scores=car.best_scores))

    best_car = cars_to_keep[0]  # We add the best car at the end, so we will see it on top of the others
    cars.append(Car(genetic=best_car.genetic, best_scores=best_car.best_scores, color='yellow'))

    return cars


def random_attribution(value):
    """
    We want to attribute a random value to a variable, but we want that values close to the actual value has more chance

    Args:
        value (int): the actual value (between 1 and 6)

    Returns:
        value (int): the new value (between 1 and 6)
    """
    rand = random.random()
    if rand < 1/5:
        value = value + random.uniform(-5, 5)  # We add a random value between -1 and 1
    elif rand < 1/4:
        value = value + random.uniform(-4, 4)
    elif rand < 1/3:
        value = value + random.uniform(-3, 3)
    elif rand < 1/2:
        value = value + random.uniform(-2, 2)
    else:
        value = value + random.uniform(-1, 1)
    return max(1, min(6, round(value)))  # We round the value between 1 and 6
