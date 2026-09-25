import threading

import speech_recognition as sr


def speak(text):
    def run():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    threading.Thread(target=run, daemon=True).start()


def start_voice(hud):
    recognizer = sr.Recognizer()

    def listen():
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.6)
                hud.set_listening(True)
                while True:
                    try:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=12)
                        command = recognizer.recognize_google(audio).strip()
                        hud.voice_event.emit(f"Heard: {command}")
                        hud.command_received.emit(command)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        continue
                    except sr.RequestError as error:
                        hud.voice_event.emit(f"Speech recognition unavailable: {error}")
                        break
        except (OSError, AttributeError) as error:
            hud.voice_event.emit(f"Microphone unavailable: {error}")
        finally:
            hud.set_listening(False)

    threading.Thread(target=listen, daemon=True).start()