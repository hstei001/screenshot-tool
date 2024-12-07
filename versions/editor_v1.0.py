from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QToolBar,
                             QButtonGroup, QGraphicsView, QGraphicsScene, QColorDialog,
                             QFileDialog, QDialog, QMessageBox, QApplication, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QPainterPath, QFont
import numpy as np
from enum import Enum, auto

class DrawingTool(Enum):
    ARROW = auto()
    RECTANGLE = auto()
    TEXT = auto()

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = None
        self.current_tool = DrawingTool.ARROW
        self.pen_color = QColor('#FF0000')  # Default red
        self.pen_width = 2
        self.last_point = None
        self.current_item = None
        self.text_font = QFont('Arial', 12)
        self.text_item = None
        self.text_content = ""

    def mousePressEvent(self, event):
        pos = event.scenePos()
        if self.current_tool == DrawingTool.TEXT:
            # Remove any existing temporary text item
            if self.text_item:
                self.removeItem(self.text_item)
            
            # Create new text item at click position
            self.text_content = ""
            self.text_item = self.addText(self.text_content, self.text_font)
            self.text_item.setDefaultTextColor(self.pen_color)
            self.text_item.setPos(pos)
        else:
            self.last_point = pos
            self.current_path = QPainterPath()
            self.current_path.moveTo(pos)

    def mouseMoveEvent(self, event):
        if self.last_point is None or self.current_tool == DrawingTool.TEXT:
            return
        
        pos = event.scenePos()
        
        # Remove the previous temporary item if it exists
        if self.current_item:
            self.removeItem(self.current_item)
        
        # Create new path for preview
        if self.current_tool == DrawingTool.ARROW:
            # Draw arrow
            path = QPainterPath()
            path.moveTo(self.last_point)
            path.lineTo(pos)
            
            # Add arrowhead
            angle = np.arctan2(pos.y() - self.last_point.y(), pos.x() - self.last_point.x())
            arrowSize = 20
            arrowP1 = pos - QPointF(np.cos(angle + np.pi/6) * arrowSize,
                                  np.sin(angle + np.pi/6) * arrowSize)
            arrowP2 = pos - QPointF(np.cos(angle - np.pi/6) * arrowSize,
                                  np.sin(angle - np.pi/6) * arrowSize)
            
            path.moveTo(arrowP1)
            path.lineTo(pos)
            path.lineTo(arrowP2)
            
        elif self.current_tool == DrawingTool.RECTANGLE:
            # Draw rectangle
            path = QPainterPath()
            path.addRect(QRectF(self.last_point, pos))
        
        # Add the preview item
        pen = QPen(self.pen_color, self.pen_width)
        self.current_item = self.addPath(path, pen)

    def mouseReleaseEvent(self, event):
        if self.current_item:
            # The temporary item becomes permanent
            self.current_item = None
            self.last_point = None

    def keyPressEvent(self, event):
        if self.current_tool == DrawingTool.TEXT and self.text_item:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Finish text editing
                self.text_item = None
            elif event.key() == Qt.Key_Backspace:
                # Handle backspace
                self.text_content = self.text_content[:-1]
                self.text_item.setPlainText(self.text_content)
            else:
                # Add typed character
                char = event.text()
                if char:
                    self.text_content += char
                    self.text_item.setPlainText(self.text_content)

