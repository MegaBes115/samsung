import cv2 as cv
import pymurapi as mur

auv = mur.mur_init()
mur_view = auv.get_videoserver()
cap0 = cv.VideoCapture(0)

while True:
    ok, frame0 = cap0.read()
    cv.putText(frame0, "cam0", (5,25), cv.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2, cv.LINE_AA)
    mur_view.show(frame0, 1)    
