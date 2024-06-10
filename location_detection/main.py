# main.py
import os
#from util import process_video_stream
from urllib.parse import urlparse, parse_qs
import pafy

def extract_youtube_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    
    Args:
    - url (str): The YouTube URL.
    
    Returns:
    - str: The video ID.
    """
    parsed_url = urlparse(url)
    if "youtu.be" in parsed_url.netloc:
        # Handles short URLs, e.g., https://youtu.be/VIDEO_ID
        return parsed_url.path.lstrip('/').strip()
    if "www.youtube.com" in parsed_url.netloc:
        # Handles long URLs with parameters, e.g., https://www.youtube.com/watch?v=VIDEO_ID
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    # Return None if the URL format is not recognized
    return None
'''
def process_videos_from_links(file_path):
    with open(file_path, 'r') as file:
        links = [line.strip() for line in file.readlines()]
    for url in links:
        if url:
            video_id = extract_youtube_video_id(url)
            print(f"Processing video: {url} with video ID: {video_id}")
            process_video_stream(url, video_id)
 '''

if __name__ == "__main__":
    # Get the absolute path of the current script file
    current_script_path = os.path.abspath(__file__)
    # Get the directory of the current script
    current_script_dir = os.path.dirname(current_script_path)
    links_file_path = os.path.join(current_script_dir, 'links.txt')
    time_changes = process_videos_from_links(links_file_path)

