import datetime
import os
import platform
import random
import subprocess
import webbrowser
from pathlib import Path

import psutil
import pyautogui
import wikipedia

class Features:

    def __init__(self,hud):
        self.hud = hud

    def _result(self, text):
        self.hud.log(text)
        return text

# SYSTEM

    def cpu(self):
        return self._result(f"CPU usage is {psutil.cpu_percent()} percent.")

    def ram(self):
        return self._result(f"Memory usage is {psutil.virtual_memory().percent} percent.")

    def disk(self):
        return self._result(f"Disk usage is {psutil.disk_usage('/').percent} percent.")

# WEB

    def youtube(self):
        webbrowser.open("https://youtube.com")
        return self._result("Opening YouTube.")

    def google(self):
        webbrowser.open("https://google.com")
        return self._result("Opening Google.")

    def github(self):
        webbrowser.open("https://github.com")
        return self._result("Opening GitHub.")

    def gmail(self):
        webbrowser.open("https://mail.google.com")
        return self._result("Opening Gmail.")

# UTILITIES

    def time(self):
        return self._result(datetime.datetime.now().strftime("It is %I:%M %p on %A, %B %d."))

    def random_number(self):
        return self._result(f"Your random number is {random.randint(1, 100)}.")

    def coin(self):
        return self._result(f"The coin landed on {random.choice(['heads', 'tails'])}.")

    def password(self):
        chars="abcdefghijklmnopqrstuvwxyz123456789"
        pwd="".join(random.choice(chars) for i in range(10))
        return self._result(f"Generated password: {pwd}")

# FILE SYSTEM

    def list_files(self):
        items = list(Path.cwd().iterdir())[:12]
        names = ", ".join(item.name for item in items) or "nothing"
        return self._result(f"Items in {Path.cwd()}: {names}.")

    def create_file(self):
        Path("jarvis.txt").touch()
        return self._result(f"Created {Path('jarvis.txt').resolve()}.")

    def read_file(self):
        try:
            with open("jarvis.txt") as f:
                return self._result(f.read() or "jarvis.txt is empty.")
        except OSError as error:
            return self._result(f"I could not read jarvis.txt: {error}")

# FUN

    def joke(self):

        return self._result("I can tell a joke when an AI provider is connected. Try asking me to search the web instead.")

    def fact(self):

        return self._result("I avoid inventing facts locally. Connect an AI provider and ask me a specific question.")

# SCREEN

    def screenshot(self):

        img = pyautogui.screenshot()

        output = Path.cwd() / "screen.png"
        img.save(output)
        return self._result(f"Screenshot saved to {output}.")

# AI SEARCH

    def wiki(self,topic):

        try:
            result = wikipedia.summary(topic,2)
            return self._result(result)
        except Exception as error:
            return self._result(f"Wikipedia search failed: {error}")

    def open_path(self, target):
        path = Path(target).expanduser().resolve()
        if not path.exists():
            return self._result(f"I could not find {path}.")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return self._result(f"Opened {path}.")

    def system_info(self):
        return self._result(
            f"{platform.system()} {platform.release()}, {psutil.cpu_count()} logical cores, "
            f"{round(psutil.virtual_memory().total / 1073741824, 1)} GB RAM."
        )