class EditorWidget(QWidget):
    def __init__(self, screenshot, parent=None):
        super().__init__(parent)
        
        if isinstance(screenshot, QImage):
            self.screenshot = screenshot
        elif isinstance(screenshot, np.ndarray):
            height, width, channel = screenshot.shape
            bytes_per_line = 3 * width
            self.screenshot = QImage(screenshot.data, width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            raise ValueError("Screenshot must be QImage or numpy array")
            
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        
        # Create toolbar with modern style
        toolbar = QToolBar()
        toolbar.setMovable(True)  # Allow toolbar to be moved
        toolbar.setFloatable(True)  # Allow toolbar to float
        toolbar.setOrientation(Qt.Horizontal)  # Set horizontal orientation
        toolbar.setAllowedAreas(Qt.AllToolBarAreas)  # Allow toolbar in all areas
        
        toolbar.setStyleSheet("""
            QToolBar {
                background: #2d2d2d;
                border: none;
                spacing: 8px;
                padding: 8px;
                border-radius: 4px;
                margin: 4px;
            }
            QPushButton {
                background: #3d3d3d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #4d4d4d;
            }
            QPushButton:pressed {
                background: #5d5d5d;
            }
            QPushButton:checked {
                background: #0078d4;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                padding: 0 8px;
            }
        """)
        
        # Create tool buttons with icons
        arrow_btn = QPushButton("🎯 Arrow")
        arrow_btn.setCheckable(True)
        arrow_btn.setChecked(True)
        
        rect_btn = QPushButton("⬜ Rectangle")
        rect_btn.setCheckable(True)
        
        text_btn = QPushButton("📝 Text")
        text_btn.setCheckable(True)
        
        # Add buttons to toolbar with spacers
        toolbar.addWidget(arrow_btn)
        toolbar.addWidget(rect_btn)
        toolbar.addWidget(text_btn)
        
        toolbar.addWidget(QLabel("|"))  # Separator
        
        # Color button with current color indicator
        self.color_btn = QPushButton("🎨 Color")
        self.color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(self.color_btn)
        
        toolbar.addWidget(QLabel("|"))  # Separator
        
        # Save button with icon
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_screenshot)
        toolbar.addWidget(save_btn)
        
        # Create button group for exclusive selection
        self.tool_group = QButtonGroup(self)
        self.tool_group.addButton(arrow_btn, 0)
        self.tool_group.addButton(rect_btn, 1)
        self.tool_group.addButton(text_btn, 2)
        self.tool_group.buttonClicked.connect(self.tool_changed)
        
        # Add toolbar to layout
        layout.addWidget(toolbar, 0, Qt.AlignTop)
        
        # Create graphics view
        self.scene = GraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        
        # Set view properties for better quality
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.view.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, False)
        self.view.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        
        # Enable focus and keyboard tracking
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.view.setFocus()
        
        # Set dark theme for view
        self.view.setStyleSheet("""
            QGraphicsView {
                border: none;
                background: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #5d5d5d;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6d6d6d;
            }
            QScrollBar:horizontal {
                border: none;
                background: #2d2d2d;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #5d5d5d;
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6d6d6d;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }
        """)
        
        # Add screenshot to scene
        pixmap = QPixmap.fromImage(self.screenshot)
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self.pixmap_item)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        
        layout.addWidget(self.view)
        
        # Fit view to window
        QTimer.singleShot(100, self.fit_to_view)

    def fit_to_view(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def tool_changed(self, button):
        if button.text() == "🎯 Arrow":
            self.scene.current_tool = DrawingTool.ARROW
        elif button.text() == "⬜ Rectangle":
            self.scene.current_tool = DrawingTool.RECTANGLE
        elif button.text() == "📝 Text":
            self.scene.current_tool = DrawingTool.TEXT

    def choose_color(self):
        color = QColorDialog.getColor(self.scene.pen_color, self)
        if color.isValid():
            self.scene.pen_color = color
            # Update color button with current color
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color.name()};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background: {color.lighter().name()};
                }}
            """)

    def save_screenshot(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filename:
            # Create a pixmap the size of the scene
            pixmap = QPixmap(self.scene.sceneRect().size().toSize())
            pixmap.fill(Qt.transparent)
            
            # Create a painter to render the scene
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            
            # Render the scene
            self.scene.render(painter)
            painter.end()
            
            # Save with high quality
            if filename.lower().endswith('.png'):
                pixmap.save(filename, 'PNG', quality=100)
            else:
                pixmap.save(filename, 'JPEG', quality=100)

    def keyPressEvent(self, event):
        # Forward key events to the scene
        self.scene.keyPressEvent(event)

class EditorDialog(QDialog):
    def __init__(self, screenshot, parent=None):
        super().__init__(parent)
        self.edited_screenshot = None
        self.setWindowTitle("✏️ Edit Screenshot")
        self.setModal(True)
        
        # Set size to 80% of screen size
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        
        # Center on screen
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create editor widget
        self.editor = EditorWidget(screenshot, self)
        layout.addWidget(self.editor)
        
        # Set dark theme
        self.setStyleSheet("""
            QDialog {
                background: #1e1e1e;
                color: white;
            }
            QToolBar {
                background: #2d2d2d;
                border: none;
                spacing: 8px;
                padding: 8px;
                border-radius: 4px;
                margin: 4px;
            }
            QMessageBox {
                background: #2d2d2d;
                color: white;
            }
            QMessageBox QPushButton {
                background: #3d3d3d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: #4d4d4d;
            }
            QColorDialog {
                background: #2d2d2d;
                color: white;
            }
            QColorDialog QPushButton {
                background: #3d3d3d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QColorDialog QPushButton:hover {
                background: #4d4d4d;
            }
        """)
        
        # Ensure dialog stays on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
