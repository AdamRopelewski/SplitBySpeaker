# Split by Speaker

This repository processes a given audio or video file by splitting it into segments based on detected speakers and retaining only the parts containing speech. 

## Features
- Splits audio or video into speaker-differentiated segments.
- Saves only segments with detected speech.


## Requirements
- **FFmpeg**: Ensure FFmpeg is installed and available in your system's PATH.
- **Transcript and Diarization (SRT File)**: A pre-prepared `.srt` file containing transcription and speaker diarization is required. 

### Recommended Tool
For generating transcription and diarization, we recommend using [Whisper-WebUI](https://github.com/jhj0517/Whisper-WebUI).

## Purpose
This tool is ideal for creating fast and efficient datasets for AI voice training, such as those used in Retrieval-based Voice Conversion (RVC).


## Usage

1. Run the command: `python main.py`
2. Select the folder containing the audio files.
3. Choose the corresponding `.srt` file for transcription and diarization.
4. Indicate whether the `.srt` file contains diarization and if you want to split the audio by speaker.


**Note**: This project is still in development and may have some unfinished features or bugs.