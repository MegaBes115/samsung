import colorsys
import sys
import os
import imutils
from time import sleep, time
from typing import Tuple, Union
from functions import Color, ColorRange, relative_number_ratio_by_frame
import cv2
import numpy as np
from scipy import integrate
#import pymurapi as mur

#TODO: Все функции, кроме bonk_buoy()


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def find_numbers_rect(image: np.ndarray) -> list[np.ndarray, np.ndarray]:

             # Чтение изображения, создание оттенков серого, размытие по Гауссу, расширение, обнаружение контуров
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    dilate = cv2.dilate(blurred, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    edged = cv2.Canny(dilate, 30, 120, 3)
 
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[1] if imutils.is_cv3() else cnts[0] # Совместимость, ага
    docCnt: list[np.ndarray] = []
 
    
    if len(cnts) > 0:
        for c in cnts:
            if cv2.contourArea(c) > 50:
                            # Приблизительный контур
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                            # Если наш приблизительный контур имеет четыре точки, то это - околоквадрат с цифрой
                if len(approx) == 4:
                    element = [approx, c]
                    docCnt.append(element)
                
 
    # Оквадрачиваем изображение
    rectangular: list[np.ndarray] = [[four_point_transform(image, a[0].reshape(4, 2)), a[1]] for a in docCnt]
    return rectangular

def find_2nd_parking_err(image: np.ndarray):
    """Finds error between center of 2nd slot and center of screen

    Args:
        image (np.ndarray): Input image, not cropped

    Returns:
        float: Error
    """


def find_gates_err(image: np.ndarray) -> Tuple[float, bool]:
    """Finds error between gates' middlepoint position and center of videofeed

    Args:
        image (cv2.): image, in which gates are to be found, not cropped

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


# def get_auv_image(auv: mur.auv, hsv: bool=True) -> np.ndarray:
#     """Returns camera feed in numpy.ndarray

#     Args:
#         auv (mur.auv): AUV, which camera is to be read
#         hsv (bool): True if returned image is needed to be in HSV colorspace 
#     Returns:
#         np.ndarray: Image
#     """
#     pass

def find_marker(image: np.ndarray) -> bool:
    """Finds marker, green or blue

    Args:
        image (np.ndarray): Image input, not cropped

    Returns:
        bool: True if green
    """
    pass

def circle_marker(green: bool):
    """Goes around marker by reglament

    Args:
        green (bool): True if marker is green
    """

    pass

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

def bonk_buoy(color: ColorRange):
    """Bonk selected buoy

    Args:
        color (ColorRange): color of buoy, which is to be bonked
    """
    success = True
    area = 0
    buoy_error = 0
    while success and area > 50000 and not stabilize_yaw(buoy_error, 0, 50):
        buoy_error, success, area = find_buoy_error(get_auv_image(auv)) # While buoy is found, move to it
    auv.set_motor_power(0,100) # ↓
    auv.set_motor_power(1,100) # Bonk buoy
    sleep(2)                   # ↑ #TODO: Adjust time
    
if __name__ == "__main__":
    red_range = ColorRange(Color(348/2,215,227), Color(368/2,235,247))
    white_range = ColorRange(Color(0, 0, 240), Color(10/2, 10, 255))
    black_range = ColorRange(Color(0, 0, 0), Color(10/2, 10, 10))
    ##########
    #1st part#
    ##########
    #auv = mur.mur_init() # Init
    print(os.getcwd() + r"/test/images/numbers_test_hard.png" if not "win" in sys.platform else os.getcwd() + "\\test\\images\\numbers_test_hard")
    image = cv2.imread(os.getcwd() + r"/test/images/numbers_test_hard.png" if not "win" in sys.platform else os.getcwd() + "\\test\\images\\numbers_test_hard.png")
    image_draw = image.copy()
    a = 0
    nums: list[list[np.ndarray, np.ndarray]] = find_numbers_rect(image)
    nums.sort(key=lambda r: r[0].size)
    min_area_img = nums[0][0]
    min_size = (min_area_img.shape[0], min_area_img.shape[1])
    for i in nums:
        num_size = (i[0].shape[0], i[0].shape[1])
        original_contour = i[1]
        resize = np.divide(min_size, num_size)
        transformed = cv2.resize(i[0].copy(), None, None, *resize, cv2.INTER_CUBIC)
        generator = relative_number_ratio_by_frame(transformed, red_range, white_range, black_range)
        cnts, _ = cv2.findContours(cv2.inRange(cv2.cvtColor(transformed, cv2.COLOR_BGR2HSV), (0, 0, 0), (180, 10, 10)), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts.sort(key=lambda r: cv2.contourArea(r), reverse=True)
        filtered_cnts = []
        for cnt in cnts:
            if cv2.contourArea(cnt) > 50:
                filtered_cnts.append(cnt)
        cv2.drawContours(transformed, filtered_cnts, -1, (0,255,0), 2, cv2.LINE_4)
        num = cv2.contourArea(cnts[0])
        cv2.imshow((str(num_size) + "->" + str(min_size) + ", area=" + str(num)) if num_size != min_size else "minarea, area=" + str(num), transformed)
        cv2.drawContours(image_draw, original_contour, -1, (0,255,0), 4, cv2.LINE_4)
        
    cv2.imshow("original_image_detected", image_draw)
    cv2.waitKey()
    # err, found = find_gates_err(get_auv_image(auv)) # Find gates
    # if found:
    #     while not stabilize_yaw(err, 1, 50) and found:
    #         err, found = find_gates_err(get_auv_image(auv)) # While gates are found, go in the middle 
    # auv.set_motor_power(0,100) # ↓
    # auv.set_motor_power(1,100) # Pass gates
    # sleep(2)                   # ↑ #TODO: Adjust time
    # circle_marker(find_marker(get_auv_image(auv)))
    # err, found = find_gates_err(get_auv_image(auv)) # Backwards gates pass
    # if found:
    #     while found and not stabilize_yaw(err, .1, 50):
    #         err, found = find_gates_err(get_auv_image(auv)) # While gates are found, go in the middle 
    # auv.set_motor_power(0,75)  # ↓
    # auv.set_motor_power(1,100) # Turn after gates
    # sleep(2)                   # ↑ #TODO: Adjust time and power
    # auv.set_motor_power(0,90)  # ↓
    # auv.set_motor_power(1,100) # Translation between 1st and 2nd parts
    # sleep(2)                   # ↑ #TODO: Adjust time and power        
    
    # ##########
    # #2nd part#
    # ##########
    
    
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
    # ##########
    # #3rd part#
    # ##########
    # ratio = relative_number_ratio_by_frame(get_auv_image(auv, False), ColorRange(Color(170, 20, 20), Color(5, 255, 255)), ColorRange(Color(0, 0, 191.25), Color(180, 25.5, 255)), ColorRange(Color(0, 0, 0), Color(255, 255, 63.75)))
    
