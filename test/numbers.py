from typing import List, Tuple, TypeVar
import cv2
import numpy as np
import pymurapi as mur
import time as t

auv = mur.mur_init()
# mur_view = auv.get_videoserver()

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

class Color:
    def __init__(self, x: float, y: float, z: float, name: str = ...) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.z = z
    def to_tuple(self) -> Tuple:
        return (self.x, self.y, self.z)

class ColorRange:
    def __init__(self, min_color: Color = ...,
                 max_color: Color = ...,
                 name: str = ...,) -> None:
        self.name = name
        self.min_color = min_color
        self.max_color = max_color

        self.min_color.name = name
        self.max_color.name = name

    def to_tuple(self) -> Tuple[Tuple, Tuple]:
        return (self.min_color.to_tuple(), self.max_color.to_tuple())

def vec2_2_center(a, b):
    return (
        int((a[0] + b[0]) / 2),
        int((a[1] + b[1]) / 2)
    )

def vec2_3_center(a, b, c):
    return (
        int((a[0] + b[0] + c[0]) / 3),
        int((a[1] + b[1] + c[1]) / 3)
    )

def vec2_4_center(a, b, c, d):
    return (
        int((a[0] + b[0] + c[0] + d[0]) / 4),
        int((a[1] + b[1] + c[1] + d[1]) / 4)
    )

def rect_norm_points(rect):
    """Returns corrected rect points coordinates.

    Args:
        rect (CV2 rect): CV2 rectange.

    Returns:
        Corners points coordinates: topLeft, topRight, bottomRight, bottomLeft
    """
    if rect[2] > 45:
        return cv2.boxPoints(rect).astype(int)
    else:
        d, a, b, c = cv2.boxPoints(rect).astype(int)
        return (a, b, c, d)

T = TypeVar('T')
def clamp(value: T, min: T, max: T) -> T:
    return min if value < min else max if value > max else value
        
# black = ColorRange(Color(66, 103, 19), Color(101, 255, 66), "black")
# white = ColorRange(Color(0, 0, 127), Color(180, 96, 197), "white")
# red = ColorRange(Color(0, 0, 56), Color(19, 255, 255), "red")

# cam = cv2.VideoCapture(0)
pd = PD(0.1, 0.001)

def move_to_2(max_contour_ares: float = 1000):
    while True:
        # r, frame = cam.read()
        frame = auv.get_image_front()
        frame = cv2.bilateralFilter(frame,9,75,75)
        draw = frame.copy()
        # assert r, "Cam not captured"
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)
        # thresh = cv2.adaptiveThreshold(blur,255,1,1,105, 13)
        thresh = cv2.adaptiveThreshold(blur,255,1,1,21, 13)
        cnts, hierarhy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if cv2.contourArea(cnt) > 50:
                _, _, w, h = cv2.boundingRect(cnt)
                if w < h:
                    rect = cv2.minAreaRect(cnt)
                    a, b, c, d = cv2.boxPoints(rect)
                    center = vec2_4_center(a, b, c, d)
                    if thresh[center[1]][center[0]] == 0:
                        topLeft, topRight, bottomRight, bottomLeft = rect_norm_points(rect)
                        middleLeft = vec2_2_center(topLeft, bottomLeft)
                        middleRight = vec2_2_center(topRight, bottomRight)
                        bottomCenter = vec2_2_center(bottomLeft, bottomRight)
                        topCenter = vec2_2_center(topLeft, topRight)
                        point_top = vec2_2_center(topCenter, vec2_2_center(topCenter, vec2_2_center(topCenter, center)))
                        point_bottom = vec2_2_center(bottomCenter, vec2_2_center(bottomCenter, vec2_2_center(bottomCenter, center)))
                        point_left = vec2_2_center(middleLeft, bottomLeft)
                        point_right = vec2_2_center(middleRight, bottomRight)
                        point_top_middle = vec2_2_center(center, topCenter)
                        point_left_middle = vec2_2_center(center, middleLeft)
                        point_right_bottom = vec2_4_center(center, middleRight, bottomRight, bottomCenter)
                        if thresh[point_top[1]][point_top[0]] == 255\
                            and thresh[point_bottom[1]][point_bottom[0]] == 255\
                            and thresh[point_left[1]][point_left[0]] == 0\
                            and thresh[point_right[1]][point_right[0]] == 0\
                            and thresh[point_top_middle[1]][point_top_middle[0]] == 0\
                            and thresh[point_left_middle[1]][point_left_middle[0]] == 0\
                            and thresh[point_right_bottom[1]][point_right_bottom[0]] == 0:
                            cv2.circle(draw, center, 3, (0, 255, 0), 3)
                            # cv2.drawContours(draw,[np.int0((a, b, c, d))],0,(0,0,255),2)
                            error = center[0] - 320//2
                            U = pd.process(error)
                            # print(cv2.contourArea(cnt))
                            auv.set_motor_power(0, U + 50)
                            auv.set_motor_power(1, -U + 50)
                            if area >= max_contour_ares:
                                return
        cv2.imshow('frame', draw)
        cv2.imshow('mask', thresh)
        cv2.waitKey(1)

yaw = auv.get_yaw()
move_to_2()
yaw = auv.get_yaw()
