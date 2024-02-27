from flask import Flask
from fetch_audio import get_reciters, get_surahs

app = Flask(__name__)

VERSION= "v1"

@app.route(f"/{VERSION}/reciters")
def get_reciters_request():
    return get_reciters()

@app.route(f"/{VERSION}/surahs")
def get_surahs_request():
    return get_surahs()

@app.route(f"/{VERSION}/generate")
def post_generate_request():
    return "<p>Hello, World!</p>"

@app.route(f"/{VERSION}/job/")
def get_job_request():
    return "<p>Hello, World!</p>"