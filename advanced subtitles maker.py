import tkinter as tk
from tkinter import filedialog
import subprocess
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Function to map language names to IBM Watson language codes
def get_language_code(language_name):
    language_map = {
        "korean": "ko-KR",
        "english": "en-US",
        "hindi": "hi-IN",
        "french": "fr-FR",
        "spanish": "es-ES",
        "german": "de-DE",
        "chinese": "zh-CN",
        "japanese": "ja-JP",
        "russian": "ru-RU",
        "italian": "it-IT",
    }
    return language_map.get(language_name.lower(), None)

# Function to convert seconds to the ASS timestamp format
def second_to_timecode(x):
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, millisecond = divmod(x, 1)
    millisecond = int(millisecond * 1000)
    return f'{int(hour):02}:{int(minute):02}:{int(second):02},{int(millisecond):03}'

# Function to extract audio from a video file using FFmpeg
def extract_audio(video_file, audio_file='audio.wav'):
    subprocess.run(['ffmpeg', '-i', video_file, '-ac', '1', audio_file], check=True)
    return audio_file

# Function to use IBM Watson for speech recognition
def transcribe_audio(audio_file, api_key, service_url, model):
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(service_url)

    with open(audio_file, 'rb') as audio:
        result = speech_to_text.recognize(
            audio=audio,
            content_type='audio/wav',
            model=model
        ).get_result()
    return result

# Function to generate styled subtitles in ASS format
def generate_styled_subtitles(video_file, subtitle_file, api_key, service_url, video_language, subtitle_language):
    video_language_code = get_language_code(video_language)
    subtitle_language_code = get_language_code(subtitle_language)

    if not video_language_code or not subtitle_language_code:
        print("Unsupported language. Please enter a supported language.")
        return

    audio_file = extract_audio(video_file)
    transcription_model = f'{video_language_code}_BroadbandModel'
    transcription_result = transcribe_audio(audio_file, api_key, service_url, transcription_model)

    # ASS header with custom style
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,0,2,20,20,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(subtitle_file, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        for result in transcription_result['results']:
            for alternative in result['alternatives']:
                start_time = second_to_timecode(alternative['start_time'])
                end_time = second_to_timecode(alternative['end_time'])
                text_line = alternative['transcript']
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0000,0000,0000,,{text_line}\n")

# GUI creation function
def create_gui():
    window = tk.Tk()
    window.title("Subtitle Generator")

    # GUI elements (labels, entries, buttons)

    # Video File Path
    tk.Label(window, text="Video File Path:").grid(row=0)
    video_path_entry = tk.Entry(window, width=50)
    video_path_entry.grid(row=0, column=1)
    tk.Button(window, text="Browse", command=lambda: select_file(video_path_entry)).grid(row=0, column=2)

    # API Key
    tk.Label(window, text="IBM API Key:").grid(row=1)
    api_key_entry = tk.Entry(window, width=50)
    api_key_entry.grid(row=1, column=1)

    # Service URL
    tk.Label(window, text="IBM Service URL:").grid(row=2)
    service_url_entry = tk.Entry(window, width=50)
    service_url_entry.grid(row=2, column=1)

    # Video Language Dropdown
    tk.Label(window, text="Video Language:").grid(row=3)
    video_language_var = tk.StringVar(window)
    video_language_var.set("english")  # default value
    video_language_options = ["korean", "english", "hindi", "french", "spanish", "german", "chinese", "japanese", "russian", "italian"]
    video_language_menu = tk.OptionMenu(window, video_language_var, *video_language_options)
    video_language_menu.grid(row=3, column=1)

    # Subtitle Language Dropdown
    tk.Label(window, text="Subtitle Language:").grid(row=4)
    subtitle_language_var = tk.StringVar(window)
    subtitle_language_var.set("english")  # default value
    subtitle_language_menu = tk.OptionMenu(window, subtitle_language_var, *video_language_options)
    subtitle_language_menu.grid(row=4, column=1)

    # Generate Button
    tk.Button(window, text="Generate Subtitles", command=lambda: generate_styled_subtitles(
        video_path_entry.get(), 'styled_subtitles.ass', api_key_entry.get(), service_url_entry.get(), video_language_var.get(), subtitle_language_var.get()
    )).grid(row=5, columnspan=3)

    window.mainloop()

def select_file(entry_field):
    file_path = filedialog.askopenfilename()
    entry_field.delete(0, tk.END)
    entry_field.insert(0, file_path)

# ... Rest of the functions ...

if __name__ == "__main__":
    create_gui()

