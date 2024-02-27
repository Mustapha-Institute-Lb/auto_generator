import json, os
from enum import Enum

class GenerationJobStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"

class Status(Enum):
    FAILED = "Failed"
    STARTED = "Started"
    FETCH_AUDIO = "Fetching Audio"
    DOWNLOAD_AUDIO = "Downloading Audio"
    AUDIO_DURATION = "Computing Audio Duration"
    GENERATE_CAPTIONS = "Generating Captions"
    FETCH_VIDEO =  "Fetching Video"
    DOWNLOAD_VIDEO =  "Downloading Video"
    CROP_VIDEOS =  "Cropping Video"
    COMPOSE_VIDEO =  "Composing Video"
    COMPLETED =  "Completed"

status_progress_dict = {
   Status.FAILED: 0,
   Status.STARTED: 0,
   Status.FETCH_AUDIO: 10,
   Status.DOWNLOAD_AUDIO: 20,
   Status.AUDIO_DURATION: 30,
   Status.GENERATE_CAPTIONS: 40,
   Status.FETCH_VIDEO: 50,
   Status.DOWNLOAD_VIDEO: 60,
   Status.CROP_VIDEOS: 70,
   Status.COMPOSE_VIDEO: 80,
   Status.COMPLETED: 100,
}

FILENAME = "status.json"

class StatusUpdater:
    
    def  __init__(self, directory):
        self.status_file_path = os.path.join(directory, FILENAME)
        self.status = None

    def get_status(self):
       return self.status

    def set_status_failed(self, error_message):
       self.status = Status.FAILED
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": error_message}, file)
    
    def set_status_started(self):
       self.status = Status.STARTED
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
    
    def set_status_fetch_audio(self):
       self.status = Status.FETCH_AUDIO
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)

    def set_status_download_audio(self):
       self.status = Status.FETCH_AUDIO
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
    
    def set_status_compute_audio_duration(self):
       self.status = Status.AUDIO_DURATION
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
       
    def set_status_generate_captions(self):
       self.status = Status.GENERATE_CAPTIONS
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)  
    
    def set_status_fetch_video(self):
       self.status = Status.FETCH_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)   

    def set_status_download_video(self):
       self.status = Status.DOWNLOAD_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)   

    def set_status_crop_video(self):
       self.status = Status.CROP_VIDEOS
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
       
    def set_status_compose_video(self):
       self.status = Status.COMPOSE_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
         
    def set_status_completed(self):
       self.status = Status.COMPLETED
       with open(self.status_file_path, "w") as file:
         json.dump({"status": self.status.value,
                  "progress": status_progress_dict[self.status],
                  "message": ""}, file)
       
class StatusReader:
   
    def __init__(self, directory):
        self.status_file = open( os.path.join(directory, FILENAME), "r")

    def get_status(self):
       status = json.load(self.status_file)
       status["status"] = Status(status["status"])
       return status 
    
    def close(self):
       self.status_file.close()
       
    