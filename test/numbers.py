from typing import List, Tuple
import cv2
import numpy as np
# import pymurapi as mur

# auv = mur.mur_init()
# mur_view = auv.get_videoserver()

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

def find_red_rects(rgb: np.ndarray, red_range: ColorRange) -> List[Tuple[int, int, int]]:
    """Find red rects on image.

    Args:
        rgb (np.ndarray): RGB CV2 frame.

    Returns:
        List[Tuple[int, int, int]]: List of rects (x, y, w, h)
    """
    cropped = []
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    bin = cv2.inRange(hsv, red_range.min_color.to_tuple(), red_range.max_color.to_tuple())
    cnts, _ = cv2.findContours(bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area < 200: continue
        (x, y, w, h) = cv2.boundingRect(cnt)
        cropped.append((x, y, w, h))
    return cropped

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


def find_numbers_rect(image: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:

             # Чтение изображения, создание оттенков серого, размытие по Гауссу, расширение, обнаружение контуров
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    dilate = cv2.dilate(blurred, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    edged = cv2.Canny(dilate, 30, 120, 3)
 
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] 
    docCnt = []
 
    
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
    rectangular = [(four_point_transform(image, a[0].reshape(4, 2)), a[1]) for a in docCnt]
    return rectangular

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
        
black = ColorRange(Color(66, 103, 19), Color(101, 255, 66), "black")
white = ColorRange(Color(0, 0, 127), Color(180, 96, 197), "white")
red = ColorRange(Color(0, 0, 56), Color(19, 255, 255), "red")

cam = cv2.VideoCapture(1)

while True:
    r, frame = cam.read()
    draw = frame.copy()
    assert r, "Cam not captured"
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    thresh = cv2.adaptiveThreshold(blur,255,1,1,105, 13)
    cnts, hierarhy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in cnts:
        if cv2.contourArea(cnt) > 1000:
            _, _, w, h = cv2.boundingRect(cnt)
            if w < h:
                rect = cv2.minAreaRect(cnt)
                a, b, c, d = cv2.boxPoints(rect)
                center = vec2_4_center(a, b, c, d)
                if thresh[center[1]][center[0]] == 0:
                    
                    # cv2.drawContours(draw, [cnt], -1, (255, 0, 0))
                    # cv2.drawContours(draw,[],0,(0,0,255),2)
                    # cv2.putText(draw, str(rect[2]), center, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))
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
                    try:
                        if thresh[point_top[1]][point_top[0]] == 255\
                            and thresh[point_bottom[1]][point_bottom[0]] == 255\
                            and thresh[point_left[1]][point_left[0]] == 0\
                            and thresh[point_right[1]][point_right[0]] == 0\
                            and thresh[point_top_middle[1]][point_top_middle[0]] == 0\
                            and thresh[point_left_middle[1]][point_left_middle[0]] == 0\
                            and thresh[point_right_bottom[1]][point_right_bottom[0]] == 0:
                            cv2.circle(draw, center, 3, (0, 255, 0), 3)
                            cv2.circle(draw, middleLeft, 3, (0, 0, 255), 3)
                            cv2.circle(draw, middleRight, 3, (0, 0, 255), 3)
                            cv2.circle(draw, topLeft, 3, (0, 0, 255), 3)
                            cv2.circle(draw, topRight, 3, (0, 0, 255), 3)
                            cv2.circle(draw, bottomRight, 3, (0, 0, 255), 3)
                            cv2.circle(draw, bottomLeft, 3, (0, 0, 255), 3)
                            cv2.circle(draw, bottomCenter, 3, (0, 0, 255), 3)
                            cv2.circle(draw, topCenter, 3, (0, 0, 255), 3)
                            cv2.circle(draw, point_top, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_bottom, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_left, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_right, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_top_middle, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_left_middle, 3, (0, 255, 255), 3)
                            cv2.circle(draw, point_right_bottom, 3, (0, 255, 255), 3)
                    except:
                        pass
            
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray,(5,5),0)
    # ret3,th3 = cv2.threshold(blur,3,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # avg_color_per_row = np.average(frame, axis=0)
    # avg_color = np.average(avg_color_per_row, axis=0)
    # draw = frame.copy()
    # draw -= np.full(frame.shape,yh avg_color).astype('uint8') 
    
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # binMask = cv2.inRange(hsv, *black.to_tuple())
    # # result = relative_number_ratio_by_frame(frame, red, white, black)
    # rects = find_red_rects(frame, red)
    # # print(rects[0].shape)
    # for x, y, w, h in find_red_rects(frame, red):
    #     cropped = frame[y:y+h, x:x+w, :]
    #     for cleared, cnt in find_numbers_rect(cropped):
    #         hsvCrop = cv2.cvtColor(cleared, cv2.COLOR_BGR2HSV)
    #         blackBin = cv2.inRange(hsvCrop, *black.to_tuple())
    #         squareWhite = hsvCrop.shape[0] * hsvCrop.shape[1]

    #         x, y, w, h = cv2.boundingRect(cnt)

    #         cv2.rectangle(draw, (x, y), (x+w, y+h), (255, 0, 0), 3)
    #         area = cv2.countNonZero(blackBin)
    #         ratio = squareWhite / area if area != 0 else 0
    #         cv2.putText(draw, str(ratio), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0))

    # mur_view.show(frame, 0)
    # mur_view.show(draw, 1)
    cv2.imshow('frame', draw)
    cv2.imshow('mask', thresh)
    cv2.waitKey(1)