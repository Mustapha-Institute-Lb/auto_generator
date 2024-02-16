from codebase import fetch_audio, fetch_video, ffmpeg_utils
from codebase.utils import remove_directory
from codebase.composer import compose_video
import os, time, datetime
from enum import Enum

PERF_LOG_FILE = "./perf.txt"

class Resolution(Enum):
    HD = (1080, 1920)
    SD = (360, 640)

def generate_video(reciter, surah, start, end, hd=False, clean_resources=True, verbose=True, monitor_performance=False):
    """
    Generate a video by combining recitations with matching videos based on certain criteria.

    Parameters:
        reciter (str): Name of the reciter.
        surah (str): Name or number of the Surah.
        start (int): Start Ayat number.
        end (int): End Ayat number.
        hd (bool, optional): If True, generate the video in HD resolution. Default is False (SD resolution).
        clean_resources (bool, optional): If True, clean up temporary resources after video generation. Default is True.
        verbose (bool, optional): If True, print detailed progress information. Default is True.
        monitor_performance (bool, optional): If True, log performance metrics to a file. Default is False.

    Returns:
        None

    Example:
        generate_video("ReciterName", "Al-Fatiha", 1, 7, hd=True)
    """
    # video settings
    video_keyword = "aerial landscape"
    size = Resolution.HD.value if hd else Resolution.SD.value


    # create a temp directory
    temp_dir = os.path.join(os.getcwd(), "generator_temporary")
    if(os.path.exists(temp_dir)):
        remove_directory(temp_dir)
    audio_dir = "mp3"
    video_dir = "mp4"
    captions_filename = "captions.txt"
    output_file = "generated.mp4"
    os.mkdir(temp_dir)

    # create performance file
    monitor_performance_file = None
    if monitor_performance:
        monitor_performance_file = open(PERF_LOG_FILE, "a")
        monitor_performance_file.write(f"\n(time) {datetime.datetime.now()};")

    # fetch recitations
    sttime = time.time()
    state = "fetch recitation"
    if(verbose): print("Fetching recitations")
    audios = fetch_audio.get_recitations(reciter, surah, start, end)
    surah_name = audios["surah"]
    reciter_name = audios["reciter"]
    recitations = audios["recitations"]

    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")  
     

    # download recitations
    sttime = time.time()
    state = "download recitation"
    if(verbose): print("Downloading recitations")
    recitations_files = fetch_audio.download_recitations([r["audio_link"] for r in recitations],\
                                                          os.path.join(temp_dir, audio_dir), verbose)
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")    

    # recitations captions
    recitations_captions = [r["text"] for r in recitations]

    # recitations durations
    sttime = time.time()
    state = "recitation duration"
    if(verbose): print("Computing durations")
    recitations_durations = fetch_audio.recitations_durations(recitations_files)
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")      

    # generate captions file
    sttime = time.time()
    state = "generate captions"
    if(verbose): print("Generating captions")
    fetch_audio.generate_ayat_caption_file(recitations_captions, recitations_durations, os.path.join(temp_dir, captions_filename))
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")   

    # fetch videos
    sttime = time.time()
    state= "fetch videos"
    if(verbose): print("Fetching videos")
    min_duration = sum(recitations_durations)
    blacklist = ["animal", "animals", "cow", "dog", "cat", "human", "person", "woman", "women", "couple", "man", "men", "cross", "church", "people", "mother", "daughter", "son", "sister", "brother", "father"]
    videos = fetch_video.get_videos_conditioned(video_keyword, min_duration, blacklist, size)
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")     
    
    # download videos
    sttime = time.time()
    state = "download videos"
    if(verbose): print("Downloading videos")
    videos_links = [v["link"] for v in videos]
    videos_files = fetch_video.download_videos(videos_links, os.path.join(temp_dir, video_dir), videos)
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")       

    # crop videos
    sttime = time.time()
    state = "crop videos"
    if(verbose): print("Cropping videos")
    for i, video_file in enumerate(videos_files):
        width = videos[i]["width"]
        height = videos[i]["height"]
        sttime_1 = time.time()
        if(verbose): print(f"- File {os.path.basename(video_file)}", end=" ")  
        ffmpeg_utils.crop_video(video_file, width, height, size[0], size[1])
        if(verbose): print(f"{time.time() - sttime_1:.2f} s")
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")      

    # compose video
    sttime = time.time()
    state= "compose video"
    if(verbose): print("Composing final video")
    compose_video(video_dir= os.path.join(temp_dir, video_dir),
                 audio_dir= os.path.join(temp_dir, audio_dir),
                 text_file= os.path.join(temp_dir, captions_filename),
                 title = surah_name,
                 subtitle = reciter_name,
                 output_file= os.path.join(os.getcwd(), output_file),
                 width= size[0],
                 height= size[1],
                 hd= hd)
    
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")    

    if(clean_resources):
        remove_directory(temp_dir)

    if(monitor_performance): monitor_performance_file.close()
