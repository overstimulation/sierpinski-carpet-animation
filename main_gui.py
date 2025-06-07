import sys

from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from main import create_sierpinski_animation


class PowerOfThreeSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.allowed_sizes = [3**n for n in range(1, 11)]  # 3, 9, ..., 3^10
        self.setRange(self.allowed_sizes[0], self.allowed_sizes[-1])
        self.setValue(self.allowed_sizes[7])  # Default to 2187 (3^7)
        self.setKeyboardTracking(False)

    def keyPressEvent(self, event):
        # Ignore all key presses to block keyboard input
        event.ignore()

    def stepBy(self, steps):
        current = self.value()
        try:
            idx = self.allowed_sizes.index(current)
        except ValueError:
            idx = 0
        idx = max(0, min(idx + steps, len(self.allowed_sizes) - 1))
        self.setValue(self.allowed_sizes[idx])

    def validate(self, text, pos):
        try:
            val = int(text)
            if val in self.allowed_sizes:
                return (QValidator.State.Acceptable, text, pos)
            else:
                return (QValidator.State.Intermediate, text, pos)
        except ValueError:
            return (QValidator.State.Invalid, text, pos)

    def valueFromText(self, text):
        try:
            val = int(text)
            if val in self.allowed_sizes:
                return val
            else:
                return self.value()
        except ValueError:
            return self.value()

    def textFromValue(self, value):
        return str(value)


class SierpinskiGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sierpiński Carpet Animation Generator by @overstimulation on GitHub")
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)
        layout = QVBoxLayout()

        # Maximum recursion depth
        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("Maximum recursion depth:"))
        self.order_spin = QSpinBox()
        self.order_spin.setRange(1, 1000)
        self.order_spin.setValue(15)
        order_layout.addWidget(self.order_spin)
        layout.addLayout(order_layout)

        # Carpet size as 3^n (only powers of 3 allowed, no exponent shown)
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Carpet size as 3^n:"))
        self.size_spin = PowerOfThreeSpinBox()
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)

        # Frames for transition between orders
        frames_layout = QHBoxLayout()
        frames_layout.addWidget(QLabel("Frames per order:"))
        self.frames_spin = QSpinBox()
        self.frames_spin.setRange(1, 1000)
        self.frames_spin.setValue(15)
        frames_layout.addWidget(self.frames_spin)
        layout.addLayout(frames_layout)

        # Speed of the animation
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Frames per second:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 1000)
        self.fps_spin.setValue(10)
        fps_layout.addWidget(self.fps_spin)
        layout.addLayout(fps_layout)

        # Output filename
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Output file name (without extension):"))
        self.file_edit = QLineEdit("sierpinski_carpet_animation")
        file_layout.addWidget(self.file_edit)
        layout.addLayout(file_layout)

        # Output format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "GIF"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Run button
        self.run_button = QPushButton("Create animation")
        self.run_button.clicked.connect(self.run_animation)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_animation(self):
        self.run_button.setEnabled(False)
        try:
            size = self.size_spin.value()
            as_mp4 = self.format_combo.currentText() == "MP4"
            create_sierpinski_animation(
                max_order=self.order_spin.value(),
                frames_per_order=self.frames_spin.value(),
                size=size,
                output_filename=self.file_edit.text(),
                as_mp4=as_mp4,
                fps=self.fps_spin.value(),
            )
        finally:
            self.run_button.setEnabled(True)


# Main execution block
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SierpinskiGUI()
    window.show()
    sys.exit(app.exec())
