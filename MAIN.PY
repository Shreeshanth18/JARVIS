import sys
from PyQt5.QtWidgets import QApplication

from hud import JarvisHUD
from brain import JarvisCore
from voice import speak, start_voice

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