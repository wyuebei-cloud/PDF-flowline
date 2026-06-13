# Flowline Direction Checker - Project Spec & Roadmap

## Overview

A standalone Python desktop tool for civil engineers to verify drainage flow directions on scanned PDF grading plans. The user circles two FS (Finished Surface) elevation numbers on a plan sheet, the tool OCR-reads both values, and draws an arrow from the higher elevation to the lower one — indicating the intended flow direction.

Primary users: PE-licensed civil engineers and project managers who review grading plans but prefer not to open 3D models. The tool must be simple enough that a manager can double-click an exe and start using it without any setup.

## Core Workflow

1. Open a scanned PDF grading plan (render page as high-res image)
2. Pan/zoom to the area of interest
3. Draw a rectangle around the first FS number → OCR reads it → display recognized value for confirmation/edit
4. Draw a rectangle around the second FS number → same process
5. Tool compares the two values → draws an arrow from HIGH to LOW on the PDF view
6. User can repeat for additional pairs on the same sheet
7. Export: save all arrows as PDF annotations back to the original file (or a copy)

## Technical Stack

- Python 3.11+
- PyQt6 for GUI (modern, well-documented, cross-platform)
- PyMuPDF (fitz) for PDF rendering and annotation writing
- Tesseract OCR (via pytesseract) as primary OCR engine
- Pillow for image preprocessing before OCR
- PyInstaller for packaging to standalone exe

## Architecture

```
flowline_checker/
├── main.py                 # Entry point, app initialization
├── ui/
│   ├── main_window.py      # Main window layout, menu, toolbar
│   ├── pdf_viewer.py       # PDF display widget with pan/zoom
│   ├── selection_overlay.py # Handles rectangle drawing on top of PDF
│   └── value_dialog.py     # Popup to confirm/edit OCR result
├── core/
│   ├── pdf_handler.py      # PDF loading, page rendering, annotation writing
│   ├── ocr_engine.py       # Image preprocessing + Tesseract OCR
│   └── flow_logic.py       # Compare values, compute arrow geometry
├── models/
│   └── data_types.py       # Data classes: ElevationPoint, FlowArrow, etc.
├── resources/
│   └── icons/              # Toolbar icons
├── requirements.txt
├── build.spec              # PyInstaller config
└── README.md
```

## Implementation Phases

### Phase 1: PDF Viewer with Pan/Zoom
**Goal:** Render a scanned PDF page and let the user navigate it comfortably.

Tasks:
- Load PDF with PyMuPDF, render selected page at 300 DPI to QPixmap
- Implement a QGraphicsView-based viewer with mouse wheel zoom and click-drag pan
- Page navigation (prev/next) for multi-page PDFs
- File > Open dialog to select PDF

Acceptance criteria: User can open any scanned PDF, zoom into a specific area smoothly, and switch pages.

### Phase 2: Rectangle Selection + OCR
**Goal:** User draws a rectangle on the PDF, tool OCR-reads the enclosed region and shows the result.

Tasks:
- Overlay layer that captures mouse press/drag/release to define a selection rectangle
- Crop the selected region from the rendered image
- Image preprocessing pipeline: grayscale → contrast enhancement (CLAHE) → binary threshold → optional deskew
- Run Tesseract with digit-optimized config: `--psm 7 -c tessedit_char_whitelist=0123456789.`
- Display result in a small popup/inline label next to the selection, editable by user
- Store confirmed value + bounding box center coordinates

Key OCR config notes (from testing on real grading plan scans):
- PSM 7 (single text line) works well for small cropped regions
- Whitelist to `0123456789.` since we only need elevation numbers
- CLAHE preprocessing significantly improves contrast on scan artifacts
- The "FS" suffix can be used as a visual anchor but should be stripped from the numeric result

Acceptance criteria: User draws a box around "31.97 FS", tool shows "31.97" for confirmation.

### Phase 3: Arrow Generation + Display
**Goal:** After two points are confirmed, draw an arrow from high to low.

