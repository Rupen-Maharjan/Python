import sys
import os
import subprocess
import threading
import time
import re
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QFrame, QSplitter,
    QProgressBar, QScrollArea, QGridLayout, QGroupBox, QHeaderView,
    QSizePolicy, QSpacerItem, QCheckBox, QSpinBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSize, pyqtProperty
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QLinearGradient,
    QBrush, QPen, QFontDatabase, QIcon, QKeySequence,
    QRadialGradient, QConicalGradient, QMovie
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import math
import random


PALETTE = {
    "base":        "#1e1e2e",
    "mantle":      "#181825",
    "crust":       "#11111b",
    "surface0":    "#313244",
    "surface1":    "#45475a",
    "surface2":    "#585b70",
    "overlay0":    "#6c7086",
    "overlay1":    "#7f849c",
    "text":        "#cdd6f4",
    "subtext0":    "#a6adc8",
    "subtext1":    "#bac2de",
    "lavender":    "#b4befe",
    "blue":        "#89b4fa",
    "sapphire":    "#74c7ec",
    "sky":         "#89dceb",
    "teal":        "#94e2d5",
    "green":       "#a6e3a1",
    "yellow":      "#f9e2af",
    "peach":       "#fab387",
    "maroon":      "#eba0ac",
    "red":         "#f38ba8",
    "mauve":       "#cba6f7",
    "pink":        "#f5c2e7",
    "flamingo":    "#f2cdcd",
    "rosewater":   "#f5e0dc",
}

CAPTURED_DIR = Path("captured")
CAPTURED_DIR.mkdir(exist_ok=True)

OUI_MAP = {
    "00:50:f2": "Microsoft", "00:0c:e7": "Apple", "00:17:f2": "Apple",
    "ac:de:48": "Apple", "f8:ff:c2": "Apple", "00:1a:11": "Google",
    "94:65:9c": "Samsung", "00:23:76": "Samsung", "78:52:1a": "Samsung",
    "8c:71:f8": "Samsung", "b0:72:bf": "OnePlus", "14:ab:c5": "OnePlus",
    "94:87:e0": "Xiaomi", "f8:a2:d6": "Xiaomi", "50:64:2b": "Xiaomi",
    "00:26:b9": "Sony", "30:17:c8": "Sony", "10:68:3f": "Huawei",
    "48:00:31": "Huawei", "00:1c:bf": "Realtek", "00:0f:b5": "Netgear",
    "c8:3a:35": "Tenda", "18:a6:f7": "TP-Link", "f4:f2:6d": "TP-Link",
    "00:1d:0f": "Asus", "04:92:26": "Asus", "b8:27:eb": "Raspberry Pi",
    "dc:a6:32": "Raspberry Pi", "e4:5f:01": "Raspberry Pi",
}

def oui_lookup(mac):
    if not mac:
        return "Unknown Device"
    prefix = mac[:8].lower()
    return OUI_MAP.get(prefix, "Unknown Device")


STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {PALETTE['base']};
    color: {PALETTE['text']};
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {PALETTE['surface0']};
    background: {PALETTE['base']};
    border-radius: 8px;
}}
QTabBar::tab {{
    background: {PALETTE['mantle']};
    color: {PALETTE['subtext0']};
    padding: 10px 22px;
    border: none;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {PALETTE['surface0']};
    color: {PALETTE['mauve']};
    border-bottom: 2px solid {PALETTE['mauve']};
}}
QTabBar::tab:hover:!selected {{
    background: {PALETTE['surface0']};
    color: {PALETTE['text']};
}}
QPushButton {{
    background: {PALETTE['surface0']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['surface1']};
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {PALETTE['surface1']};
    border-color: {PALETTE['mauve']};
    color: {PALETTE['mauve']};
}}
QPushButton:pressed {{
    background: {PALETTE['surface2']};
}}
QPushButton#primary {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['mauve']},stop:1 {PALETTE['blue']});
    color: {PALETTE['crust']};
    border: none;
    font-weight: 700;
}}
QPushButton#primary:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['pink']},stop:1 {PALETTE['mauve']});
    color: {PALETTE['crust']};
}}
QPushButton#danger {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['red']},stop:1 {PALETTE['maroon']});
    color: {PALETTE['crust']};
    border: none;
    font-weight: 700;
}}
QPushButton#danger:hover {{
    background: {PALETTE['red']};
    color: {PALETTE['crust']};
}}
QPushButton#success {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['green']},stop:1 {PALETTE['teal']});
    color: {PALETTE['crust']};
    border: none;
    font-weight: 700;
}}
QPushButton#warning {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['yellow']},stop:1 {PALETTE['peach']});
    color: {PALETTE['crust']};
    border: none;
    font-weight: 700;
}}
QLineEdit {{
    background: {PALETTE['mantle']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['surface1']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border-color: {PALETTE['mauve']};
}}
QComboBox {{
    background: {PALETTE['mantle']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['surface1']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    min-width: 120px;
}}
QComboBox:focus {{
    border-color: {PALETTE['mauve']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {PALETTE['mauve']};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background: {PALETTE['mantle']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['surface1']};
    selection-background-color: {PALETTE['surface0']};
    selection-color: {PALETTE['mauve']};
}}
QTextEdit {{
    background: {PALETTE['crust']};
    color: {PALETTE['green']};
    border: 1px solid {PALETTE['surface0']};
    border-radius: 6px;
    padding: 10px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    line-height: 1.6;
}}
QTreeWidget {{
    background: {PALETTE['crust']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['surface0']};
    border-radius: 6px;
    alternate-background-color: {PALETTE['mantle']};
    show-decoration-selected: 1;
}}
QTreeWidget::item {{
    padding: 5px 4px;
    border-radius: 4px;
}}
QTreeWidget::item:selected {{
    background: {PALETTE['surface0']};
    color: {PALETTE['mauve']};
}}
QTreeWidget::item:hover {{
    background: {PALETTE['surface0']};
}}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    border-image: none;
    image: none;
}}
QHeaderView::section {{
    background: {PALETTE['mantle']};
    color: {PALETTE['subtext0']};
    padding: 8px 10px;
    border: none;
    border-right: 1px solid {PALETTE['surface0']};
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
}}
QScrollBar:vertical {{
    background: {PALETTE['mantle']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {PALETTE['surface1']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {PALETTE['mauve']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {PALETTE['mantle']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {PALETTE['surface1']};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {PALETTE['mauve']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QGroupBox {{
    border: 1px solid {PALETTE['surface0']};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    font-size: 12px;
    color: {PALETTE['mauve']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {PALETTE['mauve']};
    left: 12px;
}}
QLabel#section {{
    color: {PALETTE['mauve']};
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.5px;
}}
QLabel#badge_green {{
    background: {PALETTE['green']};
    color: {PALETTE['crust']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#badge_red {{
    background: {PALETTE['red']};
    color: {PALETTE['crust']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#badge_yellow {{
    background: {PALETTE['yellow']};
    color: {PALETTE['crust']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#badge_blue {{
    background: {PALETTE['blue']};
    color: {PALETTE['crust']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QFrame#separator {{
    background: {PALETTE['surface0']};
    max-height: 1px;
    border: none;
}}
QFrame#card {{
    background: {PALETTE['mantle']};
    border: 1px solid {PALETTE['surface0']};
    border-radius: 10px;
}}
QProgressBar {{
    background: {PALETTE['surface0']};
    border-radius: 4px;
    height: 6px;
    text-align: center;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PALETTE['mauve']},stop:1 {PALETTE['blue']});
    border-radius: 4px;
}}
"""


class AnimatedBanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        self.particles = []
        self.wave_offset = 0.0
        self.sakura = []
        self.stars = []
        self._init_particles()
        self._init_sakura()
        self._init_stars()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(30)

    def _init_particles(self):
        for _ in range(22):
            self.particles.append({
                "x": random.uniform(0, 1),
                "y": random.uniform(0, 1),
                "vx": random.uniform(-0.0008, 0.0008),
                "vy": random.uniform(-0.0004, 0.0004),
                "r": random.uniform(1.5, 4.0),
                "alpha": random.uniform(0.3, 0.9),
                "color": random.choice([
                    PALETTE["mauve"], PALETTE["blue"], PALETTE["lavender"],
                    PALETTE["pink"], PALETTE["sapphire"]
                ])
            })

    def _init_sakura(self):
        for _ in range(14):
            self.sakura.append({
                "x": random.uniform(0, 1),
                "y": random.uniform(-0.1, 1.1),
                "vx": random.uniform(-0.0003, 0.0003),
                "vy": random.uniform(0.0005, 0.0018),
                "angle": random.uniform(0, 360),
                "spin": random.uniform(-2, 2),
                "size": random.uniform(6, 13),
                "alpha": random.uniform(0.5, 0.95),
                "color": random.choice([PALETTE["pink"], PALETTE["flamingo"], PALETTE["rosewater"], PALETTE["mauve"]])
            })

    def _init_stars(self):
        for _ in range(35):
            self.stars.append({
                "x": random.uniform(0, 1),
                "y": random.uniform(0, 1),
                "r": random.uniform(0.5, 1.8),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.03, 0.09),
            })

    def _animate(self):
        self.wave_offset += 0.025
        w, h = self.width(), self.height()

        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0: p["x"] = 1.0
            if p["x"] > 1: p["x"] = 0.0
            if p["y"] < 0: p["y"] = 1.0
            if p["y"] > 1: p["y"] = 0.0

        for s in self.sakura:
            s["x"] += s["vx"] + 0.0003 * math.sin(self.wave_offset + s["y"] * 5)
            s["y"] += s["vy"]
            s["angle"] += s["spin"]
            if s["y"] > 1.1:
                s["y"] = -0.05
                s["x"] = random.uniform(0, 1)
            if s["x"] < 0: s["x"] = 1.0
            if s["x"] > 1: s["x"] = 0.0

        for st in self.stars:
            st["phase"] += st["speed"]

        self.update()

    def _draw_sakura_petal(self, painter, cx, cy, size, angle, color):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(angle)
        c = QColor(color)
        for i in range(5):
            painter.save()
            painter.rotate(i * 72)
            grad = QRadialGradient(0, -size * 0.4, size * 0.6)
            grad.setColorAt(0, c)
            grad.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(-size * 0.3), int(-size * 0.9), int(size * 0.6), int(size * 0.7))
            painter.restore()
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#0f0f1a"))
        grad.setColorAt(0.35, QColor(PALETTE["crust"]))
        grad.setColorAt(0.7, QColor("#1a1030"))
        grad.setColorAt(1.0, QColor("#0d0d1e"))
        painter.fillRect(0, 0, w, h, QBrush(grad))

        for st in self.stars:
            alpha = int(80 + 90 * (0.5 + 0.5 * math.sin(st["phase"])))
            c = QColor(PALETTE["lavender"])
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.PenStyle.NoPen)
            r = st["r"] * (0.7 + 0.3 * math.sin(st["phase"] * 1.3))
            painter.drawEllipse(QPoint(int(st["x"] * w), int(st["y"] * h)), max(1, int(r)), max(1, int(r)))

        for i in range(4):
            pts_x = [j * w / 80 for j in range(81)]
            amp = 10 + i * 4
            freq = 0.04 + i * 0.015
            phase = self.wave_offset * (0.7 + i * 0.3) + i * math.pi / 3
            colors = [PALETTE["mauve"], PALETTE["blue"], PALETTE["sapphire"], PALETTE["lavender"]]
            c = QColor(colors[i % len(colors)])
            c.setAlpha(25 + i * 8)
            pen = QPen(c, 1.5)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            prev_x = int(pts_x[0])
            prev_y = int(h * 0.6 + amp * math.sin(freq * pts_x[0] + phase))
            for j in range(1, len(pts_x)):
                nx = int(pts_x[j])
                ny = int(h * 0.6 + amp * math.sin(freq * pts_x[j] + phase))
                painter.drawLine(prev_x, prev_y, nx, ny)
                prev_x, prev_y = nx, ny

        for p in self.particles:
            c = QColor(p["color"])
            c.setAlpha(int(p["alpha"] * 200))
            grad_p = QRadialGradient(p["x"] * w, p["y"] * h, p["r"] * 4)
            grad_p.setColorAt(0, c)
            grad_p.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            painter.setBrush(QBrush(grad_p))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(int(p["x"] * w), int(p["y"] * h)), int(p["r"] * 4), int(p["r"] * 4))

        for s in self.sakura:
            painter.save()
            painter.setOpacity(s["alpha"])
            self._draw_sakura_petal(painter, s["x"] * w, s["y"] * h, s["size"], s["angle"], s["color"])
            painter.restore()

        connection_pen = QPen(QColor(180, 180, 255, 20), 0.5)
        painter.setPen(connection_pen)
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i >= j:
                    continue
                dx = (p1["x"] - p2["x"]) * w
                dy = (p1["y"] - p2["y"]) * h
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 90:
                    alpha = int(30 * (1 - dist / 90))
                    c = QColor(PALETTE["mauve"])
                    c.setAlpha(alpha)
                    painter.setPen(QPen(c, 0.5))
                    painter.drawLine(
                        int(p1["x"] * w), int(p1["y"] * h),
                        int(p2["x"] * w), int(p2["y"] * h)
                    )

        overlay = QLinearGradient(0, 0, 0, h)
        overlay.setColorAt(0, QColor(0, 0, 0, 0))
        overlay.setColorAt(1, QColor(PALETTE["base"]))
        painter.fillRect(0, 0, w, h, QBrush(overlay))

        title_font = QFont("JetBrains Mono", 28, QFont.Weight.Bold)
        painter.setFont(title_font)
        gtext = QLinearGradient(0, 0, w, 0)
        gtext.setColorAt(0.0, QColor(PALETTE["mauve"]))
        gtext.setColorAt(0.4, QColor(PALETTE["lavender"]))
        gtext.setColorAt(0.7, QColor(PALETTE["blue"]))
        gtext.setColorAt(1.0, QColor(PALETTE["sapphire"]))
        painter.setPen(QPen(QBrush(gtext), 1))
        painter.drawText(QRect(0, 38, w, 60), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "NetShade")

        sub_font = QFont("JetBrains Mono", 11)
        painter.setFont(sub_font)
        painter.setPen(QColor(PALETTE["subtext0"]))
        painter.drawText(QRect(0, 95, w, 30), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         "Wi-Fi Security Testing Framework")

        dev_font = QFont("JetBrains Mono", 9)
        painter.setFont(dev_font)
        painter.setPen(QColor(PALETTE["overlay0"]))
        painter.drawText(QRect(0, 125, w, 24), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         "Developed by Rupen Maharjan")

        painter.setPen(QPen(QColor(PALETTE["surface1"]), 1))
        painter.drawLine(0, h - 1, w, h - 1)
        painter.end()


class ConsoleOutput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.document().setMaximumBlockCount(2000)

    def append_line(self, text, color=None):
        self.moveCursor(self.textCursor().MoveOperation.End)
        ts = time.strftime("%H:%M:%S")
        if color is None:
            color = PALETTE["green"]
        prompt = f'<span style="color:{PALETTE["overlay0"]};">[{ts}]</span>'
        content = f'<span style="color:{color};">{text}</span>'
        self.insertHtml(f'{prompt} {content}<br>')
        self.ensureCursorVisible()

    def append_success(self, text):
        self.append_line(f"✓ {text}", PALETTE["green"])

    def append_error(self, text):
        self.append_line(f"✗ {text}", PALETTE["red"])

    def append_warn(self, text):
        self.append_line(f"⚠ {text}", PALETTE["yellow"])

    def append_info(self, text):
        self.append_line(f"ℹ {text}", PALETTE["blue"])

    def append_raw(self, text):
        self.append_line(text, PALETTE["subtext1"])


class WorkerThread(QThread):
    output = pyqtSignal(str, str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, cmd, shell=False):
        super().__init__()
        self.cmd = cmd
        self.shell = shell
        self.process = None
        self._stop = False

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, shell=self.shell, bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._stop:
                    break
                line = line.rstrip()
                if line:
                    self.output.emit(line, "raw")
            self.process.wait()
            self.finished.emit(self.process.returncode)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._stop = True
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass


def detect_interface():
    try:
        result = subprocess.run(["iwconfig"], capture_output=True, text=True)
        lines = result.stdout + result.stderr
        ifaces = re.findall(r'^(\w+)\s+IEEE', lines, re.MULTILINE)
        for iface in ifaces:
            if "mon" in iface:
                return iface, "wlan0mon"
        if ifaces:
            return ifaces[0], ifaces[0]
        return "wlan0", "wlan0"
    except Exception:
        return "wlan0", "wlan0"


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(18)

        self.iface_label = QLabel("Interface: —")
        self.iface_label.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")
        self.mode_badge = QLabel("MANAGED")
        self.mode_badge.setObjectName("badge_blue")
        self.mode_badge.setFixedHeight(20)

        self.target_label = QLabel("Target: —")
        self.target_label.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color:{PALETTE['green']};font-size:14px;")
        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")

        layout.addWidget(self.iface_label)
        layout.addWidget(self.mode_badge)
        layout.addWidget(self.target_label)
        layout.addItem(spacer)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)

    def update_interface(self, iface, mode):
        self.iface_label.setText(f"Interface: {iface}")
        if "mon" in mode.lower():
            self.mode_badge.setObjectName("badge_red")
            self.mode_badge.setText("MONITOR")
        else:
            self.mode_badge.setObjectName("badge_blue")
            self.mode_badge.setText("MANAGED")
        self.mode_badge.style().unpolish(self.mode_badge)
        self.mode_badge.style().polish(self.mode_badge)

    def set_target(self, ssid, bssid):
        if ssid:
            self.target_label.setText(f"Target: {ssid}  [{bssid}]")
        else:
            self.target_label.setText("Target: —")

    def set_status(self, text, color=None):
        self.status_text.setText(text)
        if color:
            self.status_dot.setStyleSheet(f"color:{color};font-size:14px;")
            self.status_text.setStyleSheet(f"color:{color};font-size:11px;")
        else:
            self.status_dot.setStyleSheet(f"color:{PALETTE['green']};font-size:14px;")
            self.status_text.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")


class WifiCardTab(QWidget):
    mode_changed = pyqtSignal(str, str)

    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.iface, self.mon_iface = detect_interface()
        self.worker = None
        self._build_ui()
        self._refresh_state()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Wi-Fi Card Control")
        header.setObjectName("section")
        header.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(header)

        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(14)

        card_layout.addWidget(QLabel("Interface:"), 0, 0)
        self.iface_combo = QComboBox()
        self._populate_interfaces()
        card_layout.addWidget(self.iface_combo, 0, 1)

        card_layout.addWidget(QLabel("Current Mode:"), 1, 0)
        self.mode_label = QLabel("—")
        self.mode_label.setStyleSheet(f"color:{PALETTE['sapphire']};font-weight:700;")
        card_layout.addWidget(self.mode_label, 1, 1)

        card_layout.addWidget(QLabel("Monitor Interface:"), 2, 0)
        self.mon_label = QLabel("—")
        self.mon_label.setStyleSheet(f"color:{PALETTE['mauve']};font-weight:700;")
        card_layout.addWidget(self.mon_label, 2, 1)

        card_layout.addWidget(QLabel("Driver:"), 3, 0)
        self.driver_label = QLabel("—")
        self.driver_label.setStyleSheet(f"color:{PALETTE['subtext0']};")
        card_layout.addWidget(self.driver_label, 3, 1)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        self.toggle_btn = QPushButton("Enable Monitor Mode")
        self.toggle_btn.setObjectName("primary")
        self.toggle_btn.setMinimumHeight(42)
        self.toggle_btn.setMinimumWidth(200)
        self.toggle_btn.clicked.connect(self._toggle_monitor)

        self.kill_btn = QPushButton("Kill Interfering Processes")
        self.kill_btn.setObjectName("warning")
        self.kill_btn.setMinimumHeight(42)
        self.kill_btn.clicked.connect(self._kill_processes)

        self.refresh_btn = QPushButton("Refresh State")
        self.refresh_btn.setMinimumHeight(42)
        self.refresh_btn.clicked.connect(self._refresh_state)

        btn_row.addWidget(self.toggle_btn)
        btn_row.addWidget(self.kill_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.console = ConsoleOutput()
        self.console.setFixedHeight(240)
        layout.addWidget(self.console)
        layout.addStretch()

    def _populate_interfaces(self):
        self.iface_combo.clear()
        try:
            result = subprocess.run(["iwconfig"], capture_output=True, text=True)
            lines = result.stdout + result.stderr
            ifaces = re.findall(r'^(\w+)\s+IEEE', lines, re.MULTILINE)
            for iface in ifaces:
                self.iface_combo.addItem(iface)
            if not ifaces:
                self.iface_combo.addItem("wlan0")
        except Exception:
            self.iface_combo.addItem("wlan0")

    def _get_current_iface(self):
        return self.iface_combo.currentText() or "wlan0"

    def _refresh_state(self):
        iface = self._get_current_iface()
        try:
            result = subprocess.run(["iwconfig", iface], capture_output=True, text=True)
            output = result.stdout + result.stderr
            if "Monitor" in output:
                mode = "Monitor"
                self.mode_label.setText("Monitor Mode")
                self.mode_label.setStyleSheet(f"color:{PALETTE['red']};font-weight:700;")
                self.toggle_btn.setText("Disable Monitor Mode")
                self.toggle_btn.setObjectName("danger")
            else:
                mode = "Managed"
                self.mode_label.setText("Managed Mode")
                self.mode_label.setStyleSheet(f"color:{PALETTE['green']};font-weight:700;")
                self.toggle_btn.setText("Enable Monitor Mode")
                self.toggle_btn.setObjectName("primary")
            self.toggle_btn.style().unpolish(self.toggle_btn)
            self.toggle_btn.style().polish(self.toggle_btn)

            mon = iface + "mon" if "mon" not in iface else iface
            mon_result = subprocess.run(["iwconfig", mon], capture_output=True, text=True)
            if mon in (mon_result.stdout + mon_result.stderr) and "Monitor" in (mon_result.stdout + mon_result.stderr):
                self.mon_label.setText(mon)
            else:
                self.mon_label.setText("None")

            driver_result = subprocess.run(["ethtool", "-i", iface], capture_output=True, text=True)
            driver_match = re.search(r'driver:\s+(\S+)', driver_result.stdout)
            self.driver_label.setText(driver_match.group(1) if driver_match else "Unknown")

            self.status_bar.update_interface(iface, mode)
            self.mode_changed.emit(iface, mon if "None" not in self.mon_label.text() else iface)
        except Exception as e:
            self.console.append_error(f"Could not read interface state: {e}")

    def _toggle_monitor(self):
        iface = self._get_current_iface()
        if "Enable" in self.toggle_btn.text():
            self.console.append_info(f"Starting monitor mode on {iface}...")
            self.status_bar.set_status("Enabling monitor mode...", PALETTE["yellow"])
            self._run_cmd(["sudo", "airmon-ng", "start", iface])
        else:
            self.console.append_info(f"Stopping monitor mode on {iface}...")
            self.status_bar.set_status("Disabling monitor mode...", PALETTE["yellow"])
            mon = iface + "mon" if "mon" not in iface else iface
            self._run_cmd(["sudo", "airmon-ng", "stop", mon])

    def _kill_processes(self):
        self.console.append_warn("Killing interfering processes (NetworkManager, wpa_supplicant)...")
        self._run_cmd(["sudo", "airmon-ng", "check", "kill"])

    def _run_cmd(self, cmd):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.worker = WorkerThread(cmd)
        self.worker.output.connect(lambda t, _: self.console.append_raw(t))
        self.worker.finished.connect(self._on_cmd_done)
        self.worker.error.connect(self.console.append_error)
        self.worker.start()
        self.toggle_btn.setEnabled(False)
        self.kill_btn.setEnabled(False)

    def _on_cmd_done(self, rc):
        self.toggle_btn.setEnabled(True)
        self.kill_btn.setEnabled(True)
        if rc == 0:
            self.console.append_success("Command completed.")
            self.status_bar.set_status("Ready")
        else:
            self.console.append_error(f"Command exited with code {rc}")
            self.status_bar.set_status("Error", PALETTE["red"])
        QTimer.singleShot(500, self._refresh_state)


class ScanThread(QThread):
    network_found = pyqtSignal(dict)
    client_found = pyqtSignal(dict)
    raw_output = pyqtSignal(str)

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.process = None
        self._stop = False
        self._networks = {}
        self._clients = {}

    def run(self):
        try:
            self.process = subprocess.Popen(
                ["sudo", "airodump-ng", "--output-format", "csv", "--write", "/tmp/ns_scan", self.iface],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            csv_thread = threading.Thread(target=self._parse_csv, daemon=True)
            csv_thread.start()
            for line in iter(self.process.stdout.readline, ''):
                if self._stop:
                    break
                self.raw_output.emit(line.rstrip())
            self.process.wait()
        except Exception as e:
            self.raw_output.emit(f"Error: {e}")

    def _parse_csv(self):
        csv_path = "/tmp/ns_scan-01.csv"
        while not self._stop:
            time.sleep(2)
            if not os.path.exists(csv_path):
                continue
            try:
                with open(csv_path, "r", errors="ignore") as f:
                    content = f.read()
                sections = content.split("\r\n\r\n")
                if len(sections) < 1:
                    continue
                bss_lines = sections[0].strip().splitlines()
                sta_lines = sections[1].strip().splitlines() if len(sections) > 1 else []

                for line in bss_lines[2:]:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 14:
                        continue
                    bssid = parts[0]
                    if not re.match(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', bssid):
                        continue
                    net = {
                        "bssid": bssid,
                        "channel": parts[3],
                        "power": parts[8],
                        "ssid": parts[13] if parts[13] else "<Hidden>",
                        "privacy": parts[5],
                        "clients": []
                    }
                    if bssid not in self._networks:
                        self._networks[bssid] = net
                        self.network_found.emit(net)
                    else:
                        self._networks[bssid].update(net)
                        self.network_found.emit(net)

                for line in sta_lines[2:]:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 6:
                        continue
                    sta_mac = parts[0]
                    if not re.match(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', sta_mac):
                        continue
                    ap_bssid = parts[5]
                    sta = {
                        "bssid": sta_mac,
                        "ap_bssid": ap_bssid,
                        "power": parts[3],
                        "device": oui_lookup(sta_mac)
                    }
                    key = sta_mac
                    if key not in self._clients:
                        self._clients[key] = sta
                        self.client_found.emit(sta)
                    else:
                        old = self._clients[key]
                        if old != sta:
                            self._clients[key] = sta
                            self.client_found.emit(sta)
            except Exception:
                pass

    def stop(self):
        self._stop = True
        if self.process:
            try:
                subprocess.run(["sudo", "kill", str(self.process.pid)], capture_output=True)
                self.process.terminate()
            except Exception:
                pass
        for f in ["/tmp/ns_scan-01.csv", "/tmp/ns_scan-01.cap"]:
            try:
                os.remove(f)
            except Exception:
                pass


class ScanTab(QWidget):
    target_selected = pyqtSignal(str, str, str)

    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.scan_thread = None
        self.mon_iface = "wlan0mon"
        self._networks = {}
        self._net_items = {}
        self._client_items = {}
        self._net_counter = 0
        self._build_ui()

    def set_monitor_iface(self, iface):
        self.mon_iface = iface

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("Wi-Fi Scanner with Client Detection")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        hdr.addWidget(title)
        hdr.addStretch()

        self.network_count_badge = QLabel("0 Networks")
        self.network_count_badge.setObjectName("badge_blue")
        self.client_count_badge = QLabel("0 Clients")
        self.client_count_badge.setObjectName("badge_green")
        hdr.addWidget(self.network_count_badge)
        hdr.addWidget(self.client_count_badge)
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        iface_lbl = QLabel("Monitor Interface:")
        iface_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};")
        self.mon_iface_edit = QLineEdit("wlan0mon")
        self.mon_iface_edit.setFixedWidth(130)

        self.scan_btn = QPushButton("▶  Start Scan")
        self.scan_btn.setObjectName("primary")
        self.scan_btn.setMinimumHeight(38)
        self.scan_btn.setMinimumWidth(140)
        self.scan_btn.clicked.connect(self._toggle_scan)

        self.set_target_btn = QPushButton("Set as Target")
        self.set_target_btn.setObjectName("success")
        self.set_target_btn.setMinimumHeight(38)
        self.set_target_btn.clicked.connect(self._set_target)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.clicked.connect(self._clear)

        ctrl.addWidget(iface_lbl)
        ctrl.addWidget(self.mon_iface_edit)
        ctrl.addWidget(self.scan_btn)
        ctrl.addWidget(self.set_target_btn)
        ctrl.addWidget(self.clear_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["#", "BSSID", "SSID / Device", "PWR", "CH", "Security", "Clients"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.setColumnWidth(0, 42)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(3, 60)
        self.tree.setColumnWidth(4, 55)
        self.tree.setColumnWidth(5, 100)
        self.tree.setColumnWidth(6, 65)
        self.tree.setMinimumHeight(280)
        self.tree.itemDoubleClicked.connect(self._on_tree_click)
        splitter.addWidget(self.tree)

        self.console = ConsoleOutput()
        self.console.setFixedHeight(130)
        splitter.addWidget(self.console)

        layout.addWidget(splitter)

        self.status_lbl = QLabel("Ready to scan.")
        self.status_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")
        layout.addWidget(self.status_lbl)

    def _toggle_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self._stop_scan()
        else:
            self._start_scan()

    def _start_scan(self):
        iface = self.mon_iface_edit.text().strip() or self.mon_iface
        self._net_counter = 0
        self.scan_thread = ScanThread(iface)
        self.scan_thread.network_found.connect(self._on_network)
        self.scan_thread.client_found.connect(self._on_client)
        self.scan_thread.raw_output.connect(lambda t: self.console.append_raw(t))
        self.scan_thread.start()

        self.scan_btn.setText("■  Stop Scan")
        self.scan_btn.setObjectName("danger")
        self.scan_btn.style().unpolish(self.scan_btn)
        self.scan_btn.style().polish(self.scan_btn)
        self.status_lbl.setText(f"Scanning on {iface}…")
        self.status_bar.set_status(f"Scanning {iface}", PALETTE["yellow"])
        self.console.append_info(f"Scan started on {iface}")

    def _stop_scan(self):
        if self.scan_thread:
            self.scan_thread.stop()
            self.scan_thread.wait()
        self.scan_btn.setText("▶  Start Scan")
        self.scan_btn.setObjectName("primary")
        self.scan_btn.style().unpolish(self.scan_btn)
        self.scan_btn.style().polish(self.scan_btn)
        self.status_lbl.setText(f"Scan stopped. {len(self._networks)} networks found.")
        self.status_bar.set_status("Ready")
        self.console.append_info("Scan stopped.")

    def _on_network(self, net):
        bssid = net["bssid"]
        if bssid not in self._net_items:
            self._net_counter += 1
            net["_id"] = self._net_counter
            self._networks[bssid] = net
            item = QTreeWidgetItem()
            item.setText(0, str(self._net_counter))
            item.setText(1, bssid)
            ssid = net["ssid"] or "<Hidden>"
            item.setText(2, ssid)
            item.setText(3, net["power"])
            item.setText(4, net["channel"])
            item.setText(5, net["privacy"])
            item.setText(6, "0")
            item.setData(0, Qt.ItemDataRole.UserRole, net)
            item.setForeground(1, QColor(PALETTE["blue"]))
            item.setForeground(2, QColor(PALETTE["text"]))
            item.setForeground(3, self._power_color(net["power"]))
            item.setForeground(4, QColor(PALETTE["sapphire"]))
            item.setForeground(5, QColor(PALETTE["peach"]))
            self.tree.addTopLevelItem(item)
            self._net_items[bssid] = item
            self._update_badge()
        else:
            item = self._net_items[bssid]
            item.setText(3, net["power"])
            item.setForeground(3, self._power_color(net["power"]))

    def _on_client(self, sta):
        ap_bssid = sta.get("ap_bssid", "").strip()
        sta_bssid = sta["bssid"]

        parent_item = self._net_items.get(ap_bssid)
        if not parent_item:
            return

        if sta_bssid in self._client_items:
            child = self._client_items[sta_bssid]
            child.setText(2, sta["device"])
            child.setText(3, sta.get("power", ""))
        else:
            child = QTreeWidgetItem()
            child.setText(0, "")
            child.setText(1, f"  └─ {sta_bssid}")
            child.setText(2, sta["device"])
            child.setText(3, sta.get("power", ""))
            child.setText(4, "")
            child.setText(5, "Client")
            child.setForeground(1, QColor(PALETTE["teal"]))
            child.setForeground(2, QColor(PALETTE["green"]))
            child.setForeground(5, QColor(PALETTE["overlay1"]))
            parent_item.addChild(child)
            parent_item.setExpanded(True)
            parent_item.setText(6, str(parent_item.childCount()))
            self._client_items[sta_bssid] = child
            self._update_client_badge()

    def _power_color(self, power):
        try:
            p = int(power)
            if p > -50:
                return QColor(PALETTE["green"])
            elif p > -70:
                return QColor(PALETTE["yellow"])
            else:
                return QColor(PALETTE["red"])
        except Exception:
            return QColor(PALETTE["subtext0"])

    def _update_badge(self):
        n = self.tree.topLevelItemCount()
        self.network_count_badge.setText(f"{n} Networks")

    def _update_client_badge(self):
        n = len(self._client_items)
        self.client_count_badge.setText(f"{n} Clients")

    def _on_tree_click(self, item, col):
        net = item.data(0, Qt.ItemDataRole.UserRole)
        if net:
            self.status_bar.set_target(net.get("ssid", ""), net.get("bssid", ""))
            self.console.append_info(f"Selected: {net.get('ssid','')} [{net.get('bssid','')}]")

    def _set_target(self):
        item = self.tree.currentItem()
        if not item:
            self.console.append_warn("Select a network first.")
            return
        net = item.data(0, Qt.ItemDataRole.UserRole)
        if net:
            self.target_selected.emit(net.get("bssid", ""), net.get("ssid", ""), net.get("channel", ""))
            self.console.append_success(f"Target set: {net.get('ssid','')} [{net.get('bssid','')}]")
            self.status_bar.set_target(net.get("ssid", ""), net.get("bssid", ""))
        else:
            self.console.append_warn("Please select a network (not a client row).")

    def get_networks(self):
        result = []
        for bssid, net in self._networks.items():
            result.append(net)
        return sorted(result, key=lambda n: n.get("_id", 0))

    def _clear(self):
        self.tree.clear()
        self._networks.clear()
        self._net_items.clear()
        self._client_items.clear()
        self._net_counter = 0
        self._update_badge()
        self._update_client_badge()
        self.console.append_info("Cleared scan results.")


class HandshakeTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.worker = None
        self._target_bssid = ""
        self._target_ssid = ""
        self._target_channel = ""
        self._networks = []
        self._build_ui()

    def set_target(self, bssid, ssid, channel):
        self._target_bssid = bssid
        self._target_ssid = ssid
        self._target_channel = channel
        self._refresh_combo()
        for i in range(self.wifi_combo.count()):
            if bssid in self.wifi_combo.itemText(i):
                self.wifi_combo.setCurrentIndex(i)
                break
        self.console.append_info(f"Auto-selected target: {ssid} [{bssid}]")

    def update_networks(self, networks):
        self._networks = networks
        self._refresh_combo()

    def _refresh_combo(self):
        self.wifi_combo.clear()
        for net in self._networks:
            label = f"[{net.get('_id',0)}] {net.get('ssid','?')} — {net.get('bssid','')}"
            self.wifi_combo.addItem(label, net)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Handshake Capture")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        card = QFrame()
        card.setObjectName("card")
        cly = QGridLayout(card)
        cly.setContentsMargins(22, 18, 22, 18)
        cly.setSpacing(12)

        cly.addWidget(QLabel("Target Network:"), 0, 0)
        self.wifi_combo = QComboBox()
        self.wifi_combo.setMinimumWidth(320)
        cly.addWidget(self.wifi_combo, 0, 1, 1, 2)

        cly.addWidget(QLabel("Monitor Interface:"), 1, 0)
        self.iface_edit = QLineEdit("wlan0mon")
        self.iface_edit.setFixedWidth(140)
        cly.addWidget(self.iface_edit, 1, 1)

        cly.addWidget(QLabel("Save As:"), 2, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("handshake_name (e.g. home_wifi)")
        cly.addWidget(self.name_edit, 2, 1, 1, 2)

        cly.addWidget(QLabel("Save Path:"), 3, 0)
        path_lbl = QLabel(str(CAPTURED_DIR.resolve()))
        path_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")
        cly.addWidget(path_lbl, 3, 1, 1, 2)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        self.capture_btn = QPushButton("▶  Start Capture")
        self.capture_btn.setObjectName("primary")
        self.capture_btn.setMinimumHeight(42)
        self.capture_btn.setMinimumWidth(180)
        self.capture_btn.clicked.connect(self._toggle_capture)

        btn_row.addWidget(self.capture_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.console = ConsoleOutput()
        layout.addWidget(self.console)

    def _toggle_capture(self):
        if self.worker and self.worker.isRunning():
            self._stop()
        else:
            self._start()

    def _start(self):
        net = self.wifi_combo.currentData()
        if not net:
            self.console.append_warn("No network selected.")
            return
        name = self.name_edit.text().strip()
        if not name:
            self.console.append_warn("Please enter a name for the capture.")
            return

        iface = self.iface_edit.text().strip() or "wlan0mon"
        bssid = net.get("bssid", "")
        channel = net.get("channel", "")
        save_path = str(CAPTURED_DIR / name)

        cmd = ["sudo", "airodump-ng", "--bssid", bssid, "-c", channel, "-w", save_path, iface]
        self.worker = WorkerThread(cmd)
        self.worker.output.connect(self._handle_output)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self.console.append_error)
        self.worker.start()

        self.capture_btn.setText("■  Stop Capture")
        self.capture_btn.setObjectName("danger")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)
        self.status_bar.set_status("Capturing handshake…", PALETTE["yellow"])
        self.console.append_info(f"Capturing from {net.get('ssid','')} [{bssid}] → {save_path}.*")

    def _handle_output(self, text, _):
        self.console.append_raw(text)
        if "WPA handshake" in text:
            self.console.append_success("🎉 Handshake captured!")
            self.status_bar.set_status("Handshake captured!", PALETTE["green"])

    def _stop(self):
        if self.worker:
            self.worker.stop()
        self.capture_btn.setText("▶  Start Capture")
        self.capture_btn.setObjectName("primary")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)
        self.status_bar.set_status("Ready")

    def _on_done(self, rc):
        self.capture_btn.setText("▶  Start Capture")
        self.capture_btn.setObjectName("primary")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)
        self.status_bar.set_status("Ready")


class AttackThread(QThread):
    output = pyqtSignal(str, str)
    finished = pyqtSignal(int)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.process = None
        self._stop = False

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._stop:
                    break
                if line.strip():
                    self.output.emit(line.rstrip(), "raw")
            self.process.wait()
            self.finished.emit(self.process.returncode)
        except Exception as e:
            self.output.emit(f"Error: {e}", "error")

    def stop(self):
        self._stop = True
        if self.process:
            try:
                subprocess.run(["sudo", "kill", "-9", str(self.process.pid)], capture_output=True)
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass


class DeauthDoSTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.deauth_worker = None
        self.dos_worker = None
        self._target_bssid = ""
        self._target_ssid = ""
        self._target_channel = ""
        self._build_ui()

    def set_target(self, bssid, ssid, channel):
        self._target_bssid = bssid
        self._target_ssid = ssid
        self._target_channel = channel
        self.deauth_bssid_edit.setText(bssid)
        self.dos_bssid_edit.setText(bssid)
        self.dos_channel_edit.setText(channel)
        self.target_info.setText(f"Target: {ssid}  [{bssid}]  CH:{channel}")
        self.target_info.setStyleSheet(f"color:{PALETTE['green']};font-size:11px;font-weight:600;")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Deauthentication & DoS Attack")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        self.target_info = QLabel("No target selected — use Scanner tab to set target.")
        self.target_info.setStyleSheet(f"color:{PALETTE['overlay0']};font-size:11px;")
        layout.addWidget(self.target_info)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        deauth_widget = QFrame()
        deauth_widget.setObjectName("card")
        dl = QVBoxLayout(deauth_widget)
        dl.setContentsMargins(18, 16, 18, 16)
        dl.setSpacing(10)

        dh = QLabel("Deauthentication")
        dh.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        dh.setStyleSheet(f"color:{PALETTE['peach']};")
        dl.addWidget(dh)

        dg = QGridLayout()
        dg.setSpacing(8)

        dg.addWidget(QLabel("AP BSSID:"), 0, 0)
        self.deauth_bssid_edit = QLineEdit()
        self.deauth_bssid_edit.setPlaceholderText("Auto-filled from target")
        dg.addWidget(self.deauth_bssid_edit, 0, 1)

        dg.addWidget(QLabel("Interface:"), 1, 0)
        self.deauth_iface_edit = QLineEdit("wlan0mon")
        dg.addWidget(self.deauth_iface_edit, 1, 1)

        dg.addWidget(QLabel("Target Client:"), 2, 0)
        self.client_edit = QLineEdit()
        self.client_edit.setPlaceholderText("Leave empty = broadcast (all clients)")
        dg.addWidget(self.client_edit, 2, 1)

        dl.addLayout(dg)

        self.deauth_btn = QPushButton("▶  Start Deauth")
        self.deauth_btn.setObjectName("danger")
        self.deauth_btn.setMinimumHeight(40)
        self.deauth_btn.clicked.connect(self._toggle_deauth)
        dl.addWidget(self.deauth_btn)

        self.deauth_console = ConsoleOutput()
        dl.addWidget(self.deauth_console)
        splitter.addWidget(deauth_widget)

        dos_widget = QFrame()
        dos_widget.setObjectName("card")
        dosl = QVBoxLayout(dos_widget)
        dosl.setContentsMargins(18, 16, 18, 16)
        dosl.setSpacing(10)

        dosh = QLabel("Wi-Fi DoS / Jamming")
        dosh.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        dosh.setStyleSheet(f"color:{PALETTE['red']};")
        dosl.addWidget(dosh)

        dosg = QGridLayout()
        dosg.setSpacing(8)

        dosg.addWidget(QLabel("AP BSSID:"), 0, 0)
        self.dos_bssid_edit = QLineEdit()
        self.dos_bssid_edit.setPlaceholderText("Auto-filled from target")
        dosg.addWidget(self.dos_bssid_edit, 0, 1)

        dosg.addWidget(QLabel("Interface:"), 1, 0)
        self.dos_iface_edit = QLineEdit("wlan0mon")
        dosg.addWidget(self.dos_iface_edit, 1, 1)

        dosg.addWidget(QLabel("Channel:"), 2, 0)
        self.dos_channel_edit = QLineEdit()
        self.dos_channel_edit.setPlaceholderText("Auto-filled")
        dosg.addWidget(self.dos_channel_edit, 2, 1)

        dosl.addLayout(dosg)

        self.dos_btn = QPushButton("▶  Start DoS")
        self.dos_btn.setObjectName("danger")
        self.dos_btn.setMinimumHeight(40)
        self.dos_btn.clicked.connect(self._toggle_dos)
        dosl.addWidget(self.dos_btn)

        self.dos_console = ConsoleOutput()
        dosl.addWidget(self.dos_console)
        splitter.addWidget(dos_widget)

        layout.addWidget(splitter)

    def _toggle_deauth(self):
        if self.deauth_worker and self.deauth_worker.isRunning():
            self._stop_deauth()
        else:
            self._start_deauth()

    def _start_deauth(self):
        bssid = self.deauth_bssid_edit.text().strip() or self._target_bssid
        iface = self.deauth_iface_edit.text().strip() or "wlan0mon"
        client = self.client_edit.text().strip()

        if not bssid:
            self.deauth_console.append_warn("No target BSSID. Set a target in the Scanner tab.")
            return

        if client:
            cmd = ["sudo", "aireplay-ng", "--deauth", "0", "-a", bssid, "-c", client, iface]
        else:
            cmd = ["sudo", "aireplay-ng", "--deauth", "0", "-a", bssid, iface]

        self.deauth_worker = AttackThread(cmd)
        self.deauth_worker.output.connect(lambda t, _: self.deauth_console.append_raw(t))
        self.deauth_worker.finished.connect(lambda rc: self._on_deauth_done(rc))
        self.deauth_worker.start()

        self.deauth_btn.setText("■  Stop Deauth")
        target_desc = f"all clients" if not client else client
        self.deauth_console.append_info(f"Deauth started → {bssid} [{target_desc}]")
        self.status_bar.set_status("Deauthenticating…", PALETTE["red"])

    def _stop_deauth(self):
        if self.deauth_worker:
            self.deauth_worker.stop()
            self.deauth_worker.wait()
        self.deauth_btn.setText("▶  Start Deauth")
        self.deauth_console.append_warn("Deauth stopped.")
        self.status_bar.set_status("Ready")

    def _on_deauth_done(self, rc):
        self.deauth_btn.setText("▶  Start Deauth")
        self.status_bar.set_status("Ready")

    def _toggle_dos(self):
        if self.dos_worker and self.dos_worker.isRunning():
            self._stop_dos()
        else:
            self._start_dos()

    def _start_dos(self):
        bssid = self.dos_bssid_edit.text().strip() or self._target_bssid
        iface = self.dos_iface_edit.text().strip() or "wlan0mon"
        channel = self.dos_channel_edit.text().strip() or self._target_channel

        if not bssid:
            self.dos_console.append_warn("No target BSSID. Set a target in the Scanner tab.")
            return

        if channel:
            subprocess.run(["sudo", "iwconfig", iface, "channel", channel], capture_output=True)

        cmd = ["sudo", "aireplay-ng", "--deauth", "0", "-a", bssid, iface]
        self.dos_worker = AttackThread(cmd)
        self.dos_worker.output.connect(lambda t, _: self.dos_console.append_raw(t))
        self.dos_worker.finished.connect(lambda rc: self._on_dos_done(rc))
        self.dos_worker.start()

        self.dos_btn.setText("■  Stop DoS")
        self.dos_console.append_info(f"DoS/Jamming started → {bssid} on CH{channel}")
        self.status_bar.set_status("DoS active — jamming target…", PALETTE["red"])

    def _stop_dos(self):
        if self.dos_worker:
            self.dos_worker.stop()
            self.dos_worker.wait()
        self.dos_btn.setText("▶  Start DoS")
        self.dos_console.append_warn("DoS stopped.")
        self.status_bar.set_status("Ready")

    def _on_dos_done(self, rc):
        self.dos_btn.setText("▶  Start DoS")
        self.status_bar.set_status("Ready")


class CrackConvertTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Password Cracking & File Conversion")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        crack_widget = QFrame()
        crack_widget.setObjectName("card")
        cl = QVBoxLayout(crack_widget)
        cl.setContentsMargins(18, 16, 18, 16)
        cl.setSpacing(10)

        ch = QLabel("Aircrack-ng Password Cracker")
        ch.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        ch.setStyleSheet(f"color:{PALETTE['mauve']};")
        cl.addWidget(ch)

        cg = QGridLayout()
        cg.setSpacing(8)

        cg.addWidget(QLabel(".cap File:"), 0, 0)
        cap_row = QHBoxLayout()
        self.cap_edit = QLineEdit()
        self.cap_edit.setPlaceholderText("/path/to/capture.cap")
        self.cap_browse = QPushButton("Browse")
        self.cap_browse.setFixedWidth(70)
        self.cap_browse.clicked.connect(lambda: self._browse(self.cap_edit, "cap Files (*.cap *.pcap)"))
        cap_row.addWidget(self.cap_edit)
        cap_row.addWidget(self.cap_browse)
        cg.addLayout(cap_row, 0, 1)

        cg.addWidget(QLabel("Wordlist:"), 1, 0)
        wl_row = QHBoxLayout()
        self.wl_edit = QLineEdit("/usr/share/wordlists/rockyou.txt")
        self.wl_browse = QPushButton("Browse")
        self.wl_browse.setFixedWidth(70)
        self.wl_browse.clicked.connect(lambda: self._browse(self.wl_edit, "Text Files (*.txt);;All (*)"))
        wl_row.addWidget(self.wl_edit)
        wl_row.addWidget(self.wl_browse)
        cg.addLayout(wl_row, 1, 1)

        cl.addLayout(cg)

        crack_btn_row = QHBoxLayout()
        self.crack_btn = QPushButton("▶  Start Cracking")
        self.crack_btn.setObjectName("primary")
        self.crack_btn.setMinimumHeight(40)
        self.crack_btn.clicked.connect(self._toggle_crack)

        self.stop_crack_btn = QPushButton("■  Stop")
        self.stop_crack_btn.setObjectName("danger")
        self.stop_crack_btn.setMinimumHeight(40)
        self.stop_crack_btn.setEnabled(False)
        self.stop_crack_btn.clicked.connect(self._stop_crack)

        crack_btn_row.addWidget(self.crack_btn)
        crack_btn_row.addWidget(self.stop_crack_btn)
        crack_btn_row.addStretch()
        cl.addLayout(crack_btn_row)

        self.crack_console = ConsoleOutput()
        cl.addWidget(self.crack_console)
        splitter.addWidget(crack_widget)

        conv_widget = QFrame()
        conv_widget.setObjectName("card")
        cvl = QVBoxLayout(conv_widget)
        cvl.setContentsMargins(18, 16, 18, 16)
        cvl.setSpacing(10)

        cvh = QLabel("File Conversion")
        cvh.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        cvh.setStyleSheet(f"color:{PALETTE['sapphire']};")
        cvl.addWidget(cvh)

        cvg = QGridLayout()
        cvg.setSpacing(8)

        cvg.addWidget(QLabel(".cap File:"), 0, 0)
        conv_cap_row = QHBoxLayout()
        self.conv_cap_edit = QLineEdit()
        self.conv_cap_edit.setPlaceholderText("/path/to/handshake.cap")
        self.conv_cap_browse = QPushButton("Browse")
        self.conv_cap_browse.setFixedWidth(70)
        self.conv_cap_browse.clicked.connect(lambda: self._browse(self.conv_cap_edit, "cap Files (*.cap *.pcap)"))
        conv_cap_row.addWidget(self.conv_cap_edit)
        conv_cap_row.addWidget(self.conv_cap_browse)
        cvg.addLayout(conv_cap_row, 0, 1)

        cvg.addWidget(QLabel("Output Dir:"), 1, 0)
        out_row = QHBoxLayout()
        self.out_dir_edit = QLineEdit(str(CAPTURED_DIR.resolve()))
        self.out_dir_browse = QPushButton("Browse")
        self.out_dir_browse.setFixedWidth(70)
        self.out_dir_browse.clicked.connect(self._browse_dir)
        out_row.addWidget(self.out_dir_edit)
        out_row.addWidget(self.out_dir_browse)
        cvg.addLayout(out_row, 1, 1)
        cvl.addLayout(cvg)

        conv_btn_row = QHBoxLayout()

        hc_btn = QPushButton("→ Hashcat (.hc22000)")
        hc_btn.setObjectName("warning")
        hc_btn.setMinimumHeight(40)
        hc_btn.clicked.connect(self._to_hashcat)

        jtr_btn = QPushButton("→ John the Ripper (.hccap)")
        jtr_btn.setObjectName("success")
        jtr_btn.setMinimumHeight(40)
        jtr_btn.clicked.connect(self._to_john)

        conv_btn_row.addWidget(hc_btn)
        conv_btn_row.addWidget(jtr_btn)
        cvl.addLayout(conv_btn_row)

        self.conv_console = ConsoleOutput()
        cvl.addWidget(self.conv_console)
        splitter.addWidget(conv_widget)

        layout.addWidget(splitter)

    def _browse(self, edit, filt):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", str(Path.home()), filt)
        if path:
            edit.setText(path)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(Path.home()))
        if d:
            self.out_dir_edit.setText(d)

    def _toggle_crack(self):
        if self.worker and self.worker.isRunning():
            self._stop_crack()
        else:
            self._start_crack()

    def _start_crack(self):
        cap = self.cap_edit.text().strip()
        wl = self.wl_edit.text().strip()
        if not cap:
            self.crack_console.append_warn("Please specify a .cap file.")
            return
        if not wl:
            self.crack_console.append_warn("Please specify a wordlist.")
            return
        if not os.path.exists(cap):
            self.crack_console.append_error(f"File not found: {cap}")
            return
        if not os.path.exists(wl):
            self.crack_console.append_error(f"Wordlist not found: {wl}")
            return

        cmd = ["sudo", "aircrack-ng", cap, "-w", wl]
        self.worker = WorkerThread(cmd)
        self.worker.output.connect(self._handle_crack_output)
        self.worker.finished.connect(self._on_crack_done)
        self.worker.error.connect(self.crack_console.append_error)
        self.worker.start()

        self.crack_btn.setEnabled(False)
        self.stop_crack_btn.setEnabled(True)
        self.status_bar.set_status("Cracking…", PALETTE["yellow"])
        self.crack_console.append_info(f"aircrack-ng started: {cap}")

    def _handle_crack_output(self, text, _):
        if "KEY FOUND" in text.upper():
            self.crack_console.append_success(text)
            self.status_bar.set_status("KEY FOUND!", PALETTE["green"])
        elif "failed" in text.lower() or "not found" in text.lower():
            self.crack_console.append_warn(text)
        else:
            self.crack_console.append_raw(text)

    def _stop_crack(self):
        if self.worker:
            self.worker.stop()
        self.crack_btn.setEnabled(True)
        self.stop_crack_btn.setEnabled(False)
        self.status_bar.set_status("Ready")

    def _on_crack_done(self, rc):
        self.crack_btn.setEnabled(True)
        self.stop_crack_btn.setEnabled(False)
        self.status_bar.set_status("Ready")
        if rc == 0:
            self.crack_console.append_success("Aircrack-ng finished.")
        else:
            self.crack_console.append_warn(f"Aircrack-ng exited with code {rc}")

    def _to_hashcat(self):
        cap = self.conv_cap_edit.text().strip()
        out_dir = self.out_dir_edit.text().strip() or str(CAPTURED_DIR.resolve())
        if not cap:
            self.conv_console.append_warn("Please specify a .cap file.")
            return
        if not os.path.exists(cap):
            self.conv_console.append_error(f"File not found: {cap}")
            return
        stem = Path(cap).stem
        out = os.path.join(out_dir, stem + ".hc22000")
        if shutil.which("hcxtools") or shutil.which("cap2hashcat") or shutil.which("hcxpcapngtool"):
            tool = "hcxpcapngtool"
            cmd = ["sudo", tool, "-o", out, cap]
        else:
            cmd = ["sudo", "aircrack-ng", cap, "-J", os.path.join(out_dir, stem)]
            self.conv_console.append_warn("hcxpcapngtool not found, using aircrack-ng fallback.")
        w = WorkerThread(cmd)
        w.output.connect(lambda t, _: self.conv_console.append_raw(t))
        w.finished.connect(lambda rc: self.conv_console.append_success(f"Hashcat file saved → {out}") if rc == 0 else self.conv_console.append_error(f"Conversion failed (code {rc})"))
        w.error.connect(self.conv_console.append_error)
        w.start()
        self.conv_console.append_info(f"Converting to Hashcat format → {out}")

    def _to_john(self):
        cap = self.conv_cap_edit.text().strip()
        out_dir = self.out_dir_edit.text().strip() or str(CAPTURED_DIR.resolve())
        if not cap:
            self.conv_console.append_warn("Please specify a .cap file.")
            return
        if not os.path.exists(cap):
            self.conv_console.append_error(f"File not found: {cap}")
            return
        stem = Path(cap).stem
        out = os.path.join(out_dir, stem)
        cmd = ["sudo", "aircrack-ng", cap, "-J", out]
        w = WorkerThread(cmd)
        w.output.connect(lambda t, _: self.conv_console.append_raw(t))
        w.finished.connect(lambda rc: self.conv_console.append_success(f"John file saved → {out}.hccap") if rc == 0 else self.conv_console.append_error(f"Conversion failed (code {rc})"))
        w.error.connect(self.conv_console.append_error)
        w.start()
        self.conv_console.append_info(f"Converting to John the Ripper format → {out}.hccap")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetShade — Wi-Fi Security Testing Framework")
        self.setMinimumSize(1100, 780)
        self.resize(1280, 860)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.banner = AnimatedBanner()
        root.addWidget(self.banner)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 10, 16, 10)
        content_layout.setSpacing(10)

        self.status_bar_widget = StatusBar()
        content_layout.addWidget(self.status_bar_widget)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.card_tab = WifiCardTab(self.status_bar_widget)
        self.scan_tab = ScanTab(self.status_bar_widget)
        self.hs_tab = HandshakeTab(self.status_bar_widget)
        self.attack_tab = DeauthDoSTab(self.status_bar_widget)
        self.crack_tab = CrackConvertTab(self.status_bar_widget)

        self.tabs.addTab(self.card_tab, "⚡ Card Control")
        self.tabs.addTab(self.scan_tab, "📡 Scanner")
        self.tabs.addTab(self.hs_tab, "🤝 Handshake")
        self.tabs.addTab(self.attack_tab, "💥 Deauth & DoS")
        self.tabs.addTab(self.crack_tab, "🔓 Crack & Convert")

        self.card_tab.mode_changed.connect(self._on_mode_changed)
        self.scan_tab.target_selected.connect(self._on_target_selected)

        content_layout.addWidget(self.tabs)
        root.addWidget(content)

    def _on_mode_changed(self, iface, mon_iface):
        self.scan_tab.set_monitor_iface(mon_iface)
        self.scan_tab.mon_iface_edit.setText(mon_iface)
        self.hs_tab.iface_edit.setText(mon_iface)
        self.attack_tab.deauth_iface_edit.setText(mon_iface)
        self.attack_tab.dos_iface_edit.setText(mon_iface)

    def _on_target_selected(self, bssid, ssid, channel):
        self.hs_tab.update_networks(self.scan_tab.get_networks())
        self.hs_tab.set_target(bssid, ssid, channel)
        self.attack_tab.set_target(bssid, ssid, channel)
        self.status_bar_widget.set_target(ssid, bssid)


def main():
    if os.geteuid() != 0:
        print("[NetShade] Run with sudo for full functionality: sudo python3 netshade.py")

    app = QApplication(sys.argv)
    app.setApplicationName("NetShade")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Rupen Maharjan")

    app.setStyleSheet(STYLESHEET)

    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(PALETTE["base"]))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(PALETTE["text"]))
    pal.setColor(QPalette.ColorRole.Base, QColor(PALETTE["mantle"]))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(PALETTE["crust"]))
    pal.setColor(QPalette.ColorRole.Text, QColor(PALETTE["text"]))
    pal.setColor(QPalette.ColorRole.Button, QColor(PALETTE["surface0"]))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(PALETTE["text"]))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(PALETTE["mauve"]))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(PALETTE["crust"]))
    app.setPalette(pal)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
