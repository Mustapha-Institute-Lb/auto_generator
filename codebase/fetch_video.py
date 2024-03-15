import json, os, logging, time
from random import randint
from codebase.utils import download_file, request_json
from codebase.exceptions import NamedError

def get_index_smallest_larger_size(of_width, of_height, sizes):
  """
    Get the index of the smallest larger size in a list of sizes compared to the given dimensions.

    Parameters:
        of_width (int): The width to compare against.
        of_height (int): The height to compare against.
        sizes (list): List of tuples where each tuple contains (index, width, height).

    Returns:
        int: Index of the smallest larger size. Returns -1 if no size is larger.

    Example:
        get_index_smallest_larger_size(800, 600, [(1024, 768), (1280, 720), (2, 640, 480)])
    """
  sizes = [(i, w, h) for i,(w, h) in enumerate(sizes)]
  
  # Get Larger
  sizes = [(i, w-of_width, h-of_height) for (i, w, h) in sizes]
  sizes = [(i,w,h) for (i,w,h) in sizes if ((w>0) and (h>0))]
  
  if (sizes == []):
    return -1
  
  # Get Smallest Width
  sizes = [ (i,w,h) for (i,w,h) in sizes if w == min([w for (_, w, _) in sizes])]
  
  # Get Smallest Height
  sizes = [ (i,w,h) for (i,w,h) in sizes if h == min([h for (_, _, h) in sizes])]
  
  return sizes[0][0]

def get_pexeles_video(keyword, width, height):
  """
  Fetch a video from pexels.com using a keyword and with width and height nearest >= to requried size.

  Parameters:
      keyword (str): The keyword associated with the required video. Ex. "nature", "river", "mountain".
      width (int): Pexeles return a pool of sizes. This parameter specify the nearest width.  
      height (int): Pexeles return a pool of sizes. This parameter specify the nearest height.  
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
    error_message = "Problem fetching video"
    logging.error(error_message)
    raise Exception(error_message)
  total_videos = data["total_results"]
  total_pages = total_videos//per_page

  # Get a random page
  page = randint(1, total_pages)

  # Get a random video from the API
  query = base_query + keyword + "&page="+ str(page) +"&per_page=" + str(per_page)
  data = request_json(query, headers= {'Authorization': api_key})
  if(not data):
    error_message = "Problem fetching video"
    logging.error(error_message)
    raise Exception(error_message)
  
  video = data["videos"][0]

  logging.info(f"Fetched video descriptor: {video['url']}")

  # Generate tags
  url = video['url'][:-1] if video['url'][-1]=="/" else video['url']
  video_title = url.split("/")[-1]
  tags = video_title.split("-")

  logging.info("\n" + json.dumps(video, indent=2) + "\n")

  # Select Video with resolution nearest (but larger) to teh required size
  videos_sizes = [ (v["width"], v["height"]) for v in video["video_files"]]
  video_index = get_index_smallest_larger_size(width, height, videos_sizes)
  if video_index==-1:
     logging.info(f"Couldn't find a video with resolution >= ({width}, {height})")
     return {}
  else:
    video_file = video["video_files"][video_index]
    return {"id": video["id"], "duration": video["duration"],
            "width": video_file["width"], "height": video_file["height"],
            "tags": tags, "link": video_file["link"]}

def get_videos_conditioned(keyword, required_duration, blacklist, size):
  """
  Keep on fetching unique videos from pexels.com until their collective duration surpasses a threshold or the required duration, adhering to certain conditions.

  Parameters:
      keyword (str): The keyword associated with the required video. Ex. "nature", "river", "mountain".
      required_duration (int): The required duration.
      blacklist (list, optional): A list of words that shouldn't occur in the video URL.
      size (int, int): The required minimum width and height as a tuple (min_width, min_height).
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
    video = get_pexeles_video(keyword, width= size[0], height= size[1])

    if video == {}:
        logging.info("Dismissed a non-valid sized video")
        continue

    if video["id"] in ids:
        logging.info("Dismissed a non-valid video, id already fetched")
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
      error_message = "Problem downloading video"
      logging.error(error_message)
      raise Exception(error_message)
    videos_files+= [file_path]
  return videos_files