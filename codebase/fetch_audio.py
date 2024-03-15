import requests, json, os, logging, time
from codebase.utils import download_file, request_json
from codebase.exceptions import NamedError

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
from pydub import AudioSegment

def get_reciters(with_code=True):
  """
    Fetch all reciters' names and ids from the Islamic Network API.

    Returns:
        A list of dictionaries containing the following keys: ['id', 'name', 'code'].
        code is ommited if with_code is False

    Example:
        # Fetch all reciters' names and ids
        get_reciters()
        Result: [{'id': 1, 'name': 'عبد الباسط عبد الصمد المرتل', 'code': 'ar.abdulbasitmurattal'},
                 {'id': 2, 'name': 'عبد الله بصفر', 'code': 'ar.abdullahbasfar'}, ...]
  """
  content = request_json("https://api.alquran.cloud/v1/edition/format/audio")
  reciters = []
  id=1
  for reciter in content["data"]:
      if reciter["language"] == "ar":
        if with_code:
          reciters+= [{"id": id, "name": reciter["name"], "code": reciter["identifier"]}]
        else:
          reciters+= [{"id": id, "name": reciter["name"]}]
        id+=1
  return reciters

def get_surahs(with_base=True):
  """
    Fetch all surah names and ids from the Islamic Network API.

    Returns:
        A list of dictionaries containing the following keys: ['id', 'name', 'aya_base', 'n_aya'].
        - 'id': Surah ID.
        - 'name': Surah name.
        - 'aya_base': The number of the first verse of the surah out of all Quran verses.
                      (aya_base is omited if with_base is False)
        - 'n_aya': The number of verses in the surah.

    Example:
        # Fetch all surah names and ids
        get_surahs()
        Result: [{'id': 1, 'name': 'سُورَةُ ٱلْفَاتِحَةِ', 'aya_base': 0, 'n_aya': 7},
                 {'id': 2, 'name': 'سُورَةُ البَقَرَةِ', 'aya_base': 7, 'n_aya': 286}, ...]
    """
  content = request_json("https://api.alquran.cloud/v1/meta")
  surahs = []
  id=1
  aya_base= 0
  for surah in content["data"]["surahs"]["references"]:
    if with_base:
      surahs+= [{"id": id, "name": surah["name"], "aya_base": aya_base, "n_aya": surah["numberOfAyahs"]}]
    else:
      surahs+= [{"id": id, "name": surah["name"], "n_aya": surah["numberOfAyahs"]}]
    aya_base+= surah["numberOfAyahs"]
    id+=1
  return surahs

def get_recitations(reciter_number, surah_number, start, end):
  """
    Fetch recitations of specific ayat from the Islamic Network API.

    Parameters:
        reciter_number (int): The id of the reciter. Retrieve reciter IDs using get_reciters().
        surah_number (int): The id of the surah (chapter) containing the ayat.
        start (int): The starting ayah number of the required recitations.
        end (int): The last ayah number of the required recitations.

    Returns:
        dict: A dictionary containing information about the recitations.
            - 'surah': The name of the surah.
            - 'reciter': The name of the reciter.
            - 'recitations': A list of dictionaries with keys 'text' and 'audio_link'.
                - 'text': Arabic text of the ayah.
                - 'audio_link': Link to the audio resource, downloadable using curl.

    Raises:
        FetchError: If there is an issue fetching recitations.
        Exception: If there are validation errors such as invalid reciter or surah IDs,
                   out-of-range ayah numbers, or incorrect order of start and end.

    Example:
        get_recitations(1, 1, 1, 2)
        Result: {'surah': 'سورة الفاتحة', 'reciter': 'عبد الباسط عبد الصمد',
                 'recitations': [{'text': 'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ\n',
                                  'audio_link': 'https://cdn.islamic.network/.../1.mp3'}, ...]}
  """


  # validate surah and reciter id's
  logging.info(f"Getting surahs data")
  surahs = get_surahs()
  logging.info(f"Getting reciters data")
  reciters = get_reciters()
  
  if reciter_number > len(reciters):
    error_message = f"Reciter id ({reciter_number}) should be between (1, {len(reciters)})"
    logging.error(error_message)
    raise NamedError(error_message)
  
  if surah_number > len(surahs):
    error_message = f"Surah id ({surah_number}) should be between (1, {len(surahs)})"
    logging.error(error_message)
    raise NamedError(error_message)

  reciter = [reciter for reciter in get_reciters() if reciter["id"] == reciter_number][0]

  # validate aya numbers
  surah = [surah for surah in surahs if surah["id"]==surah_number][0]
  if end > surah["n_aya"]:
    message = f"For {surah['name']} end aya ({end}) should be less than ({surah['n_aya']})"
    logging.error(message)
    raise NamedError(message)
  if start < 1:
    message = f"Start aya ({start}) can't be less than one"
    logging.error(message)
    raise NamedError(message)
  if end < start:
    message= f"End aya ({end}) can't be less than start aya ({start})"
    logging.error(message)
    raise NamedError(message)
  
  # from aya number per surah to aya number per quran
  required_ayat= []
  for n in range(start, end+1):
    required_ayat+= [ n + surah["aya_base"] ]

  # remove bismillah
  remove_bismillah = True if((not surah_number==1) and (start==1)) else False
  logging.debug(f"Remove Basmalah: {remove_bismillah}")


  # fetch ayat
  recitations = []
  for i, aya in enumerate(required_ayat):
    audio_link = "https://cdn.islamic.network/quran/audio/192/" + str(reciter["code"]) + "/" + str(aya) + ".mp3"
    logging.info(f"Getting recitation {audio_link}")
    text_response = request_json(f"https://api.alquran.cloud/v1/ayah/{str(aya)}")
    
    if(not text_response):
      error_message = f"Error in fetching text of aya number {str(aya)}"
      logging.error(error_message)
      raise NamedError(error_message)
    
    text = text_response["data"]["text"]
    if(i==0 and remove_bismillah):
      text = text.replace("بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ", "")
    recitations+= [{"text": text.strip(), "audio_link": audio_link}]

  return {'surah': surah['name'], 'reciter': reciter["name"] ,'recitations': recitations, }

