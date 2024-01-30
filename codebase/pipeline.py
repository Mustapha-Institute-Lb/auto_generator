from codebase import fetch_audio, fetch_video, ffmpeg_utils
from codebase.utils import remove_directory
from codebase.composer import compose_video
import os

def generate_video(reciter, surah, start, end, debug):
    
    # video settings
    video_keyword = "landscape"
    min_width = 1080
    min_height = 1920

    # create a temp directory
    temp_dir = os.path.join(os.getcwd(), "generator_temporary")
    if(os.path.exists(temp_dir)):
        remove_directory(temp_dir, debug)
    audio_dir = "mp3"
    video_dir = "mp4"
    captions_filename = "captions.txt"
    output_file = "generated.mp4"
    os.mkdir(temp_dir)

    # fetch recitations
    recitations = fetch_audio.get_recitations(reciter, surah, start, end, debug)

    # download recitations
    recitations_files = fetch_audio.download_recitations([r["audio_link"] for r in recitations],\
                                                          os.path.join(temp_dir, audio_dir),\
                                                              debug)
    
    # recitations captions
    recitations_captions = [r["text"] for r in recitations]

    # recitations durations
    recitations_durations = fetch_audio.recitations_durations(recitations_files, debug)

    # gnerate captions file
    fetch_audio.generate_ayat_caption_file(recitations_captions, recitations_durations, os.path.join(temp_dir, captions_filename), debug= debug)
    
    # fetch videos
    min_duration = sum(recitations_durations)
    blacklist = ["human", "person", "woman", "women", "couple", "man", "men", "cross", "church", "people", "mother", "daughter", "son", "sister", "brother", "father"]
    videos = fetch_video.get_videos_conditioned(video_keyword, min_duration, blacklist, min_width, min_height, debug)

    # download videos
    videos_links = [v["link"] for v in videos]
    videos_files = fetch_video.download_videos(videos_links, os.path.join(temp_dir, video_dir), debug)

    # crop videos
    for i, video_file in enumerate(videos_files):
        width = videos[i]["width"]
        height = videos[i]["height"]
        ffmpeg_utils.crop_video_16_9(video_file, width, height, debug)

    compose_video(os.path.join(temp_dir, video_dir),
                                 os.path.join(temp_dir, audio_dir),
                                 os.path.join(temp_dir, captions_filename),
                                 os.path.join(os.getcwd(), output_file),
                                 debug=debug
                                )
    
    remove_directory(temp_dir, debug)
