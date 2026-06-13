from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen

class SelectionOverlay(QWidget):
    selection_completed = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        self.active = False # Controls if OCR mode is on

    def paintEvent(self, event):
        if self.is_selecting and self.active:
            painter = QPainter(self)
            # Draw semi-transparent rect
            painter.setBrush(QColor(0, 120, 215, 60))
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine))
            rect = QRect(self.begin, self.end)
            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if not self.active:
            event.ignore()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.is_selecting = True
            self.update()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.active:
            self.end = event.pos()
            self.update()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self.is_selecting and self.active:
            self.end = event.pos()
            self.is_selecting = False
            self.update()
            final_rect = QRect(self.begin, self.end).normalized()
            if final_rect.width() > 5 and final_rect.height() > 5:
                self.selection_completed.emit(final_rect)
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event):
        # We never handle zooming, pass it to the PDF viewer
        event.ignore()

