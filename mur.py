import colorsys
import time
from typing import Union
import cv2 as cv
import numpy as np
from scipy import integrate
import pymurapi as mur

auv = mur.mur_init()


class MotorController:
    def __init__(self, motor_id: int, target_auv: mur.auv.Auv):
        """
        Initializes controller

        :param motor_id:
            id of controlled motor
        :param target_auv:
            AUV, whose motors will be controlled
        :returns: MotorController
        """
        self.id = motor_id
        self.auv = target_auv

    def set_power(self, power: Union[float, int]) -> None:
        """
        Sets power of this motor

        :param power:
            Power to set motor to, automatically clamps power to -100 to 100 boundaries
        """
        self.auv.set_motor_power(self.id, power if -100 < power < 100 else -100 if power < -100 else 100)


class PIDReg:
    def __init__(self, p_coeff, i_coeff, d_coeff):
        self.p_coeff = p_coeff
        self.i_coeff = i_coeff
        self.d_coeff = d_coeff
        self.prev_iter_time = 0
        self.dt = 0
        self.de = 0

    def compute(self, error: float) -> float:
        """Compute control signal of given PIDReg, rudimentary FBL-protection included

        Args:
            error (float): Error, based of which result will be computed
        Returns:
            float: Control signal, pass this into control sequence
        """
        self.dt = time.thread_time()
        control_signal: float = \
            self.p_coeff * error + \
            self.i_coeff * integrate.quad(lambda _: error * self.dt, 0, self.dt / 2)[0] + \
            self.d_coeff * (self.de / self.dt)
        control_signal = 50 if control_signal > 100 else -50 if control_signal < -100 else control_signal
        self.de = control_signal
        return control_signal


yaw_pidr = PIDReg(.5, .01, .1)
lf_motor = MotorController(0, auv)
rf_motor = MotorController(1, auv)


def move(angle: int = auv.get_yaw()):
    global lf_motor, rf_motor, yaw_pidr
    stab_counter = 0
    while stab_counter <= 10:
        stab_counter += 1
        x_error_ = clamp_angle(angle - auv.get_yaw())
        u_ = yaw_pidr.compute(x_error_)
        lf_motor.set_power(-u_)
        rf_motor.set_power(u_)
        if x_error_ > 1:
            stab_counter = 0
    return auv.get_yaw()


def clamp_angle(angle):
    if angle > 180:
        return angle - 360
    if angle < -180:
        return angle + 360
    return angle


def arrow_direction(arrow_contour):
    arr_rect = cv.minAreaRect(arrow_contour)
    arr_box = np.int0(cv.boxPoints(arr_rect))
    arr_moments = cv.moments(arrow_contour)
    arr_cx = int(arr_moments['m10'] / arr_moments['m00'])
    arr_cy = int(arr_moments['m01'] / arr_moments['m00'])
    if arr_cy > arr_rect[0][0] + arr_rect[1][1] / 2:
        print("up")
    else:
        print("down")
    print(arr_rect[0][1] + arr_rect[1][1] / 2)


hsv_values = dict(
    white=((0, 0, 191.25), (180, 25.5, 255)), lightgrey=((0, 0, 127.5), (255, 255, 191.25)),
    darkgrey=((0, 0, 63.75), (255, 255, 127.5)), black=((0, 0, 0), (255, 255, 63.75)),
    red=((170, 20, 20), (5, 255, 255)), pink=((135, 20, 20), (170, 255, 255)),
    purple=((115, 20, 20), (135, 255, 255)), blue=((100, 20, 20), (115, 255, 255)),
    lblue=((92.5, 20, 20), (100, 255, 255)), green=((60, 20, 20), (92.5, 255, 255)),
    yellow=((25, 20, 20), (60, 255, 255)), orange=((10, 20, 20), (20, 255, 255)),
    color=((0, 20, 20), (180, 255, 255))
)
if __name__ == '__main__':

    while True:
        img = auv.get_image_front()
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img2 = img.copy()
        for k, v in hsv_values.items():
            # if k != "color" and not "grey" in k and k != "white" and k != "black":
            if k == "green":
                maskedimg = cv.inRange(hsv, *v, None) if k != 'red' else cv.inRange(hsv, v[0], (255, 255, 255)) + \
                                                                         cv.inRange(hsv, (0, 0, 0), v[1])
                contours, _ = cv.findContours(maskedimg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                if contours:
                    for contour in contours:
                        if 20000 > cv.contourArea(contour) > 50:
                            try:
                                rect = cv.minAreaRect(contour)
                                box = np.int0(cv.boxPoints(rect))
                                color = np.ndarray.flatten((np.array(v[0]) + np.array(v[1])) / 2)
                                color[2] = color[1] = 1
                                color[0] /= 180
                                color = colorsys.hsv_to_rgb(*color)
                                color = list(round(i * 255) for i in color)
                                color.reverse()
                                cv.drawContours(img2, [box], -1, color, 1, cv.LINE_8, None, 2, (0, 0))
                                size = cv.getTextSize(k, cv.FONT_HERSHEY_PLAIN, 2, 1)
                                txt_pos = [
                                    int(rect[0][0] + (rect[1][0] / 2) - size[0][0]),  # x
                                    int(rect[0][1] + (rect[1][1] / 2) + size[0][1])  # y
                                ]
                                cv.putText(img2, k, txt_pos, cv.FONT_HERSHEY_PLAIN, 2, color, 1, cv.LINE_AA)
                                M = cv.moments(contour)
                                cx = int(M['m10'] / M['m00'])
                                x_error = -((160 - cx) / 2)
                                u = yaw_pidr.compute(x_error)
                                lf_motor.set_power(50 + u)
                                rf_motor.set_power(50 - u)
                                cy = int(M['m01'] / M['m00'])
                                y_error = ((120 - cy) / 2)
                                arrow_direction(contour)
                                cv.circle(img2, (int(cx), int(cy)), 1, (0, 255, 0), 2)
                            except ZeroDivisionError:
                                pass
                        if cv.contourArea(contour) > 20000:
                            rf_motor.set_power(0)
                            lf_motor.set_power(0)
                            auv.shoot()
                else:
                    rf_motor.set_power(0)
                    lf_motor.set_power(0)
        cv.imshow("img", img2)
        cv.waitKey(2)
