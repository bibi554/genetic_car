from src.other.camera_utils import *  # Utils functions for the camera
from src.data.data_structures import ColorDice  # To find the color of each dice
from src.render.dice_menu import save_camera_frame  # To save the camera frame
from src.other.utils import convert_to_new_window  # Utils functions
import matplotlib.pyplot as plt  # To show images
import src.data.variables as var  # Variables
import random  # To generate random numbers
import numpy as np  # To use numpy
import pygame  # To use Pygame
import cv2  # To use OpenCV

"""
This file contains the functions used to get the score of the dice from the camera with OpenCV
"""

# The parameters of the threshold to make a black and white image for each color
param_thresh = {'yellow': 170, 'orange': 90, 'red': 60, 'dark_yellow': 100, 'green': 80, 'black': 20}

# The BGR values of each color (observation)
bgr_values = {'yellow': (49, 113, 149), 'orange': (44, 66, 169), 'red': (50, 35, 111), 'dark_yellow': (41, 73, 121), 'green': (70, 93, 41), 'black': (44, 38, 39)}

# The BGR values of each color (real)
real_bgr_values = {'yellow': (0, 255, 255), 'orange': (0, 102, 204), 'red': (0, 0, 204), 'dark_yellow': (0, 152, 152), 'green': (0, 204, 0), 'black': (0, 0, 0)}

# The last scores we stored for each color (used to compare with the new scores to avoid changing the score too often)
scores_colors = {'yellow': [], 'orange': [], 'red': [], 'dark_yellow': [], 'green': [], 'black': []}

# The rects kept in memory (when we detect a rectangle, if it overlaps with a rectangle in memory, we display the rectangle in memory)
memory_rects = {}  # Format : {rect : lifetime_remaining} ; lifetime_remaining : the number of frames the rectangle will be displayed unless it is detected again

# The scores we will return, initialized to random values
final_score = {}

frame_view = np.empty([2, 2])  # The frame of the camera (viewed by the user)
count_iterations = 0  # The number of iterations of the program

# The parameters of the HoughCircles function
list_p1 = [150]
list_p2 = [16]
list_dp = [5]
dict_p1 = {'red': [150], 'green': [150, 100], 'yellow': [150], 'orange': [150], 'dark_yellow': [150], 'black': [150]}
dict_p2 = {'red':  [16], 'green': [16, 59], 'yellow': [16], 'orange': [16], 'dark_yellow': [16], 'black': [16]}
dict_dp = {'red': [5], 'green': [5, 65], 'yellow': [5], 'orange': [5], 'dark_yellow': [5], 'black': [5]}


# Optimization and debug parameters
show_clicks = False  # To show the coordinates and color of the position where the user clicked

# To find what is the color of each dice
write_mean_bgr = False
file_write_mean_bgr = open(var.PATH_DATA + '/mean_bgr', 'a')  # The file in which we will write the parameters

# Optimization parameters for HoughCircles function
optimize = False  # To optimize the parameters of the HoughCircles function
p1_min, p1_max = 50, 200  # The min and max values of the parameters
p2_min, p2_max = 10, 80
dp_min, dp_max = 30, 150
colors_optimize_values = {'green': 6}  # The colors we want to optimize and the value of the dice we want to optimize
colors_optimize_coordinates = {'green': [(326, 359), (332, 370), (337, 380), (344, 351), (349, 362), (354, 372)]}  # The coordinates of the dice we want to optimize
waiting = 100  # The number of iterations we wait before starting to optimize
dict_p1_opti, dict_p2_opti, dict_dp_opti = {}, {}, {}  # Format : {value : count}
p1_red, p2_red, dp_red, p1_green, p2_green, dp_green = {}, {}, {}, {}, {}, {}
p1_yellow, p2_yellow, dp_yellow, p1_orange, p2_orange, dp_orange = {}, {}, {}, {}, {}, {}
p1_dark_yellow, p2_dark_yellow, dp_dark_yellow, p1_black, p2_black, dp_black = {}, {}, {}, {}, {}, {}
dict_colors = {'red': [p1_red, p2_red, dp_red], 'green': [p1_green, p2_green, dp_green], 'yellow': [p1_yellow, p2_yellow, dp_yellow],
               'orange': [p1_orange, p2_orange, dp_orange], 'dark_yellow': [p1_dark_yellow, p2_dark_yellow, dp_dark_yellow], 'black': [p1_black, p2_black, dp_black]}


