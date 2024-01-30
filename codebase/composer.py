import os
from codebase.ffmpeg_utils import *
    
def preprocess_text(text_file, words_per_view=5):
    output = []
    for line in open(text_file, "r", encoding= "utf-8"):
        start, end, text = line.split(":")
        start, end = float(start), float(end)
        duration = end - start
        words = text.split(" ")
        duration_per_word = duration / len(words)
        n_chunks = len(words)//words_per_view + 1
        cumulative_duration = start
        for i in range(0, n_chunks):
            chunk_words = words[(i)*words_per_view:(i+1)*words_per_view]
            chunk_duration = len(chunk_words) * duration_per_word
            text = ' '.join(chunk_words)
            output.append({"start_time": cumulative_duration,
                            "end_time": cumulative_duration + chunk_duration,
                            "text": text})
            cumulative_duration = cumulative_duration + chunk_duration
    return output

def compose_video(video_dir, audio_dir, text_file, output_file, debug= False):

    video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir)]
    audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir)]

    video_file = ffmpeg_mp4_concat(video_files, os.path.join(video_dir,"video.mp4"), debug)
    audio_file = ffmpeg_mp3_concat(audio_files, os.path.join(audio_dir,"audio.mp3"), debug)

    # audio_file = os.path.join(audio_dir, "audio.mp3")
    # video_file = os.path.join(video_dir, "video.mp4")

    intermediate_file = "./intermediate.mp4"
    ffmpeg_mp3_mp4_compose(video_file, audio_file, intermediate_file, debug)

    timed_texts = preprocess_text(text_file)
    ffmpeg_mp4_timed_text_compose(intermediate_file, output_file, timed_texts, debug)

    os.remove(intermediate_file)