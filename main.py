import cv2
import time
import argparse
from pathlib import Path


def progressbar(it, prefix=""):
    count = len(it)

    def show(j):
        x = int(60*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(60-x))}] {j}/{count}",
              end='\r', flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True)


def main():
    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", type=argparse.FileType('r'))
    parser.add_argument("-o", "--outputDirectory", type=Path,
                        help="path for pictures", default="output")
    parser.add_argument("-t", "--threads", type=int,
                        help="no. of threads", default=8)
    parser.add_argument("-p", "--percentage", type=int,
                        help="percentage less of highest clarity found as minimum clarity", default=5)
    p = parser.parse_args()

    # calculate time start to process
    start = time.time()

    # open video file
    video = cv2.VideoCapture(p.inputFile.name)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    max_clarity = 0
    processed_frames = []

    # process clarity of every frame
    for fno in progressbar(range(0, total_frames), "1/2:"):
        video.set(cv2.CAP_PROP_POS_FRAMES, fno)
        _, image = video.read()
        # calculate clarity (the higher, the clearer)
        clarity = cv2.Laplacian(image, cv2.CV_64F).var()
        frame = {'fno': fno, 'clarity': clarity, 'image': image}
        processed_frames.append(frame)
        # get highest clarity
        if (clarity > max_clarity):
            max_clarity = clarity

    # extract multiple frames of similar clarity
    allowance_rate = (100 - p.percentage) / 100
    min_clarity = max_clarity * allowance_rate
    for frame in progressbar(processed_frames, "2/2:"):
        if (frame['clarity'] > min_clarity):
            cv2.imwrite(
                f"{p.outputDirectory}/{frame['fno']}.png", frame['image'])

    # calculate time end to process
    end = time.time()

    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # log data
    print(f"Time elapsed: {round(end - start, 2)}s")
    print("Total frames:", total_frames)
    print(f"Resolution: {width}x{height}")
    print(f"Clarity: {round(min_clarity, 2)} to {round(max_clarity, 2)}")
    print("FPS:", fps)


if __name__ == '__main__':
    main()
