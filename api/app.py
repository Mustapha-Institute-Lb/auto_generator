from flask import Flask
from fetch_audio import get_reciters, get_surahs
import uuid, os, logging, logging.config
from enum import Enum

app = Flask(__name__)

class Status(Enum):
    SUCCESS = "success"
    FAIL = "fail"

VERSION= "v1"
TEMP_DIR_NAME = "api_temporary"
logging.config.fileConfig('logging.conf')

TEMP_DIR = os.path.join(os.getcwd(), TEMP_DIR_NAME )
if(not os.path.exists(TEMP_DIR)):
    os.mkdir(TEMP_DIR)


@app.get(f"/{VERSION}/reciters")
def get_reciters_request():
    return get_reciters(with_code=False)

@app.get(f"/{VERSION}/surahs")
def get_surahs_request():
    return get_surahs(with_base=False)

@app.post(f"/{VERSION}/generate")
def post_generate_request():

    try:
        reciter_id = request.form["reciter_id"]
        surah_id = request.form["surah_id"]
        start_aya = request.form["start_aya"]
        end_aya = request.form["end_aya"]

        job_name = uuid.uuid1()
        job_file_path = os.path.join(TEMP_DIR, job_name)
        job_file = open(job_file_path, "w")
        return {"status": Status.SUCCESS, "job_id": job_name}

    except Exception as e:
        return {"status": Status.FAIL, "message": "Job creation failed"} 

@app.get(f"/{VERSION}/job/")
def get_job_request():
    return "<p>Hello, World!</p>"