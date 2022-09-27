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
    
    # frame = cv2.resize(frame, (800, 450))
    hp1 = 455
    hp2 = 1130
    hp1_end = 340
    hp2_end = 610
    length1 = 185
    length2 = 455
    hp1_image = frame[45:55, 155:hp1_end]
    hp2_image = frame[45:55, 155:hp2_end]
    estimated_remaining_hp = 0
    patience = 10
    p_count = 0

    for i in range(length1):
        avg = 0
        for j in range(10):
            r = hp1_image[j, i][0]
            g = hp1_image[j, i][1]
            b = hp1_image[j, i][2]
            avg = (r + g + b) / 3
        #print(i, avg)
        if i > 2:
            if avg < 40:
                p_count += 1
        
        if p_count > patience:
            print(i / length1)
            break


    
 


    #runes_image = frame[1020:1050, 1715:1868]
    #print(runes_image.shape)
    #runes_image = cv2.resize(runes_image, (154*3, 30*3))
    #runes_held = pytesseract.image_to_string(runes_image,  lang='eng',config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
    #print(runes_held)
    #print(runes_held == "")
    #frame = frame[1020:1050, 1715:1869]
    cv2.imshow('ELDEN RING', hp1_image)
    # print(frame.shape)

    if cv2.waitKey(1) == 27:
        break

cap.release()