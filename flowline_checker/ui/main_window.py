from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QToolBar, 
                             QStatusBar, QFileDialog, QLabel, QInputDialog, 
                             QGraphicsEllipseItem, QGraphicsTextItem, QSlider, QMessageBox, QGraphicsItemGroup)
from PyQt6.QtGui import QAction, QColor, QPen, QPolygonF, QCursor, QPixmap, QPainter, QImage, QFont, QKeySequence
from PyQt6.QtCore import Qt, QRectF, QPointF, QSettings, QThread, pyqtSignal
import numpy as np
import cv2
import math
import os
from ui.pdf_viewer import PDFViewer
from ui.value_dialog import ValueDialog
from core.pdf_handler import PDFHandler
from core.ocr_engine import OCREngine
from models.data_types import ElevationPoint, FlowArrow

class OCRWorker(QThread):
    finished = pyqtSignal(object, str, str, object)  # value, raw_text, model_name, point_obj

    def __init__(self, ocr_engine, img_cv, point_obj):
        super().__init__()
        self.ocr_engine = ocr_engine
        self.img_cv = img_cv
        self.point_obj = point_obj

    def run(self):
        try:
            preprocessed = self.ocr_engine.preprocess_for_ocr(self.img_cv)
            value, raw_text, model_name = self.ocr_engine.recognize_elevation(preprocessed)
            self.finished.emit(value, raw_text, model_name, self.point_obj)
        except Exception as e:
            self.finished.emit(None, f"LOCAL_ERROR: {str(e)}", "Error", self.point_obj)

class ClickableTextItem(QGraphicsTextItem):
    def __init__(self, text, point_obj, click_callback):
        super().__init__(text)
        self.point_obj = point_obj
        self.click_callback = click_callback
        self.setDefaultTextColor(QColor("blue"))
        font = QFont("Arial", 16)
        font.setBold(True)
        self.setFont(font)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_callback(self, self.point_obj)
            event.accept()
        else:
            super().mousePressEvent(event)

