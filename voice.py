import threading
import time

import speech_recognition as sr


speaking = threading.Event()


def speak(text):
    def run():
        speaking.set()
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
        finally:
            speaking.clear()

    threading.Thread(target=run, daemon=True).start()


def start_voice(hud):
    recognizer = sr.Recognizer()

    def listen():
        wake_armed = False
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.6)
                hud.set_listening(True)
                while True:
                    try:
                        if speaking.is_set():
                            time.sleep(0.1)
                            continue
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=12)
                        if speaking.is_set():
                            continue
                        command = recognizer.recognize_google(audio).strip()
                        hud.voice_event.emit(f"Heard: {command}")
                        normalized = command.lower()
                        if "jarvis" not in normalized and not wake_armed:
                            hud.voice_event.emit("Waiting for wake word: JARVIS")
                            continue
                        if "jarvis" in normalized:
                            wake_index = normalized.find("jarvis")
                            command = command[wake_index + len("jarvis"):].strip(" ,.!?")
                        if not command:
                            wake_armed = True
                            hud.voice_event.emit("Wake word accepted. Listening for your command...")
                            continue
                        wake_armed = False
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