def capture_dice():
    """
    Main program

    Returns:
        (dict) : The scores of the dice
    """
    global final_score, frame_view, count_iterations

    final_score = {'yellow': random.randint(1, 6), 'orange': random.randint(1, 6), 'red': random.randint(1, 6),
                   'dark_yellow': random.randint(1, 6), 'green': random.randint(1, 6), 'black': random.randint(1, 6)}

    rect_window = pygame.rect.Rect(convert_to_new_window((425, 175, 640, 480)))

    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)  # 0 corresponds to the default camera, you can change it if you have multiple cameras

    while True:
        count_iterations += 1  # We increment the number of iterations

        _, frame = cap.read()  # Read a frame from the camera

        if frame is None:  # We don't have a camera connected
            print('Aucune caméra détectée')
            return end_capture_dice(cap)

        frame_view = frame.copy()  # We make a copy of the frame to display it on the window (with rectangles, texts, ...)

        rectangles = find_rectangles(frame)  # Find the rectangles on the image

        # Draw the rectangles on the image
        # draw_rectangle(rectangles, thickness=1)

        # We take in memory for each color the bgr color and the rectangle to prevent 2 colors from being the same
        colors = {}  # List of the colors of the dice (key: name_color, value: ColorDice)

        for rect in rectangles:
            x, y, w, h = rect  # We get the coordinates of the rectangle
            image = frame[y:y+h, x:x+w]  # We get the image of the rectangle

            mean_bgr = compute_mean_bgr(image)  # We compute the mean BGR values of the rectangle

            # Write the mean BGR values in a file
            if write_mean_bgr:
                write_mean_bgr_value(rect, mean_bgr)

            colors = determine_colors(ColorDice(mean_bgr, rect), colors)  # We determine the color of the rectangle

        for color in colors:
            rect = x, y, w, h = colors[color].rect  # We get the coordinates of the rectangle
            image = frame[y:y+h, x:x+w]  # We get the image of the rectangle

            if np.size(image) == 0:  # If the image is empty, we don't do anything
                break

            # We draw the rectangle on the image
            draw_rectangle((x, y, w, h), real_bgr_values[color])

            score = determine_score(image, rect, color, scores_colors[color])  # We determine the score of the dice

            if color in final_score:
                final_score[color] = score  # We add the score to the final score

            # We write the value of the dice on the image
            cv2.putText(frame_view, f'Score: {score}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 50, 50), 2)

        # We display the frame on the window
        image_rgb = cv2.cvtColor(frame_view, cv2.COLOR_BGR2RGB)  # Convert the image to RGB
        image_pygame = pygame.surfarray.make_surface(image_rgb)  # Convert the image to a pygame image
        image_turned = pygame.transform.rotate(image_pygame, -90)  # Rotate the image
        image = pygame.transform.flip(image_turned, True, False)  # Flip the image
        image = pygame.transform.scale(image, (rect_window.width, rect_window.height))  # Resize the image
        var.WINDOW.blit(image, rect_window)  # We display the frame on the window
        pygame.draw.rect(var.WINDOW, (1, 1, 1), rect_window, 2)  # We draw a rectangle on the window
        var.WINDOW.blit(var.LARGE_FONT.render("Cliquez n'importe où pour quitter cette fenêtre", True, (255, 0, 255)), convert_to_new_window((440, 600)))  # Text of the selected dice
        pygame.display.flip()  # We update the window

        if count_iterations == waiting and optimize:
            print('Fin')
            display_dictionaries_optimization()  # Sort the dictionaries

        # Detect a click on the window to stop the program
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:  # We stop the program after a click
                if show_clicks:
                    show_click(rect_window, frame)  # We display the click
                var.WINDOW.blit(var.BACKGROUND, rect_window, rect_window)  # We erase the window

                frame_view = cv2.cvtColor(frame_view, cv2.COLOR_BGR2RGB)  # Convert the image to RGB
                save_camera_frame(frame_view)  # Save the image into the data (CAMERA_FRAME and RECT_CAMERA_FRAME)

                return end_capture_dice(cap)  # End the capture of the dice


def end_capture_dice(cap):
    """
    End the capture of the dice

    Args:
        cap (cv2.VideoCapture): VideoCapture object

    Returns:
        (list) : The scores of the dice
    """
    cap.release()  # Release the VideoCapture object
    cv2.destroyAllWindows()  # Close all windows

    return list(final_score.values())


def optimize_parameters(image, color, value, rect):
    """
    Optimize the parameters of the HoughCircles function by testing different values and printing the results
    Args:
        image (numpy.ndarray): Image on which to optimize the parameters (must be in grayscale)
        color (str): Color of the dice
        value (int): Number of circles to detect
        rect (tuple): Coordinates of the rectangle
    """
    for p1 in range(p1_min, p1_max + 1):
        print(p1)
        for p2 in range(p2_min, p2_max + 1):
            for dp in range(dp_min, dp_max + 1):
                if p1 > p2:
                    optimize_hough_circles(image, color, value, rect, p1, p2, dp)


def optimize_hough_circles(image, color, value, rect, p1, p2, dp):
    """
    Run the HoughCircles function with the given parameters and verify if the result is correct to save the parameters
    in dictionaries

    Args:
        image (numpy.ndarray): Image on which to optimize the parameters (must be in grayscale)
        color (str): Color of the dice
        value (int): Number of circles to detect
        rect (tuple): Coordinates of the rectangle
        p1 (int): First parameter of the HoughCircles function
        p2 (int): Second parameter of the HoughCircles function
        dp (int): Third parameter of the HoughCircles function
    """
    c = cv2.HoughCircles(image=image, method=cv2.HOUGH_GRADIENT, dp=dp / 10, minDist=5, param1=p1, param2=p2,
                         minRadius=1, maxRadius=10)
    if c is not None and verif_coordinates(c[0, :], rect, colors_optimize_coordinates[color]):
        if len(c) == value:  # All points are detected
            print(f'Bingo : {p1} {p2} {dp}')

        if p1 not in dict_p1_opti:
            dict_p1_opti[p1] = 1
        else:
            dict_p1_opti[p1] += 1
        if p2 not in dict_p2_opti:
            dict_p2_opti[p2] = 1
        else:
            dict_p2_opti[p2] += 1
        if dp not in dict_dp_opti:
            dict_dp_opti[dp] = 1
        else:
            dict_dp_opti[dp] += 1
        if p1 not in dict_colors[color][0]:
            dict_colors[color][0][p1] = 1
        else:
            dict_colors[color][0][p1] += 1
        if p2 not in dict_colors[color][1]:
            dict_colors[color][1][p2] = 1
        else:
            dict_colors[color][1][p2] += 1
        if dp not in dict_colors[color][2]:
            dict_colors[color][2][dp] = 1
        else:
            dict_colors[color][2][dp] += 1


def display_dictionaries_optimization():
    """
    Sort the dictionaries of the optimization of the parameters of the HoughCircles function
    """
    global dict_p1_opti, dict_p2_opti, dict_dp_opti, p1_red, p2_red, dp_red, p1_green, p2_green, dp_green, p1_yellow, p2_yellow,\
        dp_yellow, p1_orange, p2_orange, dp_orange, p1_dark_yellow, p2_dark_yellow, dp_dark_yellow, p1_black, p2_black, dp_black

    # We sort the dictionaries
    dict_p1_opti = {k: v for k, v in sorted(dict_p1_opti.items(), key=lambda item: item[1], reverse=True)}
    dict_p2_opti = {k: v for k, v in sorted(dict_p2_opti.items(), key=lambda item: item[1], reverse=True)}
    dict_dp_opti = {k: v for k, v in sorted(dict_dp_opti.items(), key=lambda item: item[1], reverse=True)}
    p1_red = {k: v for k, v in sorted(p1_red.items(), key=lambda item: item[1], reverse=True)}
    p2_red = {k: v for k, v in sorted(p2_red.items(), key=lambda item: item[1], reverse=True)}
    dp_red = {k: v for k, v in sorted(dp_red.items(), key=lambda item: item[1], reverse=True)}
    p1_green = {k: v for k, v in sorted(p1_green.items(), key=lambda item: item[1], reverse=True)}
    p2_green = {k: v for k, v in sorted(p2_green.items(), key=lambda item: item[1], reverse=True)}
    dp_green = {k: v for k, v in sorted(dp_green.items(), key=lambda item: item[1], reverse=True)}
    p1_yellow = {k: v for k, v in sorted(p1_yellow.items(), key=lambda item: item[1], reverse=True)}
    p2_yellow = {k: v for k, v in sorted(p2_yellow.items(), key=lambda item: item[1], reverse=True)}
    dp_yellow = {k: v for k, v in sorted(dp_yellow.items(), key=lambda item: item[1], reverse=True)}
    p1_orange = {k: v for k, v in sorted(p1_orange.items(), key=lambda item: item[1], reverse=True)}
    p2_orange = {k: v for k, v in sorted(p2_orange.items(), key=lambda item: item[1], reverse=True)}
    dp_orange = {k: v for k, v in sorted(dp_orange.items(), key=lambda item: item[1], reverse=True)}
    p1_dark_yellow = {k: v for k, v in sorted(p1_dark_yellow.items(), key=lambda item: item[1], reverse=True)}
    p2_dark_yellow = {k: v for k, v in sorted(p2_dark_yellow.items(), key=lambda item: item[1], reverse=True)}
    dp_dark_yellow = {k: v for k, v in sorted(dp_dark_yellow.items(), key=lambda item: item[1], reverse=True)}
    p1_black = {k: v for k, v in sorted(p1_black.items(), key=lambda item: item[1], reverse=True)}
    p2_black = {k: v for k, v in sorted(p2_black.items(), key=lambda item: item[1], reverse=True)}
    dp_black = {k: v for k, v in sorted(dp_black.items(), key=lambda item: item[1], reverse=True)}

    # We create the file
    with open(var.PATH_DATA + '/optimization', 'w') as file_write:
        # We print the dictionaries
        file_write.write(f'p1 : {dict_p1_opti}\np2 : {dict_p2_opti}\ndp : {dict_dp_opti}\np1_red : {p1_red}\np2_red : {p2_red}\n'
                         f'dp_red : {dp_red}\np1_green : {p1_green}\np2_green : {p2_green}\ndp_green : {dp_green}\n'
                         f'p1_yellow : {p1_yellow}\np2_yellow : {p2_yellow}\ndp_yellow : {dp_yellow}\np1_orange : {p1_orange}\n'
                         f'p2_orange : {p2_orange}\ndp_orange : {dp_orange}\np1_dark_yellow : {p1_dark_yellow}\n'
                         f'p2_dark_yellow : {p2_dark_yellow}\ndp_dark_yellow : {dp_dark_yellow}\np1_black : {p1_black}\n'
                         f'p2_black : {p2_black}\ndp_black : {dp_black}')


def find_rectangles(frame):
    """
    Find the rectangles on the frame of the camera

    Args:
        frame (numpy.ndarray): Frame of the camera

    Returns:
        list: The list of rectangles found
    """
    contours = find_contours(frame)  # We find the contours
    rectangles = check_contours_validity(contours)  # We check the validity of the contours
    rectangles = check_overlapping_rectangles(rectangles)  # We remove the duplicate rectangles
    rectangles = add_offset(rectangles, offset=7)  # We add an offset to the rectangles
    rectangles = add_rect_from_memory(rectangles)  # We add the rectangles from the memory
    rectangles = check_overlapping_rectangles(rectangles)  # We remove the duplicate rectangles again

    update_memory_rect()  # We update the memory of the rectangles (we decrease the lifetime of the rectangles)

    return rectangles


def find_contours(image):
    """
    Find the contours of the dice on the image

    Args:
        image (numpy.ndarray): Image on which to find the contours

    Returns:
        list: The list of contours found
    """
    contours = []  # The list of contours found
    for (str_color, value) in param_thresh.items():  # For each color we have a threshold_color

        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # We convert the image from BGR to gray
        gray_img = cv2.medianBlur(gray_img, 3)  # We apply a median blur to the image to erase useless details

        # We apply a threshold to the image : it turns the image into a black and white image
        thresh = cv2.threshold(gray_img, value, 255, cv2.THRESH_BINARY_INV)[1]

        # We create a kernel to close the edges of the dice
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        edges_1 = cv2.Canny(gray_img, 9, 150, 3)  # Detect edges from the gray image
        edges_2 = cv2.Canny(thresh, 9, 150, 3)  # Detect edges from the threshold image

        for edges in [edges_1, edges_2]:
            close = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)  # Close the edges of the dice
            contour_found, _ = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # We find the contours of the image
            contours += contour_found  # We merge the contours found by the two methods

    return contours


