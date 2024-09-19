import os
from lumaai import LumaAI
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ------------------------------
# Configuration
# ------------------------------

LUMA_API_KEY = os.getenv("LUMA_API_KEY")

client = LumaAI(
    auth_token=LUMA_API_KEY,
)

# Create a generation

generation = client.generations.create(
    prompt="Cyborg doing a backflip",
    keyframes={
      "frame1": {
        "type": "image",
        "url": "https://sigil.b-cdn.net/cyborgb.jpeg"
      }
    }
)

# Get the generation ID
generation_id = generation.id

video_url = ""

print("Waiting for video generation...")
while True:
    generation = client.generations.get(id=generation_id)
    if generation.assets != None:
        if generation.assets.video != None: 
          video_url = generation.assets.video
          print(generation)
          break
    time.sleep(5)  # Wait for 5 seconds before checking again
    print("Polling Again")


print("Video generated. Downloading...")
print(video_url)

response = requests.get(video_url, stream=True)
file_name = f"luma_video_{generation_id}.mp4"

with open(file_name, 'wb') as file:
    file.write(response.content)

print(f"Video downloaded as {file_name}")

