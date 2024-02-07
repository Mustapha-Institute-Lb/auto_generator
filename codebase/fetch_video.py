import json, os, logging, time
from random import randint
from codebase.utils import download_file, request_json


class MaintainableFetchError(Exception):
    """Custom exception class."""
    pass

def get_pexeles_video(keyword):
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
  data = request_json(query, headers= {'Authorization': api_key})
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
  data = request_json(query, headers= {'Authorization': api_key})
  if(not data):
    print("Problem fetching video:\n\
            (1) Check your network connection")
    exit()
  video = data["videos"][0]

  logging.info(f"Fetched video descriptor: {video['url']}")

  # Generate tags
  url = video['url'][:-1] if video['url'][-1]=="/" else video['url']
  video_title = url.split("/")[-1]
  tags = video_title.split("-")

  logging.info("\n" + json.dumps(video, indent=2) + "\n")

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

def get_videos_conditioned(keyword, required_duration, blacklist, min_width=1080, min_height=1920):
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
    video = get_pexeles_video(keyword)

    if video == {}:
        logging.info("Dismissed a non-valid video")
        continue

    if video["id"] in ids:
        logging.info("Dismissed a non-valid video, id already fetched")
        continue

    if video["width"] < min_width:
        logging.info(f"Dismissed a non-valid video, width {video['width']} is less than min. width {min_width}")
        continue

    if video["height"] < min_height:
        logging.info(f"Dismissed a non-valid video, height {video['height']} is less than min. height {min_height}")
        continue

    blacklisted = set(video["tags"]).intersection(set(blacklist))
    if blacklisted:
        logging.info(f"Dismissed a non-valid video, contains blacklisted words: ({blacklisted})")
        continue

    logging.info(f"Fetched video link {video['link']}")
    ids+= [video["id"]]
    videos+= [video]
    total_duration+= video["duration"]
  return videos

def download_videos(videos_links, destination, verbose=True):
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

  logging.info(f"Downloading videos {str(videos_links)}")
  videos_files = []
  for i, link in enumerate(videos_links):
    file_path = os.path.join(destination, "video_"+str(i)+".mp4")
    logging.info(f"Downloading video {link}")
    if verbose: print(f"- File {os.path.basename(file_path)}", end=" ")
    sttime = time.time()
    succsess = download_file(link, file_path)
    if verbose: print(f"{time.time()-sttime:.2f} s")
    if not succsess: 
      logging.error("Problem downloading video:\n\
             (1) Check your network connection")
      exit()
    videos_files+= [file_path]
  return videos_files