import os
import cv2
import re
import json

# Saved Run directory from AI
source_dir = 'vods'
# Setup output directory
outdir = 'tree_dataset'
if not os.path.exists(outdir):
    os.mkdir(outdir)
# Load annoations
annotation_file = 'tree_dataset.json'
annotation_dict = {}
if os.path.exists(annotation_file):
    with open(annotation_file, 'r') as f:
        annotation_dict = json.loads(f.read())

def draw_circle(event,x,y,flags,param):
    global num_clicks_per_frame, prev_click_x, prev_click_y, annotation_dict, iteration
    if event == cv2.EVENT_LBUTTONDBLCLK:
        if num_clicks_per_frame == 0:
            cv2.circle(img,(x,y),5,(255,0,0),-1)
            prev_click_x = x
            prev_click_y = y
        else:
            cv2.rectangle(img,(x,y), (prev_click_x, prev_click_y),(255,0,0),5)
            annotation_dict[str(iteration).zfill(10) + '.jpg'] = {'x1': x,
                                                                  'y1': y,
                                                                  'x2': prev_click_x,
                                                                  'y2': prev_click_y}
        num_clicks_per_frame += 1


for file_name in os.listdir(source_dir):
    cap = cv2.VideoCapture(os.path.join(source_dir, file_name))
    cv2.namedWindow('data')
    cv2.setMouseCallback('data', draw_circle)

    pause = False
    num_clicks_per_frame = 0
    prev_click_x = None
    prev_click_y = None
    iteration = 0

    max_frame_num = 0
    for file_name in os.listdir(outdir):
        match = re.search(r"(\d+).jpg", file_name)
        if not match is None:
            myFrameNumber = int(match[1])
            if myFrameNumber > max_frame_num:
                max_frame_num = myFrameNumber

    iteration = max_frame_num

    while True:
        if not pause:
            ret, img = cap.read()
            if not ret:
                break
            original_frame = img.copy()

            prev_click_x = None
            prev_click_y = None
            num_clicks_per_frame = 0
            iteration += 1

            cv2.putText(img, str(iteration).zfill(10) + '.jpg', (1920 - 500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        cv2.imshow('data', img)
        if pause:
            while True:
                cv2.imshow('data', img)
                key = cv2.waitKey(1)
                if key == 32 or key == 27 or key == 13 or key == 10:
                    break
        else:
            key = cv2.waitKey(1)

        if key == 27: # esc
            break
        if key == 32: # space 
            pause = not pause
        if key == 13 or key == 10: # enter/return
            if not str(iteration).zfill(10) + '.jpg' in annotation_dict.keys():
                annotation_dict[str(iteration).zfill(10) + '.jpg'] = { "x1": None,
                                                                    "y1": None,
                                                                    "x2": None,
                                                                    "y2": None }
            cv2.imwrite(os.path.join(outdir, str(iteration).zfill(10) + '.jpg'), original_frame)
            cv2.rectangle(img,(0,0), (1920, 1080),(0,255,0),10)
            with open(annotation_file, 'w') as f:
                json.dump(annotation_dict, f, indent=4)
