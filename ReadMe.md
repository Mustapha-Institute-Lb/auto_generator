### A codebase to generate quranic videos on the go

#### Installation on Linux
* install python
* install pip
* install venv `python -m pip install virtualenv`
* create a vertual environment `virtualenv .venv`
* activate the envirnoment `source .venv/bin/activate`
* install requirnments `python -m pip install -r requirments.txt`

#### Installation on Windows
* install python
* install pip
* install ffmpeg (you can use choco)
* install venv `python -m pip install virtualenv`
* create a vertual environment `virtualenv .venv`
* activate the envirnoment `.venv\Scripts\activate.bat` (on windows)
* install requirnments `python -m pip install -r requirments.txt`


#### Usage
#### Code Structure

* **fetch_video**: It containes API utilities to fetch videos form pexles.com and download them. 

* **fetch_audio**:  It containes API utilities to fetch ayat audio from islamic network and download them.

* **process_video**: It containes utilities to process videos and combine video parts: video, audio, and text.