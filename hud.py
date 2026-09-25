import math
import time

import psutil
from PyQt5.QtCore import QPointF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class JarvisHUD(QWidget):
    command_received = pyqtSignal(str)
    ai_response = pyqtSignal(str, bool)
    voice_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS // PERSONAL INTELLIGENCE")
        self.setMinimumSize(1100, 720)
        self.resize(1480, 880)
        self.setStyleSheet("QWidget { color: #d9faff; font-family: Segoe UI; } QLineEdit { background: #07131c; border: 1px solid #245b67; border-radius: 8px; padding: 14px; color: #e9feff; font-size: 15px; } QPushButton { background: #12a7a0; border: 0; border-radius: 8px; padding: 12px 22px; color: #031215; font-weight: bold; } QPushButton:hover { background: #42d5c5; } QLabel#title { color: #eaffff; font-size: 22px; font-weight: 700; } QLabel#muted { color: #71939a; font-size: 11px; letter-spacing: 1px; } QLabel#reply { color: #e2fbfb; font-size: 17px; }")
        self.phase = 0
        self.command_text = "Awaiting instruction"
        self.response_text = "Systems online. Ask me anything."
        self.voice_state = "VOICE LINK: STANDBY"
        self.history = []
        self._build_controls()
        self.ai_response.connect(self._receive_ai_response)
        self.voice_event.connect(self._show_voice_event)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(50)

    def _build_controls(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(38, 30, 38, 30)
        root.setSpacing(14)
        header = QHBoxLayout()
        title = QLabel("JARVIS")
        title.setObjectName("title")
        header.addWidget(title)
        subtitle = QLabel("PERSONAL INTELLIGENCE SYSTEM  /  ONLINE")
        subtitle.setObjectName("muted")
        header.addWidget(subtitle)
        header.addStretch()
        self.clock_label = QLabel()
        self.clock_label.setObjectName("muted")
        header.addWidget(self.clock_label)
        root.addLayout(header)
        root.addWidget(self._status_strip())
        root.addStretch(1)
        self.response = QLabel(self.response_text)
        self.response.setObjectName("reply")
        self.response.setWordWrap(True)
        self.response.setMinimumHeight(76)
        root.addWidget(self.response)
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask JARVIS to open a site, inspect the system, create a file...")
        self.input.returnPressed.connect(self.submit_text)
        row.addWidget(self.input)
        button = QPushButton("SEND  >")
        button.clicked.connect(self.submit_text)
        row.addWidget(button)
        root.addLayout(row)

    def _status_strip(self):
        strip = QWidget()
        strip.setStyleSheet("background: #07131c; border: 1px solid #173943; border-radius: 10px;")
        row = QHBoxLayout(strip)
        row.setContentsMargins(18, 10, 18, 10)
        self.state_label = QLabel(self.voice_state)
        self.state_label.setObjectName("muted")
        row.addWidget(self.state_label)
        row.addStretch()
        for label in ("LOCAL ACTIONS", "AI STREAM", "VOICE INPUT"):
            item = QLabel("●  " + label)
            item.setStyleSheet("color: #43d5bd; font-size: 11px;")
            row.addWidget(item)
        return strip

    def submit_text(self):
        command = self.input.text().strip()
        if command:
            self.input.clear()
            self.command_received.emit(command)

    def set_activity(self, command):
        self.command_text = command.upper()
        self.voice_state = "PROCESSING REQUEST"
        self.state_label.setText(self.voice_state)
        self.history.append(("YOU", command))
        self.update()

    def log(self, text):
        self.response_text = str(text)
        self.response.setText(self.response_text)
        self.voice_state = "VOICE LINK: READY"
        self.state_label.setText(self.voice_state)
        self.update()

    def _receive_ai_response(self, text, finished):
        if finished:
            self.voice_state = "AI RESPONSE COMPLETE"
        self.response_text = text
        self.response.setText(text)
        self.state_label.setText(self.voice_state)
        self.update()

    def _show_voice_event(self, text):
        self.voice_state = "VOICE INPUT RECEIVED"
        self.state_label.setText(self.voice_state)
        self.command_text = text.upper()
        self.update()

    def set_listening(self, listening):
        self.voice_state = "MICROPHONE: LISTENING" if listening else "VOICE LINK: READY"
        self.state_label.setText(self.voice_state)
        self.update()

    def update_scene(self):
        self.phase = (self.phase + 2) % 3600
        self.clock_label.setText(time.strftime("%H:%M:%S  /  %d %b %Y").upper())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()
        background = QLinearGradient(0, 0, width, height)
        background.setColorAt(0, QColor("#03070c"))
        background.setColorAt(0.55, QColor("#061923"))
        background.setColorAt(1, QColor("#020508"))
        painter.fillRect(self.rect(), background)
        self._draw_grid(painter, width, height)
        self._draw_header(painter, width)
        self._draw_reactor(painter, width * 0.67, height * 0.45)
        self._draw_telemetry(painter, width, height)
        self._draw_side_panel(painter, width, height)

    def _draw_grid(self, painter, width, height):
        painter.setPen(QPen(QColor(20, 100, 116, 42), 1))
        for x in range(0, width, 64):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height, 64):
            painter.drawLine(0, y, width, y)

    def _draw_header(self, painter, width):
        painter.setPen(QColor("#65f4ff"))
        painter.setFont(QFont("Consolas", 12, QFont.Bold))
        painter.drawText(34, 40, "JARVIS / CORE ONLINE")
        painter.setPen(QColor("#77939b"))
        painter.drawText(34, 63, self.voice_state)
        painter.drawText(width - 220, 40, time.strftime("%H:%M:%S"))
        painter.drawText(width - 220, 63, time.strftime("%d %b %Y").upper())

    def _draw_reactor(self, painter, cx, cy):
        radius = min(self.width(), self.height()) * 0.22
        glow = QRadialGradient(QPointF(cx, cy), radius * 1.3)
        glow.setColorAt(0, QColor(24, 190, 210, 70))
        glow.setColorAt(0.55, QColor(12, 90, 120, 25))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius * 1.3, radius * 1.3)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#28d9e8"), 2))
        for ring in (0.48, 0.64, 0.80, 0.96):
            painter.drawEllipse(QPointF(cx, cy), radius * ring, radius * ring)
        painter.setPen(QPen(QColor(100, 240, 255, 170), 3))
        for index in range(24):
            angle = math.radians(self.phase * 0.7 + index * 15)
            inner = radius * (0.99 if index % 2 else 1.05)
            outer = radius * 1.12
            painter.drawLine(QPointF(cx + math.cos(angle) * inner, cy + math.sin(angle) * inner), QPointF(cx + math.cos(angle) * outer, cy + math.sin(angle) * outer))
        painter.setPen(QPen(QColor("#b5fbff"), 2))
        painter.setFont(QFont("Consolas", 20, QFont.Bold))
        painter.drawText(int(cx - radius), int(cy - 8), int(radius * 2), 30, Qt.AlignCenter, "J A R V I S")
        painter.setFont(QFont("Consolas", 9))
        painter.setPen(QColor("#65f4ff"))
        painter.drawText(int(cx - radius), int(cy + 24), int(radius * 2), 20, Qt.AlignCenter, self.command_text[:32])

    def _draw_telemetry(self, painter, width, height):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        painter.setFont(QFont("Consolas", 11))
        values = (("CPU LOAD", cpu), ("MEMORY", ram), ("STORAGE", disk))
        for index, (label, value) in enumerate(values):
            x = 38 + index * 150
            y = height - 116
            painter.setPen(QColor("#77939b"))
            painter.drawText(x, y, label)
            painter.setPen(QColor("#65f4ff"))
            painter.drawText(x, y + 25, f"{value:05.1f}%")
            painter.setPen(QPen(QColor(25, 115, 125), 3))
            painter.drawLine(x, y + 38, x + 112, y + 38)
            painter.setPen(QPen(QColor("#65f4ff"), 3))
            painter.drawLine(x, y + 38, x + int(112 * value / 100), y + 38)
        painter.setPen(QColor(50, 140, 150, 100))
        painter.drawText(width - 245, height - 58, "LOCAL TASK ENGINE // READY")

    def _draw_side_panel(self, painter, width, height):
        painter.setPen(QPen(QColor(30, 80, 91), 1))
        painter.setBrush(QColor(5, 16, 24, 220))
        painter.drawRoundedRect(30, 115, 300, height - 300, 12, 12)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor("#6fe9df"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(52, 150, "ACTIVITY STREAM")
        painter.setPen(QColor("#71939a"))
        painter.setFont(QFont("Segoe UI", 10))
        y = 185
        for speaker, message in self.history[-6:]:
            painter.setPen(QColor("#43d5bd" if speaker == "YOU" else "#779da5"))
            painter.drawText(52, y, speaker)
            painter.setPen(QColor("#c6e7e8"))
            painter.drawText(52, y + 20, message[:32])
            y += 52