def check_contours_validity(contours):
    """
    Verify that the rectangle is not too big or too small, and that it is not too close to the edge of the image

    Args:
        contours (list): List of contours found

    Returns:
        list: List of rectangles found
    """
    rectangles = []  # List of rectangles
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)  # We get the coordinates of the rectangle
        min_size = 35  # Minimum size of the rectangle
        max_size = 80  # Maximum size of the rectangle
        if min_size < w < max_size and min_size < h < max_size:  # If the rectangle is not too big or too small
            # Check if the rectangle is not too close to the edge of the image
            if x > 5 and y > 5 and x + w < 635 and y + h < 475:
                rectangles.append((x, y, w, h))

    return rectangles


def add_rect_from_memory(rectangles):
    """
    Add the rectangles from the memory to the list of rectangles

    Args:
        rectangles (list): List of rectangles found

    Returns:
        list: List of rectangles found
    """
    new_rectangles = []

    for memory_rect in memory_rects:
        new_rectangles.append(memory_rect)
        for rect in rectangles:
            # If we find a rect that is already in the memory, we reset the lifetime of the rectangle
            if overlapping_rectangles(rect, memory_rect, area_threshold=0.8):
                memory_rects[memory_rect] = 20  # We reset the lifetime of the rectangle
                break

    for rect in rectangles:
        new_rectangles.append(rect)
        memory_rects[rect] = 20  # We add the rectangle to the memory

    return new_rectangles


