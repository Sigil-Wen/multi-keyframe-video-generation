import os
import time
import requests
from urllib.parse import quote
from lumaai import LumaAI
from moviepy.editor import VideoFileClip, concatenate_videoclips
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# ------------------------------
# Configuration
# ------------------------------

# Bunny.net Edge Storage configuration
STORAGE_ZONE_NAME = os.getenv("STORAGE_ZONE_NAME")
API_KEY = os.getenv("API_KEY")
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT")
CDN_ENDPOINT = os.getenv("CDN_ENDPOINT")
LUMA_API_KEY = os.getenv("LUMA_API_KEY")

# Directory paths
PHOTO_DIRECTORY = "./photos"
GENERATED_VIDEOS_DIRECTORY = "./generated_videos"
FINAL_VIDEO_PATH = "final_output.mp4"

# Ensure the generated videos directory exists
os.makedirs(GENERATED_VIDEOS_DIRECTORY, exist_ok=True)

# LumaAI configuration
client = LumaAI(auth_token=LUMA_API_KEY)

# ------------------------------
# Functions
# ------------------------------

def upload_file(file_path, remote_path):
    with open(file_path, 'rb') as file:
        headers = {
            'AccessKey': API_KEY,
            'Content-Type': 'application/octet-stream'
        }
        url = f"{STORAGE_ENDPOINT}/{STORAGE_ZONE_NAME}/{quote(remote_path)}"
        response = requests.put(url, data=file, headers=headers)
        
        if response.status_code == 201:
            return f"{CDN_ENDPOINT}/{quote(remote_path)}"
        else:
            print(f"Failed to upload {file_path}. Status code: {response.status_code}")
            return None

def upload_photos_from_directory(directory):
    uploaded_urls = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_path = os.path.join(directory, filename)
            remote_path = filename
            url = upload_file(file_path, remote_path)
            if url:
                uploaded_urls.append(url)
                print(f"Uploaded: {url}")
    return uploaded_urls

def initiate_video_generation(prompt, frame1_url, frame2_url):
    # Create a generation
    generation = client.generations.create(
        prompt=prompt,
        keyframes={
            "frame0": {
                "type": "image",
                "url": frame1_url
            },
            "frame1": {
                "type": "image",
                "url": frame2_url
            }
        }
    )
    return generation.id

def poll_generation_status(generation_id):
    while True:
        generation = client.generations.get(id=generation_id)
        if generation.assets is not None and generation.assets.video is not None:
            video_url = generation.assets.video
            print(f"Generation {generation_id} completed. Video URL: {video_url}")
            return video_url
        time.sleep(5)  # Wait for 5 seconds before checking again
        print(f"Polling generation ID: {generation_id} again...")

def download_video(video_url, output_path, generation_id):
    print(f"Downloading video for generation ID: {generation_id} from {video_url}...")
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        file_name = os.path.join(output_path, f"transition_{generation_id}.mp4")
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Video downloaded as {file_name}")
        return file_name
    else:
        print(f"Failed to download video {video_url}. Status code: {response.status_code}")
        return None

def generate_all_videos(prompt, uploaded_photo_urls):
    generated_video_paths = []
    transition_tasks = []

    videogensequence = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Step 1: Initiate all video generation requests
        for i in range(len(uploaded_photo_urls) - 1):
            frame1_url = uploaded_photo_urls[i]
            frame2_url = uploaded_photo_urls[i + 1]
            generation_id = initiate_video_generation(prompt, frame1_url, frame2_url)
            videogensequence.append(generation_id)
            transition_tasks.append((generation_id, frame1_url, frame2_url))
            print(f"Initiated generation ID: {generation_id} for frames {i} and {i+1}")
        
        # Step 2: Poll all generation statuses in parallel
        future_to_gen_id = {executor.submit(poll_generation_status, gen_id): gen_id for gen_id, _, _ in transition_tasks}
        video_urls = {}
        for future in as_completed(future_to_gen_id):
            gen_id = future_to_gen_id[future]
            try:
                video_url = future.result()
                video_urls[gen_id] = video_url
            except Exception as exc:
                print(f"Generation {gen_id} generated an exception: {exc}")
    
    # Step 3: Download all videos concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        download_futures = {
            executor.submit(download_video, url, GENERATED_VIDEOS_DIRECTORY, gen_id): gen_id 
            for gen_id, url in video_urls.items()
        }
        for future in as_completed(download_futures):
            gen_id = download_futures[future]
            try:
                video_path = future.result()
                if video_path:
                    generated_video_paths.append(video_path)
            except Exception as exc:
                print(f"Downloading video for generation {gen_id} generated an exception: {exc}")
    
    return generated_video_paths, videogensequence

def combine_videos(video_paths, output_path):
    print("Combining videos...")
    clips = [VideoFileClip(video) for video in video_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    print(f"Final video saved as {output_path}")

# ------------------------------
# Main Workflow
# ------------------------------

def main():
    # Step 1: Upload photos to Bunny.net
    print("Uploading photos to Bunny.net...")
    uploaded_photo_urls = upload_photos_from_directory(PHOTO_DIRECTORY)
    
    if len(uploaded_photo_urls) < 2:
        print("Need at least two photos to create transition videos.")
        return
    
    # Step 2: Generate transition videos between each pair of photos concurrently
    print("Generating transition videos between photo pairs...")
    prompt = "Smoothly zoom in between two images seamlessly."
    generated_video_paths, videogensequence = generate_all_videos(prompt, uploaded_photo_urls)
    
    if not generated_video_paths:
        print("No videos were generated.")
        return
    
    # Step 3: Combine all generated videos into one final video
    print("Combining all generated videos into a single MP4 file...")

    sorted_generated_video_paths = []

    for gen_id in videogensequence:
       for path in generated_video_paths:
           if gen_id in path:
              sorted_generated_video_paths.append(path)

    combine_videos(sorted_generated_video_paths, FINAL_VIDEO_PATH)
    print("All done!")

if __name__ == "__main__":
    main()