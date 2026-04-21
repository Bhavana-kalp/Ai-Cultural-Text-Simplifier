import speech_recognition as sr

def speech_to_text() -> str:
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)

        text = recognizer.recognize_google(audio, language="hi-IN")
        return text.strip()

    except sr.WaitTimeoutError:
        return "Listening timed out"
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "API unavailable"