def update_memory_rect():
    """
    Update the memory of the rectangles (we decrease the lifetime of the rectangles and delete the old ones)
    """
    # We update the lifetime of the rectangles in memory
    memory_rect_to_delete = []
    for rect in memory_rects:
        memory_rects[rect] -= 1  # We decrease the number of times the rectangle is in the memory
        if memory_rects[rect] == 0:  # If the rectangle is not in the memory anymore
            memory_rect_to_delete.append(rect)  # We add the rectangle to the list of rectangles to delete

    # We delete the rectangles from the memory
    for rect in memory_rect_to_delete:
        del memory_rects[rect]


def determine_colors(color_dice, dict_color_dice):
    """
    Determine the colors of the dice on the image. We try to find the color with the minimum distance between the mean
    BGR values and the BGR values of each color. There may be conflicts between the colors, and in this case, we
    keep the better one, and we recall the function with the other one.

    Args:
        color_dice (ColorDice): ColorDice object representing the dice
        dict_color_dice (dict): Dictionary of the ColorDice objects, with the name of the color as key

    Returns:
        (dict) : Dictionary of the ColorDice objects
    """
    # Calculate the distance between the mean BGR values and the BGR values of each color if necessary
    if not color_dice.distances:
        color_dice.distances = {}  # Format: {name_color: distance}
        for name, bgr in bgr_values.items():
            color_dice.distances[name] = np.linalg.norm(color_dice.color - bgr)

    if color_dice.bad_colors is None:  # If we don't have any bad colors for the dice
        # We simply get the color with the minimum distance
        name_color = min(color_dice.distances, key=color_dice.distances.get)  # We get the color with the minimum distance

    else:  # If we know the dice has some colors that are not possible
        # We get the color with the minimum distance, except the bad colors
        min_distance = None
        name_color = ''
        for name, distance in color_dice.distances.items():
            if name not in color_dice.bad_colors and (min_distance is None or distance < min_distance):
                min_distance = distance
                name_color = name
        if min_distance is None:  # If we didn't find any color, we reject this color and exit the function
            return dict_color_dice

    # We check if the color is already in the list
    if name_color not in dict_color_dice:
        dict_color_dice[name_color] = color_dice  # We add the color to the list if it is not in it
    else:
        # We check what dice has the closest mean_bgr to the BGR value we want
        if np.linalg.norm(dict_color_dice[name_color].color - bgr_values[name_color]) > np.linalg.norm(color_dice.color - bgr_values[name_color]):
            # If the new dice is closer to the color we want, we replace the old dice by the new one
            old_dice = dict_color_dice[name_color]
            dict_color_dice[name_color] = color_dice

            # We restart the function with the old dice
            old_dice.bad_colors.append(name_color)
            dict_color_dice = determine_colors(old_dice, dict_color_dice)
        else:
            # If the old dice is closer to the color we want, we restart the function with the new dice
            color_dice.bad_colors.append(name_color)
            dict_color_dice = determine_colors(color_dice, dict_color_dice)

    return dict_color_dice


