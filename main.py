from time import sleep
from typing import Tuple
from functions import Color, ColorRange
import cv2
import numpy as np
from pdreg import PDReg
import pymurapi as mur

# TODO: Все функции, кроме bonk_buoy()


def find_gates_err(image: np.ndarray, color: ColorRange) -> Tuple[float, bool]:
    """Finds error between gates' middlepoint position and center of videofeed

    Args:
        image (np.ndarray): image, in which gates are to be found, not cropped
        color (ColorRange):

    Returns:
        float: Error
        bool: True if gates are found
    """
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array(color[0])  # нижняя граница жёлтого
    upper = np.array(color[1])  # верхняя граница жёлтого
    mask0 = cv2.inRange(img_hsv, lower, upper)
    #    cv2.imshow("mask", mask0)
    list_object = []
    contours, hierarchy = cv2.findContours(mask0, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) > 300:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            list_object.append([cv2.contourArea(cnt), x, y])
    list_object.sort()
    if len(list_object) > 1:
        x_center = (list_object[0][1] + list_object[1][1])//2
        return (image.shape[0] / 2 - x_center, True)
    else:
        return(0, False)


def stabilize_yaw(err: float, additional_fwd: float, live: bool, pdreg: PDReg, auv: mur.auv.Auv.Auv):
    """Stabilizes yaw on target, with backlash in degrees, denoted by possible_err

    Args:
        target (float): Target, on which the AUV is to be stabilized
        possible_err (float): Possible backlash in degrees (-180 to 180)
        additional_fwd  (float): Additional forward power (-100 to 100)
    Returns:
        bool: Stabilizing status, True if stabilized
    """
    err = pdreg.compute(err)
    auv.set_motor_power(0, additional_fwd + err)
    auv.set_motor_power(1, additional_fwd - err)


def get_auv_image(auv: mur.auv.Auv, hsv=True: bool) -> np.ndarray:
    """Returns camera feed in numpy.ndarray

    Args:
        auv (mur.auv.Auv): AUV, which camera is to be read
        hsv (bool): True if returned image is needed to be in HSV colorspace
    Returns:
        np.ndarray: Image
    """
    if isinstance(auv, mur.simulator.Simulator):
        return cv2.cvtColor(auv.get_image_bottom()) if hsv else cv2.auv.get_image_bottom()
    else:
        cum = cv2.VideoCapture(0)
        return cv2.cvtColor(cum.read()[1]) if hsv else cum.read()


def find_marker(image: np.ndarray, blue: ColorRange, green: ColorRange) -> bool:
    """Finds marker, green or blue

    Args:
        image (np.ndarray): Image input, not cropped

    Returns:
        bool: True if marker is green
    """
    img_hsv = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)

    lower_blue = np.array(blue.min_color.to_tuple())  # нижняя граница синего
    upper_blue = np.array(blue.max_color.to_tuple())  # верхняя граница синего

    lower_green = np.array(green.min_color.to_tuple())  # нижняя граница зелёного
    upper_green = np.array(green.max_color.to_tuple())  # верхняя граница зелёного

    mask_blue = cv2.inRange(img_hsv, lower_blue, upper_blue)
    mask_green = cv2.inRange(img_hsv, lower_green, upper_green)

    contours_green, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cg_area = 0
    for cg in contours_green:
        area = cv2.contourArea(cg)
        cg_area += area if area > 50 else 0

    contours_blue, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cb_area = 0
    for cb in contours_blue:
        area = cv2.contourArea(cb)
        cb_area += area if area > 50 else 0

    return cg_area > cb_area


def circle_marker(green: bool, auv: mur.auv.Auv.Auv):
    """Goes around marker by reglament

    Args:
        green (bool): True if marker is green
    """  # TODO: adjust time & power
    lmt = green
    rmt = -green
    auv.set_motor_power(lmt, 85)
    auv.set_motor_power(rmt, 100)
    sleep(1)
    auv.set_motor_power(rmt, 85)
    auv.set_motor_power(lmt, 100)
    sleep(1)
    auv.set_motor_power(lmt, 100)
    auv.set_motor_power(rmt, 100)
    sleep(1)
    auv.set_motor_power(lmt, 100)
    auv.set_motor_power(rmt, 70)
    sleep(1)
    auv.set_motor_power(lmt, 85)
    auv.set_motor_power(rmt, 100)
    sleep(1)


def find_buoy_error(image: np.ndarray, range: ColorRange) -> Tuple[float, bool, float]:
    """Finds error between selected buoy's center and videofeed center

    Args:
        image (np.ndarray): Image input, not cropped
        range (ColorRange): Color range of buoy which is to be found

    Returns:
        float: Error between center of feed and buoy's x position
        bool: True if found
        float: Area of found buoy
    """
    pass  # TODO: implement, possibly delete 3rd returned value


