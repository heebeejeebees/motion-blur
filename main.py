import cv2
import time

# configs
TOP_PERCENTAGE = 5

# open video file
video = cv2.VideoCapture('assets/sample.mov')

# TODO allow cropping of video

# get metadata
fps = int(video.get(cv2.CAP_PROP_FPS))
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# calculate time start to process
start = time.time()

max_clarity = 0
all_fno_frame = {}

# TODO multithreaded

# process clarity of every frame
for fno in range(0, total_frames):
    video.set(cv2.CAP_PROP_POS_FRAMES, fno)
    _, image = video.read()
    # calculate clarity (the higher, the clearer)
    clarity = cv2.Laplacian(image, cv2.CV_64F).var()
    frame = {'clarity': clarity, 'image': image}
    all_fno_frame[fno] = frame
    # get highest clarity
    if (clarity > max_clarity):
        max_clarity = clarity

# extract multiple frames of similar clarity
allowance_rate = (100 - TOP_PERCENTAGE) / 100
min_clarity = max_clarity * allowance_rate
for fno, frame in all_fno_frame.items():
    if (frame['clarity'] > min_clarity):
        cv2.imwrite(f'output/{fno}.png', frame['image'])

# calculate time end to process
end = time.time()

# log data
print(f"Time elapsed: {round(end - start, 2)}s")
print("Total frames:", total_frames)
print(f"Resolution: {width}x{height}")
print(f"Clarity: {round(min_clarity, 2)} to {max_clarity}")
print("FPS:", fps)
