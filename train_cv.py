import os
from pickletools import optimize
import cv2
import json
import numpy as np
import tensorflow as tf


datasetdir = 'tree_dataset'
print(len(os.listdir(datasetdir)))

image = tf.keras.Input(shape=[None, None, 3], name='image')
backbone = tf.keras.applications.MobileNetV2(input_shape=[None, None, 3], include_top=False)(image)
output = tf.keras.layers.Dense(4)(backbone)
model = tf.keras.Model(inputs=image, outputs=output)
model.compile(loss=tf.keras.losses.BinaryCrossentropy, optimizer='adam')
annotation_dict = {}
with open('tree_dataset.json', 'r') as f:
    annotation_dict = json.loads(f.read())

x = []
y = []
for file in os.listdir(datasetdir):
    x.append(cv2.imread(os.path.join(datasetdir, file)))
    if not annotation_dict[file]['x1'] is None:
        shape = x[-1].shape
        x1 = float(annotation_dict[file]['x1']) / shape[1]
        y1 = float(annotation_dict[file]['y1']) / shape[0]
        x2 = float(annotation_dict[file]['x2']) / shape[1]
        y2 = float(annotation_dict[file]['y2']) / shape[0]
        y.append(np.array([x1, y1, x2, y2]).astype(np.float32))
    else:
        y.append(np.array([0, 0, 0, 0]).astype(np.float32))
x = np.array(x)
y = np.array(y)


model.fit(x=x,
          y=y,
          batch_size=4,
          epochs=100,
          validation_split=0.1,
          shuffle=True)
