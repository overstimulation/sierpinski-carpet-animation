import os
import sys
import warnings

from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QImage, QPixmap, QValidator
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from main_cli import create_sierpinski_animation

# Author: overstimulation
# Repo: https://github.com/overstimulation/sierpinski-carpet-animation

# Suppress warnings
warnings.filterwarnings("ignore")  # Suppress all warnings


class PowerOfThreeSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.allowed_sizes = [3**n for n in range(1, 11)]  # 3, 9, ..., 3^10
        self.setRange(self.allowed_sizes[0], self.allowed_sizes[-1])
        self.setValue(self.allowed_sizes[6])  # Default to 2187 (3^7)
        self.setKeyboardTracking(False)

    def keyPressEvent(self, event):
        event.ignore()  # Ignore all key presses to block keyboard input

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
        self.setWindowTitle("Sierpiński Carpet Animation Generator by @overstimulation")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        layout = QVBoxLayout()

        # Add clickable repo link at the top
        repo_label = QLabel(
            '<a href="https://github.com/overstimulation/sierpinski-carpet-animation">'
            "Contribute or view source on GitHub</a>"
        )
        repo_label.setOpenExternalLinks(True)
        repo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(repo_label)

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

        # Live preview label
        self.preview_label = QLabel("Live preview will appear here")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(220)
        layout.addWidget(self.preview_label)

        # Phase label above progress bar
        self.phase_label = QLabel("Idle")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.phase_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Run button
        self.run_button = QPushButton("Create animation")
        self.run_button.clicked.connect(self.run_animation)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def update_preview(self, np_array):
        # Convert numpy array to QImage and display in QLabel
        if np_array is None:
            self.preview_label.setText("Live preview will appear here")
            return
        h, w = np_array.shape
        # Convert 1/0 to 255/0 grayscale
        img = (np_array * 255).astype("uint8")
        qimg = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg).scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio)
        self.preview_label.setPixmap(pixmap)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_phase(self, text):
        self.phase_label.setText(text)

    def run_animation(self):
        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.update_preview(None)
        self.phase_label.setText("Starting...")
        # Start worker thread for animation generation
        self.worker = AnimationWorker(
            max_order=self.order_spin.value(),
            frames_per_order=self.frames_spin.value(),
            size=self.size_spin.value(),
            output_filename=self.file_edit.text(),
            as_mp4=self.format_combo.currentText() == "MP4",
            fps=self.fps_spin.value(),
        )
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.preview_signal.connect(self.update_preview)
        self.worker.phase_signal.connect(self.update_phase)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_error(self, error_msg):
        self.run_button.setEnabled(True)
        QMessageBox.critical(self, "Error during animation generation", error_msg)
        self.phase_label.setText("Error")

    def on_worker_finished(self):
        self.run_button.setEnabled(True)
        # Show pop-up dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Animation Complete")
        msg.setText("The animation has been created successfully.")
        ok_button = msg.addButton("Okay", QMessageBox.ButtonRole.AcceptRole)
        open_button = msg.addButton("Open file", QMessageBox.ButtonRole.ActionRole)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

        if msg.clickedButton() == open_button:
            # Determine file extension
            ext = ".mp4" if self.format_combo.currentText() == "MP4" else ".gif"
            filename = self.file_edit.text() + ext
            filepath = os.path.abspath(filename)
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))


class AnimationWorker(QThread):
    progress_signal = Signal(int)
    preview_signal = Signal(object)  # numpy array
    finished_signal = Signal()
    phase_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, max_order, frames_per_order, size, output_filename, as_mp4, fps):
        super().__init__()
        self.max_order = max_order
        self.frames_per_order = frames_per_order
        self.size = size
        self.output_filename = output_filename
        self.as_mp4 = as_mp4
        self.fps = fps

    def run(self):
        def progress_callback(val):
            self.progress_signal.emit(val)

        def preview_callback(np_array):
            self.preview_signal.emit(np_array)

        def phase_callback(text):
            self.phase_signal.emit(text)

        # Pass phase_callback to create_sierpinski_animation
        try:
            create_sierpinski_animation(
                max_order=self.max_order,
                frames_per_order=self.frames_per_order,
                size=self.size,
                output_filename=self.output_filename,
                as_mp4=self.as_mp4,
                fps=self.fps,
                progress_callback=progress_callback,
                preview_callback=preview_callback,
                phase_callback=phase_callback,
            )
            self.phase_signal.emit("Done")
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))


# Main execution block
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SierpinskiGUI()
    window.show()
    sys.exit(app.exec())
