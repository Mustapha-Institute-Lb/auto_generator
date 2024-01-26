import requests, json, os
from utils import download_file
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
from pydub import AudioSegment


class FetchError(Exception):
    """Custom exception class."""
    pass

def get_reciters():
  """ A function to fetch all reciters names and ids from islamic nework api.
  :return: A list of dictionaries that containes the following: [id, name, code]
  :raises Error:
  .. note:: 
  Example usage:
  >>> get_reciters()
  Result: [{'id': 1,'name': 'عبد الباسط عبد الصمد المرتل', 'code': 'ar.abdulbasitmurattal'}, { 'id':2, 'name': 'عبد الله بصفر', 'code': 'ar.abdullahbasfar'}, ...]
  """
  response = requests.get("https://api.alquran.cloud/v1/edition/format/audio")
  content = json.loads(response.content.decode('utf8').replace("'", '"'))
  reciters = []
  id=1
  for reciter in content["data"]:
      if reciter["language"] == "ar":
        reciters+= [{"id": id, "name": reciter["name"], "code": reciter["identifier"]}]
        id+=1
  return reciters

def get_surahs():
  """ A function to fetch all surah names and ids from islamic nework api.
  :return: A list of dictionaries that containes the following: [id, name, aya_base, n_aya]
           aya_base is the number of the first aya of the surah out of all quran ayat numbers
           n_aya is teh number of ayat in the surah
  :raises Error:
  .. note:: 
  Example usage:
  >>> get_surahs()
  Result: [{'id': 1, 'name': 'سُورَةُ ٱلْفَاتِحَةِ', 'aya_base': 0, 'n_aya': 7}, {'id': 2, 'name': 'سُورَةُ البَقَرَةِ', 'aya_base': 7, 'n_aya': 286}, ..]
  """
  response = requests.get("https://api.alquran.cloud/v1/meta")
  content = json.loads(response.content)
  surahs = []
  id=1
  aya_base= 0
  for surah in content["data"]["surahs"]["references"]:
    surahs+= [{"id": id, "name": surah["name"], "aya_base": aya_base, "n_aya": surah["numberOfAyahs"]}]
    aya_base+= surah["numberOfAyahs"]
    id+=1
  return surahs

def get_recitations(reciter_number, surah_number, start, end, debug=False):
  """ A function to fetch ayat recitations  from islamic nework api.
  :param reciter_number: The id of the reciter approx. 20 reciters can be fetched using get_reciters()
  :param surah_number: The id of the surah
  :param start: The starting aya number of the required recitations
  :param end: The last aya number of the required recitations
  :return: A list of dictionaries that containes the following: [text, audio_link]
           text is aya text in arabic
           audio_link is the link to the audio resource downloadable using curl
  :raises Error:
  .. note:: 
  Example usage:
  >>> get_recitations(1, 1, 1, 2)
  Result: [{'text': 'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ\n', 'audio_link': 'https://cdn.islamic.network/.../1.mp3'}, ...]
  """

  # validate surah and reciter id's
  surahs = get_surahs()
  reciter = [reciter["code"] for reciter in get_reciters() if reciter["id"] == reciter_number][0]
  if not reciter :
    raise FetchError("Reciter id doesnt exist")
  if surah_number not in [surah["id"] for surah in surahs]:
    raise FetchError("Surah id doesnt exist")

  # validate aya numbers
  surah = [surah for surah in surahs if surah["id"]==surah_number][0]
  if end > surah["n_aya"]:
    raise Exception(f"Surah {surah['name']} only contain {surah['n_aya']} ayat. Aya number {end} was required")
  if start < 1:
    raise Exception(f"start can't be less than one")
  if end < start:
    raise Exception(f"end can't be less than start")
  
  # from aya number per surah to aya number per quran
  required_ayat= []
  for n in range(start, end+1):
    required_ayat+= [ n + surah["aya_base"] ]

  # fetch ayat
  recitations = []
  for aya in required_ayat:
    audio_link = "https://cdn.islamic.network/quran/audio/192/" + str(reciter) + "/" + str(aya) + ".mp3"
    if(debug): print(f"Getting recitation {audio_link}")
    text_response = requests.get("https://api.alquran.cloud/v1/ayah/" + str(aya))
    if(text_response.status_code == 200):
      text = json.loads(text_response.content.decode('utf8').replace("'", '"'))["data"]["text"]
    else:
      raise FetchError(f"Error in fetching text of aya number {str(aya)}")
    recitations+= [{"text": text, "audio_link": audio_link}]

  return recitations

def download_recitations(recitations, destination, debug=False):
  """ A function to download audios of several recitations to a certain destination using curl.
  :param videos: Array of links for download
  :param destination: The designated destination
  :param debug: A param to debug the output
  :return: An array of the downloaded filenames
  .. note:: 
  Example usage:
  >>> download_recitations([link1, linke2, ...], "./temp/mp3/")
  Result: ["./temp/mp3/recitation_0.mp3", "./temp/mp3/recitation_1.mp3", ...]
  """
  
  audios = []

  if(not os.path.exists(destination)):
    os.mkdir(destination)

  for i, recitation_link in enumerate(recitations):
    file_path = os.path.join(destination, "recitation_" + str(i) + ".mp3")
    if(debug): print(f"Downloading recitation {recitation_link}")
    succsess = download_file(recitation_link, file_path, debug)
    if not succsess: 
      print("Problem downloading recitation:\n\
             (1) Change reciter and ayat\n\
             (2) Check your network connection")
      exit()
    audios+= [file_path]
  return audios

def recitations_durations(audio_file_names, debug=False):
  """ A function to retrieve audio durations of a list of mp3 files
  :param audio_file_names: Array of complete filenamess
  :return: An array of durations
  .. note:: 
  Example usage:
  >>> audio_durations(["./temp/mp3/recitation_0.mp3", "./temp/mp3/recitation_1.mp3", ...])
  Result: [12.333, 4, 6, ...]
  """
  durations = []
  for filename in audio_file_names:
    if(debug): print(f"Computing {filename} duration: ", end=" ")
    if os.path.exists(filename):
      audio = AudioSegment.from_mp3(filename)
      duration_in_seconds = len(audio) / 1000.0
      if(debug): print(str(duration_in_seconds))
      durations += [duration_in_seconds]
    else:
      print("File doesn't exist")
      exit()
  return durations
