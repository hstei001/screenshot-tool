import sys
import mss
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QHBoxLayout,
                           QFileDialog, QMessageBox, QDialog, QComboBox)
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QImage
from editor import EditorDialog
import time
from PIL import Image

class VideoRecorder(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.temp_file = None
    
    def run(self):
        try:
            import cv2
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                self.temp_file = f.name
            
            # Initialize screen capture
            with mss.mss() as sct:
                # Get monitor
                monitor = sct.monitors[1]  # Primary monitor
                
                # Get the screen size
                width = monitor["width"]
                height = monitor["height"]
                
                # Initialize video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(self.temp_file, fourcc, 30.0, (width, height))
                
                self.running = True
                while self.running:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    
                    # Convert to numpy array
                    frame = np.array(screenshot)
                    
                    # Convert from BGRA to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Write frame
                    out.write(frame)
                
                # Release everything
                out.release()
                
                # Emit the temporary file path
                self.finished.emit(self.temp_file)
                
        except Exception as e:
            print(f"Error recording video: {e}")
            if self.temp_file and os.path.exists(self.temp_file):
                os.remove(self.temp_file)
    
    def stop(self):
        self.running = False

class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screenshot_delay = 0  # Default delay in seconds
        self.countdown_timer = None
        self.countdown_remaining = 0
        self.video_recorder = VideoRecorder()
        self.video_recorder.finished.connect(self.recording_finished)
        self.is_recording = False
        self.last_position = None  # Store the last position
        self.initUI()

    def initUI(self):
        """Initialize the UI"""
        # Set window flags to make it frameless and always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_widget)
        
        # Create title bar
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add title label
        title_label = QLabel("Screenshot Tool")
        title_label.setObjectName("titleLabel")
        title_bar_layout.addWidget(title_label)
        
        # Add spacer
        title_bar_layout.addStretch()
        
        # Add close button
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)
        
        self.main_layout.addWidget(title_bar)

        # Create toolbar
        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)

        # Screenshot button with icon
        self.screenshot_btn = QPushButton("📸")
        self.screenshot_btn.setObjectName("actionButton")
        self.screenshot_btn.setToolTip("Take Screenshot")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        toolbar_layout.addWidget(self.screenshot_btn)

        # Video button
        self.video_btn = QPushButton("🎥")
        self.video_btn.setObjectName("actionButton")
        self.video_btn.setToolTip("Record Video")
        self.video_btn.clicked.connect(self.toggle_recording)
        toolbar_layout.addWidget(self.video_btn)

        # Delay label and combo box
        delay_label = QLabel("Delay:")
        delay_label.setObjectName("toolbarLabel")
        toolbar_layout.addWidget(delay_label)

        self.delay_combo = QComboBox()
        self.delay_combo.setObjectName("delayCombo")
        self.delay_combo.addItems(["0s", "3s", "5s", "10s"])
        self.delay_combo.currentTextChanged.connect(self.update_delay)
        toolbar_layout.addWidget(self.delay_combo)

        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("actionButton")
        settings_btn.setToolTip("Settings")
        toolbar_layout.addWidget(settings_btn)

        self.main_layout.addWidget(self.toolbar)

        # Store initial position
        self.last_position = self.pos()

        # Set window properties and styling
        self.setStyleSheet("""
            QWidget {
                color: white;
                font-family: 'Segoe UI', Arial;
            }
            #titleBar {
                background: #2b2b2b;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            #titleLabel {
                font-size: 14px;
                font-weight: bold;
            }
            #closeButton {
                background: transparent;
                border: none;
                font-size: 20px;
                color: #aaa;
                padding: 5px;
                border-radius: 3px;
            }
            #closeButton:hover {
                background: #c42b1c;
                color: white;
            }
            #toolbar {
                background: #333333;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            #actionButton {
                background: #444444;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 16px;
                min-width: 35px;
                min-height: 35px;
            }
            #actionButton:hover {
                background: #555555;
            }
            #toolbarLabel {
                color: #aaa;
                font-size: 13px;
            }
            #delayCombo {
                background: #444444;
                border: none;
                padding: 5px;
                border-radius: 3px;
                color: white;
                min-width: 80px;
            }
            #delayCombo:hover {
                background: #555555;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)

        self.resize(400, 80)
        self.center_on_screen()

    def update_delay(self, delay_text):
        if delay_text == "0s":
            self.screenshot_delay = 0
        else:
            self.screenshot_delay = int(delay_text.replace("s", ""))

    def take_screenshot(self):
        if self.screenshot_delay > 0:
            # Start countdown
            self.countdown_remaining = self.screenshot_delay
            self.screenshot_btn.setText(str(self.countdown_remaining))
            self.screenshot_btn.setEnabled(False)
            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)
        else:
            # Take screenshot immediately with a small delay
            self.screenshot_btn.setEnabled(False)
            QTimer.singleShot(500, self.capture_screen)

    def update_countdown(self):
        self.countdown_remaining -= 1
        if self.countdown_remaining > 0:
            self.screenshot_btn.setText(str(self.countdown_remaining))
        else:
            self.countdown_timer.stop()
            self.countdown_timer = None
            self.screenshot_btn.setText("📸")
            self.screenshot_btn.setEnabled(False)
            # Take screenshot after countdown
            QTimer.singleShot(500, self.capture_screen)

    def capture_screen(self):
        """Capture the screen content"""
        try:
            # Store the current position
            current_pos = self.pos()
            
            # Hide window for screenshot
            self.hide()
            QApplication.processEvents()
            time.sleep(0.1)  # Small delay to ensure window is hidden
            
            with mss.mss() as sct:
                # Get the primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                
                # Capture the screen
                screenshot = sct.grab(monitor)
                
                # Convert to QImage with high quality
                img = Image.frombytes('RGBA', screenshot.size, screenshot.bgra, 'raw', 'BGRA')
                # Convert to RGB while maintaining quality
                img = img.convert('RGB')
                
                # Create QImage with native format
                w, h = img.size
                image = QImage(img.tobytes('raw', 'RGB'), w, h, w * 3, QImage.Format_RGB888)
                
                # Show the window again at its original position
                self.move(current_pos)
                self.show()
                
                # Show editor dialog
                editor_dialog = EditorDialog(image, self)
                editor_dialog.exec_()
                
                # Re-enable the screenshot button
                self.screenshot_btn.setEnabled(True)
                self.screenshot_btn.setText("📸")
                
        except Exception as e:
            print(f"Error capturing screenshot: {e}")  # Debug print
            self.show()
            self.screenshot_btn.setEnabled(True)
            self.screenshot_btn.setText("📸")
            QMessageBox.critical(self, "Error", f"Failed to capture screenshot: {str(e)}")

    def handle_capture_error(self, error_msg):
        """Handle errors during capture"""
        self.show()  # Ensure window is visible
        self.screenshot_btn.setEnabled(True)
        self.screenshot_btn.setText("📸")
        QMessageBox.critical(self, "Error", f"Failed to capture screenshot: {error_msg}")

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.video_btn.setText("⏹")
            self.video_btn.setProperty('recording', True)
            self.video_btn.style().unpolish(self.video_btn)
            self.video_btn.style().polish(self.video_btn)
            self.video_recorder.start()
        else:
            self.video_recorder.stop()

    def recording_finished(self, temp_file):
        self.is_recording = False
        self.video_btn.setText("🎥")
        self.video_btn.setProperty('recording', False)
        self.video_btn.style().unpolish(self.video_btn)
        self.video_btn.style().polish(self.video_btn)
        
        # Ask user where to save the video
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Video",
            f"screen_recording_{timestamp}.mp4",
            "Video Files (*.mp4)"
        )
        
        if filename:
            import shutil
            shutil.move(temp_file, filename)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            # Store position when starting to drag
            self.last_position = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if event.buttons() == Qt.LeftButton:
            # Update position while dragging
            newPos = self.pos() + event.globalPos() - self.dragPos
            self.move(newPos)
            self.last_position = newPos  # Update last known position
            self.dragPos = event.globalPos()
            event.accept()

    def moveEvent(self, event):
        """Store the window position when it's moved"""
        super().moveEvent(event)
        self.last_position = self.pos()

    def showEvent(self, event):
        """Restore position when window is shown"""
        super().showEvent(event)
        if self.last_position:
            self.move(self.last_position)

    def focusInEvent(self, event):
        """Handle when window gets focus"""
        super().focusInEvent(event)
        if self.last_position:
            self.move(self.last_position)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().size()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())
