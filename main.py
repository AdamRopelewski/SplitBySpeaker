import os
import pysrt
from pydub import AudioSegment
import unicodedata
import re
from tkinter import filedialog
import tkinter as tk
import subprocess

AUDIO_EXT = ".wav"
FILE_COUNTER = 0


def get_output_filename():
    global FILE_COUNTER
    FILE_COUNTER += 1
    return f"segment_{FILE_COUNTER}{AUDIO_EXT}"


def process_subtitle(audio, sub, output_dir, padding=0.0):
    """
    Args:
        - padding(int) - how much additional sound to include before and after audio, can be useful for
        audio that is getting clipped.
    """
    start_time = max(0, sub.start.ordinal - padding * 1000)
    end_time = min(len(audio), sub.end.ordinal + padding * 1000)
    segment = audio[start_time:end_time]
    output_filename = get_output_filename()
    output_path = os.path.join(output_dir, output_filename)
    segment.export(output_path, format="wav")
    print(f"Saved segment to {output_path}")


def diarize_audio_with_srt(audio_file, srt_file, output_dir):
    """
    Use whisperx generated SRT files in order to split the audio files with speaker
    numbering and diarization

    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - directory for the outputted files

    """
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)
    for sub in subs:
        speaker = sub.text.split("|")[0]
        sanitized_speaker = sanitize_filename(speaker)
        speaker_dir = os.path.join(output_dir, sanitized_speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        process_subtitle(audio, sub, speaker_dir)


def extract_audio_with_srt(audio_file, srt_file, output_dir):
    """
    Use whisperx generated SRT files in order to split the audio files

    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - drectory for the outputted files
    """
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)
    os.makedirs(output_dir, exist_ok=True)
    for sub in subs:
        process_subtitle(audio, sub, output_dir)


def sanitize_filename(filename):
    # Remove diacritics and normalize Unicode characters
    normalized = unicodedata.normalize("NFKD", filename)
    sanitized = "".join(c for c in normalized if not unicodedata.combining(c))

    # Regular Expression to match invalid characters
    invalid_chars_pattern = r'[<>:"/\\|?*]'

    # Replace invalid characters with an underscore
    return re.sub(invalid_chars_pattern, "_", sanitized)


def select_input_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select input folder").replace("/", "\\")


def process_files(input_folder, srt_file, diarize=False):
    ALLOWED_EXTENTIONS = [
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".m4a",
        "opus",
        ".webm",
        ".mkv",
        ".mp4",
    ]
    output_dir = os.path.join(input_folder, "output")
    os.makedirs(output_dir, exist_ok=True)

    for audio_file in os.listdir(input_folder):
        audio_file_path = os.path.join(input_folder, audio_file)
        if not os.path.isfile(audio_file_path):
            continue
        if not any(audio_file.endswith(ext) for ext in ALLOWED_EXTENTIONS):
            continue
        if not audio_file.endswith(".wav"):
            wav_file_path = os.path.join(
                input_folder, f"{os.path.splitext(audio_file)[0]}{AUDIO_EXT}"
            )
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", audio_file_path, wav_file_path], check=True
                )
                audio_file_path = wav_file_path
            except subprocess.CalledProcessError as e:
                print(f"Failed to convert {audio_file} to WAV\n{e.output}")
                continue

        speaker_segments_dir = os.path.join(output_dir, os.path.splitext(audio_file)[0])
        os.makedirs(speaker_segments_dir, exist_ok=True)
        if diarize:
            diarize_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)
        else:
            extract_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)


def main():
    input_folder = None
    srt_file = None
    diarize = None
    input_folder = select_input_folder()
    srt_file = filedialog.askopenfilename(
        title="Select SRT file", filetypes=[("SRT files", "*.srt")]
    )
    diarize = tk.messagebox.askyesno("Diarize", "Would you like to diarize the audio?")

    print(input_folder, srt_file, diarize)
    if input_folder == "" or srt_file == "":
        tk.messagebox.showerror(
            "Error", "Please select an input folder and SRT file to continue."
        )
        return

    print(input_folder, srt_file, diarize)
    process_files(input_folder, srt_file, diarize)


if __name__ == "__main__":
    main()
