import colorsys
from time import sleep, time
from typing import Tuple, Union
from functions import*
import cv2 as cv
import numpy as np
from scipy import integrate

import pymurapi as mur


def find_gates_err(image: np.ndarray) -> Tuple(float, bool):
    """Finds error between gates' middlepoint position and center of videofeed

    Args:
        image (cv.): image, in which gates are to be found, not cropped

    Returns:
        float: Error
        bool: True if gates are found
    """
    pass

def stabilize_yaw(target: float, possible_err: float, additional_fwd: float) -> bool: 
    """Stabilizes yaw on target, with backlash in degrees, denoted by possible_err

    Args:
        target (float): Target, on which the AUV is to be stabilized
        possible_err (float): Possible backlash in degrees (-180 to 180)
        additional_fwd  (float): Additional forward power (-100 to 100)
    Returns:
        bool: Stabilizing status, True if stabilized
    """
    pass


def get_auv_image(auv: mur.auv) -> np.ndarray:
    """Returns camera feed in numpy.ndarray

    Args:
        auv (mur.auv): AUV, which camera is to be read
    Returns:
        np.ndarray: Image
    """
    pass

def find_marker(image: np.ndarray) -> bool:
    """Find marker, green or blue

    Args:
        image (np.ndarray): Image input, not cropped

    Returns:
        bool: True if green
    """
    pass

def circle_marker(green: bool):
    """Goes around marker as in the reglament

    Args:
        green (bool): True if marker is green
    """

    pass

def find_buoy_error(image: np.ndarray, range: ColorRange) -> Tuple(float, bool, float):
    """Finds buoys

    Args:
        image (np.ndarray): Image input, not cropped
        range (ColorRange): Color range of buoy which is to be found

    Returns:
        float: Error between center of feed and buoy's x position
        bool: True if found
        float: Area of found buoy
    """

def bonk_buoy(color: ColorRange):
    """Bonk selected buoy

    Args:
        color (ColorRange): color of buoy, which is to be bonked
    """
    success = True
    area = 0
    while success and area > 50000 and not stabilize_yaw(buoy_error, 0, 50):
        buoy_error, success, area = find_buoy_error(get_auv_image(auv)) # While buoy is found, move to it
    auv.set_motor_power(0,100) # ↓
    auv.set_motor_power(1,100) # Bonk buoy
    sleep(2)                   # ↑ #TODO: Adjust time
    
if __name__ == "__main__":
    ##########
    #1st part#
    ##########
    auv = mur.mur_init() # Init
    err, found = find_gates_err(get_auv_image(auv)) # Find gates
    if found:
        while not stabilize_yaw(err, 1, 50) and found:
            err, found = find_gates_err(get_auv_image(auv)) # While gates are found, go in the middle 
    auv.set_motor_power(0,100) # ↓
    auv.set_motor_power(1,100) # Pass gates
    sleep(2)                   # ↑ #TODO: Adjust time
    circle_marker(find_marker(get_auv_image(auv)))
    err, found = find_gates_err(get_auv_image(auv)) # Backwards gates pass
    if found:
        while found and not stabilize_yaw(err, .1, 50):
            err, found = find_gates_err(get_auv_image(auv)) # While gates are found, go in the middle 
    auv.set_motor_power(0,75)  # ↓
    auv.set_motor_power(1,100) # Turn after gates
    sleep(2)                   # ↑ #TODO: Adjust time and power
    auv.set_motor_power(0,90)  # ↓
    auv.set_motor_power(1,100) # Translation between 1st and 2nd parts
    sleep(2)                   # ↑ #TODO: Adjust time and power        
    
    ##########
    #2nd part#
    ##########
    # Bonk red buoy
    color = ColorRange(Color((170, 20, 20), (5, 255, 255), "red"))
    buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    begin_finding_time = time()
    while not success:
        buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
        if time() - begin_finding_time < 5:
            auv.set_motor_power(0,-20) # ↓
            auv.set_motor_power(1,+20) # Finding buoy, turning left
        elif 10 > time() - begin_finding_time > 5:
            auv.set_motor_power(0,+20) # ↓
            auv.set_motor_power(1,-20) # Finding buoy, turning right
        else:
            # die
            pass
    bonk_buoy(color)
    auv.set_motor_power(0,-100) # ↓
    auv.set_motor_power(1,-100) # Unbonk buoy
    sleep(5)                    # ↑ #TODO: Adjust time
    # Bonk yellow buoy
    color = ColorRange(Color((25, 20, 20), (60, 255, 255), "yellow"))
    buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    begin_finding_time = time()
    while not success:
        buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
        if time() - begin_finding_time < 5:
            auv.set_motor_power(0,-20) # ↓
            auv.set_motor_power(1,+20) # Finding buoy, turning left
        elif 10 > time() - begin_finding_time > 5:
            auv.set_motor_power(0,+20) # ↓
            auv.set_motor_power(1,-20) # Finding buoy, turning right
        else:
            # die
            pass
    bonk_buoy(color)
    auv.set_motor_power(0,-100) # ↓
    auv.set_motor_power(1,-100) # Unbonk buoy
    sleep(5)                    # ↑ #TODO: Adjust time
    # Bonk green buoy
    color = ColorRange(Color((60, 20, 20), (92.5, 255, 255), "green"))
    buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    begin_finding_time = time()
    while not success:
        buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
        if time() - begin_finding_time < 5:
            auv.set_motor_power(0,-20) # ↓
            auv.set_motor_power(1,+20) # Finding buoy, turning left
        elif 10 > time() - begin_finding_time > 5:
            auv.set_motor_power(0,+20) # ↓
            auv.set_motor_power(1,-20) # Finding buoy, turning right
        else:
            # die
            pass
    bonk_buoy(color)
    auv.set_motor_power(0,-100) # ↓
    auv.set_motor_power(1,-100) # Unbonk buoy
    sleep(5)                    # ↑ #TODO: Adjust time
    ############
    # 3rd step #
    ############