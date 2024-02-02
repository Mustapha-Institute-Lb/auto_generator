import os, logging, re
import subprocess

with open("logging.conf", "r") as log_config:
    LOG_FILE = re.findall(r"args=\('([^']+\.[^']+)',", log_config.read(), re.MULTILINE)[0]


def ffmpeg_mp3_mp4_compose(video_file, audio_file, output_file):
    """Combine an audio file and a video file using FFmpeg, trimming the video to match the audio duration.
    Parameters:
        audio_file (str): Path to the audio file (e.g., MP3 file).
        video_file (str): Path to the video file (e.g., MP4 file).
        output_file (str): Path for the output combined video file.
        debug (boolean): print output

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If FFmpeg commands fail.

    Example:
        >>> audio_file = 'path/to/your/audio.mp3'
        >>> video_file = 'path/to/your/video.mp4'
        >>> output_file = 'path/to/your/output.mp4'
        >>> ffmpeg_mp3_mp4_compose(audio_file, video_file, output_file)
        >>> print(f"The combined video is saved at {output_file}.")

    Note:
        Make sure to replace placeholder file paths with actual paths.
        Ensure FFmpeg and FFprobe are installed on your system.
    """

    cmd = [
        'ffmpeg',
        '-hide_banner', 
        '-loglevel', "error", 
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-shortest',
        output_file
    ]

    logging.info(f"Running compose command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return output_file

def ffmpeg_mp4_concat(input_filenames, output_filename):
    """
    Concatenate multiple MP4 video files into a single MP4 file using FFmpeg.

    Parameters:
        input_filenames (list): List of input MP4 video file names to be concatenated.
        output_filename (str): Output file name for the concatenated MP4 video.
        debug (bool, optional): If True, sets the log level to 'error' for more verbose output.
                               If False (default), sets the log level to 'quiet' for minimal output.

    Raises:
        subprocess.CalledProcessError: If the FFmpeg command fails.

    Example:
        # Concatenate three MP4 video files into a single output file
        input_files = ['video1.mp4', 'video2.mp4', 'video3.mp4']
        output_file = 'output_concatenated.mp4'
        ffmpeg_mp4_concat(input_files, output_file)
    """    

    cmd = [
        'ffmpeg',
        '-hide_banner', 
        '-loglevel', "error", 
    ]

    for i, input_file in enumerate(input_filenames):
        cmd.extend(['-i', input_file])
    filter_complex = ''.join([f'[{i}:v:0]' for i in range(len(input_filenames))])
    filter_complex += f'concat=n={len(input_filenames)}:v=1[outv]'
    cmd.extend(['-filter_complex', filter_complex])
    cmd.extend(['-map', '[outv]', output_filename])

    logging.info(f"Running concat command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return output_filename

def ffmpeg_mp3_concat(input_filenames, output_filename):
    """
    Concatenate multiple MP3 audio files into a single MP3 file using FFmpeg.
    
    Parameters:
        input_filenames (list): List of input MP3 audio file names to be concatenated.
        output_filename (str): Output file name for the concatenated MP3 audio.
        debug (bool, optional): If True, sets the log level to 'error' for more verbose output.
                               If False (default), sets the log level to 'quiet' for minimal output.
    
    Raises:
        subprocess.CalledProcessError: If the FFmpeg command fails.

    Example:
        # Concatenate three MP3 audio files into a single output file
        input_files = ['audio1.mp3', 'audio2.mp3', 'audio3.mp3']
        output_file = 'output_concatenated.mp3'
        ffmpeg_mp3_concat(input_files, output_file)
    """    
    
    cmd = [
        'ffmpeg',
        '-hide_banner', 
        '-loglevel', "error", 
        '-i', 'concat:' + '|'.join(input_filenames),
        '-c', 'copy',
        output_filename
    ]

    logging.info(f"Running concat command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return output_filename

def ffmpeg_crop(input_filename, output_filename, x, y, w, h, debug= False):
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
        '-c:a', 'copy',
        output_filename
    ]

    logging.info(f"Running crop command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

    return

def ffmpeg_mp4_timed_text_compose(input_filename, output_filename, timed_texts):
    """
    """
    
    font_file = "./resources/font/amiri.ttf"
    fontsize = 90
    fontcolor = "white"
    x = "(w-text_w)/2" 
    y = "(h-text_h)/2+50"

    cmd = [
    'ffmpeg',
    '-i', input_filename]

    filters = []
    for timed_text in timed_texts:
        filters += [(
            f"drawtext=text='{timed_text['text']}':x={x}:y={y}:fontsize={str(fontsize)}:fontfile={font_file}:"
            f"fontcolor={fontcolor}:enable='between(t,{str(timed_text['start_time'])},{str(timed_text['end_time'])})'"
            #","
            # f"fade=in:st={str(timed_text['start_time'])}:d=1,"
            # f"fade=out:st={str(timed_text['end_time']-2)}:d=1"
        )]
    cmd+= ['-filter_complex', ",".join(filters)]

    cmd += [
        '-c:a', 'copy',
        output_filename
        ]

    logging.info(f"Running text compose command: {' '.join(cmd)}")
    subprocess.run(cmd, stdout= open(LOG_FILE, 'a'), stderr=open(LOG_FILE, 'a'), check=True)

def crop_video_16_9(filename, width, height):
    """
    Crop a centered 16:9 rectangle from a video using FFmpeg.

    Parameters:
        filename (str): Video file complete path and name. Expecting ".mp4" extension.
        width (int): Video resolution width.
        height (int): Video resolution height.
        debug (bool, optional): Debug flag. If True, sets the log level to 'error' for more verbose output.
                               If False (default), sets the log level to 'quiet' for minimal output.

    Returns:
        None. It overwrites the original video with a cropped one.

    Raises:
        Exception: If video resolution is less than 1080x1920.

    Example:
        # Crop a centered 16:9 rectangle from a video with resolution 1920x1080
        crop_video("./video.mp4", 1920, 1080)
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

    ffmpeg_crop(backed_up_filename, filename, x_offset, y_offset, expected_width, expected_height)    

    os.remove(backed_up_filename)