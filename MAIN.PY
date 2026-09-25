import sys
import os
from PyQt5.QtWidgets import QApplication

from hud import JarvisHUD
from brain import JarvisCore
from voice import speak, start_voice


def load_local_env():
	env_path = os.path.join(os.path.dirname(__file__), ".env")
	if not os.path.exists(env_path):
		return
	with open(env_path, encoding="utf-8") as env_file:
		for raw_line in env_file:
			line = raw_line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue
			line = line.removeprefix("$env:")
			name, value = line.split("=", 1)
			os.environ.setdefault(name.strip(), value.strip().strip('"\''))


load_local_env()

app = QApplication(sys.argv)

hud = JarvisHUD()
core = JarvisCore(hud)

def handle_command(command):
	response = core.process(command)
	if response:
		speak(response)


def speak_ai_response(text, finished):
	if finished:
		speak(text)


hud.command_received.connect(handle_command)
hud.ai_response.connect(speak_ai_response)
start_voice(hud)

hud.show()

sys.exit(app.exec_())