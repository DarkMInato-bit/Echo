import os
import tempfile
from gtts import gTTS
from playsound import playsound

def play_text_to_speech(text):
    """Converts text to speech, plays it, and cleans up the temporary file."""
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        tts.save(temp_audio_path)
    
    try:
        playsound(temp_audio_path)
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
