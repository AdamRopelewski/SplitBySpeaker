import os
import pysrt
from pydub import AudioSegment
import unicodedata
import re
from tkinter import filedialog, messagebox
import tkinter as tk
import subprocess

AUDIO_EXT = ".wav"
FILE_COUNTER = 0


class FileChooserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio and SRT File Selection")
        self.root.resizable(False, False)

        # Display Instructions Label
        self.instructions = tk.Label(
            root,
            text="Please follow the instructions:\n\n"
            "1. Choose the folder containing your audio files.\n"
            "2. Choose the corresponding SRT file with transcription and diarization (if available).\n"
            "3. Decide if you'd like to use diarization for splitting the audio files by speaker\n"
            "4. Click continue.",
            justify="left",
            padx=10,
            pady=10,
        )
        self.instructions.pack()

        # Button to select input folder
        self.folder_button = tk.Button(
            root, text="Select Folder with Audio Files", command=self.select_folder
        )
        self.folder_button.pack(pady=10)

        # Button to select SRT file
        self.srt_button = tk.Button(
            root, text="Select SRT File", command=self.select_srt
        )
        self.srt_button.pack(pady=10)

        # Button to confirm diarization option
        self.diarization_label = tk.Label(root, text="Diarization Option:")
        self.diarization_label.pack(pady=5)

        # Create a frame to hold the Yes and No buttons next to each other
        self.diarization_frame = tk.Frame(root)
        self.diarization_frame.pack(pady=5)

        self.diarize_yes_button = tk.Button(
            self.diarization_frame, text="Yes", command=lambda: self.set_diarize(True)
        )
        self.diarize_no_button = tk.Button(
            self.diarization_frame, text="No", command=lambda: self.set_diarize(False)
        )

        # Pack both buttons to the left within the frame
        self.diarize_yes_button.pack(side=tk.LEFT, padx=5)
        self.diarize_no_button.pack(side=tk.LEFT, padx=5)

        # Button to continue (initially disabled)
        self.continue_button = tk.Button(
            root, text="Continue", state="disabled", command=self.continue_process
        )
        self.continue_button.pack(pady=10)

        # Result labels
        self.result_label = tk.Label(root, text="", wraplength=450)
        self.result_label.pack(pady=10)

        # Store values for folder, SRT file, and diarization option
        self.input_folder = ""
        self.srt_file = ""
        self.diarize = False

    def select_folder(self):
        self.input_folder = filedialog.askdirectory(
            title="Select Folder with Audio Files"
        )
        if self.input_folder:
            self.result_label.config(text=f"Selected folder: {self.input_folder}")
            self.check_all_selections()

    def select_srt(self):
        self.srt_file = filedialog.askopenfilename(
            title="Select SRT File", filetypes=[("SRT files", "*.srt")]
        )
        if self.srt_file:
            self.result_label.config(text=f"Selected SRT file: {self.srt_file}")
            self.check_all_selections()

    def set_diarize(self, option):
        self.diarize = option
        self.result_label.config(
            text=f"Diarization option: {'Yes' if self.diarize else 'No'}"
        )
        self.check_all_selections()

    def check_all_selections(self):
        if self.input_folder and self.srt_file and self.diarize is not None:
            self.continue_button.config(state="normal")
        else:
            self.continue_button.config(state="disabled")

    def continue_process(self):
        self.root.destroy()

    def get_selections(self):
        return self.input_folder, self.srt_file, self.diarize


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


def GUI():
    # Set up the main window
    root = tk.Tk()

    # Create the FileChooserApp instance
    app = FileChooserApp(root)

    # Run the tkinter main loop
    root.mainloop()

    # After the GUI is closed, print the selections
    input_folder, srt_file, diarize = app.get_selections()
    if input_folder == "" or srt_file == "":
        # tk.messagebox.showerror(
        #     "Error", "Please select an input folder and SRT file to continue."
        # )
        exit()
        # return None, None, None
    return input_folder, srt_file, diarize


def main():
    input_folder, srt_file, diarize = GUI()
    print(input_folder, srt_file, diarize)
    process_files(input_folder, srt_file, diarize)


if __name__ == "__main__":
    main()
