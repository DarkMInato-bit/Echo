import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def get_microphone_list(self):
        """Returns list of detected microphone names."""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception:
            return []

    def recognize_speech(self, device_index=None, timeout=5, phrase_time_limit=10, on_status_change=None):
        """
        Listens from the microphone and returns recognized text.
        `on_status_change` is a callback function to update GUI status.
        """
        if on_status_change:
            on_status_change("Starting speech recognition...")

        try:
            with sr.Microphone(device_index=device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                if on_status_change:
                    on_status_change("Listening... Speak now.")
                
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                recognized_text = self.recognizer.recognize_google(audio)
                return recognized_text, None
        except sr.WaitTimeoutError:
            return None, "Listening timed out. No speech was detected."
        except sr.UnknownValueError:
            return None, "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return None, f"Speech recognition service error: {e}"
        except Exception as e:
            return None, f"An error occurred: {e}"
