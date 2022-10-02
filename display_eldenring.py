import cv2
import pytesseract
import numpy as np


cap = cv2.VideoCapture(1)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
width = 1920
height = 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while True:
    ret, frame = cap.read()

    if not ret:
        break
    
    next_text = frame[1015:1040, 155:205]
    cv2.imshow('ELDEN RING', next_text)
    # print(frame.shape)

    if cv2.waitKey(1) == 27:
        break

cap.release()