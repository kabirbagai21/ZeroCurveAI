from main import extract_youtube_video_id
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_title(url):

    response = requests.get(url)

    if response.status_code == 200:
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')

        # The title is typically within the <title> tag of the HTML
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.string.replace("- YouTube", "").strip()
            return title
    return None


def retrieve_transcript(url):
    video_id = extract_youtube_video_id(url)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ""
    for entry in transcript_list:
        transcript += entry['text'] + " "

    # Write the transcript to a text file
    with open(f"transcript.txt", "w", encoding='utf-8') as f:
        f.write(transcript)

retrieve_transcript("https://www.youtube.com/watch?v=uQTNBC_ldhs")