def write_mean_bgr_value(rect, mean_bgr):
    """
    Write the mean BGR values of the dice at the center of the image in the file mean_bgr

    Args:
        rect (tuple): Coordinates of the rectangle (x, y, w, h)
        mean_bgr (numpy.ndarray): Mean BGR values of the dice
    """
    rect_detection = (250, 150, 150, 150)
    draw_rectangle(rect_detection, color=(0, 255, 0), thickness=1)
    if overlapping_rectangles(rect, rect_detection, area_threshold=0.1):
        draw_rectangle(rect, color=(255, 0, 0), thickness=20)
        file_write_mean_bgr.write(f'{mean_bgr[0]} {mean_bgr[1]} {mean_bgr[2]}\n')


def determine_score(image, rect, color, scores):
    """
    Determine the score of the dice

    Args:
        image (numpy.ndarray): Image of the dice
        rect (tuple): Coordinates of the rectangle (x, y, w, h)
        color (str): Color of the dice
        scores (list): List of the previous scores of the dice

    Returns:
        (int): Score of the dice
    """
    circles = []

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert the image to grayscale
    circles = add_circles_by_hough_function(circles, gray_image)

    image = cv2.medianBlur(gray_image, 3)  # We blur the image
    circles = add_circles_by_hough_function(circles, image)

    image = cv2.Canny(gray_image, 50, 120)  # We apply the Canny filter to the image
    circles = add_circles_by_hough_function(circles, image)

    # Optimize the parameters of the HoughCircles function
    if count_iterations == waiting and optimize:
        if color in colors_optimize_values:
            optimize_parameters(gray_image, color, colors_optimize_values[color], rect)

    if circles:
        # We make sure we don't have any overlapping circles
        circles = remove_circles_duplicate(circles)

        score = len(circles)  # We count the number of circles

        # We convert the coordinates of the circles to the coordinates of the window
        for circle in circles:
            circle[0], circle[1] = circle[0] + rect[0], circle[1] + rect[1]

        # We draw the circles
        draw_circle(circles)
    else:
        score = random.randint(1, 6)  # If we don't find any circle, we choose a random number between 1 and 6

    if score > 6:
        score = 6

    scores.append(score)  # We add the score to the list of scores
    if len(scores) > 50:
        scores.pop(0)  # We remove the first score

    # We find the number the most present in the list of scores
    score = max(set(scores), key=scores.count)

    return score


