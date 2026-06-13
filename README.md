# PDF-flowline

**A lightweight desktop tool for civil engineers: box-select elevation numbers on scanned grading plans and automatically generate flow direction arrows.**

![screenshot](assets/screenshot.png)

---

## What it does

Open a scanned PDF grading plan, click the physical measurement points on the map, box-select the corresponding elevation numbers, and the tool will:

- OCR the elevation values using **Gemini multimodal AI**
- Compute elevation differences (Δ) between consecutive points
- Draw red flow direction arrows with delta labels
- Automatically identify **HP (High Point)** and **LP (Low Point)** extrema
- Export the annotated plan as WYSIWYG image (PNG/JPG) or native PDF vector annotations

> Built by a practicing civil engineer for civil engineers.

---

## Why Gemini? (Technical Rationale)

This tool relies on **vision-based OCR** to read elevation numbers (e.g. "31.95 FS") from scanned PDF pages — often on grayscale, noisy or hand-annotated grading plans. The key requirement is **accurate number extraction** from real-world engineering drawings.

- **Google Gemini (flash-lite series)** was chosen because its multimodal capabilities — even on the small, fast `flash-lite` tier — produce accurate elevation readings from cropped plan snippets without needing a heavy model.
- **DeepSeek** does not support image input, so it cannot be used for this task.
- The engine automatically tries `gemini-3.1-flash-lite` → `gemini-2.5-flash-lite` → `gemini-2.0-flash-lite` as fallbacks in case of API instability.

You need your own **Google AI API key** to use this tool. See [Quick Start](#-quick-start) below.

---

## 🚀 Quick Start (EXE users — no Python required)

1. Download `FlowlineChecker.exe` from the **[Releases](https://github.com/wyuebei-cloud/PDF-flowline/releases)** page.
2. Get a **Google AI API key** from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
3. Create a file named `api_key.txt` in the same folder as the EXE, paste your key inside, and save.
4. Double-click `FlowlineChecker.exe` to launch.
5. Click **Open PDF**, select your grading plan, and start drawing.

## 💻 Running from Source

```bash
# Clone the repo
git clone https://github.com/wyuebei-cloud/PDF-flowline.git
cd PDF-flowline

# Create virtual environment and install dependencies
python -m venv venv
# Windows:
venv\Scripts\activate
pip install PyQt6 pymupdf opencv-python google-genai Pillow numpy

# Place your API key
echo YOUR_API_KEY > api_key.txt

# Launch
python flowline_checker\main.py
```

## 🛠 Basic Workflow

| Step | Action |
|------|--------|
| 1 | Click **Draw Flowline** on the toolbar (cursor becomes a red crosshair) |
| 2 | Click the **physical location** on the plan where elevation is measured |
| 3 | Immediately **box-select** the elevation text (e.g. "31.95 FS") |
| 4 | A blue label appears — the app returns to drawing mode **without waiting** |
| 5 | Repeat step 2–4 for subsequent points |
| 6 | Click **Done** to finalize → arrows, deltas, HP/LP labels are generated |

- **Edit** a blue number: single-click it before pressing Done
- **Select/Deselect** an arrow: click it (blue dashed box appears)
- **Delete** selected arrow: press `Delete`
- **Undo**: `Ctrl+Z`
- **Cancel** current segment: `Esc`
- **Export**: `Ctrl+S` (WYSIWYG high-res image)

### Styling
- **Arrow Size slider** — adjusts arrowhead and line thickness globally in real time
- **Text Size slider** — adjusts delta (Δ) and HP/LP label font size

---

## 📦 Repository Structure

```
PDF-flowline/
├── flowline_checker/         # Source code
│   ├── main.py               # Entry point
│   ├── core/
│   │   ├── ocr_engine.py     # Gemini API + image preprocessing
│   │   └── pdf_handler.py    # PDF rendering, annotation, export
│   ├── ui/
│   │   ├── main_window.py    # Main window with toolbar
│   │   ├── pdf_viewer.py     # PDF viewer (pan/zoom)
│   │   ├── selection_overlay.py   # Selection box overlay
│   │   └── value_dialog.py   # Manual value edit dialog
│   └── models/
│       └── data_types.py     # ElevationPoint / FlowArrow data models
├── USER_GUIDE.md             # Full user manual (English & Chinese)
├── design_history_log.md     # Development design log (bilingual)
├── LICENSE                   # MIT License
└── README.md                 # This file
```

The pre-compiled `FlowlineChecker.exe` is distributed via **GitHub Releases**, not stored in the source tree.

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

*Made by a PE at KPFF. First-gen Chinese immigrant in the PNW. Licensed PE (WA/OR) since 2013.*
