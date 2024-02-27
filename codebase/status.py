import json, os
from enum import Enum

class Status(Enum):
    FAILED = (0,"Failed")
    STARTED = (0,"Started")
    FETCH_AUDIO = (10,"Fetching Audio")
    DOWNLOAD_AUDIO = (20,"Downloading Audio")
    AUDIO_DURATION = (30,"Computing Audio Duration")
    GENERATE_CAPTIONS = (40,"Generating Captions")
    FETCH_VIDEO = (50, "Fetching Video")
    DOWNLOAD_VIDEO = (60, "Downloading Video")
    CROP_VIDEOS = (70, "Cropping Video")
    COMPOSE_VIDEO = (80, "Composing Video")
    COMPLETED = (100, "Completed")

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
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message": error_message}, file)
    
    def set_status_started(self):
       self.status = Status.STARTED
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message": ""}, file)
    
    def set_status_fetch_audio(self):
       self.status = Status.FETCH_AUDIO
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)

    def set_status_download_audio(self):
       self.status = Status.FETCH_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)
    
    def set_status_compute_audio_duration(self):
       self.status = Status.AUDIO_DURATION
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)
       
    def set_status_generate_captions(self):
       self.status = Status.GENERATE_CAPTIONS
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)  
    
    def set_status_fetch_video(self):
       self.status = Status.FETCH_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)   

    def set_status_download_video(self):
       self.status = Status.DOWNLOAD_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)   

    def set_status_crop_video(self):
       self.status = Status.CROP_VIDEOS
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)
       
    def set_status_compose_video(self):
       self.status = Status.COMPOSE_VIDEO
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)
         
    def set_status_completed(self):
       self.status = Status.COMPLETED
       with open(self.status_file_path, "w") as file:
         json.dump({"Status": self.status.value[1],
                  "Progress": self.status.value[0],
                  "Message" : ""}, file)
       
class StatusReader:
   
    def __init__(self, directory):
        self.status_file = open( os.path.join(directory, FILENAME), "r")

    def get_status(self):
       status = json.load(self.status_file)
       return status 
    
    def close(self):
       self.status_file.close()
       
    