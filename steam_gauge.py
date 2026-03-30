# steam_gauge.py
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QFont
import math

class SteamGauge(QWidget):
    """A simple 270° steam gauge with animated needle and ticks."""

    value_changed = Signal(float)

    def __init__(self, min_value=0, max_value=30, parent=None):
        super().__init__(parent)

        # Values
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self._animated_value = min_value

        # Gauge geometry
        self.start_angle = 270
        self.sweep_angle = 270

        # Timer for auto-update
        self.fetch_value_func = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_value)
        self.timer.start(1000)

        # Animation setup
        self.anim = QPropertyAnimation(self, b"animatedValue")
        self.anim.setDuration(700)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)

    # ---------------- Properties ----------------
    def getAnimatedValue(self):
        return self._animated_value

    def setAnimatedValue(self, value):
        self._animated_value = value
        self.update()

    animatedValue = Property(float, getAnimatedValue, setAnimatedValue)

    # ---------------- Public Methods ----------------
    def set_fetch_function(self, func):
        self.fetch_value_func = func

    def refresh_value(self):
        if self.fetch_value_func:
            self.set_value(self.fetch_value_func())

    def set_value(self, value: float):
        value = max(self.min_value, min(self.max_value, value))
        if value != self.current_value:
            self.current_value = value
            self.value_changed.emit(value)
            self.anim.stop()
            self.anim.setStartValue(self._animated_value)
            self.anim.setEndValue(value)
            self.anim.start()

    # ---------------- Painting ----------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Geometry
        w, h = self.width(), self.height()
        radius = min(w, h) * 0.45
        cx, cy = w / 2, h / 2

        # Current sweep fraction
        fraction = (self._animated_value - self.min_value) / (self.max_value - self.min_value)
        current_sweep = fraction * self.sweep_angle

        # ---------------- Background Dial ----------------
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(235, 235, 235, 80))
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # ---------------- Ticks & Numbers ----------------
        tick_interval = 5
        for value in range(self.min_value, self.max_value + 1, tick_interval):
            t = (value - self.min_value) / (self.max_value - self.min_value)
            angle_deg = self.start_angle - t * self.sweep_angle
            angle_rad = math.radians(angle_deg)

            # Tick line
            x1 = cx + radius * 0.90 * math.cos(angle_rad)
            y1 = cy - radius * 0.90 * math.sin(angle_rad)
            x2 = cx + radius * 0.75 * math.cos(angle_rad)
            y2 = cy - radius * 0.75 * math.sin(angle_rad)
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(x1, y1, x2, y2)

            # Number
            tx = cx + radius * 0.60 * math.cos(angle_rad)
            ty = cy - radius * 0.60 * math.sin(angle_rad)
            painter.setFont(QFont("Arial", int(radius * 0.12)))
            painter.drawText(int(tx) - 10, int(ty) + 10, str(value))

        # ---------------- Needle ----------------
        needle_angle_deg = self.start_angle - current_sweep
        needle_angle_rad = math.radians(needle_angle_deg)
        nx = cx + radius * 0.70 * math.cos(needle_angle_rad)
        ny = cy - radius * 0.70 * math.sin(needle_angle_rad)
        painter.setPen(QPen(Qt.red, 3))
        painter.drawLine(cx, cy, nx, ny)

        # ---------------- Center Hub ----------------
        painter.setBrush(Qt.black)
        painter.drawEllipse(cx - 6, cy - 6, 12, 12)
