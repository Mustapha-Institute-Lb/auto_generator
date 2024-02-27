import sys
sys.path.append("..")

import argparse
from codebase import fetch_audio
from codebase import pipeline
import logging
import logging.config

def generate_video(reciter, surah, start, end, hd, clean_resources, verbose, monitor_performance):
    pipeline.generate_video(reciter, surah, start, end, hd, clean_resources, verbose, monitor_performance= monitor_performance)

def reciters_list():
    reciters = fetch_audio.get_reciters()
    for reciter in reciters:
        print(f"Reciter {reciter['name']} of id {reciter['id']}")

def surahs_list():
    surahs = fetch_audio.get_surahs()
    for surah in surahs:
        print(f"Surah {surah['name']} of id {surah['id']}")

def main():
    parser = argparse.ArgumentParser(description='A script to auto generate quran video mp4 files.')
    parser.add_argument('--mode', choices=['generate_video', 'reciters_list', 'surahs_list', 'help'], help='Choose the mode of operation')

    parser.add_argument('--reciter', type=int, help='The id of the required reciter. Run "reciters_list" to get the list of reciters')
    parser.add_argument('--surah', type=int, help='The id of the required surah. Run "surahs_list" to get teh list of surahs')
    parser.add_argument('--start', type=int, help='The starting aya number to start recitation from')
    parser.add_argument('--end', type=int, help='The final aya number in the required recitation')
    parser.add_argument('--hd', action= 'store_true', default=False, help='Require high definition videos default false')
    parser.add_argument('--silent', action='store_true', default=False, help='Surpress output')
    parser.add_argument('--keep_resources', action='store_true', default=False, help='Keep downloaded temporary files')
    parser.add_argument('--monitor_perf', action='store_true', default=False, help='Write a text file that includes operations times')

    args = parser.parse_args()

    if args.mode == 'help':
        parser.print_help()

    elif args.mode == "reciters_list":
        reciters_list()

    elif args.mode == "surahs_list":
        surahs_list()

    elif args.mode == 'generate_video':
        if args.reciter is None or args.surah is None or args.start is None or args.end is None:
            print("Error: 'generate_video' mode requires --reciter --surah --start and --end parameters. Run 'help' for more details.")
        else:
            generate_video(args.reciter, args.surah, args.start, args.end, args.hd, not args.keep_resources, not args.silent, args.monitor_perf)

if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    main()

