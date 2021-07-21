from cac import Color, ColorRange
import cv2
import numpy as np
from scipy import integrate
import pymurapi as mur

auv = mur.mur_init()
colors = {
    'blue': ColorRange(
        Color(40, 30, 20),
        Color(135, 255, 255)
    )
}


def detect_objects(image, color: ColorRange, name):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask0 = cv2.inRange(img_hsv, color.min_color.to_tuple(), color.max_color.to_tuple())
    list_object = []
    contours, _ = cv2.findContours(mask0, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    to_draw = image.copy()
    cv2.drawContours(to_draw, contours, -1, (128, 0, 0), 1)
    for cnt in contours:
        if cv2.contourArea(cnt) > 300:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            cv2.circle(to_draw, center, int(1), (128, 0, 128), 2)

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(to_draw, [box], 0, (0, 191, 255), 2)
            moments = cv2.moments(cnt)
            list_object.append([cv2.contourArea(cnt), x, y])
            cv2.imshow(name, to_draw)
            cv2.waitKey(1)
    list_object.sort()
    if len(list_object) > 1:
        x_center = (list_object[0][1] + list_object[1][1]) // 2
        print(x_center)
        return x_center
    else:
        print(-1)
        return -1


if __name__ == '__main__':
    #    print(colors['red'])
    while True:
        for k,v in colors:
            detect_objects(auv.get_image_bottom(), v, "color")