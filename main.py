import ctypes
import cv2
import time
import argparse
from pathlib import Path
import multiprocessing as mp


def add_parse_args():
    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", type=argparse.FileType('r'))
    parser.add_argument("-o", "--outputDirectory", type=Path,
                        help="path for pictures", default="output")
    parser.add_argument("-t", "--threads", type=int,
                        help="no. of threads", default=8)
    parser.add_argument("-p", "--percentage", type=int,
                        help="percentage less of highest clarity found as minimum clarity", default=5)
    return parser.parse_args()


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


def video_to_image(input_file_name, image_queue):
    # open video file
    video = cv2.VideoCapture(input_file_name)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total frames:", total_frames)
    # process clarity of every frame
    for fno in progressbar(range(0, total_frames), "1/2:"):
        video.set(cv2.CAP_PROP_POS_FRAMES, fno)
        success, image = video.read()
        image_queue.put({'fno': fno, 'image': image})


def calc_clarity(image_queue, frame_queue, max_clarity):
    # calculate clarity (the higher, the clearer)
    while True:
        image = image_queue.get()
        clarity = cv2.Laplacian(image['image'], cv2.CV_64F).var()
        frame_queue.put({'fno': image['fno'],
                         'clarity': clarity, 'image': image['image']})
        # get highest clarity
        if (clarity > max_clarity.value):
            max_clarity.value = clarity


def extract_clear_frames(frame_queue, max_clarity, percentage, output_dir):
    # extract multiple frames of similar clarity
    min_clarity = max_clarity.value * (100 - percentage) / 100
    print(
        f"Clarity: {round(min_clarity, 2)} to {round(max_clarity.value, 2)}")
    while True:
        # frame = progressbar(frame_queue.get(), "2/2:")
        frame = frame_queue.get()
        if (frame['clarity'] > min_clarity):
            cv2.imwrite(
                f"{output_dir}/{frame['fno']}.png", frame['image'])


def main():
    p = add_parse_args()

    # calculate time start to process
    start = time.time()

    mp.set_start_method('spawn')
    q1 = mp.Queue()
    p1 = mp.Process(target=video_to_image, args=(
        p.inputFile.name, q1))
    print("p1.start()")
    p1.start()
    max_clarity = mp.Value(ctypes.c_float, 0.0)
    q2 = mp.Queue()
    p2 = mp.Process(target=calc_clarity, args=(q1, q2, max_clarity))
    print("p2.start()")
    p2.start()
    print("p1.join()")
    p1.join()

    p3 = mp.Process(target=extract_clear_frames, args=(
        q2, max_clarity, p.percentage, p.outputDirectory))
    print("p3.start()")
    p3.start()
    print("p2.join()")  # TODO stucks here
    p2.join()
    print("q1.close()")
    q1.close()
    print("p3.join()")
    p3.join()
    print("q2.close()")
    q2.close()

    # calculate time end to process
    end = time.time()
    print(f"Time elapsed: {round(end - start, 2)}s")


if __name__ == '__main__':
    main()
