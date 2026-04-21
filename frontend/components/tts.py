from gtts import gTTS
import tempfile
import os

def text_to_speech(text: str) -> str:
    """
    Convert text to speech and return audio file path
    """
    if not text:
        return None

    tts = gTTS(text=text, lang="hi")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)

    return temp_file.name