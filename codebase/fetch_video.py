import subprocess, json, os
from random import randint
from utils import download_file, request_json

class MaintainableFetchError(Exception):
    """Custom exception class."""
    pass

def get_pexeles_video(keyword, debug=False):
    """ A function to fetch a video from pexeles.com using a keyword
    :param keyword: The keyword associated with the required video. Ex. "nature", "river", "mountain"
    :param debug: A param to debug the output
    :return: A video dictionary that containes the following: [id, duration, width, height, link] 
             The link attribute containes an http link to the video resource that can be downloaded.
             Or an empty one.
    :raises Error:
    .. note:: 
    Example usage:
    >>> get_pexeles_video("mountain")
    Result: {'id': 6528623, 'duration': 44, 'width': 3840, 'height': 2160, 'link': 'https://player.vimeo.com/external/501600816.hd.mp4?s=82...}
    """

    # Get total number of videos associated with the keyword
    per_page = 1
    api_key = "fpKSq3NBtPzsmv82jJ2ZTDG946ILieYMpYdJx5hwVJjnti7gPCcZSTa9"
    base_query = "https://api.pexels.com/videos/search?query="
    query = base_query + keyword
    data = request_json(query, headers= {'Authorization': api_key}, debug= debug)
    if(not data):
      print("Problem fetching video:\n\
             (1) Check your network connection")
      exit()
    total_videos = data["total_results"]
    total_pages = total_videos//per_page

    # Get a random page
    page = randint(1, total_pages)

    # Get a random video from the API
    query = base_query + keyword + "&page="+ str(page) +"&per_page=" + str(per_page)
    data = request_json(query, headers= {'Authorization': api_key}, debug= debug)
    if(not data):
      print("Problem fetching video:\n\
             (1) Check your network connection")
      exit()
    video = data["videos"][0]

    if debug:
      print(f"Fetched video descriptor: {video['url'][:80]+ '...'}")

    # Get the "HD" file
    result = {}
    for video_file in video["video_files"]:
      if(video_file["quality"] == "hd"):
        result= {"id": video["id"],
                 "duration": video["duration"],
                 "width": video["width"],
                 "height": video["height"],
                 "link": video_file["link"]}
        break
    return result

def get_videos_conditioned(keyword, required_duration, min_width=1080, min_height=1920, debug=False):
  """ A function to keep on fetching unique videos from pexeles.com to until thier collective duration
        surpasses a threshold or the required duration and adhere to some conditions.
  :param keyword: The keyword associated with the required video. Ex. "nature", "river", "mountain"
  :param required_duration: The required duration
  :param min_width: The required minimum width
  :param min_height: The required minuimum height
  :param debug: A param to debug the output
  :return: An array of video dictionaries that containes the following: [id, duration, width, height, link] 
  .. note:: 
  Example usage:
  >>> get_videos_to_duration("mountain", 30)
  Result: [{... 'duration': 15, ...}, {... 'duration': 20, ...}]
  """
  total_duration= 0
  videos = []
  ids= []
  while(total_duration < required_duration):
    video={}
    video = get_pexeles_video(keyword, debug)
    if (video=={} or video["id"] in ids or video["width"]< min_width or video["height"]< min_height):
      if(debug): print("Dismissed a non-valid video")
      continue
    if(debug): print(f"Fetched video link {video['link'][:80] + '...'}")
    ids+= [video["id"]]
    videos+= [video]
    total_duration+= video["duration"]
  return videos

def download_videos(videos_links, destination, debug=False):
  """ A function to download videos to a certain destination using curl.
  :param videos_links: Array of links for download
  :param destination: The designated destination
  :param debug: A param to debug the output
  :return: An array of the downloaded filenames
  .. note:: 
  Example usage:
  >>> download_videos([link1, linke2, ...], "./temp/mp4/")
  Result: ["./temp/mp4/video_0.mp4", "./temp/mp4/video_1.mp4", ...]
  """

  if(not os.path.exists(destination)):
    os.mkdir(destination)

  if(debug): print(f"Downloading videos {str(videos_links)[:80]+'...'}")
  videos_files = []
  for i, link in enumerate(videos_links):
    file_path = destination + "/video_" + str(i) + ".mp4"
    if(debug): print(f"Downloading video {link[:80]+'...'}")
    succsess = download_file(link, file_path, debug)
    if not succsess: 
      print("Problem downloading video:\n\
             (1) Check your network connection")
      exit()
    videos_files+= [file_path]
  return videos_files