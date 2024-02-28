# A script to delete jobs that are more than 1 day old
import os, time
from app import TEMP_DIR_NAME
from codebase.utils import remove_directory
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A script to remove generation jobs.')
    parser.add_argument('--hours', type=float, help='The age of jobs that should be deleted in hours')

    args = parser.parse_args()

    for job_directory in os.listdir(TEMP_DIR_NAME):
        job_path = os.path.join(TEMP_DIR_NAME, job_directory)
        creation_time = os.path.getmtime(job_path)
        time_delta = (time.time() - creation_time)/(3600)
        if time_delta >= args.hours:
            remove_directory(job_path)
            print(f"Removed {job_directory}")


