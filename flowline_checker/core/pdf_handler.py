import fitz
from PyQt6.QtGui import QImage, QPixmap
import math

class PDFHandler:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.filepath = pdf_path  # Store path for use by callers (e.g. export dialog)
        self.current_page_idx = 0
        self.num_pages = len(self.doc)
        self.dpi = 300 # Global DPI property used to match QGraphicsView scaling

    def render_page(self, page_number: int):
        if page_number < 0 or page_number >= self.num_pages:
            return None
        
        self.current_page_idx = page_number
        page = self.doc.load_page(page_number)
        
        # Performance: Render at specific DPI for clarity on FS numbers
        zoom = self.dpi / 72  # PDF default is 72 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to QPixmap (BGR as per fitz default samples)
        # fitz samples are RGB888, stride is width * 3
        image_format = QImage.Format.Format_RGB888
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, image_format)
        
        # IMPORTANT: pix.samples is a buffer. To be safe, we copy the QImage 
        # so it doesn't reference memory that might be freed by fitz.
        return QPixmap.fromImage(qimg.copy())

    def get_page_count(self):
        return self.num_pages

    def add_arrow_annotation(self, page_number, p1, p2, visual_arrow_size, text_size, drawn_labels=None, label_text=None):
        page = self.doc.load_page(page_number)
        
        # 1. Absolute geometric mapping algorithm (handles Rotation + CropBox Offsets + DPI Zoom)
        zoom = self.dpi / 72
        max_zoom = zoom
        mat = fitz.Matrix(zoom, zoom)
        
        # The transformation matrix used by PyMuPDF to generate the pixel map
        trans = page.rotation_matrix * mat
        
        # The boundaries of the page on the pixel map using the unrotated cropbox
        screen_rect = page.cropbox * trans
        inv_trans = ~trans
        
        # Revert mapped GUI pixels (0,0 indexed) to unrotated native PDF geometry
        scaled_start = fitz.Point(p1.x + screen_rect.x0, p1.y + screen_rect.y0) * inv_trans
        scaled_end = fitz.Point(p2.x + screen_rect.x0, p2.y + screen_rect.y0) * inv_trans
        
        # 2. Add PyMuPDF native line annotation
        annot = page.add_line_annot(scaled_start, scaled_end)
        
        # 3. Setting properties
        # Arrows with heads
        annot.set_line_ends(fitz.PDF_ANNOT_LE_NONE, fitz.PDF_ANNOT_LE_CLOSED_ARROW)
        
        # Color processing: FitZ expects RGB floats in [0, 1]
        red_color = [1.0, 0.0, 0.0]
        annot.set_colors(stroke=red_color)
        
        # Pen width scaling (GUI pen width is 3 -> scale back or keep readable). We will use dynamic calculation
        pen_width = max(1.0, (visual_arrow_size / zoom) * 0.2)
        annot.set_border(width=pen_width)
        
        # Apply changes permanently to PDF geometry buffer
        annot.update()

        # 4. Add Delta/Length/Slope Text Annotation (freetext)
        if label_text is None:
            delta = abs(p1.value - p2.value)
            label_text = f"{delta:.2f}"
        label_lines = label_text.split("\n")
        num_lines = len(label_lines)
        max_line_len = max(len(line) for line in label_lines)

        # Calculate position in screen space first (highly robust to rotation/reflection)
        mid_x = (p1.x + p2.x) / 2
        mid_y = (p1.y + p2.y) / 2
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        angle = math.atan2(dy, dx)
        offset_distance = text_size * 0.8 * (1 + 0.5 * (num_lines - 1))
        offset_x = -math.sin(angle) * offset_distance
        offset_y = math.cos(angle) * offset_distance
        
        text_screen_x = mid_x + offset_x
        text_screen_y = mid_y + offset_y
        
        # Transform the target label center back to unrotated PDF page geometry
        scaled_text_center = fitz.Point(text_screen_x + screen_rect.x0, text_screen_y + screen_rect.y0) * inv_trans
        
        # Scale font size and boxes back to PDF point space; box grows with the longest line and line count
        pdf_font_size = max(6.0, text_size / zoom)
        box_w = pdf_font_size * max(3.5, 0.62 * max_line_len)
        box_h = pdf_font_size * 1.5 * num_lines
        
        # Swap box width/height if the page is rotated 90 or 270 degrees
        if page.rotation in (90, 270):
            unrotated_w = box_h
            unrotated_h = box_w
        else:
            unrotated_w = box_w
            unrotated_h = box_h
            
        text_rect = fitz.Rect(
            scaled_text_center.x - unrotated_w / 2,
            scaled_text_center.y - unrotated_h / 2,
            scaled_text_center.x + unrotated_w / 2,
            scaled_text_center.y + unrotated_h / 2
        )
        
        text_annot = page.add_freetext_annot(
            text_rect,
            label_text,
            fontsize=pdf_font_size,
            fontname="helv-bold",
            text_color=red_color,
            align=1,  # Center aligned
            rotate=page.rotation
        )
        if text_annot:
            text_annot.update()
            
        # 5. Add HP / LP Labels (freetext)
        if drawn_labels is None:
            drawn_labels = set()
            
        for pt in (p1, p2):
            if pt.label and (pt.x, pt.y) not in drawn_labels:
                # Place the label above the elevation point in screen space
                offset = (text_size + 4) * 0.8
                label_screen_x = pt.x
                label_screen_y = pt.y - offset
                
                # Transform screen coordinates back to unrotated PDF space
                scaled_label_center = fitz.Point(label_screen_x + screen_rect.x0, label_screen_y + screen_rect.y0) * inv_trans
                
                label_color = [1.0, 0.0, 1.0] if pt.label == "HP" else [0.0, 0.0, 1.0]  # Magenta or Blue
                label_font_size = max(8.0, (text_size + 4) / zoom)
                
                lw = label_font_size * 2.5
                lh = label_font_size * 1.5
                
                # Swap box width/height if the page is rotated 90 or 270 degrees
                if page.rotation in (90, 270):
                    unrotated_lw = lh
                    unrotated_lh = lw
                else:
                    unrotated_lw = lw
                    unrotated_lh = lh
                    
                label_rect = fitz.Rect(
                    scaled_label_center.x - unrotated_lw / 2,
                    scaled_label_center.y - unrotated_lh / 2,
                    scaled_label_center.x + unrotated_lw / 2,
                    scaled_label_center.y + unrotated_lh / 2
                )
                
                label_annot = page.add_freetext_annot(
                    label_rect,
                    pt.label,
                    fontsize=label_font_size,
                    fontname="helv-bold",
                    text_color=label_color,
                    align=1,  # Center aligned
                    rotate=page.rotation
                )
                if label_annot:
                    label_annot.update()
                
                drawn_labels.add((pt.x, pt.y))
        
    def save_copy(self, output_path):
        self.doc.save(output_path)
        
    def close(self):
        if self.doc:
            self.doc.close()
