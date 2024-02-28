# A script to delete jobs that are more than 1 day old
import os, time
from app import TEMP_DIR_NAME
from codebase.utils import remove_directory

if __name__ == "__main__":
    for job_directory in os.listdir(TEMP_DIR_NAME):
        job_path = os.path.join(TEMP_DIR_NAME, job_directory)
        creation_time = os.path.getmtime(job_path)
        time_delta = (time.time() - creation_time)/(3600*24)
        if time_delta >= 1:
            remove_directory(job_path)
            print(f"Removed {job_directory}")


