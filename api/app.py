import sys
sys.path.append("..")

from flask import Flask, request
from codebase.fetch_audio import get_reciters, get_surahs
from codebase.pipeline import generate_video
import uuid, os, logging, logging.config
from threading import Thread
from enum import Enum

app = Flask(__name__)

class Status(str, Enum):
    SUCCESS = "Success"
    FAIL = "Fail"

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
        reciter_id = int(request.form["reciter_id"])
        surah_id = int(request.form["surah_id"])
        start_aya = int(request.form["start_aya"])
        end_aya = int(request.form["end_aya"])

        job_name = str(uuid.uuid1())
        job_dir_path = os.path.join(TEMP_DIR, job_name)
        job_dir = os.mkdir(job_dir_path)

        thread = Thread(target=generate_video,
                        args=(reciter_id, surah_id, start_aya, end_aya, job_dir_path))
        thread.start()

        return {"status": Status.SUCCESS, "job_id": job_name}

    except KeyError as e:
        logging.error(e.args)
        return {"status": Status.FAIL, "message": "Wrong or missing body param"} 

    except Exception as e:
        logging.error(e.args)
        return {"status": Status.FAIL, "message": "Job creation failed"} 

@app.get(f"/{VERSION}/job/")
def get_job_request():
    return "<p>Hello, World!</p>"