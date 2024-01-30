import json, os
from random import randint
from codebase.utils import download_file, request_json

LOG_FILE= "./log.txt"

class MaintainableFetchError(Exception):
    """Custom exception class."""
    pass

def get_pexeles_video(keyword, debug=False):
  """
  Fetch a video from pexels.com using a keyword.

  Parameters:
      keyword (str): The keyword associated with the required video. Ex. "nature", "river", "mountain".
      debug (bool, optional): A parameter to debug the output. If True, provides more verbose output.
                            If False (default), output is minimal.

  Returns:
      A video dictionary containing the following keys: ['id', 'duration', 'width', 'height', 'link', 'tags'].
      - 'id': Video ID.
      - 'duration': Duration of the video.
      - 'width': Width of the video.
      - 'height': Height of the video.
      - 'link': HTTP link to the video resource that can be downloaded.
      - 'tags': Words occurring in the pexels-link.

  Raises:
      Error: If there is an issue fetching the video.

  Example:
      get_pexels_video("mountain")
      Result: {'id': 6528623, 'duration': 44, 'width': 3840, 'height': 2160, 'link': 'https://player.vimeo.com/external/501600816.hd.mp4?s=82...',
              'tags': ['mountain', ...]}
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

  # Generate tags
  url = video['url'][:-1] if video['url'][-1]=="/" else video['url']
  video_title = url.split("/")[-1]
  tags = video_title.split("-")

  if debug:
    with open(LOG_FILE, "a") as f:
      f.write("\n")
      f.write(json.dumps(video, indent=2))
      f.write("\n")

  # Get the largest "HD" file
  sizes = [v["height"] for v in video["video_files"]]
  max_index = [ i for i,s in enumerate(sizes) if s == max(sizes)][0]
  video_file = video["video_files"][max_index]
  result= {}
  if(video_file["quality"] == "hd"):
    result= {"id": video["id"], "duration": video["duration"],
             "width": video_file["width"], "height": video_file["height"],
             "tags": tags, "link": video_file["link"]}
  return result

def get_videos_conditioned(keyword, required_duration, blacklist, min_width=1080, min_height=1920, debug=False):
  """
  Keep on fetching unique videos from pexels.com until their collective duration surpasses a threshold or the required duration, adhering to certain conditions.

  Parameters:
      keyword (str): The keyword associated with the required video. Ex. "nature", "river", "mountain".
      required_duration (int): The required duration.
      blacklist (list, optional): A list of words that shouldn't occur in the video URL.
      min_width (int, optional): The required minimum width.
      min_height (int, optional): The required minimum height.
      debug (bool, optional): A parameter to debug the output. If True, provides more verbose output.
                            If False (default), output is minimal.

  Returns:
      An array of video dictionaries containing the following keys: ['id', 'duration', 'width', 'height', 'link'].
      - 'id': Video ID.
      - 'duration': Duration of the video.
      - 'width': Width of the video.
      - 'height': Height of the video.
      - 'link': HTTP link to the video resource.

  Example:
      get_videos_to_duration("mountain", 30)
      Result: [{... 'duration': 15, ...}, {... 'duration': 20, ...}]
  """

  total_duration= 0
  videos = []
  ids= []
  while(total_duration < required_duration):
    video={}
    video = get_pexeles_video(keyword, debug)

    if video == {}:
        if debug: print("Dismissed a non-valid video")
        continue

    if video["id"] in ids:
        if debug: print("Dismissed a non-valid video, id already fetched")
        continue

    if video["width"] < min_width:
        if debug: print(f"Dismissed a non-valid video, width {video['width']} is less than min. width {min_width}")
        continue

    if video["height"] < min_height:
        if debug: print(f"Dismissed a non-valid video, height {video['height']} is less than min. height {min_height}")
        continue

    blacklisted = set(video["tags"]).intersection(set(blacklist))
    if blacklisted:
        if debug: print(f"Dismissed a non-valid video, contains blacklisted words: ({blacklisted})")
        continue

    if(debug): print(f"Fetched video link {video['link'][:80] + '...'}")
    ids+= [video["id"]]
    videos+= [video]
    total_duration+= video["duration"]
  return videos

def download_videos(videos_links, destination, debug=False):
  """
  Download videos to a certain destination using curl.

  Parameters:
      videos_links (list): Array of links for download.
      destination (str): The designated destination.
      debug (bool, optional): A parameter to debug the output. If True, provides more verbose output.
                            If False (default), output is minimal.

  Returns:
      An array of the downloaded filenames.

  Example:
      download_videos([link1, link2, ...], "./temp/mp4/")
      Result: ["./temp/mp4/video_0.mp4", "./temp/mp4/video_1.mp4", ...]
  """
  if(not os.path.exists(destination)):
    os.mkdir(destination)

  if(debug): print(f"Downloading videos {str(videos_links)[:80]+'...'}")
  videos_files = []
  for i, link in enumerate(videos_links):
    file_path = os.path.join(destination, "video_"+str(i)+".mp4")
    if(debug): print(f"Downloading video {link[:80]+'...'}")
    succsess = download_file(link, file_path, debug)
    if not succsess: 
      print("Problem downloading video:\n\
             (1) Check your network connection")
      exit()
    videos_files+= [file_path]
  return videos_files