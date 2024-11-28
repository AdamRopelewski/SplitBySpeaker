# Split by Speaker

This repository processes audio or video files by splitting them into segments based on detected speakers, retaining only parts containing speech. This is useful for creating datasets for AI training and speech analysis.

## Features
- Automatically splits audio or video files into segments, each differentiated by speaker.
- Retains only segments with detected speech, eliminating silences and non-speech parts.

## Requirements
- **FFmpeg**: Ensure FFmpeg is installed and available in your system's PATH.
- **Transcript and Diarization (SRT File)**: A pre-prepared `.srt` file containing transcription and speaker diarization is required.

### Recommended Tool
For generating transcription and diarization, we recommend using [Whisper-WebUI](https://github.com/jhj0517/Whisper-WebUI), which provides robust speech-to-text and speaker separation.

## Purpose
This tool is designed for creating fast and efficient datasets for AI training, particularly for applications like Retrieval-based Voice Conversion (RVC).

## Usage

1. Run the command: `python main.py`
2. Select the folder containing the audio files.
3. Choose the corresponding `.srt` file for transcription and diarization.
4. Indicate whether the `.srt` file contains diarization and if you want to split the audio by speaker.

**Note**: This project is still in development and may contain unfinished features or bugs.

For RVC training, we recommend using [UVR](https://github.com/Anjok07/ultimatevocalremovergui) with models like MDX-Net (model: voc_ft) to remove any unwanted sounds and enhance the quality of the audio.