Tasks:
- After second point is confirmed, compare the two elevation values
- Draw an arrow on the QGraphicsScene: thick colored line with arrowhead, from higher value's bbox center to lower value's bbox center
- Label the arrow with the delta (e.g., "Δ = 0.04")
- Arrow styling: configurable color (default red), line width proportional to zoom level
- Allow user to undo last arrow, or clear all arrows

Acceptance criteria: Two confirmed points produce a visible directional arrow. Arrow direction is correct (high → low).

### Phase 4: Export Annotations to PDF
**Goal:** Write the arrows back to the PDF file as standard annotations.

Tasks:
- Map arrow coordinates from screen space back to PDF page coordinate space
- Use PyMuPDF to add Line annotations with arrow endpoint style
- Optionally add a text annotation with the elevation values and delta
- Save as a new PDF (never overwrite original)
- Filename convention: `original_name_flowcheck.pdf`

Acceptance criteria: Exported PDF opens in Bluebeam/Adobe with visible arrow annotations that match what was shown on screen.

### Phase 5: UX Polish + Packaging
**Goal:** Make it usable by managers. Package as standalone exe.

Tasks:
- Toolbar with clear icons: Open PDF, Select Point, Undo Arrow, Clear All, Export
- Status bar showing current mode ("Select Point 1 of 2", "Ready", etc.)
- Keyboard shortcuts: Ctrl+Z undo, Ctrl+S export, Escape cancel selection
- Remember last opened directory
- Error handling: graceful messages for corrupt PDFs, OCR failures
- PyInstaller packaging: single-folder bundle with Tesseract binary included
- Test on a clean Windows 10/11 machine without Python installed

Acceptance criteria: A non-technical user can download the folder, double-click the exe, open a PDF, and complete the full workflow without reading documentation.

## OCR Preprocessing Pipeline (Detail)

Based on testing with actual grading plan scans (see test results below), the recommended pipeline is:

```
Raw crop (from user selection)
  → Convert to grayscale
  → Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
  → Upscale 2x if region is small (<100px height)
  → Binary threshold (Otsu's method)
  → Tesseract with --psm 7 -c tessedit_char_whitelist=0123456789.
  → Strip non-numeric characters from result
  → Return float value + confidence score
```

If confidence < 0.6, highlight the result in yellow and prompt user to verify/edit.

## Test Results from Prototype OCR (Reference Data)

Tested on a real grading plan scan with the following FS values visible: 32.01, 31.95, 31.97, 31.96, 32.02

Tesseract (full-image, default PSM 6): Found 31.95, 32.02, 31.96 correctly. Missed 32.01 and 31.97.
EasyOCR (full-image): Found 31.95, 32.02, 31.96 with decimal points. Recognized 32.01 and 31.97 but dropped decimal points ("3201", "3197").

Note: These results are from full-image scanning. Cropped-region OCR with preprocessing is expected to perform significantly better since background noise is eliminated and the target text fills the frame.

## Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| OCR misreads decimal point | High | User confirmation step is mandatory; yellow highlight for low confidence |
| Scanned PDF resolution too low | Medium | Warn user if rendered DPI < 200; allow manual DPI override |
| Arrow coordinates don't map correctly to PDF space | Medium | Unit test with known coordinates; validate by re-opening exported PDF |
| PyInstaller bundle too large (>500MB) | Low | Use --exclude-module for unnecessary deps; consider Nuitka as alternative |
| Tesseract not bundled correctly on Windows | Medium | Include tesseract.exe in package; set TESSDATA_PREFIX at runtime |

## Future Enhancements (Not in MVP)

- Batch mode: auto-detect all "XX.XX FS" patterns on a page and list them
- Slope calculation: given two elevations + the measured distance between them, compute and display slope %
- Comparison with design intent: import expected flow directions and flag mismatches
- Multi-page report: generate a summary of all checked flowlines across all pages
- Integration with Bluebeam: investigate Bluebeam's COM API for direct plugin capability
