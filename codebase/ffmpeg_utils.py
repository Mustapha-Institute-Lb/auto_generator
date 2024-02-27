import os, logging, re
import subprocess

with open("logging.conf", "r") as log_config:
    LOG_FILE = re.findall(r"args=\('([^']+\.[^']+)',", log_config.read(), re.MULTILINE)[0]

def ffmpeg_crop(input_filename, output_filename, x, y, w, h):
    """
    Crop a video file using FFmpeg.

    Parameters:
        input_filename (str): Input video file name to be cropped.
        output_filename (str): Output file name for the cropped video.
        x (int): X-coordinate for the top-left corner of the crop area.
        y (int): Y-coordinate for the top-left corner of the crop area.
        w (int): Width of the crop area.
        h (int): Height of the crop area.
        debug (bool, optional): If True, sets the log level to 'error' for more verbose output.
                               If False (default), sets the log level to 'quiet' for minimal output.

    Raises:
        subprocess.CalledProcessError: If the FFmpeg command fails.

    Example:
        # Crop a video file with coordinates (100, 50), width 800, and height 600
        input_file = 'input_video.mp4'
        output_file = 'output_cropped.mp4'
        ffmpeg_crop(input_file, output_file, 100, 50, 800, 600)
    """

    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', "error",
        '-i', input_filename,
        '-vf', f'crop={w}:{h}:{x}:{y}',
        '-preset', 'ultrafast',
        '-an',
        output_filename
    ]

    logging.info(f"Running crop command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return

def crop_video(filename, width, height, expected_width, expected_height):
    """
    Crop a video file to the specified dimensions.

    Parameters:
        filename (str): The path to the input video file.
        width (int): The original width of the video.
        height (int): The original height of the video.
        expected_width (int): The desired width after cropping.
        expected_height (int): The desired height after cropping.

    Raises:
        Exception: If the original video resolution is smaller than the expected resolution.

    Returns:
        None

    Example:
        crop_video("input_video.mp4", 1920, 1080, 1280, 720)
    """

    if (width<expected_width or height<expected_height):
       raise Exception(f"Video resolution should be greater than ({expected_width}, {expected_height}) passed resolution ({width}, {height})")

    x_offset = (width - expected_width) // 2
    y_offset = (height - expected_height) // 2

    backed_up_filename = filename+".bck"
    os.rename(src=filename, dst=backed_up_filename)

    ffmpeg_crop(backed_up_filename, filename, x_offset, y_offset, expected_width, expected_height)    

    os.remove(backed_up_filename)

def ffmpeg_compose(video_files, width, height, audio_files, captions_with_time, title, subtitle, output_filename, hd):
    """
    Composes a video by concatenating multiple video and audio files, adding captions,
    title, and subtitle using FFmpeg.

    Parameters:
    - video_files (list): List of input video file paths to be concatenated.
    - width (int): Width of the output video.
    - height (int): Height of the output video.
    - audio_files (list): List of input audio file paths to be concatenated.
    - captions_with_time (list): List of dictionaries containing timed captions.
      Each dictionary should have 'text', 'start_time', and 'end_time' keys.
    - Title: Title on top of the video
    - Subtitle: Under the top of the video
    - output_filename (str): Output file path for the composed video.
    - hd (bool): If True, use HD settings for font size. If False, use SD settings.

    Returns:
    - output_filename (str): Output file path of the composed video.

    Example:
        ffmpeg_compose(["video1.mp4", "video2.mp4"], ["audio1.mp3", "audio2.mp3"],
                        [{"text": "Caption 1", "start_time": 10, "end_time": 15},
                         {"text": "Caption 2", "start_time": 20, "end_time": 25}],
                        "output_video.mp4", hd=True)
    """


    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', "info",
    ]

    # Add input video files to the command
    for input_file in video_files:
        cmd.extend(['-i', input_file])

    # Add input audio files to the command
    for input_file in audio_files:
        cmd.extend(['-i', input_file])

    # Concatenate video streams
    v_filter = ''.join([f'[{i}:v]' for i in range(len(video_files))]) + \
               f'concat=n={len(video_files)}:v=1:a=0[outv]'

    # Concatenate audio streams
    a_filter = ''.join([f'[{i}:a]' for i in range(len(video_files), len(video_files) + len(audio_files))]) + \
               f'concat=n={len(audio_files)}:v=0:a=1[outa]'

    # Combine video and audio streams
    av_filter = v_filter + ";" + a_filter

    # Add black transparent overlay
    overlay_filter = f"color=c=black@0.3:s={width}x{height}:r=1:d=1[outblacked]; [outv][outblacked] overlay [outbg]"

    # Create drawtext filter for each timed caption
    # Configure text overlay parameters
    font_file = "../resources/font/amiri.ttf"
    h1_fontsize = 100 if hd else 33
    h2_fontsize = 30 if hd else 11
    fontcolor = "white"
    centered_x = "(w-text_w)/2"
    caption_y = f"(h-text_h)/2+{100 if hd else 33}"
    title_y = f"{100 if hd else 33}"
    subtitle_y =  f"{300 if hd else 99}"

    drawtexts = []
    for timed_text in captions_with_time:
        drawtexts += [(
            f"drawtext=text='{timed_text['text']}':x={centered_x}:y={caption_y}:fontsize={str(h1_fontsize)}:"
            f"fontfile={font_file}:fontcolor={fontcolor}:"
            f"enable='between(t,{str(timed_text['start_time'])},{str(timed_text['end_time'])})'"
        )]

    # create drawtext filter for title and subtitle
    duration = captions_with_time[-1]["end_time"]

    drawtexts += [(
            f"drawtext=text='{title}':x={centered_x}:y={title_y}:fontsize={str(h1_fontsize)}:"
            f"fontfile={font_file}:fontcolor={fontcolor}:"
            f"enable='between(t,{str(0)},{str(duration)})'"
        )]
    
    drawtexts += [(
            f"drawtext=text='{subtitle}':x={centered_x}:y={subtitle_y}:fontsize={str(h2_fontsize)}:"
            f"fontfile={font_file}:fontcolor={fontcolor}:"
            f"enable='between(t,{str(0)},{str(duration)})'"
        )]


    text_filter = f"[outbg]{','.join(drawtexts)}[outf]"

    # Build the complete FFmpeg command
    cmd += ['-filter_complex', f"{av_filter}; {overlay_filter}; {text_filter}",
            '-map', '[outf]',
            '-map', '[outa]',
            '-preset', 'ultrafast',
            output_filename
            ]

    # Run the FFmpeg command
    logging.info(f"Running compose command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout=open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return output_filename


def ffmpeg_cut(input_filename, start_time, duration):
    """
    Overwrites an input video file by cutting a section and saving it using FFmpeg.

    Parameters:
    - input_filename (str): Input and output video file path.
    - start_time (int or float): Start time in seconds.
    - duration (int or float): Duration of the cut in seconds.

    Returns:
    - input_filename (str): Output file path of the cut video (same as input_filename).
    """

    temp_output_filename = "temp_cut_output.mp4"

    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', "info",
        '-i', input_filename,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-preset', 'ultrafast',
        temp_output_filename
    ]

    # Run the FFmpeg command
    logging.info(f"Running cut command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout=open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    # Move the temporary output file to overwrite the original input file
    os.replace(temp_output_filename, input_filename)

    return input_filename