def download_recitations(recitations, destination, verbose=True):
  """
  Download audios of several recitations to a certain destination using curl.

  Parameters:
      videos (list): Array of links for download.
      destination (str): The designated destination.
      debug (bool, optional): A parameter to debug the output. If True, provides more verbose output.
                            If False (default), output is minimal.

  Returns:
      An array of the downloaded filenames.

  Example:
      download_recitations([link1, link2, ...], "./temp/mp3/")
      Result: ["./temp/mp3/recitation_0.mp3", "./temp/mp3/recitation_1.mp3", ...]
  """

  
  audios = []

  if(not os.path.exists(destination)):
    os.mkdir(destination)

  for i, recitation_link in enumerate(recitations):
    file_path = os.path.join(destination, "recitation_" + str(i) + ".mp3")
    logging.info(f"Downloading recitation {recitation_link}")
    if verbose: print(f"- File {os.path.basename(file_path)}", end=" ")
    sttime = time.time()
    succsess = download_file(recitation_link, file_path)
    if verbose: print(f"{time.time()-sttime:.2f} s")
    if not succsess:
      error_message = f"No recitation available change reciter"
      logging.error(error_message)
      raise NamedError(error_message)
    audios+= [file_path]
  return audios

def recitations_durations(audio_file_names):
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
    if os.path.exists(filename):
      audio = AudioSegment.from_mp3(filename)
      duration_in_seconds = len(audio) / 1000.0
      logging.info(f"Computing {os.path.basename(filename)} duration: {str(duration_in_seconds)}")
      durations += [duration_in_seconds]
    else:
      print("File doesn't exist")
      exit()
  return durations

def generate_ayat_caption_file(ayat_texts, ayat_durations, destination):
  """
  Write ayat text to a text file alongside the timestamp. Similar to subtitles files.

  Parameters:
      ayat_texts (list): Array of ayat Arabic text.
      ayat_durations (list): Array of ayat recitation durations.
      destination (str): Captions filename and path.

  Returns:
      Nothing. Writes a file to the specified destination.

  Example:
      generate_ayat_caption_file(["بسم الله الرحمن الرحيم", ...], [3.44, ...], "./temp/captions.txt")
      Result: (Nothing)
  """

  endocding="utf-8"
  seperator=":"
  
  if(not len(ayat_durations) == len(ayat_texts)):
    raise Exception("Both ayat texts and durations arrays should be of the same size")
  
  file = open(destination, "w", encoding= endocding)
  cummulative_duration= 0
  logging.info("Generating ayat captions file")
  for i in range(0, len(ayat_durations)):
    file.write(f"{cummulative_duration}{seperator}{cummulative_duration+ayat_durations[i]}{seperator}{ayat_texts[i]}\n")
    cummulative_duration+=ayat_durations[i]
  file.close()
  return