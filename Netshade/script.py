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
    QSizePolicy, QSpacerItem, QCheckBox, QSpinBox, QMenu
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSize
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QLinearGradient,
    QBrush, QPen, QFontDatabase, QIcon,
    QRadialGradient
)
import math
import random


# ---------------------------------------------------------------------------
# Theme palette (Catppuccin Mocha)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
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
QPushButton:disabled {{
    background: {PALETTE['surface0']};
    color: {PALETTE['overlay0']};
    border-color: {PALETTE['surface0']};
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
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
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
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
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


# ---------------------------------------------------------------------------
# Animated banner
# ---------------------------------------------------------------------------
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
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)

    def _init_particles(self):
        colors = [PALETTE["mauve"], PALETTE["blue"], PALETTE["lavender"], PALETTE["pink"], PALETTE["sapphire"]]
        for _ in range(22):
            self.particles.append({
                "x": random.uniform(0, 1), "y": random.uniform(0, 1),
                "vx": random.uniform(-0.0008, 0.0008), "vy": random.uniform(-0.0004, 0.0004),
                "r": random.uniform(1.5, 4.0), "alpha": random.uniform(0.3, 0.9),
                "color": random.choice(colors)
            })

    def _init_sakura(self):
        colors = [PALETTE["pink"], PALETTE["flamingo"], PALETTE["rosewater"], PALETTE["mauve"]]
        for _ in range(14):
            self.sakura.append({
                "x": random.uniform(0, 1), "y": random.uniform(-0.1, 1.1),
                "vx": random.uniform(-0.0003, 0.0003), "vy": random.uniform(0.0005, 0.0018),
                "angle": random.uniform(0, 360), "spin": random.uniform(-2, 2),
                "size": random.uniform(6, 13), "alpha": random.uniform(0.5, 0.95),
                "color": random.choice(colors)
            })

    def _init_stars(self):
        for _ in range(35):
            self.stars.append({
                "x": random.uniform(0, 1), "y": random.uniform(0, 1),
                "r": random.uniform(0.5, 1.8),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.03, 0.09),
            })

    def _animate(self):
        self.wave_offset += 0.025
        for p in self.particles:
            p["x"] = (p["x"] + p["vx"]) % 1.0
            p["y"] = (p["y"] + p["vy"]) % 1.0
        for s in self.sakura:
            s["x"] += s["vx"] + 0.0003 * math.sin(self.wave_offset + s["y"] * 5)
            s["y"] += s["vy"]
            s["angle"] += s["spin"]
            if s["y"] > 1.1:
                s["y"] = -0.05
                s["x"] = random.uniform(0, 1)
            s["x"] %= 1.0
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
            r = max(1, int(st["r"] * (0.7 + 0.3 * math.sin(st["phase"] * 1.3))))
            painter.drawEllipse(QPoint(int(st["x"] * w), int(st["y"] * h)), r, r)

        # Wave lines
        wave_colors = [PALETTE["mauve"], PALETTE["blue"], PALETTE["sapphire"], PALETTE["lavender"]]
        for i in range(4):
            amp = 10 + i * 4
            freq = 0.04 + i * 0.015
            phase = self.wave_offset * (0.7 + i * 0.3) + i * math.pi / 3
            c = QColor(wave_colors[i % len(wave_colors)])
            c.setAlpha(25 + i * 8)
            painter.setPen(QPen(c, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            prev_x = 0
            prev_y = int(h * 0.6 + amp * math.sin(freq * 0 + phase))
            for j in range(1, 81):
                nx = int(j * w / 80)
                ny = int(h * 0.6 + amp * math.sin(freq * nx + phase))
                painter.drawLine(prev_x, prev_y, nx, ny)
                prev_x, prev_y = nx, ny

        # Particles + connections
        for p in self.particles:
            c = QColor(p["color"])
            c.setAlpha(int(p["alpha"] * 200))
            grad_p = QRadialGradient(p["x"] * w, p["y"] * h, p["r"] * 4)
            grad_p.setColorAt(0, c)
            grad_p.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
            painter.setBrush(QBrush(grad_p))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(int(p["x"] * w), int(p["y"] * h)), int(p["r"] * 4), int(p["r"] * 4))

        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i >= j:
                    continue
                dx = (p1["x"] - p2["x"]) * w
                dy = (p1["y"] - p2["y"]) * h
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 90:
                    c = QColor(PALETTE["mauve"])
                    c.setAlpha(int(30 * (1 - dist / 90)))
                    painter.setPen(QPen(c, 0.5))
                    painter.drawLine(int(p1["x"] * w), int(p1["y"] * h), int(p2["x"] * w), int(p2["y"] * h))

        # Sakura
        for s in self.sakura:
            painter.save()
            painter.setOpacity(s["alpha"])
            self._draw_sakura_petal(painter, s["x"] * w, s["y"] * h, s["size"], s["angle"], s["color"])
            painter.restore()

        # Bottom fade overlay
        overlay = QLinearGradient(0, 0, 0, h)
        overlay.setColorAt(0, QColor(0, 0, 0, 0))
        overlay.setColorAt(1, QColor(PALETTE["base"]))
        painter.fillRect(0, 0, w, h, QBrush(overlay))

        # Title text
        painter.setFont(QFont("JetBrains Mono", 28, QFont.Weight.Bold))
        gtext = QLinearGradient(0, 0, w, 0)
        gtext.setColorAt(0.0, QColor(PALETTE["mauve"]))
        gtext.setColorAt(0.4, QColor(PALETTE["lavender"]))
        gtext.setColorAt(0.7, QColor(PALETTE["blue"]))
        gtext.setColorAt(1.0, QColor(PALETTE["sapphire"]))
        painter.setPen(QPen(QBrush(gtext), 1))
        painter.drawText(QRect(0, 38, w, 60), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "NetShade")

        painter.setFont(QFont("JetBrains Mono", 11))
        painter.setPen(QColor(PALETTE["subtext0"]))
        painter.drawText(QRect(0, 95, w, 30), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         "Wi-Fi Security Testing Framework")

        painter.setFont(QFont("JetBrains Mono", 9))
        painter.setPen(QColor(PALETTE["overlay0"]))
        painter.drawText(QRect(0, 125, w, 24), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         "Developed by Rupen Maharjan")

        painter.setPen(QPen(QColor(PALETTE["surface1"]), 1))
        painter.drawLine(0, h - 1, w, h - 1)
        painter.end()


# ---------------------------------------------------------------------------
# Console output widget with buffered appends
# ---------------------------------------------------------------------------
class ConsoleOutput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.document().setMaximumBlockCount(2000)
        self._buffer = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._flush_buffer)
        self._timer.start(100)
        self._last_flush = time.time()

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)

    def _flush_buffer(self):
        if not self._buffer:
            return
        self.moveCursor(self.textCursor().MoveOperation.End)
        batch, self._buffer = self._buffer[:50], self._buffer[50:]
        self.insertHtml("".join(batch))
        self.ensureCursorVisible()

    def _enqueue(self, html_line):
        self._buffer.append(html_line)
        now = time.time()
        if now - self._last_flush > 0.5 or len(self._buffer) > 100:
            self._flush_buffer()
            self._last_flush = now

    def append_line(self, text, color=None):
        color = color or PALETTE["green"]
        ts = time.strftime("%H:%M:%S")
        prompt = f'<span style="color:{PALETTE["overlay0"]};">[{ts}]</span>'
        content = f'<span style="color:{color};">{text}</span>'
        self._enqueue(f'{prompt} {content}<br>')

    def append_success(self, text): self.append_line(f"✓ {text}", PALETTE["green"])
    def append_error(self, text):   self.append_line(f"✗ {text}", PALETTE["red"])
    def append_warn(self, text):    self.append_line(f"⚠ {text}", PALETTE["yellow"])
    def append_info(self, text):    self.append_line(f"ℹ {text}", PALETTE["blue"])
    def append_raw(self, text):     self.append_line(text, PALETTE["subtext1"])

    def clear_log(self):
        self.clear()
        self._buffer.clear()


