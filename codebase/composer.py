import os, math
from codebase.ffmpeg_utils import *

def preprocess_text(text_file, words_per_view=5):
    output = []
    for line in open(text_file, "r", encoding= "utf-8"):
        start, end, text = line.split(":")
        start, end = float(start), float(end)
        duration = end - start
        words = text.split(" ")
        duration_per_word = duration / len(words)
        n_chunks = math.ceil(len(words)/words_per_view)
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

def compose_video(video_dir, audio_dir, text_file, output_file, width, height, hd):

    video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir)]
    audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir)]

    # generate timed captions
    captions_with_time = preprocess_text(text_file)

    # compose audio, video, and text
    ffmpeg_compose(video_files= video_files,
                   width= width,
                   height= height,
                   audio_files= audio_files,
                   captions_with_time= captions_with_time,
                   output_filename=output_file,
                   hd = hd)
    
    # cut concatenated video to audio duration
    complete_duration = captions_with_time[-1]["end_time"] + 1
    ffmpeg_cut(output_file, 0, complete_duration)