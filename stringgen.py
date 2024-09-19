import os
import requests
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()

# Bunny.net Edge Storage configuration
STORAGE_ZONE_NAME = os.getenv("STORAGE_ZONE_NAME")
API_KEY = os.getenv("API_KEY")
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT")
CDN_ENDPOINT = os.getenv("CDN_ENDPOINT")
LUMA_API_KEY = os.getenv("LUMA_API_KEY")

def upload_file(file_path, remote_path):
    with open(file_path, 'rb') as file:
        headers = {
            'AccessKey': API_KEY,
            'Content-Type': 'application/octet-stream'
        }
        url = f"{STORAGE_ENDPOINT}/{STORAGE_ZONE_NAME}/{quote(remote_path)}"
        response = requests.put(url, data=file, headers=headers)
        
        if response.status_code == 201:
            return f"https://sigil.b-cdn.net//{quote(remote_path)}"
        else:
            print(f"Failed to upload {file_path}. Status code: {response.status_code}")
            return None

def upload_photos_from_directory(directory):
    uploaded_urls = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_path = os.path.join(directory, filename)
            remote_path = filename
            url = upload_file(file_path, remote_path)
            if url:
                uploaded_urls.append(url)
                print(f"Uploaded: {url}")
    return uploaded_urls

# Upload all photos from the ./photos directory
photo_directory = "./photos"
uploaded_urls = upload_photos_from_directory(photo_directory)

print("\nAll uploaded photo URLs:")
for url in uploaded_urls:
    print(url)