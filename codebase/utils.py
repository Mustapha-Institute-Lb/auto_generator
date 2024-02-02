import os, requests, json, logging

def request_json(url, headers= {}):
    response = requests.get(url, headers= headers)
    if response.status_code == 200:
        return json.loads(response.content)
    elif response.status_code == 404: 
        logging.error(f"Error: The requested resource doesn't exist. Status code: {response.status_code}")
        logging.info(f"Requested resource: {url}")
        return ""
    else:
        logging.error(f"Error: Unable to fetch resource. Status code: {response.status_code}")
        logging.info(f"Requested resource: {url}")
        return ""

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return True
    elif response.status_code == 404: 
        logging.error(f"Error: The requested resource doesn't exist. Status code: {response.status_code}")
        logging.info(f"Requested resource: {url}")
        return False
    else:
        logging.error(f"Error: Unable to download file. Status code: {response.status_code}")
        logging.info(f"Requested resource: {url}")
        return False

def remove_directory(path):
    try:
        for file_or_dir in os.listdir(path):
            full_path = os.path.join(path, file_or_dir)
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                remove_directory(full_path)
        os.rmdir(path)
        logging.info(f"Directory '{path}' removed.")
    except OSError as e:
        logging.error(f"Error: {e}")

