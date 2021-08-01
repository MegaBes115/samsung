from typing import List, Tuple, TypeVar, Union
import cv2
import numpy as np
from color import Color, ColorRange
import time as t
import pymurapi as mur


class PD:
    _kp = 0.0
    _kd = 0.0
    _prev_error = 0.0
    _timestamp = 0

    def __init__(self, kp: float = ..., kd: float = ...):
        if kp is not ...:
            self.set_p_gain(kp)
        if kd is not ...:
            self.set_d_gain(kd)

    def set_p_gain(self, value):
        self._kp = value

    def set_d_gain(self, value):
        self._kd = value

    def process(self, error):
        timestamp = int(round(t.time() * 1000))  # в timestamp записываем
        try:
            # время(выраженное в секундах) и домножаем до милисекунд, round отбрасывает знаки после запятой
            output = self._kp * error + self._kd / \
                (timestamp - self._timestamp) * (error - self._prev_error)
            # вычесляем выходное значение на моторы по ПД регулятору и записываем в output
            self._timestamp = timestamp  # перезаписываем время
            self._prev_error = error  # перезаписываем ошибку
            return output
        except ZeroDivisionError:
            return 0

def relative_number_ratio_by_frame(rgb: np.ndarray, red_range: ColorRange, white_range: ColorRange, black_range: ColorRange) -> List[Tuple[Tuple[int, int, int, int], float]]:
    """Gets relative number ratio using frame area.

    Args:
        rgb (np.ndarray): RGB image

    Returns:
        List[Tuple[Tuple[int, int, int, int], float]] - List of: 1) Tuple of number bounding rect: (x, y, w, h) 1) Float value of ratio; 
    """
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    bin = cv2.inRange(hsv, red_range.min_color.to_tuple(), red_range.max_color.to_tuple())
    cnts, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    list_of = []
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area < 200: continue
        (x, y, w, h) = cv2.boundingRect(cnt)
        cropped = hsv[y:y+h, x:x+w, :]
        bin2 = cv2.inRange(cropped, white_range.min_color.to_tuple(), white_range.max_color.to_tuple())
        cnts2, _ = cv2.findContours(bin2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt2 in cnts2:
            area2 = cv2.contourArea(cnt2)
            if area2 < 200: continue
            bin3 = cv2.inRange(cropped, black_range.min_color.to_tuple(), black_range.max_color.to_tuple())
            cnts3, _ = cv2.findContours(bin3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt3 in cnts3:
                area3 = cv2.contourArea(cnt3)
                if area3 < 200: continue
                (x3, y3, w3, h3) = cv2.boundingRect(cnt3)
                list_of.append(((x3+x, y3+y, w3, h3), area2/area3))
    return list_of

def relative_number_ratio_by_rect(rgb: np.ndarray, red_range: ColorRange, black_range: ColorRange) -> List[Tuple[Tuple[int, int, int, int], float]]:
    """Gets relative number ratio using `cv2.minAreaRect`.

    Args:
        rgb (np.ndarray): RGB image

    Returns:
        List[Tuple[Tuple[int, int, int, int], float]] - List of: 1) Tuple of number bounding rect: (x, y, w, h) 1) Float value of ratio; 
    """
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    bin = cv2.inRange(hsv, red_range.min_color.to_tuple(), red_range.max_color.to_tuple())
    cnts, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    list_of = []
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area < 200: continue
        (x, y, w, h) = cv2.boundingRect(cnt)
        cropped = hsv[y:y+h, x:x+w, :]
        bin3 = cv2.inRange(cropped, black_range.min_color.to_tuple(), black_range.max_color.to_tuple())
        cnts3, _ = cv2.findContours(bin3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt3 in cnts3:
            area3 = cv2.contourArea(cnt3)
            rect = cv2.minAreaRect(cnt3)
            ((_, _), (w, h), _) = rect
            rectangle_area = w * h
            if area3 < 200: continue
            (x3, y3, w3, h3) = cv2.boundingRect(cnt3)
            list_of.append(((x3+x, y3+y, w3, h3), rectangle_area/area3))
    return list_of

def find_gates_err(image: np.ndarray) -> Tuple[float, bool]:
    """Finds error between gates' middlepoint position and center of videofeed

    Args:
        image (cv.): image, in which gates are to be found, not cropped

    Returns:
        float: Error
        bool: True if gates are found
    """
    pass #TODO implement

def stabilize_yaw(target: float, possible_err: float, additional_fwd: float) -> bool: 
    """Stabilizes yaw on target, with backlash in degrees, denoted by possible_err

    Args:
        target (float): Target, on which the AUV is to be stabilized
        possible_err (float): Possible backlash in degrees (-180 to 180)
        additional_fwd  (float): Additional forward power (-100 to 100)
    Returns:
        bool: Stabilizing status, True if stabilized
    """
    pass #TODO implement


def get_auv_image() -> np.ndarray:
    """Returns camera feed in numpy.ndarray

    Returns:
        np.ndarray: Image
    """
    pass #TODO implement

def find_marker(image: np.ndarray) -> bool:
    """Find marker, green or blue

    Args:
        image (np.ndarray): Image input, not cropped

    Returns:
        bool: True if green
    """
    pass #TODO implement

def circle_marker(green: bool) -> None:
    """`|blocks thread|` Goes around marker as in the reglament 

    Args:
        green (bool): True if marker is green
    """

    pass #TODO implement

def find_buoy_error(image: np.ndarray, range: ColorRange) -> Tuple[float, bool, float]:
    """Finds buoys

    Args:
        image (np.ndarray): Image input, not cropped
        range (ColorRange): Color range of buoy which is to be found

    Returns:
        float: Error between center of feed and buoy's x position
        bool: True if found
        float: Area of found buoy
    """ #TODO implement

def opencv_show_func(frame, window_name: str = "window"):
    cv2.imshow(window_name, frame)
    cv2.waitKey(1)

def simulator_get_front_frame_func(auv):
    return auv.get_image_front()

def simulator_get_bottom_frame_func(auv):
    return auv.get_image_bottom()

T = TypeVar('T')
def clamp(v: T, min_v: T, max_v: T) -> T: 
    """Clamp value between two ranges.

    Args:
        v (T): Value
        min_v (T): Min value
        max_v (T): Max value

    Returns:
        T: Clamped value
    """
    if v > max_v:
        return max_v
    if v < min_v:
        return min_v
    return v

def stabilizate_value_by_time(timer: float, value_to_set: float, current_value: float, accuracy: float, time_to_keep_value: float) -> Union[float, bool]:
    """Stabilizate value to be in accuracy range for any time.

    Args:
        timer (float): Timer.
        value_to_set (float): Value must to be that.
        current_value (float): Current value
        accuracy (float): Accuracy range.
        time_to_keep_value (float): For this time value will be kept.

    Returns:
        Union[float, bool]: float - timer. Must be reset for this func after. bool - if stabilizated.
    """
    # print(value_to_set - accuracy, value_to_set + accuracy)
    if value_to_set - accuracy <= current_value and current_value <= value_to_set + accuracy:
        if t.time() > timer + time_to_keep_value:
            return timer, True
    else:
        timer = t.time() 
    return timer, False

# if __name__ == "__main__":
#     red_range = ColorRange(Color(348/2,215,227), Color(368/2,235,247))
#     white_range = ColorRange(Color(0, 0, 240), Color(10/2, 10, 255))
#     black_range = ColorRange(Color(0, 0, 0), Color(10/2, 10, 10))

#     img = cv2.imread('d:/test/images/numbers_test.png')
#     draw = img.copy()
#     l = list(relative_number_ratio_by_frame(img, red_range, white_range, black_range))
#     l.sort(key=lambda r: r[1])
#     _, ((x, y, w, h), ratio), _, *other = l
#     l2 = list(relative_number_ratio_by_rect(img, red_range, black_range))
#     l2.sort(key=lambda r: r[1])
#     _, ((x2, y2, w2, h2), ratio2), _, *other = l2
#     print(ratio, ratio2)
#     cv2.rectangle(draw, (x, y), (x+w, h+y), (255, 0, 0), 2)
#     cv2.rectangle(draw, (x2, y2), (x2+w2, h2+y2), (255, 0, 0), 2)
#     cv2.imshow('draw', draw)
#     cv2.waitKey(0)