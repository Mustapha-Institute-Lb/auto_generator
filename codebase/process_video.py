import os
import ffmpeg
import time

def crop_video_16_9(filename, width, height):
    """
    A function to crop a centeredt 16:9 rectangle from a video ussing ffmpeg
    :param filename: Vidoe file complete path and name. Expecting ".mp4" extension.
    :param width: Video resolution width.
    :param height: Video resolution height.
    :return: Nothing. It overwrites the originial video with a cropped one. 
    :raises Exception: Video resolution < 1080x1920
    .. note:: 
    Example usage:
    >>> crop_video("./video.mp4", 1920, 1080)
    Result: (Nothing)
    """
    expected_width = 1080
    expected_height= 1920

    if (width<expected_width or height<expected_height):
       raise Exception(f"Video resolution should be greater than 1080x1920 passed resolution ({width}, {height})")

    x_offset = (width - expected_width) // 2
    y_offset = (height - expected_height) // 2

    backed_up_filename = filename+".bck"
    os.rename(src=filename, dst=backed_up_filename)
    time.sleep(3)
    ffmpeg.input(filename=backed_up_filename).crop(x=x_offset, y=y_offset, width=expected_width, height=expected_height).output(filename).run()
    os.remove(backed_up_filename)

def generate_video(video_dir, audio_dir, text_file):
    pass