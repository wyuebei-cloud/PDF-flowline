from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QColor, QPen

class PDFViewer(QGraphicsView):
    selection_completed = pyqtSignal(QRectF)
    point_selected = pyqtSignal(QPointF)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        # Native QGraphicsScene based selection visualizer
        self.selection_box = QGraphicsRectItem()
        self.selection_box.setBrush(QColor(0, 120, 215, 60))
        self.selection_box.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine))
        self.selection_box.hide()
        self.scene.addItem(self.selection_box)
        
        # Pan and Zoom configuration
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(Qt.GlobalColor.lightGray)
        
        self.zoom_factor = 1.15
        
        self.drawing_selection = False
        self.interaction_mode = 'NONE' # 'NONE', 'ANCHOR', 'BOX', 'CALIBRATE'
        self.start_scene_pt = QPointF()
        
    def set_pixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.centerOn(self.pixmap_item)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_factor, self.zoom_factor)
        else:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.stash_cursor = self.viewport().cursor()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.interaction_mode in ('ANCHOR', 'CALIBRATE'):
                self.point_selected.emit(self.mapToScene(event.pos()))
            elif self.interaction_mode == 'BOX':
                self.drawing_selection = True
                self.start_scene_pt = self.mapToScene(event.pos())
                self.selection_box.setRect(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.selection_box.show()
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if hasattr(self, 'is_panning') and self.is_panning:
            delta = event.pos() - self.pan_start_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.pan_start_pos = event.pos()
            event.accept()
            return
            
        if self.drawing_selection:
            current_scene_pt = self.mapToScene(event.pos())
            rect = QRectF(self.start_scene_pt, current_scene_pt).normalized()
            self.selection_box.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            if hasattr(self, 'stash_cursor'):
                self.viewport().setCursor(self.stash_cursor)
            else:
                self.viewport().unsetCursor()
            event.accept()
            return
            
        if self.drawing_selection and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_selection = False
            self.selection_box.hide()
            
            end_scene_pt = self.mapToScene(event.pos())
            final_rect = QRectF(self.start_scene_pt, end_scene_pt).normalized()
            
            if final_rect.width() > 5 and final_rect.height() > 5:
                self.selection_completed.emit(final_rect)
        else:
            super().mouseReleaseEvent(event)