def bonk_buoy(color: ColorRange):
    """Bonk selected buoy

    Args:
        color (ColorRange): color of buoy, which is to be bonked
    """
    success = True
    area = 0
    buoy_error = 0
    while success and area < 50000 and not stabilize_yaw(buoy_error, 0, 50):
        buoy_error, success, area = find_buoy_error(get_auv_image(auv)) # While buoy is found, move to it
    auv.set_motor_power(0,100) # ↓
    auv.set_motor_power(1,100) # Bonk buoy
    sleep(2)                   # ↑ #TODO: Adjust time


if __name__ == "__main__":
    ############
    # 1st part #
    ############
    auv = mur.mur_init()  # Init
    yellow = ColorRange(Color(), Color())  # TODO: yellow
    green = ColorRange(Color(), Color())  # TODO: green
    blue = ColorRange(Color(), Color())  # TODO: blue
    rot_pdreg = PDReg(1, .01, .01)
    err, found = find_gates_err(get_auv_image(auv), yellow)  # Find gates
    if found:
        while not stabilize_yaw(err, 1, 50, True) and found:
            err, found = find_gates_err(get_auv_image(auv), yellow)  # While gates are found, go in the middle
    auv.set_motor_power(0, 100)  # ↓
    auv.set_motor_power(1, 100)  # Pass gates
    sleep(2)                     # ↑ #TODO: Adjust time
    circle_marker(find_marker(get_auv_image(auv), yellow))
    err, found = find_gates_err(get_auv_image(auv), yellow)  # Backwards gates pass
    if found:
        while found and not stabilize_yaw(err, .1, 50, True):
            err, found = find_gates_err(get_auv_image(auv), yellow)  # While gates are found, go in the middle
    # auv.set_motor_power(0,75)   # ↓
    # auv.set_motor_power(1, 100)  # Turn after gates
    # sleep(2)                    # ↑ #TODO: Adjust time and power
    # auv.set_motor_power(0,90)   # ↓
    # auv.set_motor_power(1, 100)  # Translation between 1st and 2nd parts
    # sleep(2)                    # ↑ #TODO: Adjust time and power

    # ############
    # # 2nd part #
    # ############

    # # Bonk red buoy
    # auv.set_rgb_color(255, 0, 0)
    # color = ColorRange(Color((170, 20, 20), (5, 255, 255), "red"))
    # buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    # begin_finding_time = time()
    # while not success:
    #     buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    #     if time() - begin_finding_time < 5:
    #         auv.set_motor_power(0,-20) # ↓
    #         auv.set_motor_power(1,+20) # Finding buoy, turning left
    #     elif 10 > time() - begin_finding_time > 5:
    #         auv.set_motor_power(0,+20) # ↓
    #         auv.set_motor_power(1,-20) # Finding buoy, turning right
    #     else:
    #         # die
    #         pass
    # bonk_buoy(color)
    # auv.set_motor_power(0,-100) # ↓
    # auv.set_motor_power(1,-100) # Unbonk buoy
    # sleep(5)                    # ↑ #TODO: Adjust time

    # # Bonk yellow buoy
    # auv.set_rgb_color(255, 255, 0)
    # color = ColorRange(Color((25, 20, 20), (60, 255, 255), "yellow"))
    # buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    # begin_finding_time = time()
    # while not success:
    #     buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    #     if time() - begin_finding_time < 5:
    #         auv.set_motor_power(0,-20) # ↓
    #         auv.set_motor_power(1,+20) # Finding buoy, turning left
    #     elif 10 > time() - begin_finding_time > 5:
    #         auv.set_motor_power(0,+20) # ↓
    #         auv.set_motor_power(1,-20) # Finding buoy, turning right
    #     else:
    #         # die
    #         pass
    # bonk_buoy(color)
    # auv.set_motor_power(0,-100) # ↓
    # auv.set_motor_power(1,-100) # Unbonk buoy
    # sleep(5)                    # ↑ #TODO: Adjust time

    # # Bonk green buoy
    # auv.set_rgb_color(0, 255, 0)
    # color = ColorRange(Color((60, 20, 20), (92.5, 255, 255), "green"))
    # buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    # begin_finding_time = time()
    # while not success:
    #     buoy_error, success, _ = find_buoy_error(get_auv_image(auv), color)
    #     if time() - begin_finding_time < 5:
    #         auv.set_motor_power(0,-20) # ↓
    #         auv.set_motor_power(1,+20) # Finding buoy, turning left
    #     elif 10 > time() - begin_finding_time > 5:
    #         auv.set_motor_power(0,+20) # ↓
    #         auv.set_motor_power(1,-20) # Finding buoy, turning right
    #     else:
    #         # die
    #         pass
    # bonk_buoy(color)
    # auv.set_motor_power(0,-100) # ↓
    # auv.set_motor_power(1,-100) # Unbonk buoy
    # sleep(5)                    # ↑ #TODO: Adjust time
    # ############
    # # 3rd part #
    # ############
