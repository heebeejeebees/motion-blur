import cv2
import time
import argparse
from pathlib import Path
import datetime


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


def calculate_frame_range(total_frames: int, fps: float, time_start: str, time_end: str):
    s = e = '0:00'
    try:
        s = time.strptime(time_start,'%M:%S')
        e = time.strptime(time_end,'%M:%S')
    except (ValueError, TypeError):
      raise Exception("Check your timestamp options and try again.")
    start_fno = int(datetime.timedelta(minutes=s.tm_min,seconds=s.tm_sec).total_seconds() * fps)
    end_secs = datetime.timedelta(minutes=e.tm_min,seconds=e.tm_sec).total_seconds()
    end_fno = int(end_secs * fps) if end_secs != 0 else total_frames
    return range(start_fno, end_fno)


def main():
    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", type=argparse.FileType('r'))
    parser.add_argument("-o", "--outputDirectory", type=Path,
                        help="path for pictures", default="output")
    parser.add_argument("-p", "--percentage", type=int,
                        help="percentage less of highest clarity found as minimum clarity", default=5)
    parser.add_argument("-s", "--start", type=str,
                        help="start of timestamp in mm:ss", default="0:00")
    parser.add_argument("-e", "--end", type=str,
                        help="end of timestamp in mm:ss", default="0:00")
    p = parser.parse_args()

    # calculate time start to process
    start = time.time()

    # open video file
    video = cv2.VideoCapture(p.inputFile.name)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(video.get(cv2.CAP_PROP_FPS))

    max_clarity = 0
    processed_frames = []

    # process clarity of every frame
    for fno in progressbar(calculate_frame_range(total_frames, fps, p.start, p.end), "1/2:"):
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