# ---------------------------------------------------------------------------
# Generic worker thread for subprocess commands
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Helper: wireless interface detection
# ---------------------------------------------------------------------------
def get_all_wireless_ifaces():
    ifaces = []
    try:
        result = subprocess.run(["iw", "dev"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            m = re.match(r'\s+Interface\s+(\S+)', line)
            if m:
                ifaces.append(m.group(1))
    except Exception:
        pass
    if not ifaces:
        try:
            result = subprocess.run(["iwconfig"], capture_output=True, text=True, timeout=5)
            ifaces = re.findall(r'^(\w+)\s+IEEE', result.stdout + result.stderr, re.MULTILINE)
        except Exception:
            pass
    if not ifaces:
        try:
            with open("/proc/net/wireless") as f:
                for line in f.readlines()[2:]:
                    iface = line.split(":")[0].strip()
                    if iface:
                        ifaces.append(iface)
        except Exception:
            pass
    return ifaces or ["wlan0"]


def get_iface_mode(iface):
    try:
        result = subprocess.run(["iw", "dev", iface, "info"], capture_output=True, text=True, timeout=5)
        m = re.search(r'type\s+(\S+)', result.stdout)
        if m:
            return m.group(1).lower()
    except Exception:
        pass
    try:
        result = subprocess.run(["iwconfig", iface], capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr
        if re.search(r'Mode\s*:\s*Monitor', output, re.IGNORECASE):
            return "monitor"
        if re.search(r'Mode\s*:\s*Managed', output, re.IGNORECASE):
            return "managed"
    except Exception:
        pass
    return "unknown"


def detect_interface():
    ifaces = get_all_wireless_ifaces()
    managed = monitor = None
    for iface in ifaces:
        mode = get_iface_mode(iface)
        if mode == "monitor" and monitor is None:
            monitor = iface
        elif mode in ("managed", "unknown") and managed is None:
            managed = iface
    base = managed or monitor or "wlan0"
    mon = monitor or (base + "mon")
    return base, mon


# ---------------------------------------------------------------------------
# Status bar
# ---------------------------------------------------------------------------
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

        for w in [self.iface_label, self.mode_badge, self.target_label]:
            layout.addWidget(w)
        layout.addItem(spacer)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)

    def _refresh_badge_style(self, badge):
        badge.style().unpolish(badge)
        badge.style().polish(badge)

    def update_interface(self, iface, mode):
        self.iface_label.setText(f"Interface: {iface}")
        if mode == "monitor":
            self.mode_badge.setObjectName("badge_red")
            self.mode_badge.setText("MONITOR")
        else:
            self.mode_badge.setObjectName("badge_blue")
            self.mode_badge.setText("MANAGED")
        self._refresh_badge_style(self.mode_badge)

    def set_target(self, ssid, bssid):
        self.target_label.setText(f"Target: {ssid}  [{bssid}]" if ssid else "Target: —")

    def set_status(self, text, color=None):
        self.status_text.setText(text)
        dot_color = color or PALETTE["green"]
        text_color = color or PALETTE["subtext0"]
        self.status_dot.setStyleSheet(f"color:{dot_color};font-size:14px;")
        self.status_text.setStyleSheet(f"color:{text_color};font-size:11px;")


# ---------------------------------------------------------------------------
# Wi-Fi Card Control tab
# ---------------------------------------------------------------------------
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

        sep = QFrame(); sep.setObjectName("separator")
        layout.addWidget(sep)

        card = QFrame(); card.setObjectName("card")
        grid = QGridLayout(card)
        grid.setContentsMargins(22, 20, 22, 20)
        grid.setSpacing(14)

        grid.addWidget(QLabel("Interface:"), 0, 0)
        self.iface_combo = QComboBox()
        self._populate_interfaces()
        grid.addWidget(self.iface_combo, 0, 1)

        grid.addWidget(QLabel("Current Mode:"), 1, 0)
        self.mode_label = QLabel("—")
        self.mode_label.setStyleSheet(f"color:{PALETTE['sapphire']};font-weight:700;")
        grid.addWidget(self.mode_label, 1, 1)

        grid.addWidget(QLabel("Monitor Interface:"), 2, 0)
        self.mon_label = QLabel("—")
        self.mon_label.setStyleSheet(f"color:{PALETTE['mauve']};font-weight:700;")
        grid.addWidget(self.mon_label, 2, 1)

        grid.addWidget(QLabel("Driver:"), 3, 0)
        self.driver_label = QLabel("—")
        self.driver_label.setStyleSheet(f"color:{PALETTE['subtext0']};")
        grid.addWidget(self.driver_label, 3, 1)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        self.toggle_btn = QPushButton("Enable Monitor Mode")
        self.toggle_btn.setObjectName("primary")
        self.toggle_btn.setMinimumHeight(42); self.toggle_btn.setMinimumWidth(200)
        self.toggle_btn.clicked.connect(self._toggle_monitor)

        self.kill_btn = QPushButton("Kill Interfering Processes")
        self.kill_btn.setObjectName("warning")
        self.kill_btn.setMinimumHeight(42)
        self.kill_btn.clicked.connect(self._kill_processes)

        self.refresh_btn = QPushButton("Refresh State")
        self.refresh_btn.setMinimumHeight(42)
        self.refresh_btn.clicked.connect(self._refresh_state)

        for b in [self.toggle_btn, self.kill_btn, self.refresh_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.console = ConsoleOutput()
        self.console.setFixedHeight(240)
        layout.addWidget(self.console)
        layout.addStretch()

    def _populate_interfaces(self):
        prev = self.iface_combo.currentData()
        self.iface_combo.clear()
        for iface in get_all_wireless_ifaces():
            mode = get_iface_mode(iface)
            self.iface_combo.addItem(f"{iface}  [{mode}]", iface)
        if self.iface_combo.count() == 0:
            self.iface_combo.addItem("wlan0  [unknown]", "wlan0")
        # Restore previous selection
        for i in range(self.iface_combo.count()):
            if self.iface_combo.itemData(i) == prev:
                self.iface_combo.setCurrentIndex(i)
                break

    def _get_current_iface(self):
        data = self.iface_combo.currentData()
        if data:
            return data
        text = self.iface_combo.currentText()
        return text.split()[0] if text else "wlan0"

    def _refresh_state(self):
        self._populate_interfaces()
        iface = self._get_current_iface()
        try:
            mode = get_iface_mode(iface)
            all_ifaces = get_all_wireless_ifaces()

            if mode == "monitor":
                self.mode_label.setText("Monitor Mode  🔴")
                self.mode_label.setStyleSheet(f"color:{PALETTE['red']};font-weight:700;")
                self.toggle_btn.setText("Disable Monitor Mode")
                self.toggle_btn.setObjectName("danger")
                self.mon_label.setText(iface)
                self.mon_label.setStyleSheet(f"color:{PALETTE['red']};font-weight:700;")
                emit_mon = iface
            else:
                self.mode_label.setText("Managed Mode  🟢")
                self.mode_label.setStyleSheet(f"color:{PALETTE['green']};font-weight:700;")
                self.toggle_btn.setText("Enable Monitor Mode")
                self.toggle_btn.setObjectName("primary")
                mon_iface = next((i for i in all_ifaces if get_iface_mode(i) == "monitor"), None)
                if mon_iface:
                    self.mon_label.setText(mon_iface)
                    self.mon_label.setStyleSheet(f"color:{PALETTE['mauve']};font-weight:700;")
                    emit_mon = mon_iface
                else:
                    self.mon_label.setText("None")
                    self.mon_label.setStyleSheet(f"color:{PALETTE['overlay0']};font-weight:700;")
                    emit_mon = iface

            self.toggle_btn.style().unpolish(self.toggle_btn)
            self.toggle_btn.style().polish(self.toggle_btn)

            # Driver info
            try:
                dr = subprocess.run(["ethtool", "-i", iface], capture_output=True, text=True, timeout=5)
                m = re.search(r'driver:\s+(\S+)', dr.stdout)
                self.driver_label.setText(m.group(1) if m else "Unknown")
            except Exception:
                self.driver_label.setText("Unknown")

            self.status_bar.update_interface(iface, mode)
            self.mode_changed.emit(iface, emit_mon)
            self.console.append_info(f"Interface: {iface} | Mode: {mode} | Monitor: {self.mon_label.text()}")
        except Exception as e:
            self.console.append_error(f"Could not read interface state: {e}")

    def _toggle_monitor(self):
        iface = self._get_current_iface()
        if "Enable" in self.toggle_btn.text():
            self.console.append_info(f"Starting monitor mode on {iface}…")
            self.status_bar.set_status("Enabling monitor mode…", PALETTE["yellow"])
            self._run_cmd(["sudo", "airmon-ng", "start", iface])
        else:
            self.console.append_info("Stopping monitor mode…")
            self.status_bar.set_status("Disabling monitor mode…", PALETTE["yellow"])
            all_ifaces = get_all_wireless_ifaces()
            mon_iface = next((i for i in all_ifaces if get_iface_mode(i) == "monitor"), None)
            target = mon_iface or (iface + "mon")
            self._run_cmd(["sudo", "airmon-ng", "stop", target])

    def _kill_processes(self):
        self.console.append_warn("Killing interfering processes…")
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
        QTimer.singleShot(800, self._refresh_state)
        QTimer.singleShot(1500, self._refresh_state)


# ---------------------------------------------------------------------------
# Scan thread
# ---------------------------------------------------------------------------
class ScanThread(QThread):
    network_found = pyqtSignal(dict)
    client_found = pyqtSignal(dict)
    raw_output = pyqtSignal(str)

    _MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
    _CSV_PATH = "/tmp/ns_scan-01.csv"

    def __init__(self, iface, band="abg"):
        super().__init__()
        self.iface = iface
        self.band = band
        self.process = None
        self._stop = False
        self._networks = {}
        self._clients = {}
        self._lock = threading.Lock()

    def run(self):
        # Clean up old files
        for f in [self._CSV_PATH, "/tmp/ns_scan-01.cap"]:
            try: os.remove(f)
            except Exception: pass

        cmd = ["sudo", "airodump-ng", "--output-format", "csv",
               "--write", "/tmp/ns_scan", "--band", self.band, self.iface]
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True, bufsize=1)
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
        while not self._stop:
            time.sleep(2)
            if not os.path.exists(self._CSV_PATH):
                continue
            try:
                with open(self._CSV_PATH, "rb") as f:
                    content = f.read().decode('utf-8', errors='ignore')

                sep = '\r\n\r\n' if '\r\n\r\n' in content else '\n\n'
                sections = content.split(sep)
                if len(sections) < 2:
                    continue

                # Parse APs
                for line in sections[0].splitlines()[2:]:
                    if not line.strip():
                        continue
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 14:
                        continue
                    bssid = parts[0]
                    if not self._MAC_RE.match(bssid):
                        continue
                    net = {
                        "bssid": bssid, "channel": parts[3],
                        "power": parts[8], "privacy": parts[5],
                        "ssid": parts[13] or "<Hidden>",
                    }
                    with self._lock:
                        if bssid not in self._networks:
                            self._networks[bssid] = net
                            self.network_found.emit(net)
                        else:
                            self._networks[bssid].update(net)

                # Parse clients
                sta_section = sections[1].strip()
                if not sta_section:
                    continue
                for line in sta_section.splitlines()[2:]:
                    if not line.strip():
                        continue
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 6:
                        continue
                    sta_mac = parts[0]
                    ap_bssid = parts[5].strip()
                    if (not self._MAC_RE.match(sta_mac) or not self._MAC_RE.match(ap_bssid)
                            or "(not associated)" in ap_bssid.lower()):
                        continue
                    power = parts[3] if len(parts) > 3 else "-100"
                    sta = {"bssid": sta_mac, "ap_bssid": ap_bssid, "power": power}
                    key = f"{sta_mac}:{ap_bssid}"
                    with self._lock:
                        if key not in self._clients:
                            self._clients[key] = sta
                            self.client_found.emit(sta)
                        elif self._clients[key]["power"] != power:
                            self._clients[key]["power"] = power
                            self.client_found.emit(sta)
            except Exception as e:
                self.raw_output.emit(f"CSV parse error: {e}")

    def stop(self):
        self._stop = True
        if self.process:
            try:
                subprocess.run(["sudo", "kill", str(self.process.pid)],
                               capture_output=True, timeout=2)
                self.process.terminate()
            except Exception:
                pass
        for f in [self._CSV_PATH, "/tmp/ns_scan-01.cap"]:
            try: os.remove(f)
            except Exception: pass


# ---------------------------------------------------------------------------
# Scanner tab
# ---------------------------------------------------------------------------
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
        self.band_badge = QLabel("2.4 + 5 GHz")
        self.band_badge.setObjectName("badge_yellow")
        for w in [self.band_badge, self.network_count_badge, self.client_count_badge]:
            hdr.addWidget(w)
        layout.addLayout(hdr)

        sep = QFrame(); sep.setObjectName("separator")
        layout.addWidget(sep)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        iface_lbl = QLabel("Monitor Interface:")
        iface_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};")
        self.mon_iface_edit = QLineEdit("wlan0mon")
        self.mon_iface_edit.setFixedWidth(130)

        band_lbl = QLabel("Band:")
        band_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};")
        self.band_combo = QComboBox()
        self.band_combo.addItem("2.4 GHz + 5 GHz  (abg)", "abg")
        self.band_combo.addItem("2.4 GHz only  (bg)", "bg")
        self.band_combo.addItem("5 GHz only  (a)", "a")
        self.band_combo.setFixedWidth(220)
        self.band_combo.currentIndexChanged.connect(self._on_band_change)

        self.scan_btn = QPushButton("▶  Start Scan")
        self.scan_btn.setObjectName("primary")
        self.scan_btn.setMinimumHeight(38); self.scan_btn.setMinimumWidth(140)
        self.scan_btn.clicked.connect(self._toggle_scan)

        self.set_target_btn = QPushButton("Set as Target")
        self.set_target_btn.setObjectName("success")
        self.set_target_btn.setMinimumHeight(38)
        self.set_target_btn.clicked.connect(self._set_target)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.clicked.connect(self._clear)

        for w in [iface_lbl, self.mon_iface_edit, band_lbl, self.band_combo,
                  self.scan_btn, self.set_target_btn, self.clear_btn]:
            ctrl.addWidget(w)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["#", "BSSID", "SSID", "PWR", "CH", "Band", "Security", "Clients"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.setColumnWidth(0, 42); self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(3, 60); self.tree.setColumnWidth(4, 50)
        self.tree.setColumnWidth(5, 72); self.tree.setColumnWidth(6, 100)
        self.tree.setColumnWidth(7, 65)
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

    def _on_band_change(self):
        band_data = self.band_combo.currentData()
        mapping = {
            "abg": ("2.4 + 5 GHz", "badge_yellow"),
            "a":   ("5 GHz only",   "badge_blue"),
            "bg":  ("2.4 GHz only", "badge_green"),
        }
        text, obj = mapping.get(band_data, ("?", "badge_blue"))
        self.band_badge.setText(text)
        self.band_badge.setObjectName(obj)
        self.band_badge.style().unpolish(self.band_badge)
        self.band_badge.style().polish(self.band_badge)

    def _toggle_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self._stop_scan()
        else:
            self._start_scan()

    def _start_scan(self):
        iface = self.mon_iface_edit.text().strip() or self.mon_iface
        band = self.band_combo.currentData() or "abg"
        self._net_counter = 0
        self.scan_thread = ScanThread(iface, band)
        self.scan_thread.network_found.connect(self._on_network)
        self.scan_thread.client_found.connect(self._on_client)
        self.scan_thread.raw_output.connect(self.console.append_raw)
        self.scan_thread.start()

        self._set_scan_btn_state(scanning=True)
        band_label = self.band_combo.currentText().split("(")[0].strip()
        self.status_lbl.setText(f"Scanning on {iface} — {band_label}…")
        self.status_bar.set_status(f"Scanning {iface} [{band_label}]", PALETTE["yellow"])
        self.console.append_info(f"Scan started on {iface} | Band: {band_label}")

    def _stop_scan(self):
        if self.scan_thread:
            self.scan_thread.stop()
            self.scan_thread.wait()
        self._set_scan_btn_state(scanning=False)
        self.status_lbl.setText(f"Scan stopped. {len(self._networks)} networks found.")
        self.status_bar.set_status("Ready")
        self.console.append_info("Scan stopped.")

    def _set_scan_btn_state(self, scanning: bool):
        if scanning:
            self.scan_btn.setText("■  Stop Scan")
            self.scan_btn.setObjectName("danger")
        else:
            self.scan_btn.setText("▶  Start Scan")
            self.scan_btn.setObjectName("primary")
        self.scan_btn.style().unpolish(self.scan_btn)
        self.scan_btn.style().polish(self.scan_btn)

    @staticmethod
    def _power_color(power):
        try:
            p = int(power)
            if p > -50:   return QColor(PALETTE["green"])
            if p > -70:   return QColor(PALETTE["yellow"])
            return QColor(PALETTE["red"])
        except Exception:
            return QColor(PALETTE["subtext0"])

    @staticmethod
    def _channel_to_band(channel_str):
        try:
            return "5 GHz" if int(channel_str.strip()) > 14 else "2.4 GHz"
        except Exception:
            return "?"

    def _on_network(self, net):
        bssid = net["bssid"]
        band = self._channel_to_band(net.get("channel", "0"))
        net["band"] = band

        if bssid not in self._net_items:
            self._net_counter += 1
            net["_id"] = self._net_counter
            self._networks[bssid] = net
            item = QTreeWidgetItem([
                str(self._net_counter), bssid,
                net["ssid"] or "<Hidden>",
                net["power"], net["channel"], band, net["privacy"], "0"
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, net)
            item.setForeground(1, QColor(PALETTE["blue"]))
            item.setForeground(3, self._power_color(net["power"]))
            item.setForeground(4, QColor(PALETTE["sapphire"]))
            item.setForeground(5, QColor(PALETTE["peach"] if band == "5 GHz" else PALETTE["teal"]))
            item.setForeground(6, QColor(PALETTE["peach"]))
            self.tree.addTopLevelItem(item)
            self._net_items[bssid] = item
            self._update_badge()
        else:
            item = self._net_items[bssid]
            item.setText(3, net["power"])
            item.setForeground(3, self._power_color(net["power"]))

    def _on_client(self, sta):
        ap_bssid = sta.get("ap_bssid", "").strip()
        sta_mac = sta["bssid"]
        parent_item = self._net_items.get(ap_bssid)
        if not parent_item:
            return

        if sta_mac in self._client_items:
            self._client_items[sta_mac].setText(3, sta.get("power", ""))
        else:
            child = QTreeWidgetItem(["", f"  └─ {sta_mac}",
                                     f"Client  [{sta_mac[:8].upper()}]",
                                     sta.get("power", ""), "", "", "", ""])
            child.setForeground(1, QColor(PALETTE["teal"]))
            child.setForeground(2, QColor(PALETTE["overlay1"]))
            child.setForeground(3, self._power_color(sta.get("power", "-100")))
            parent_item.addChild(child)
            parent_item.setExpanded(True)
            parent_item.setText(7, str(parent_item.childCount()))
            self._client_items[sta_mac] = child
            self.client_count_badge.setText(f"{len(self._client_items)} Clients")

    def _update_badge(self):
        self.network_count_badge.setText(f"{self.tree.topLevelItemCount()} Networks")

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

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background:{PALETTE['mantle']}; color:{PALETTE['text']};
                     border:1px solid {PALETTE['surface1']}; border-radius:6px; padding:4px; }}
            QMenu::item {{ padding:6px 20px; border-radius:4px; }}
            QMenu::item:selected {{ background:{PALETTE['surface0']}; color:{PALETTE['mauve']}; }}
        """)
        bssid = item.text(1).replace("└─ ", "").strip()
        copy_bssid = menu.addAction("📋 Copy BSSID")
        copy_bssid.triggered.connect(lambda: QApplication.clipboard().setText(bssid))
        net = item.data(0, Qt.ItemDataRole.UserRole)
        if net:
            copy_all = menu.addAction("📋 Copy All Info")
            copy_all.triggered.connect(lambda: QApplication.clipboard().setText(
                f"BSSID: {net.get('bssid','')}\nSSID: {net.get('ssid','')}\n"
                f"Channel: {net.get('channel','')}\nPower: {net.get('power','')} dBm\n"
                f"Security: {net.get('privacy','')}"
            ))
            set_tgt = menu.addAction("🎯 Set as Target")
            set_tgt.triggered.connect(self._set_target)
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def get_networks(self):
        return sorted(self._networks.values(), key=lambda n: n.get("_id", 0))

    def _clear(self):
        self.tree.clear()
        self._networks.clear()
        self._net_items.clear()
        self._client_items.clear()
        self._net_counter = 0
        self._update_badge()
        self.client_count_badge.setText("0 Clients")
        self.console.append_info("Cleared scan results.")


# ---------------------------------------------------------------------------
# Handshake capture tab
# ---------------------------------------------------------------------------
class HandshakeTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.worker = None
        self._networks = []
        self._handshake_detected = False
        self._build_ui()

    def set_target(self, bssid, ssid, channel):
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

        sep = QFrame(); sep.setObjectName("separator")
        layout.addWidget(sep)

        card = QFrame(); card.setObjectName("card")
        grid = QGridLayout(card)
        grid.setContentsMargins(22, 18, 22, 18)
        grid.setSpacing(12)

        grid.addWidget(QLabel("Target Network:"), 0, 0)
        self.wifi_combo = QComboBox()
        self.wifi_combo.setMinimumWidth(320)
        grid.addWidget(self.wifi_combo, 0, 1, 1, 2)

        grid.addWidget(QLabel("Monitor Interface:"), 1, 0)
        self.iface_edit = QLineEdit("wlan0mon")
        self.iface_edit.setFixedWidth(140)
        grid.addWidget(self.iface_edit, 1, 1)

        grid.addWidget(QLabel("Save As:"), 2, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("handshake_name (e.g. home_wifi)")
        grid.addWidget(self.name_edit, 2, 1, 1, 2)

        grid.addWidget(QLabel("Save Path:"), 3, 0)
        path_lbl = QLabel(str(CAPTURED_DIR.resolve()))
        path_lbl.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;")
        grid.addWidget(path_lbl, 3, 1, 1, 2)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        self.capture_btn = QPushButton("▶  Start Capture")
        self.capture_btn.setObjectName("primary")
        self.capture_btn.setMinimumHeight(42); self.capture_btn.setMinimumWidth(180)
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

        self._handshake_detected = False
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

        self._set_capture_btn(capturing=True)
        self.status_bar.set_status("Capturing handshake…", PALETTE["yellow"])
        self.console.append_info(f"Capturing from {net.get('ssid','')} [{bssid}] → {save_path}.*")

    def _handle_output(self, text, _):
        self.console.append_raw(text)
        if not self._handshake_detected and any(
                p in text.lower() for p in ["wpa handshake", "handshake", "4-way handshake", "eapol"]):
            self._handshake_detected = True
            self.console.append_success("🎉 Handshake captured!")
            self.status_bar.set_status("Handshake captured!", PALETTE["green"])

    def _stop(self):
        if self.worker:
            self.worker.stop()
        self._set_capture_btn(capturing=False)
        self.status_bar.set_status("Ready")

    def _on_done(self, rc):
        self._set_capture_btn(capturing=False)
        self.status_bar.set_status("Ready")

    def _set_capture_btn(self, capturing: bool):
        if capturing:
            self.capture_btn.setText("■  Stop Capture")
            self.capture_btn.setObjectName("danger")
        else:
            self.capture_btn.setText("▶  Start Capture")
            self.capture_btn.setObjectName("primary")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)


# ---------------------------------------------------------------------------
# Attack thread (throttled output)
# ---------------------------------------------------------------------------
class AttackThread(QThread):
    output = pyqtSignal(str, str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.process = None
        self._stop = False
        self._line_count = 0

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._stop:
                    break
                self._line_count += 1
                # Show first 20 lines, then every 10th (reduce UI flooding)
                if line.strip() and (self._line_count <= 20 or self._line_count % 10 == 0):
                    self.output.emit(line.rstrip(), "raw")
            self.process.wait()
            self.finished.emit(self.process.returncode)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._stop = True
        if self.process:
            try:
                subprocess.run(["sudo", "kill", "-9", str(self.process.pid)],
                               capture_output=True, timeout=2)
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try: self.process.kill()
                except Exception: pass


# ---------------------------------------------------------------------------
# Deauth tab
# ---------------------------------------------------------------------------
class DeauthTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.worker = None
        self._target_bssid = ""
        self._target_channel = ""
        self._build_ui()

    def set_target(self, bssid, ssid, channel):
        self._target_bssid = bssid
        self._target_channel = channel
        self.bssid_edit.setText(bssid)
        self.channel_edit.setText(channel)
        self.target_info.setText(f"Target: {ssid}  [{bssid}]  CH:{channel}")
        self.target_info.setStyleSheet(f"color:{PALETTE['green']};font-size:11px;font-weight:700;")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Deauthentication Attack")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        layout.addWidget(sep)

        self.target_info = QLabel("No target selected — use Scanner tab to set target.")
        self.target_info.setStyleSheet(f"color:{PALETTE['overlay0']};font-size:11px;")
        layout.addWidget(self.target_info)

        card = QFrame(); card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 20, 22, 20)
        cl.setSpacing(12)

        info_lbl = QLabel("⚠️  Deauthentication sends disconnect packets to clients on the target AP.")
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet(
            f"color:{PALETTE['yellow']};font-size:11px;padding:10px;"
            f"background:{PALETTE['surface0']};border-radius:6px;")
        cl.addWidget(info_lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Target AP BSSID:"), 0, 0)
        self.bssid_edit = QLineEdit()
        self.bssid_edit.setPlaceholderText("Auto-filled from Scanner")
        grid.addWidget(self.bssid_edit, 0, 1)

        grid.addWidget(QLabel("Channel:"), 1, 0)
        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText("Auto-filled")
        self.channel_edit.setFixedWidth(80)
        grid.addWidget(self.channel_edit, 1, 1, Qt.AlignmentFlag.AlignLeft)

        grid.addWidget(QLabel("Interface:"), 2, 0)
        self.iface_edit = QLineEdit("wlan0mon")
        self.iface_edit.setFixedWidth(140)
        grid.addWidget(self.iface_edit, 2, 1, Qt.AlignmentFlag.AlignLeft)

        grid.addWidget(QLabel("Target Client:"), 3, 0)
        hbox = QHBoxLayout()
        self.client_edit = QLineEdit()
        self.client_edit.setPlaceholderText("Empty = broadcast to all clients")
        self.client_edit.setEnabled(False)
        self.broadcast_check = QCheckBox("Broadcast (all clients)")
        self.broadcast_check.setChecked(True)
        self.broadcast_check.toggled.connect(lambda checked: self.client_edit.setEnabled(not checked))
        hbox.addWidget(self.client_edit)
        hbox.addWidget(self.broadcast_check)
        grid.addLayout(hbox, 3, 1)
        cl.addLayout(grid)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶  Start Deauth Attack")
        self.start_btn.setObjectName("danger")
        self.start_btn.setMinimumHeight(42); self.start_btn.setMinimumWidth(200)
        self.start_btn.clicked.connect(self._toggle)
        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        layout.addWidget(card)
        self.console = ConsoleOutput()
        layout.addWidget(self.console)

    _MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')

    def _toggle(self):
        if self.worker and self.worker.isRunning():
            self._stop()
        else:
            self._start()

    def _start(self):
        bssid = self.bssid_edit.text().strip() or self._target_bssid
        iface = self.iface_edit.text().strip() or "wlan0mon"
        channel = self.channel_edit.text().strip() or self._target_channel
        client = "" if self.broadcast_check.isChecked() else self.client_edit.text().strip()

        if not bssid:
            self.console.append_warn("No target BSSID. Set a target in the Scanner tab first.")
            return
        if not self._MAC_RE.match(bssid):
            self.console.append_error("Invalid BSSID format. Must be XX:XX:XX:XX:XX:XX")
            return
        if client and not self._MAC_RE.match(client):
            self.console.append_error("Invalid client BSSID format.")
            return

        if channel:
            try:
                subprocess.run(["sudo", "iwconfig", iface, "channel", channel],
                               capture_output=True, check=False, timeout=2)
            except Exception:
                pass

        cmd = ["sudo", "aireplay-ng", "--deauth", "0", "-a", bssid]
        target_desc = f"client {client}" if client else "all clients (broadcast)"
        if client:
            cmd += ["-c", client]
        cmd.append(iface)

        self.worker = AttackThread(cmd)
        self.worker.output.connect(lambda t, _: self.console.append_raw(t))
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self.console.append_error)
        self.worker.start()

        self._set_btn_state(running=True)
        self.console.append_info(f"Deauth attack started → {bssid} targeting {target_desc}")
        self.status_bar.set_status(f"Deauth active [{target_desc}]", PALETTE["red"])

    def _stop(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self._set_btn_state(running=False)
        self.console.append_warn("Deauth attack stopped.")
        self.status_bar.set_status("Ready")

    def _on_done(self, rc):
        self._set_btn_state(running=False)
        self.status_bar.set_status("Ready")
        if rc != 0:
            self.console.append_error(f"Deauth process exited with code {rc}")

    def _set_btn_state(self, running: bool):
        if running:
            self.start_btn.setText("■  Stop Attack")
            self.start_btn.setObjectName("warning")
        else:
            self.start_btn.setText("▶  Start Deauth Attack")
            self.start_btn.setObjectName("danger")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)


# ---------------------------------------------------------------------------
# Crack & Convert tab  ← UNIFIED: one file picker, three actions
# ---------------------------------------------------------------------------
class CrackConvertTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.crack_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Password Cracking & File Conversion")
        title.setObjectName("section")
        title.setFont(QFont("JetBrains Mono", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        layout.addWidget(sep)

        # ── Single file selection card ──────────────────────────────────────
        file_card = QFrame(); file_card.setObjectName("card")
        fg = QGridLayout(file_card)
        fg.setContentsMargins(22, 18, 22, 18)
        fg.setSpacing(12)

        fg.addWidget(QLabel(".cap / .pcap File:"), 0, 0)
        cap_row = QHBoxLayout()
        self.cap_edit = QLineEdit()
        self.cap_edit.setPlaceholderText("/path/to/capture.cap")
        self.cap_browse = QPushButton("Browse")
        self.cap_browse.setFixedWidth(80)
        self.cap_browse.clicked.connect(self._browse_cap)
        cap_row.addWidget(self.cap_edit)
        cap_row.addWidget(self.cap_browse)
        fg.addLayout(cap_row, 0, 1)

        fg.addWidget(QLabel("Wordlist (for crack):"), 1, 0)
        wl_row = QHBoxLayout()
        self.wl_edit = QLineEdit("/usr/share/wordlists/rockyou.txt")
        self.wl_browse = QPushButton("Browse")
        self.wl_browse.setFixedWidth(80)
        self.wl_browse.clicked.connect(self._browse_wordlist)
        wl_row.addWidget(self.wl_edit)
        wl_row.addWidget(self.wl_browse)
        fg.addLayout(wl_row, 1, 1)

        fg.addWidget(QLabel("Output Directory:"), 2, 0)
        out_row = QHBoxLayout()
        self.out_dir_edit = QLineEdit(str(CAPTURED_DIR.resolve()))
        self.out_dir_browse = QPushButton("Browse")
        self.out_dir_browse.setFixedWidth(80)
        self.out_dir_browse.clicked.connect(self._browse_output_dir)
        out_row.addWidget(self.out_dir_edit)
        out_row.addWidget(self.out_dir_browse)
        fg.addLayout(out_row, 2, 1)

        layout.addWidget(file_card)

        # ── Action buttons ──────────────────────────────────────────────────
        action_card = QFrame(); action_card.setObjectName("card")
        al = QVBoxLayout(action_card)
        al.setContentsMargins(22, 16, 22, 16)
        al.setSpacing(10)

        action_hdr = QLabel("Select an Action")
        action_hdr.setStyleSheet(f"color:{PALETTE['subtext0']};font-size:11px;font-weight:600;")
        al.addWidget(action_hdr)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.crack_btn = QPushButton("▶  Crack Password")
        self.crack_btn.setObjectName("primary")
        self.crack_btn.setMinimumHeight(42)
        self.crack_btn.setToolTip("Run aircrack-ng with the selected wordlist against this capture")
        self.crack_btn.clicked.connect(self._toggle_crack)

        self.hc_btn = QPushButton("→ Export Hashcat (.hc22000)")
        self.hc_btn.setObjectName("warning")
        self.hc_btn.setMinimumHeight(42)
        self.hc_btn.setToolTip("Convert capture to Hashcat WPA2 format using hcxpcapngtool")
        self.hc_btn.clicked.connect(self._to_hashcat)

        self.jtr_btn = QPushButton("→ Export John the Ripper (.hccap)")
        self.jtr_btn.setObjectName("success")
        self.jtr_btn.setMinimumHeight(42)
        self.jtr_btn.setToolTip("Convert capture to John the Ripper format using aircrack-ng -J")
        self.jtr_btn.clicked.connect(self._to_john)

        for b in [self.crack_btn, self.hc_btn, self.jtr_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch()
        al.addLayout(btn_row)

        layout.addWidget(action_card)

        # ── Console ─────────────────────────────────────────────────────────
        self.console = ConsoleOutput()
        layout.addWidget(self.console)

    # ── File browsing ───────────────────────────────────────────────────────
    def _browse_cap(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .cap / .pcap File", str(Path.home()),
            "Capture Files (*.cap *.pcap);;All Files (*)")
        if path:
            self.cap_edit.setText(path)

    def _browse_wordlist(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist", str(Path.home()),
            "Text Files (*.txt);;All Files (*)")
        if path:
            self.wl_edit.setText(path)

    def _browse_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(Path.home()))
        if d:
            self.out_dir_edit.setText(d)

    # ── Validation helper ───────────────────────────────────────────────────
    def _validate_cap(self):
        cap = self.cap_edit.text().strip()
        if not cap:
            self.console.append_warn("Please specify a .cap file.")
            return None
        if not os.path.exists(cap):
            self.console.append_error(f"File not found: {cap}")
            return None
        return cap

    def _get_out_dir(self):
        return self.out_dir_edit.text().strip() or str(CAPTURED_DIR.resolve())

    # ── Crack ────────────────────────────────────────────────────────────────
    def _toggle_crack(self):
        if self.crack_worker and self.crack_worker.isRunning():
            self._stop_crack()
        else:
            self._start_crack()

    def _start_crack(self):
        cap = self._validate_cap()
        if not cap:
            return
        wl = self.wl_edit.text().strip()
        if not wl:
            self.console.append_warn("Please specify a wordlist.")
            return
        if not os.path.exists(wl):
            self.console.append_error(f"Wordlist not found: {wl}")
            return

        self.crack_worker = WorkerThread(["sudo", "aircrack-ng", cap, "-w", wl])
        self.crack_worker.output.connect(self._handle_crack_output)
        self.crack_worker.finished.connect(self._on_crack_done)
        self.crack_worker.error.connect(self.console.append_error)
        self.crack_worker.start()

        self._set_crack_btn(cracking=True)
        self.status_bar.set_status("Cracking…", PALETTE["yellow"])
        self.console.append_info(f"aircrack-ng started: {cap}")

    def _handle_crack_output(self, text, _):
        if "KEY FOUND" in text.upper():
            self.console.append_success(text)
            self.status_bar.set_status("KEY FOUND!", PALETTE["green"])
        elif any(k in text.lower() for k in ("failed", "not found")):
            self.console.append_warn(text)
        else:
            self.console.append_raw(text)

    def _stop_crack(self):
        if self.crack_worker:
            self.crack_worker.stop()
        self._set_crack_btn(cracking=False)
        self.status_bar.set_status("Ready")
        self.console.append_warn("Cracking stopped.")

    def _on_crack_done(self, rc):
        self._set_crack_btn(cracking=False)
        self.status_bar.set_status("Ready")
        msg = "Aircrack-ng finished." if rc == 0 else f"Aircrack-ng exited with code {rc}"
        (self.console.append_success if rc == 0 else self.console.append_warn)(msg)

    def _set_crack_btn(self, cracking: bool):
        if cracking:
            self.crack_btn.setText("■  Stop Cracking")
            self.crack_btn.setObjectName("danger")
        else:
            self.crack_btn.setText("▶  Crack Password")
            self.crack_btn.setObjectName("primary")
        self.crack_btn.style().unpolish(self.crack_btn)
        self.crack_btn.style().polish(self.crack_btn)
        self.hc_btn.setEnabled(not cracking)
        self.jtr_btn.setEnabled(not cracking)

    # ── Conversion helpers ───────────────────────────────────────────────────
    def _run_conversion(self, cmd, expected_output, label):
        """Runs a conversion command and reports result."""
        w = WorkerThread(cmd)
        w.output.connect(lambda t, _: self.console.append_raw(t))
        w.finished.connect(lambda rc: (
            self.console.append_success(f"{label} saved → {expected_output}")
            if rc == 0 else
            self.console.append_error(f"{label} conversion failed (code {rc})")
        ))
        w.error.connect(self.console.append_error)
        w.start()

    def _to_hashcat(self):
        cap = self._validate_cap()
        if not cap:
            return
        out_dir = self._get_out_dir()
        stem = Path(cap).stem
        out = os.path.join(out_dir, stem + ".hc22000")

        if shutil.which("hcxpcapngtool"):
            cmd = ["sudo", "hcxpcapngtool", "-o", out, cap]
        else:
            self.console.append_warn("hcxpcapngtool not found; using aircrack-ng fallback (limited compatibility).")
            cmd = ["sudo", "aircrack-ng", cap, "-J", os.path.join(out_dir, stem)]

        self.console.append_info(f"Converting to Hashcat format → {out}")
        self._run_conversion(cmd, out, "Hashcat file")

    def _to_john(self):
        cap = self._validate_cap()
        if not cap:
            return
        out_dir = self._get_out_dir()
        stem = Path(cap).stem
        out_base = os.path.join(out_dir, stem)
        out = out_base + ".hccap"

        cmd = ["sudo", "aircrack-ng", cap, "-J", out_base]
        self.console.append_info(f"Converting to John the Ripper format → {out}")
        self._run_conversion(cmd, out, "John the Ripper file")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetShade — Wi-Fi Security Testing Framework")
        self.setMinimumSize(1100, 780)
        self.resize(1280, 860)
        self._build_ui()
        self._set_pointer_cursors()

    def _set_pointer_cursors(self):
        for cls in (QPushButton, QComboBox):
            for widget in self.findChildren(cls):
                widget.setCursor(Qt.CursorShape.PointingHandCursor)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.banner = AnimatedBanner()
        root.addWidget(self.banner)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.setSpacing(10)

        self.status_bar_widget = StatusBar()
        cl.addWidget(self.status_bar_widget)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.card_tab   = WifiCardTab(self.status_bar_widget)
        self.scan_tab   = ScanTab(self.status_bar_widget)
        self.hs_tab     = HandshakeTab(self.status_bar_widget)
        self.attack_tab = DeauthTab(self.status_bar_widget)
        self.crack_tab  = CrackConvertTab(self.status_bar_widget)

        self.tabs.addTab(self.card_tab,   "⚡ Card Control")
        self.tabs.addTab(self.scan_tab,   "📡 Scanner")
        self.tabs.addTab(self.hs_tab,     "🤝 Handshake")
        self.tabs.addTab(self.attack_tab, "💥 Deauth")
        self.tabs.addTab(self.crack_tab,  "🔓 Crack & Convert")

        self.card_tab.mode_changed.connect(self._on_mode_changed)
        self.scan_tab.target_selected.connect(self._on_target_selected)

        cl.addWidget(self.tabs)
        root.addWidget(content)

    def _on_mode_changed(self, iface, mon_iface):
        self.scan_tab.set_monitor_iface(mon_iface)
        self.scan_tab.mon_iface_edit.setText(mon_iface)
        self.hs_tab.iface_edit.setText(mon_iface)
        self.attack_tab.iface_edit.setText(mon_iface)

    def _on_target_selected(self, bssid, ssid, channel):
        self.hs_tab.update_networks(self.scan_tab.get_networks())
        self.hs_tab.set_target(bssid, ssid, channel)
        self.attack_tab.set_target(bssid, ssid, channel)
        self.status_bar_widget.set_target(ssid, bssid)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    if os.geteuid() != 0:
        print("[NetShade] Run with sudo for full functionality: sudo python3 netshade.py")

    if not os.environ.get('XDG_RUNTIME_DIR'):
        runtime_dir = f"/tmp/runtime-{os.getuid()}"
        os.makedirs(runtime_dir, exist_ok=True)
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir

    app = QApplication(sys.argv)
    app.setApplicationName("NetShade")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Rupen Maharjan")
    app.setStyleSheet(STYLESHEET)

    pal = app.palette()
    color_map = {
        QPalette.ColorRole.Window:          PALETTE["base"],
        QPalette.ColorRole.WindowText:      PALETTE["text"],
        QPalette.ColorRole.Base:            PALETTE["mantle"],
        QPalette.ColorRole.AlternateBase:   PALETTE["crust"],
        QPalette.ColorRole.Text:            PALETTE["text"],
        QPalette.ColorRole.Button:          PALETTE["surface0"],
        QPalette.ColorRole.ButtonText:      PALETTE["text"],
        QPalette.ColorRole.Highlight:       PALETTE["mauve"],
        QPalette.ColorRole.HighlightedText: PALETTE["crust"],
    }
    for role, color in color_map.items():
        pal.setColor(role, QColor(color))
    app.setPalette(pal)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()