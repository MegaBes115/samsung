import cv2 as cv

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    img = cv.imread("/home/mango/Desktop/screenshot.png")
    
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    vals = dict(white=((0, 0, 191.25), (180, 25.5, 255)), lightgrey=((0, 0, 127.5), (255, 255, 191.25)),
                darkgrey=((0, 0, 63.75), (255, 255, 127.5)), black=((0, 0, 0), (255, 255, 63.75)),
                red=((170, 50, 50), (15, 255, 255)), pink=((135, 50, 50), (170, 255, 255)),
                purple=((115, 50, 50), (135, 255, 255)), blue=((100, 50, 50), (115, 255, 255)),
                lblue=((92.5, 50, 50), (100, 255, 255)), green=((60, 50, 50), (92.5, 255, 255)),
                yellow=((25, 50, 50), (60, 255, 255)), orange=((15, 50, 50), (25, 255, 255)),
                )

    maskedimg = cv.inRange(hsv, *vals['white'], None)

    while True:
        for k, v in vals.items():
            maskedimg = cv.inRange(hsv, *v, None) if k != 'red' else cv.inRange(hsv, v[0], (255, 255, 255)) + \
                                                                     cv.inRange(hsv, (0, 50, 50), v[1])
            cv.imshow("", maskedimg)
            cv.waitKey()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
