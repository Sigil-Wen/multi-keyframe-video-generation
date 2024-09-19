
# Luma Labs Multi Image Video Generation Script

This repository contains scripts for generating AI-powered videos using Luma Labs' API. The project focuses on creating smooth transitions between multiple image frames to produce captivating video sequences.

[![Generated video from 6 images](https://share.gifyoutube.com/KzB6Gb.gif)](https://youtube.com/shorts/q-HTApYGdng)

## Features

- Upload images to Bunny.net CDN for easy access (free)
- Generate videos using Luma AI with custom prompts and keyframes
- Parallel processing for efficient video generation
- Concatenate multiple generated videos into a final output

## Prerequisites

- Python 3.7+
- Luma AI API key
- Bunny.net Edge Storage account and API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Sigil-Wen/luma.git
   cd luma
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - `LUMA_API_KEY`: Your Luma AI API key
   - `BUNNY_STORAGE_API_KEY`: Your Bunny.net Edge Storage API key
   - `BUNNY_STORAGE_ZONE_NAME`: Your Bunny.net Storage Zone name

## Usage

1. Place your input images in the `./photos` directory.

2. Run the main script:
   ```
   python stringvideo.py
   ```

3. The script will:
   - Upload your photos to Bunny.net CDN
   - Generate transition videos between each pair of consecutive images
   - Download the generated videos
   - Concatenate all videos into a final output video

4. The final video will be saved as `final_output.mp4` in the project directory.

## Customization

You can modify the `prompt` variable in `stringvideo.py` to change the AI-generated content between keyframes. Experiment with different prompts to achieve various visual effects and transitions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Luma AI](https://lumalabs.ai/) for their powerful video generation API
- [Bunny.net](https://bunny.net/) for their CDN and Edge Storage solutions

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      },
      "frame1": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/12d17326-a7b6-4538-b9b7-4a2e146d4488/video_0_thumb.jpg"
      }
    }
)
