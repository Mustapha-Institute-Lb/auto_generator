import sys
sys.path.append("..")

from flask import Flask, request, send_file
from codebase.fetch_audio import get_reciters, get_surahs
from codebase.pipeline import generate_video, GENERATED_FILENAME
from codebase.status import Status as InternalStatus
from codebase.status import StatusReader as InternalStatusReader
import uuid, os, logging, logging.config
from threading import Thread
from enum import Enum

app = Flask(__name__)

class APIStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    RUNNIG = "Running"
    DONE = "Done"


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
        _ = os.mkdir(job_dir_path)

        thread = Thread(target=generate_video,
                        args=(reciter_id, surah_id, start_aya, end_aya, job_dir_path))
        thread.start()

        return {"status": APIStatus.SUCCESS, "job_id": job_name}

    except KeyError as e:
        logging.error(f"Error {type(e)} args: {e.args}")
        return {"status": APIStatus.FAILED, "message": "Wrong or missing body param"} 

    except Exception as e:
        logging.error(f"Error {type(e)} args: {e.args}")
        return {"status": APIStatus.FAILED, "message": "Job creation failed"} 


@app.get(f"/{VERSION}/job")
# Expects ?id=...
def get_job_status_request():

    try:
        job_id = request.args.get('id')
        job_dir = os.path.join(TEMP_DIR, job_id)
        job_status = InternalStatusReader(job_dir).get_status()

        if job_status["status"] == InternalStatus.NAMED_FAILURE:
            logging.error(f"Internal Error: {job_status['message']}")
            return {"status": APIStatus.FAILED, "message": job_status["message"]} 
        
        elif job_status["status"] == InternalStatus.UNAMED_FAILURE:
            logging.error(f"Internal Error: {job_status['message']}")
            return {"status": APIStatus.FAILED, "message": "Job status retrieval failed"} 

        elif job_status["status"] == InternalStatus.COMPLETED:
            resource_url = f"/{VERSION}/download?id={job_id}"
            return {"status": APIStatus.DONE, "resource": resource_url}
        else:
            return {"status": APIStatus.RUNNIG, "progress": job_status["progress"], "stage": job_status["status"].value}
        
    except KeyError as e:
        logging.error(f"API Error {type(e)} args: {e.args}")
        return {"status": APIStatus.FAILED, "message": "Wrong or missing body param"} 

    except Exception as e:
        logging.error(f"API Error {type(e)} args: {e.args}")
        return {"status": APIStatus.FAILED, "message": "Job status retrieval failed"} 
    
@app.get(f'/{VERSION}/download')
# Expects ?id=...
def download_video():
    try:
        job_id = request.args.get('id')
        job_dir = os.path.join(TEMP_DIR, job_id)
        generated_file = os.path.join(job_dir, GENERATED_FILENAME)
        return send_file(generated_file, mimetype="video/mp4")
    except Exception as e:
        return {"status": APIStatus.FAILED, "message": "File download failed"} 
