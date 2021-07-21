from typing import Union
from scipy import integrate
import cv2 as cv
import numpy as np
import pymurapi as mur
import colorsys
import time



def find_gates_err(image: np.ndarray) -> float: #TODO: This thing finds error between needed position of gates' middlepoint and its current position
    """Finds error between gates' middlepoint position and center of videofeed

    Args:
        image (cv.): image, in which gates are to be found, not cropped

    Returns:
        float: Error
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


def get_auv_image(auv: mur.auv) -> np.ndarray:
    """Returns camera feed in numpy.ndarray

    Args:
        auv (mur.auv): AUV, which camera is to be read
    Returns:
        np.ndarray: Image
    """
if __name__ == "__main__":
    auv = mur.mur_init()
    success, err = find_gates_err(get_auv_image(auv))
    if success:
        while not stabilize_yaw(err, 1, 50):
            success, err = find_gates_err(get_auv_image(auv))
        