def add_circles_by_hough_function(circles, image):
    """
    Find new circles with the houghCircle function and add them to the list of circles

    Args:
        circles (list): List of circles
        image (numpy.ndarray): Image of the dice

    Returns:
        (list): List of circles with the new circles
    """
    for index in range(len(list_p1)):  # We try to find circles with different parameters for the current color
        new_circles = cv2.HoughCircles(image=image, method=cv2.HOUGH_GRADIENT, dp=list_dp[index] / 10, minDist=3,
                                       param1=list_p1[index], param2=list_p2[index], minRadius=0, maxRadius=10)
        if new_circles is not None:
            for circle in new_circles[0, :]:
                circles.append(circle)

    return circles


def draw_rectangle(rectangle, color=(0, 0, 0), thickness=3):
    """
    Draw the rectangles on the frame

    Args:
        rectangle (tuple or list of tuple): The rectangle or the rectangles
        color (tuple): The color of the rectangle
        thickness (int): The thickness of the rectangle
    """
    if type(rectangle) == tuple:
        rectangle = [rectangle]
    for rect in rectangle:
        x, y, w, h = rect
        cv2.rectangle(frame_view, (x, y), (x + w, y + h), color, thickness)


def draw_circle(circles):
    """
    Draw the circles on the frame

    Args:
        circles (list): The circles to draw
    """
    for circle in circles:
        # Draw the outer circle
        cv2.circle(frame_view, (int(circle[0]), int(circle[1])), int(circle[2]), (0, 255, 0), 2)
        # Draw the center of the circle
        cv2.circle(frame_view, (int(circle[0]), int(circle[1])), 2, (0, 0, 255), 3)


def show_image(image, gray=True):
    """
    Show an image in a window

    Args:
        image (numpy.ndarray): The image
        gray (bool): If the image is in gray scale
    """
    if gray:
        plt.imshow(image, cmap='gray')  # Image with the edges
    else:
        plt.imshow(image)
    plt.show()
