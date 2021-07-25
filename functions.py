from typing import Tuple
import cv2
import numpy as np
from color import Color, ColorRange

def relative_number_ratio_by_frame(rgb: np.ndarray, red_range: ColorRange, white_range: ColorRange, black_range: ColorRange) -> Tuple[float, Tuple[int, int, int, int]]:
    """Gets relative number ratio using frame area.

    Args:
        rgb (np.ndarray): RGB image

    Returns:
        Tuple[float, Tuple[int, int, int, int]] - 1) Float value of ratio; 2) Tuple of number bounding rect: (x, y, w, h)
    """
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    bin = cv2.inRange(hsv, red_range.min_color.to_tuple(), red_range.max_color.to_tuple())
    cnts, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
                yield ((x3+x, y3+y, w3, h3), area2/area3, area2, area3, cv2.arcLength(cnt3, True)/cv2.arcLength(cnt2, True))

def relative_number_ratio_by_rect(rgb: np.ndarray, red_range: ColorRange, black_range: ColorRange) -> Tuple[float, Tuple[int, int, int, int]]:
    """Gets relative number ratio using `cv2.minAreaRect`.

    Args:
        rgb (np.ndarray): RGB image

    Returns:
        Tuple[float, Tuple[int, int, int, int]] - 1) Float value of ratio; 2) Tuple of number bounding rect: (x, y, w, h)
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
            yield ((x3+x, y3+y, w3, h3), rectangle_area/area3)

if __name__ == "__main__":
    red_range = ColorRange(Color(348/2,192,192), Color(368/2,255,255))
    white_range = ColorRange(Color(0, 0, 240), Color(180, 10, 255))
    black_range = ColorRange(Color(0, 0, 0), Color(180, 10, 10))

    img = cv2.imread('/home/mango/repos/samsung_main/test/images/numbers_test_hard.png')
    draw = img.copy()
    l = list(relative_number_ratio_by_frame(img, red_range, white_range, black_range))
    ratios = [x[1] for x in l]
    red_areas = [x[2] for x in l]
    num_areas = [x[3] for x in l]
    perimrters = [x[4] for x in l]
    l.sort(key=lambda r: r[1])
    
    # _, ((x, y, w, h), ratio), _, *other = l
    # l2 = list(relative_number_ratio_by_rect(img, red_range, black_range))
    # l2.sort(key=lambda r: r[1])
    # _, ((x2, y2, w2, h2), ratio2), _, *other = l2
    # print(ratio, ratio2)
    textSize = cv2.getTextSize("This is 2", cv2.FONT_HERSHEY_DUPLEX, 2, 2)
    cv2.putText(draw, "This is 2", (l[1][0][0], l[1][0][1]), cv2.FONT_HERSHEY_DUPLEX, 1, 2)

    for rect in l:
        textSize = cv2.getTextSize(str(l[1][4]), cv2.FONT_HERSHEY_DUPLEX, 2, 2)
        cv2.putText(draw, str(l[1][4]), (l[1][0][0] + l[1][0][2], l[1][0][1] + l[1][0][3]), cv2.FONT_HERSHEY_DUPLEX, 1, 2)
        cv2.rectangle(draw, (rect[0][0], rect[0][1]), (rect[0][0]+rect[0][2], rect[0][1]+rect[0][3]), (255, 0, 0), 2)
    print(ratios)
    print(red_areas)
    print(num_areas)
    print(perimrters)
    cv2.imshow('draw', draw)
    cv2.waitKey(0)