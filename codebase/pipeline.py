from codebase import fetch_audio, fetch_video, ffmpeg_utils
from codebase.utils import remove_directory
from codebase.composer import compose_video
import os, time, datetime

PERF_LOG_FILE = "./perf.txt"

def generate_video(reciter, surah, start, end, clean_resources=True, verbose=True, monitor_performance=False):
    
    # video settings
    video_keyword = "aerial landscape"
    min_width = 1080
    min_height = 1920

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
    recitations = fetch_audio.get_recitations(reciter, surah, start, end)
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
    if(verbose): print(f"Took {time.time()-sttime:.2f} s\n") 
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
    videos = fetch_video.get_videos_conditioned(video_keyword, min_duration, blacklist, min_width, min_height)
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
        ffmpeg_utils.crop_video_16_9(video_file, width, height)
        if(verbose): print(f"{time.time() - sttime_1:.2f} s")
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")      

    # compose video
    sttime = time.time()
    state= "compose video"
    if(verbose): print("Composing final video")
    compose_video(os.path.join(temp_dir, video_dir),
                                 os.path.join(temp_dir, audio_dir),
                                 os.path.join(temp_dir, captions_filename),
                                 os.path.join(os.getcwd(), output_file)
                )
    duration =  time.time() - sttime
    if(verbose): print(f"Took {duration:.2f} s\n")
    if(monitor_performance): monitor_performance_file.write(f"({state}) {duration};")    

    if(clean_resources):
        remove_directory(temp_dir)

    if(monitor_performance): monitor_performance_file.close()
