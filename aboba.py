from typing import Union
from numpy.lib.twodim_base import tri
import pymurapi as mur

auv = mur.mur_init()
import cv2
import math
import time as t
import numpy as np

THRUSTER_YAW_LEFT = 0
THRUSTER_YAW_RIGHT = 1
THRUSTER_DEPTH_LEFT = 2
THRUSTER_DEPTH_RIGHT = 3

THRUSTER_YAW_LEFT_DIRECTION = +1
THRUSTER_YAW_RIGHT_DIRECTION = +1
THRUSTER_DEPTH_LEFT_DIRECTION = +1
THRUSTER_DEPTH_RIGHT_DIRECTION = +1


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


def clamp(v: float, min_v: float, max_v: float) -> float:
    """Clamp value between two ranges.

    Args:
        v (float): Value
        min_v (float): Min value
        max_v (float): Max value

    Returns:
        float: Clamped value
    """
    if v > max_v:
        return max_v
    if v < min_v:
        return min_v
    return v


def keep_yaw(yaw_to_set: float, move_speed: float = 0):
    """Keep robot yaw and move forward/backward.

    Args:
        yaw_to_set (float): Yaw to set
        move_speed (float, optional): Speed to move forward. Defaults to 0.
    """
    global yaw_pd
    err = clamp(yaw_pd.process(yaw_to_set - auv.get_yaw()), -100, 100)
    auv.set_motor_power(THRUSTER_YAW_LEFT, move_speed + err * THRUSTER_YAW_LEFT_DIRECTION)
    auv.set_motor_power(THRUSTER_YAW_RIGHT, move_speed - err * THRUSTER_YAW_RIGHT_DIRECTION)
    t.sleep(0.1)


def keep_depth(depth_to_det: float):
    """Keep robot depth.

    Args:
        depth_to_det (float): Depth to set.
    """
    global depth_pd
    err = clamp(depth_pd.process(depth_to_det - auv.get_depth()), -100, 100)
    auv.set_motor_power(THRUSTER_DEPTH_LEFT, err * THRUSTER_DEPTH_LEFT_DIRECTION)
    auv.set_motor_power(THRUSTER_DEPTH_RIGHT, -err * THRUSTER_DEPTH_RIGHT_DIRECTION)
    t.sleep(0.1)


def keep(yaw_to_set: float = ..., depth_to_set: float = ..., move_speed: float = 0, time: float = 0):
    """Keep depth, yaw and move robot forward/backward.

    Args:
        yaw_to_set (float, optional): Yaw to set. Defaults to ....
        depth_to_set (float, optional): Depth to set. Defaults to ....
        move_speed (float, optional): Move forward speed. Defaults to 0.
        time (float, optional): Time to keep. Defaults to 0.
    """
    timer = t.time() + time
    while t.time() < timer:
        if yaw_to_set is not ...:
            keep_yaw(yaw_to_set, move_speed)
        else:
            auv.set_motor_power(THRUSTER_YAW_LEFT, move_speed * THRUSTER_YAW_LEFT_DIRECTION)
            auv.set_motor_power(THRUSTER_YAW_RIGHT, -move_speed * THRUSTER_YAW_RIGHT_DIRECTION)
        if depth_to_set is not ...:
            keep_depth(depth_to_set)
        t.sleep(0.01)


def stabilizate_value_by_time(timer: float, value_to_set: float, current_value: float, accuracy: float,
                              time_to_keep_value: float) -> Union[float, bool]:
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
        timer = 0
    return timer, False


yaw_pd = PD(1, 0.001)
depth_pd = PD(100, 50)

HSV_MIN = (10, 150, 150)
HSV_MAX = (20, 255, 255)


def main():
    timer = t.time()
    while True:
        # timer, stabilizated = stabilizate_value_by_time(timer, 1, auv.get_depth(), 0.2, 5)
        keep(0, 1)
        frame = auv.get_image_bottom()
        draw = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        bin = cv2.inRange(hsv, HSV_MIN, HSV_MAX)

        cnts, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in cnts:
            if cv2.contourArea(cnt) > 100:
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(draw, (x, y), (x + w, y + h), (255, 0, 0))
                (x, y), r = cv2.minEnclosingCircle(cnt)
                # print(x, y, r)
                cv2.circle(draw, (int(x), int(y)), int(r), (0, 0, 255))
                #                r, triangle = cv2.minEnclosingTriangle(cnt)
                # print(triangle.shape)
                # triangle = np.transpose(triangle, [1, 0, 2])
                # print(triangle.shape)
                # print(triangle[0][0][0])
                #                cv2.line(draw, tuple(triangle[0][0]), tuple(triangle[1][0]), (0, 0, 0))
                #                cv2.line(draw, tuple(triangle[1][0]), tuple(triangle[2][0]), (0, 0, 0))
                #                cv2.line(draw, tuple(triangle[0][0]), tuple(triangle[2][0]), (0, 0, 0))
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(draw, [box], 0, (0, 191, 255), 2)
                m = cv2.moments(cnt)
                cX = int(m["m10"] / m["m00"])
                cY = int(m["m01"] / m["m00"])
                cv2.circle(draw, (cX, cY), 5, (0, 255, 0), 3)

                # cv2.polylines(draw, [triangle.reshape((-1, 1, 2))], True, (255, 255, 0))
                # cv2.drawContours(draw, [triangle], -1, (255, 255, 0))
                # cv2.triangle
                # print(r, triangle)
        cv2.drawContours(draw, cnts, -1, (0, 255, 0))
        cv2.imshow("mask", bin)

        cv2.imshow("draw", draw)
        cv2.waitKey(1)
        # if stabilizated:
        #     print("DONE!")
        #     return



if __name__ == "__main__":
    main()
