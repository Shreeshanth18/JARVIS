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
        last_command = ""
        last_command_at = 0.0
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
                        heard_wake_word = "jarvis" in normalized
                        if not heard_wake_word and not wake_armed:
                            hud.voice_event.emit("Waiting for wake word: JARVIS")
                            continue
                        if heard_wake_word:
                            wake_index = normalized.find("jarvis")
                            command = command[wake_index + len("jarvis"):].strip(" ,.!?")
                        if not command:
                            wake_armed = True
                            hud.voice_event.emit("Wake word accepted. Listening for your command...")
                            hud.wake_detected.emit()
                            continue
                        wake_armed = False
                        now = time.monotonic()
                        if command.lower() == last_command and now - last_command_at < 4:
                            hud.voice_event.emit("Duplicate command ignored")
                            continue
                        last_command = command.lower()
                        last_command_at = now
                        hud.command_received.emit(command)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        continue
                    except sr.RequestError as error:
                        hud.voice_event.emit(f"Speech recognition unavailable: {error}")
                        break
                    except Exception as error:
                        hud.voice_event.emit(f"Voice input error: {error}")
                        time.sleep(0.5)
        except (OSError, AttributeError) as error:
            hud.voice_event.emit(f"Microphone unavailable: {error}")
        finally:
            hud.set_listening(False)

    threading.Thread(target=listen, daemon=True).start()