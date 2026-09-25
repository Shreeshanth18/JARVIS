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
			value = value.split("#", 1)[0].strip().strip('"\'')
			if value and value != "PASTE_NEW_OPENAI_KEY_HERE":
				os.environ.setdefault(name.strip(), value)


load_local_env()

app = QApplication(sys.argv)

hud = JarvisHUD()
core = JarvisCore(hud)

def handle_command(command):
	response = core.process(command)
	if response:
		speak(response)


def speak_ai_response(text, finished):
	failure_markers = ("authentication failed", "no API credits", "rate-limiting", "service returned HTTP", "service is unavailable")
	if finished and not any(marker in text.lower() for marker in failure_markers):
		speak(text)


hud.command_received.connect(handle_command)
hud.ai_response.connect(speak_ai_response)
start_voice(hud)

hud.show()

sys.exit(app.exec_())