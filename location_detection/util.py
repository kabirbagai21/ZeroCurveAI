# util.py
import cv2
import pafy
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
import numpy as np
import os
import youtube_dl
import subprocess
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the config.py by navigating up to the desired directory
config_dir = os.path.abspath(os.path.join(current_script_dir, '../'))
# Add the config directory to sys.path if it's not already there
if config_dir not in sys.path:
    sys.path.append(config_dir)
import config_main
sys.path.append(os.path.join(config_main.root_dir, 'location_detection', 'image_extracter'))
from image_extracter import run_single as detector

#ACCESSING YOUTUBE VIDEO ONLINE

def get_video_url_with_ytdlp(url):
    # Use yt-dlp to get the video's direct URL in the best mp4 format available
    command = ['yt-dlp', '-f', 'best[ext=mp4]', '--get-url', url]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    video_url = process.stdout.strip()  # Get the direct URL from the command output
    return video_url



#YOUTUBE TRANSCRIPT FUNCTIONS

#Get youtube video transcript
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        return transcript.fetch()
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID {video_id}")
        return []
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {e}")
        return []

#Helps with transcript
def get_combined_transcripts(timestamp, transcript):
    closest_transcript = min(transcript, key=lambda x: abs(x['start'] - timestamp))
    index_of_closest = transcript.index(closest_transcript)
    # Extract the index range for the transcripts before and after
    start_index = max(0, index_of_closest - 3)
    end_index = min(len(transcript), index_of_closest + 400)
    # Get the transcripts before and after
    transcript_here = " ".join([trans['text'] for trans in transcript[start_index:end_index]])
    return transcript_here



#POINTER EXTRACTION AND CROPPING

#Locate mouse pointer in frame
def find_pointer(frame, icons_folder, threshold=0.9):
    """
    Match icons from a folder in the screenshot within an image using template matching.
    Return the first match found.
    """
    matches = []
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    for icon_filename in os.listdir(icons_folder):
        if icon_filename.endswith('.png'):
            icon_path = os.path.join(icons_folder, icon_filename)
            icon = cv2.imread(icon_path, 0)
            icon_w, icon_h = icon.shape[::-1]
            res = cv2.matchTemplate(frame_gray, icon, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):  # Adjust match positions to the full image
                match_pos = (pt[0], pt[1])
                matches.append({'position': match_pos, 'size': (icon_w, icon_h), 'icon_name': icon_filename})
    #return matches #Assuming only one match we need, ok if a bit innacurate
    return matches[0]


#FINAL FUNCTIONS TO MAKE TRAINING DATA

#Final function to detect buttons and pointer in youtube frame
def detect_buttons_in_frame(frame, prev_frame, input_folder, output_folder):
    # Find the pointer in the frame
    pointer_match = find_pointer(frame, os.path.join(config_main.root_dir, 'location_detection/mouse_pointers'), 0.7)
    # Extract the bounding box of the pointer
    pointer_position = pointer_match['position']
    pointer_size = pointer_match['size']
    # Save the cropped frame around the pointer
    cropped_frame = frame[pointer_position[1]-50:pointer_position[1]+pointer_size[1]+50, pointer_position[0]-50:pointer_position[0]+pointer_size[0]+50]
    cropped_image_path = os.path.join(input_folder, f"cropped.png")
    cv2.imwrite(cropped_image_path, cropped_frame)
    # Save the frame as an image
    image_path = os.path.join(input_folder, f"full.png")
    cv2.imwrite(image_path, frame)
    # Save the frame as a post-image
    image_path = os.path.join(input_folder, f"full_pre.png")
    cv2.imwrite(image_path, prev_frame)
    # Call the run_button_detection function
    key_params = {'min-grad':20, 'ffl-block':5, 'min-ele-area':50,
                      'merge-contained-ele':False, 'merge-line-to-paragraph':False, 'remove-bar':True}
    detector.run_button_detection(image_path, output_folder, key_params = key_params)
    key_params = {'min-grad':3, 'ffl-block':5, 'min-ele-area':50,
                      'merge-contained-ele':False, 'merge-line-to-paragraph':False, 'remove-bar':True}
    detector.run_button_detection(cropped_image_path, output_folder, key_params = key_params)
    #test_image_path = "/Users/akshayiyer/Desktop/MS CS Columbia/ZeroCurve AI/ZeroCurve-AI/location_detection/test_images/inputs/sample_image.png"
    #test_output_folder = "/Users/akshayiyer/Desktop/MS CS Columbia/ZeroCurve AI/ZeroCurve-AI/location_detection/test_images/outputs"
    #detector.run_button_detection(test_image_path, test_output_folder, key_params = key_params)


#Reads frames from video and processes them into data
def process_video_stream(url, video_id):
    transcript = get_transcript(video_id)
    video_url = get_video_url_with_ytdlp(url)

    cap = cv2.VideoCapture(video_url)
    ret, prev_frame = cap.read()
    if not ret:
        print("Failed to get the first frame.")
        return
    
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_frame_gray = cv2.GaussianBlur(prev_frame_gray, (21, 21), 0)
    
    time_changes = []

    while True:
        ret, frame = cap.read()
        if cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 > 400:
            if not ret:
                break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            diff_frame = cv2.absdiff(prev_frame_gray, gray_frame)
            _, thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)
            change_ratio = cv2.countNonZero(thresh_frame) / (frame.shape[0] * frame.shape[1])

            if change_ratio > 0.03:  # Arbitrary threshold for "large change"
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                time_changes.append(timestamp)
                transcript_here = get_combined_transcripts( timestamp, transcript)
                # Create the directory for inputs and outputs for this training example if it doesn't exist
                #Make file name smaller
                timestamp = int(timestamp)
                input_folder = os.path.join('data',video_id, str(timestamp),'inputs')
                transcript_file_path = os.path.join(input_folder, 'transcript.txt')
                output_folder = os.path.join('data',video_id, str(timestamp), 'outputs')
                os.makedirs(input_folder, exist_ok=True)
                # Write the final transcript to the file
                with open(transcript_file_path, 'w') as file:
                    file.write(transcript_here)
                detect_buttons_in_frame(frame, prev_frame, input_folder, output_folder)
                    
            prev_frame_gray = gray_frame
            prev_frame = frame
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return time_changes