class ArrowGroup(QGraphicsItemGroup):
    def __init__(self, p1, p2):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable, True)

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flowline Direction Checker")
        self.resize(1200, 800)
        
        self.pdf_handler = None
        self.points = []  # List of current sequence of ElevationPoints
        self.all_finished_segments = {}  # {page_idx: [(ElevationPoint, ElevationPoint), ...]}
        self.rendered_arrows_graphics = [] # Track drawn graphics to enable dynamic slider updating
        self.ocr_workers = set()
        
        self.settings = QSettings("FlowlineCorp", "FlowlineChecker")
        
        # Use PP-OCRv6 tiny_rec (local ONNX) — no API key needed
        self.ocr_engine = OCREngine()
        
        self.current_page = 0
        self.temp_anchor = None
        self.temp_visuals = [] # Track yellow dots and dashed lines for cleanup
        
        # Build custom red crosshair for physical point selection
        self.red_cross_cursor = self._create_red_crosshair()
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        
        self.viewer = PDFViewer()
        self.viewer.selection_completed.connect(self._handle_selection)
        self.viewer.point_selected.connect(self._handle_anchor)
        self.layout.addWidget(self.viewer)
        
        # Info label for pages
        self.page_info = QLabel("Page: 0 / 0")
        
        self._create_toolbar()
        self._create_statusbar()

    def _create_red_crosshair(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        pen = QPen(QColor("red"), 2)
        painter.setPen(pen)
        # Draw precise crosshair with a small gap in the center
        painter.drawLine(0, 16, 12, 16)
        painter.drawLine(20, 16, 32, 16)
        painter.drawLine(16, 0, 16, 12)
        painter.drawLine(16, 20, 16, 32)
        painter.end()
        return QCursor(pixmap, 16, 16)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        open_action = QAction("Open PDF", self)
        open_action.triggered.connect(self._open_pdf)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        self.ocr_info_action = QAction("OCR Engine: Local PP-OCRv6", self)
        self.ocr_info_action.triggered.connect(self._show_ocr_info)
        toolbar.addAction(self.ocr_info_action)
        
        toolbar.addSeparator()
        
        self.prev_action = QAction("Prev Page", self)
        self.prev_action.triggered.connect(self._prev_page)
        self.prev_action.setEnabled(False)
        toolbar.addAction(self.prev_action)
        
        self.next_action = QAction("Next Page", self)
        self.next_action.triggered.connect(self._next_page)
        self.next_action.setEnabled(False)
        toolbar.addAction(self.next_action)
        
        toolbar.addSeparator()
        toolbar.addWidget(self.page_info)
        toolbar.addSeparator()
        
        self.select_mode_action = QAction("Draw Flowline", self)
        self.select_mode_action.setCheckable(True)
        self.select_mode_action.toggled.connect(self._toggle_select_mode)
        self.select_mode_action.setEnabled(False)
        toolbar.addAction(self.select_mode_action)
        
        self.finish_flowline_action = QAction("Done", self)
        self.finish_flowline_action.triggered.connect(self._finish_flowline)
        self.finish_flowline_action.setEnabled(False)
        toolbar.addAction(self.finish_flowline_action)
        
        toolbar.addSeparator()
        
        size_label = QLabel(" Arrow Size: ")
        toolbar.addWidget(size_label)
        
        self.arrow_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.arrow_size_slider.setRange(5, 50)
        self.arrow_size_slider.setValue(15)
        self.arrow_size_slider.setFixedWidth(100)
        self.arrow_size_slider.setToolTip("Adjust the generated arrow size")
        self.arrow_size_slider.valueChanged.connect(self._refresh_all_arrows)
        toolbar.addWidget(self.arrow_size_slider)
        
        text_size_label = QLabel(" Text Size: ")
        toolbar.addWidget(text_size_label)
        
        self.text_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_size_slider.setRange(10, 80)
        self.text_size_slider.setValue(24)
        self.text_size_slider.setFixedWidth(100)
        self.text_size_slider.setToolTip("Adjust the text size for elevation differences")
        self.text_size_slider.valueChanged.connect(self._refresh_all_arrows)
        toolbar.addWidget(self.text_size_slider)
        
        toolbar.addSeparator()
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.triggered.connect(self._undo)
        self.undo_action.setEnabled(False)
        toolbar.addAction(self.undo_action)
        
        self.export_action = QAction("Export to Image", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+S"))
        self.export_action.triggered.connect(self._export_image)
        self.export_action.setEnabled(False)
        toolbar.addAction(self.export_action)
        
        self.export_pdf_action = QAction("Export to PDF", self)
        self.export_pdf_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_pdf_action.triggered.connect(self._export_pdf)
        self.export_pdf_action.setEnabled(False)
        toolbar.addAction(self.export_pdf_action)
        
        # Transparent keyboard shortcut bindings without UI clutter
        delete_action = QAction("Delete Selected", self)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self._delete_selected)
        self.addAction(delete_action)
        
        cancel_action = QAction("Cancel", self)
        cancel_action.setShortcut(QKeySequence("Esc"))
        cancel_action.triggered.connect(self._cancel_current)
        self.addAction(cancel_action)

    def _create_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    def _show_ocr_info(self):
        QMessageBox.information(
            self,
            "OCR Engine",
            "PP-OCRv6 tiny_rec (local, offline)\n\n"
            "Baidu's latest OCR model running locally via ONNX Runtime.\n"
            "No API key or internet connection required.\n\n"
            f"Model: {self.ocr_engine._model.model_name if self.ocr_engine._model else 'loading...'}"
        )

    def _toggle_select_mode(self, enabled):
        if enabled:
            self.viewer.interaction_mode = 'ANCHOR'
            self.viewer.viewport().setCursor(self.red_cross_cursor)
            step = len(self.points) + 1
            self.status.showMessage(f"Flowline Point {step}: Click on the physical point")
            self.temp_anchor = None
            self.finish_flowline_action.setEnabled(True)
        else:
            self._finish_flowline()

    def _finish_flowline(self):
        # Check if there are any pending OCR workers or unrecognized values
        for p in self.points:
            if hasattr(p, '_text_item') and p._text_item:
                text = p._text_item.toPlainText()
                if text == "...":
                    QMessageBox.warning(self, "OCR In Progress", "Please wait for the background OCR to complete before clicking Done.")
                    return
                if text == "?" or p.value is None or (p.value == 0.0 and not p.confirmed):
                    QMessageBox.warning(self, "Invalid Value", "One or more points have unrecognized values (shown as '?'). Please click on the blue '?' to input the value manually.")
                    return

        # 1. Clean up temporary visual markers (yellow dots, dash lines, blue text items)
        for item in self.temp_visuals:
            if item.scene() == self.viewer.scene:
                self.viewer.scene.removeItem(item)
        self.temp_visuals = []
        self.ocr_workers.clear()

        # 2. HP/LP Computation for this sequence
        if len(self.points) >= 3:
            for i in range(1, len(self.points) - 1):
                prev_val = self.points[i-1].value
                curr_val = self.points[i].value
                next_val = self.points[i+1].value
                
                if curr_val < prev_val and curr_val < next_val:
                    self.points[i].label = "LP"
                elif curr_val > prev_val and curr_val > next_val:
                    self.points[i].label = "HP"

        # 3. Save completed segments logically
        if len(self.points) > 1:
            page_segments = self.all_finished_segments.setdefault(self.current_page, [])
            for i in range(len(self.points) - 1):
                page_segments.append((self.points[i], self.points[i+1]))
                
        # 4. Refresh display with sizes
        self._refresh_all_arrows()

        self.viewer.interaction_mode = 'NONE'
        self.viewer.viewport().unsetCursor()
        self.points = []
        self.temp_anchor = None
        self.select_mode_action.setChecked(False)
        self.finish_flowline_action.setEnabled(False)
        self.status.showMessage("Flowline completed. Ready.")

    def _refresh_all_arrows(self):
        # Clear currently drawn permanent arrows
        for item in self.rendered_arrows_graphics:
            if item.scene() == self.viewer.scene:
                self.viewer.scene.removeItem(item)
        self.rendered_arrows_graphics = []
        
        # Reset drawn flags for points to avoid duplicate HP/LP labels
        for page_segments in self.all_finished_segments.values():
            for p1, p2 in page_segments:
                if hasattr(p1, '_label_drawn'): del p1._label_drawn
                if hasattr(p2, '_label_drawn'): del p2._label_drawn
        
        # Redraw all finished segments based on the current slider size for current page
        current_segments = self.all_finished_segments.get(self.current_page, [])
        for p1, p2 in current_segments:
            self._draw_final_arrow(p1, p2)

    def _handle_anchor(self, pt: QPointF):
        self.temp_anchor = pt
        # Visual indicator
        marker = QGraphicsEllipseItem(pt.x()-3, pt.y()-3, 6, 6)
        marker.setBrush(QColor("yellow"))
        self.viewer.scene.addItem(marker)
        self.temp_visuals.append(marker)
        
        self.viewer.interaction_mode = 'BOX'
        self.viewer.viewport().setCursor(Qt.CursorShape.CrossCursor) # Black crosshair for box
        step = len(self.points) + 1
        self.status.showMessage(f"Flowline Point {step}: Box the elevation text")

    def _handle_selection(self, rect):
        if not self.pdf_handler or not self.temp_anchor: return
        
        # rect is QRectF in scene coords
        scene_start = rect.topLeft()
        scene_end = rect.bottomRight()
        
        pixmap_item = self.viewer.pixmap_item
        crop_rect = QRectF(pixmap_item.mapFromScene(scene_start), pixmap_item.mapFromScene(scene_end)).toRect()
        
        # 2. Extract image from pixmap
        full_pixmap = pixmap_item.pixmap()
        cropped_pixmap = full_pixmap.copy(crop_rect)
        qimg = cropped_pixmap.toImage()
        
        # Convert QImage to numpy array for CV2
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((qimg.height(), qimg.width(), 4))
        img_cv = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        
        # Create ElevationPoint with temporary values and start background OCR worker
        x, y = self.temp_anchor.x(), self.temp_anchor.y()
        point = ElevationPoint(value=0.0, x=x, y=y, confirmed=False)
        point._selection_rect = rect
        self.points.append(point)
        
        # Connect backward to previous point intuitively as a dashed line for now
        if len(self.points) > 1:
            p1, p2 = self.points[-2], self.points[-1]
            pen = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
            line = self.viewer.scene.addLine(p1.x, p1.y, p2.x, p2.y, pen)
            self.temp_visuals.append(line)
            
        # Place temporary clickable blue text item showing "..."
        text_item = ClickableTextItem("...", point, self._handle_blue_text_click)
        self.viewer.scene.addItem(text_item)
        rect_text = text_item.boundingRect()
        text_item.setPos(rect.x() - rect_text.width() - 5, rect.center().y() - rect_text.height() / 2)
        self.temp_visuals.append(text_item)
        point._text_item = text_item
        
        # Ready for next point immediately in the continuous drawing sequence (non-blocking!)
        self.viewer.interaction_mode = 'ANCHOR'
        self.viewer.viewport().setCursor(self.red_cross_cursor)
        step = len(self.points) + 1
        self.status.showMessage(f"Flowline Point {step}: Click next physical point or click Done to finish")
        
        # Start async worker for OCR
        worker = OCRWorker(self.ocr_engine, img_cv, point)
        worker.finished.connect(self._handle_ocr_result)
        self.ocr_workers.add(worker)
        worker.finished.connect(lambda: self.ocr_workers.discard(worker))
        worker.start()

    def _handle_ocr_result(self, value, raw_text, model_name, point):
        if value is not None:
            point.value = value
            point.confirmed = True
            display_text = f"{value:.2f}"
        else:
            display_text = raw_text if raw_text else "?"
            if display_text.startswith(("API_ERROR:", "LOCAL_ERROR:")):
                display_text = "?"
            point.value = 0.0
            point.confirmed = False
            
        if hasattr(point, '_text_item') and point._text_item:
            text_item = point._text_item
            text_item.setPlainText(display_text)
            
            # Recenter text_item relative to the selection rect
            if hasattr(point, '_selection_rect') and point._selection_rect:
                rect = point._selection_rect
                rect_text = text_item.boundingRect()
                text_item.setPos(rect.x() - rect_text.width() - 5, rect.center().y() - rect_text.height() / 2)

    def _handle_blue_text_click(self, text_item, point):
        current_val_str = text_item.toPlainText()
        if current_val_str in ("...", "?"):
            current_val_str = ""
            
        dialog = ValueDialog(current_val_str, self)
        if dialog.exec():
            confirmed_val = dialog.get_value()
            if confirmed_val is not None:
                point.value = confirmed_val
                point.confirmed = True
                text_item.setPlainText(f"{confirmed_val:.2f}")
                
                # Recenter text_item
                if hasattr(point, '_selection_rect') and point._selection_rect:
                    rect = point._selection_rect
                    rect_text = text_item.boundingRect()
                    text_item.setPos(rect.x() - rect_text.width() - 5, rect.center().y() - rect_text.height() / 2)

    def _draw_final_arrow(self, p1, p2):
        is_reverse = p2.value > p1.value
        start, end = (p1, p2) if not is_reverse else (p2, p1)
        
        pen = QPen(QColor("red"), 3)
        brush = QColor("red")
        
        arrow_group = ArrowGroup(p1, p2)
        
        # 1. Main body line
        line_item = self.viewer.scene.addLine(start.x, start.y, end.x, end.y, pen)
        arrow_group.addToGroup(line_item)
        
        # 2. Calculate and draw Arrowhead
        dx = end.x - start.x
        dy = end.y - start.y
        angle = math.atan2(dy, dx)
        
        arrow_size = self.arrow_size_slider.value()
        
        # Points for the triangle (pointing at end)
        pa = QPointF(end.x - arrow_size * math.cos(angle - math.pi / 6),
                     end.y - arrow_size * math.sin(angle - math.pi / 6))
        pb = QPointF(end.x - arrow_size * math.cos(angle + math.pi / 6),
                     end.y - arrow_size * math.sin(angle + math.pi / 6))
        
        polygon = QPolygonF([QPointF(end.x, end.y), pa, pb])
        poly_item = self.viewer.scene.addPolygon(polygon, pen, brush)
        arrow_group.addToGroup(poly_item)
        
        # 3. Calculate Delta and draw Text
        delta = abs(p1.value - p2.value)
        delta_text = f"{delta:.2f}"
        
        text_item = QGraphicsTextItem(delta_text)
        text_size = self.text_size_slider.value()
        
        font = QFont("Arial", text_size)
        font.setBold(True)
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor("red"))
        
        # Position the text midway
        mid_x = (start.x + end.x) / 2
        mid_y = (start.y + end.y) / 2
        
        # Dynamic tangential offset so it doesn't overlap the line
        offset_distance = text_size * 0.8
        offset_x = -math.sin(angle) * offset_distance
        offset_y = math.cos(angle) * offset_distance
        
        rect = text_item.boundingRect()
        text_item.setPos(mid_x + offset_x - rect.width() / 2, mid_y + offset_y - rect.height() / 2)
        arrow_group.addToGroup(text_item)
        
        self.viewer.scene.addItem(arrow_group)
        self.rendered_arrows_graphics.append(arrow_group)
        
        # 4. Draw High/Low Point Labels
        for pt in (p1, p2):
            if pt.label and not getattr(pt, '_label_drawn', False):
                label_item = QGraphicsTextItem(pt.label)
                l_font = QFont("Arial", text_size + 4)
                l_font.setBold(True)
                label_item.setFont(l_font)
                
                if pt.label == "HP":
                    label_item.setDefaultTextColor(QColor("magenta"))
                else:
                    label_item.setDefaultTextColor(QColor("blue"))
                    
                rect_l = label_item.boundingRect()
                label_item.setPos(pt.x - rect_l.width() / 2, pt.y - rect_l.height() - 10)
                
                self.viewer.scene.addItem(label_item)
                self.rendered_arrows_graphics.append(label_item)
                pt._label_drawn = True

    def _export_image(self):
        if not self.pdf_handler:
            self.status.showMessage("No document loaded to export.")
            return
            
        last_dir = self.settings.value("LastExportedDir", "")
        # fallback to the dir where pdf was opened if no last export
        if not last_dir and self.pdf_handler.filepath:
            last_dir = os.path.dirname(self.pdf_handler.filepath)
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Marked Up Image", last_dir, "PNG Image (*.png);;JPEG Image (*.jpg)")
        if file_path:
            self.settings.setValue("LastExportedDir", os.path.dirname(file_path))
            
            if self.points:
                self._finish_flowline()
                
            scene = self.viewer.scene
            rect = scene.sceneRect()
            
            image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(image)
            scene.render(painter)
            painter.end()
            
            try:
                image.save(file_path)
                self.status.showMessage(f"Successfully exported marked up image to: {file_path}")
            except Exception as e:
                self.status.showMessage(f"Export failed: {str(e)}")

    def _export_pdf(self):
        if not self.pdf_handler:
            self.status.showMessage("No document loaded to export.")
            return
            
        last_dir = self.settings.value("LastExportedDir", "")
        # fallback to the dir where pdf was opened if no last export
        if not last_dir and self.pdf_handler.filepath:
            last_dir = os.path.dirname(self.pdf_handler.filepath)
            
        # Propose a default filename with _flowcheck suffix
        base, ext = os.path.splitext(self.pdf_handler.filepath)
        default_path = f"{base}_flowcheck.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF with Annotations", default_path, "PDF Files (*.pdf)")
        if file_path:
            self.settings.setValue("LastExportedDir", os.path.dirname(file_path))
            
            if self.points or self.temp_anchor:
                self._finish_flowline()
                
            try:
                # Open a separate copy to keep the active loaded document clean in memory
                temp_handler = PDFHandler(self.pdf_handler.filepath)
                
                for page_idx, segments in self.all_finished_segments.items():
                    drawn_labels = set()
                    for p1, p2 in segments:
                        is_reverse = p2.value > p1.value
                        start, end = (p1, p2) if not is_reverse else (p2, p1)
                        arrow_size = self.arrow_size_slider.value()
                        text_size = self.text_size_slider.value()
                        
                        temp_handler.add_arrow_annotation(
                            page_idx, start, end, arrow_size, text_size, drawn_labels
                        )
                
                temp_handler.save_copy(file_path)
                temp_handler.close()
                
                self.status.showMessage(f"Successfully exported PDF with annotations to: {file_path}")
                QMessageBox.information(self, "Success", f"PDF successfully exported with annotations to:\n{file_path}")
            except Exception as e:
                self.status.showMessage(f"Export PDF failed: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to export PDF:\n{str(e)}")

    def _update_page_nav_state(self):
        if not self.pdf_handler:
            self.prev_action.setEnabled(False)
            self.next_action.setEnabled(False)
            self.page_info.setText("Page: 0 / 0")
            return
            
        total_pages = self.pdf_handler.get_page_count()
        self.prev_action.setEnabled(self.current_page > 0)
        self.next_action.setEnabled(self.current_page < total_pages - 1)
        self.page_info.setText(f"Page: {self.current_page + 1} / {total_pages}")

    def _open_pdf(self):
        last_dir = self.settings.value("LastOpenedDir", "")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", last_dir, "PDF Files (*.pdf)")
        if file_path:
            self.settings.setValue("LastOpenedDir", os.path.dirname(file_path))
            if self.pdf_handler:
                self.pdf_handler.close()
            
            # Clean up active drawing state
            self.points = []
            self.temp_anchor = None
            for item in self.temp_visuals:
                if item.scene() == self.viewer.scene:
                    self.viewer.scene.removeItem(item)
            self.temp_visuals = []
            
            # Terminate running OCR workers
            for worker in list(self.ocr_workers):
                worker.terminate()
                worker.wait()
            self.ocr_workers.clear()
            self.select_mode_action.setChecked(False)
            self.viewer.interaction_mode = 'NONE'
            self.viewer.viewport().unsetCursor()
            
            self.pdf_handler = PDFHandler(file_path)
            self.current_page = 0
            self.all_finished_segments = {}
            self.rendered_arrows_graphics = []
            
            # Safely flush drawn graphics without killing the underlying image object
            # Keep both the PDF image and the reusable selection_box
            for item in list(self.viewer.scene.items()):
                if item not in (self.viewer.pixmap_item, self.viewer.selection_box):
                    self.viewer.scene.removeItem(item)
                    
            self._display_current_page()
            self.status.showMessage(f"Loaded: {file_path}")
            
            # Enable actions
            self.select_mode_action.setEnabled(True)
            self.undo_action.setEnabled(True)
            self.export_action.setEnabled(True)
            self.export_pdf_action.setEnabled(True)

    def _display_current_page(self):
        if self.pdf_handler:
            pixmap = self.pdf_handler.render_page(self.current_page)
            if pixmap:
                self.viewer.set_pixmap(pixmap)
                self._update_page_nav_state()

    def _prev_page(self):
        if self.pdf_handler and self.current_page > 0:
            if self.points or self.temp_anchor:
                self._finish_flowline()
            self.current_page -= 1
            self._display_current_page()
            self._refresh_all_arrows()

    def _next_page(self):
        if self.pdf_handler and self.current_page < self.pdf_handler.get_page_count() - 1:
            if self.points or self.temp_anchor:
                self._finish_flowline()
            self.current_page += 1
            self._display_current_page()
            self._refresh_all_arrows()

    def _undo(self):
        if self.points or self.temp_anchor:
            self._cancel_current()
            return
            
        segments = self.all_finished_segments.get(self.current_page, [])
        if segments:
            segments.pop()
            self._refresh_all_arrows()
            self.status.showMessage("Undo last arrow.")

    def _cancel_current(self):
        if self.points or self.temp_anchor:
            self.points = []
            self.temp_anchor = None
            for item in self.temp_visuals:
                if item.scene() == self.viewer.scene:
                    self.viewer.scene.removeItem(item)
            self.temp_visuals = []
            
            # Terminate running OCR workers
            for worker in list(self.ocr_workers):
                worker.terminate()
                worker.wait()
            self.ocr_workers.clear()
            
            if self.select_mode_action.isChecked():
                self.viewer.interaction_mode = 'ANCHOR'
                self.viewer.viewport().setCursor(self.red_cross_cursor)
                self.status.showMessage("Drawing cancelled. Click a physical point.")

    def _delete_selected(self):
        selected_items = self.viewer.scene.selectedItems()
        deleted_any = False
        for item in selected_items:
            if isinstance(item, ArrowGroup):
                segments = self.all_finished_segments.get(self.current_page, [])
                pair = (item.p1, item.p2)
                if pair in segments:
                    segments.remove(pair)
                    deleted_any = True
        
        if deleted_any:
            self._refresh_all_arrows()
            self.status.showMessage("Selected arrows deleted.")
