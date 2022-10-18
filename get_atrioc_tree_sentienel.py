import os
import numpy as np
from pytube import YouTube
from moviepy.editor import *

source_file = 'tree_sentinel.mp4'
if not os.path.exists(source_file):
    yt = YouTube('https://www.youtube.com/watch?v=k-RnQykDyNs')
    video = yt.streams.filter(res='1080p').first()
    out_file = video.download(filename=source_file)

num_segments = 90

source_clip = VideoFileClip(source_file)
clip_duration = int(np.ceil(np.ceil(source_clip.duration) / num_segments))

for i in range(num_segments):
    if (i + 1) * clip_duration < source_clip.duration:
        clip = source_clip.subclip(i * clip_duration, (i + 1) * clip_duration)
        clip.write_videofile(str(i).zfill(2) + ".mp4")
    else:
        clip = source_clip.subclip(i * clip_duration, np.floor(source_clip.duration))
        clip.write_videofile(str(i).zfill(2) + ".mp4")