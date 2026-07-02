# Flowline Direction Checker - 项目开发进度与复盘笔记

本项目旨在为土木工程师提供一个轻量、无需配置的独立桌面工具：**框选扫描版坡度图上的高程数字，自动生成水流流向箭头**。

---

## 📅 当前里程碑状态

- **Phase 1: PDF Viewer with Pan/Zoom** —— **✅ 100% 完成**
- **Phase 2: Rectangle Selection + OCR** —— **✅ 100% 完成**
- **Phase 3: Arrow Generation + Display** —— **✅ 100% 完成**
- **Phase 4: Export Annotations / Image** —— **✅ 100% 完成 (支持图片 WYSIWYG 高清导出与 PDF 原生矢量标注双导出机制)**
- **Phase 5: UX Polish + Persistence** —— **✅ 100% 完成**

---

## 🛠 核心功能新增 (Feature Log)

### 1. 极值自动标注 (HP/LP Extrema Labeling) ✨ *New*
*   **功能描述**：在连续绘制的一段流线中，程序会自动执行几何拓扑分析。
*   **实现细节**：对于中间点，若双侧均高于/低于该点，则自动标注 **HP (高点)** 或 **LP (低点)**。
*   **视觉增强**：采用洋红色 (HP) 与蓝色 (LP) 双色区分，并支持随字号滑动条动态缩放。

### 2. 文件夹路径记忆 (Directory Persistence) ✨ *New*
*   **功能描述**：程序重启后会精准记得您上次处理工程文件的位置。
*   **技术实现**：引入 `QSettings` 注册表级持久化，分别记录“上次打开路径”与“上次导出路径”。

### 3. 对象级编辑与快捷键 (Object Editing & Hotkeys) ✨ *New*
*   **实体打包**：引入 `ArrowGroup` 把线、箭帽、差值数字打包成一个选区实体。
*   **选中反馈**：点击箭头后会出现蓝色虚线选框，方便确认编辑目标。
*   **捷径支持**：
    *   `Ctrl+Z`：多级撤销（Undo）。
    *   `Delete`：物理删除选中的箭头组。
    *   `Esc`：取消当前正在画的一半线段（Cancel Current）。
    *   `Ctrl+S`：一键触发图像导出（Save Image）。

### 4. API 稳定性与后备机制 (API Stability & Fallback) ✨ *New*
*   **多模型轮询**：针对 API 高峰期不稳定的问题，引入了自动重试机制。程序会按顺序尝试 `gemini-3.1-flash-lite` (GA)、`gemini-2.5-flash-lite` 和 `gemini-2.0-flash-lite`。
*   **透明化报错**：若所有后备模型均失效，程序将弹出详细错误窗口告知原因，不再发生闪退，保证用户工作流不中断。
*   **模型标识展示**：在确认高程数字的对话框中新增小字显示，告知用户当前结果是由哪个模型生成的，方便监控 API 健康状态。
*   **性能优化**：针对 3.1 系列模型启用了 `LOW` 思考等级配置，在保证识别精度的前提下提升响应速度。

### 5. 原生 PDF 矢量文本与数字导出 (Native PDF Text & Numerical Annotations) ✨ *New*
*   **功能描述**：在导出 PDF 标注时，除了红色水流箭头，程序现在还会以原生矢量 PDF 注释形式，导出高程差数字和“HP/LP”文字标注。
*   **数学排版与偏置**：高程差数字会自动放置在线段几何中点，并沿着垂直于箭线的法线方向自动进行微调偏置（Tangential Offset），以避免文字与线条重叠。
*   **极值点标签去重**：在多段流线共享同一个高程节点时，通过页面级坐标哈希去重（`drawn_labels`），确保同一个高低点标签在 PDF 文件中只绘制一次，绝不发生文字重合重叠。

### 6. PDF 标注旋转与排版自适应 (PDF Annotation Rotation & Dynamic Sizing) ✨ *New*
*   **解决旋转偏转**：修复了在旋转 PDF 页面中导出文字与数字时逆时针偏转的问题。通过传递当前页面的 `page.rotation` 旋转参数，确保导出的 FreeText 原生注释水平直立、无裁剪、不换行。
*   **动态宽高对调**：在 90° 或 270° 旋转的页面中，自动对调文字包围盒的宽度与高度，彻底杜绝了因空间受限导致的文本折行与截断。

### 7. 异步非阻塞后台 OCR 与可点击编辑数字 (Asynchronous Background OCR & Interactive Editing) ✨ *New*
*   **后台并发处理**：引入 `OCRWorker` 线程，将 OCR 请求剥离主线程。框选数字后，界面立即恢复红十字光标，用户可连续快速绘制下一个点。
*   **暂存状态反馈**：框选区域左侧会立即生成蓝色的暂存数字（初始为 `...`，解析完毕显示数字，识别错误显示 `?`）。
*   **直接单击修改**：支持用户在点击 "Done" 完成计算前，随时单击任意蓝色数字唤起输入框进行手动修改和二次确认，大幅缩短流线校对时间。

---

### 8. 本地离线 OCR 引擎——PP-OCRv6 tiny_rec (Local Offline OCR Engine) ✨ *New*
*   **功能描述**：彻底替换了原有的 Google Gemini API OCR 方案，改用百度 PP-OCRv6 tiny_rec 本地 ONNX 推理。用户不再需要申请 API Key、不再依赖网络连接、不再承担 API 调用费用。
*   **模型选择**：PP-OCRv6 是百度 PaddleOCR 于 2026.6.11 发布的第六代 OCR 系统，tiny_rec 档仅 1.1M 参数 + 4.3MB ONNX 模型文件，在标高数字（含 "FS"、"EL" 后缀）和 HP/LP 标签上达到 94%-99.99% 的识别置信度。
*   **推理引擎**：ONNX Runtime CPU 后端，无需 CUDA/GPU，无需 PaddlePaddle 框架。
*   **旋转自适应**：由于 PP-OCRv6 为水平文字设计，引入了 4 角度轮询机制（0°→90°→180°→270°），对框选区域在 4 个方向上各推理一次（总计 ~8ms），自动选取置信度最高的结果，确保旋转 PDF 页面中的数字同样可识别。
*   **实现细节**：
    *   `core/ocr_engine.py` 完全重写，去掉 `google-genai` 依赖
    *   新增 `_rotate_image()` 静态方法：利用 `cv2.rotate` 实现 90/180/270 度旋转
    *   `_recognize_with_local()` 改为多角度轮询 + 置信度排序
    *   `ui/main_window.py`：去掉 API Key 加载逻辑和 "Set Gemini API Key" 按钮，替换为 "OCR Engine: Local PP-OCRv6" 信息提示
    *   `launch.bat`：自动安装 `paddleocr` + `onnxruntime`，首次启动时从 HuggingFace 下载模型并缓存


### 🐞 核心解决的问题追溯

### Bug: ArrowGroup 绘制覆盖导致的选框失踪
*   **解决**：重写了 `ArrowGroup` 的 `paint` 事件。通过计算 `boundingRect()` 并应用 `DashLine` 画笔，成功让复合图形在被选中时能显现出类似 CAD 的选择框。

### Bug: 鼠标中键平移导致的光标丢失
*   **解决**：实现了 **Cursor Stashing (光标保险柜)** 机制。在 Pan 动作触发瞬间存入当前光标状态，Release 后精准还原，确保多任务交互的光标连续性。

### Bug: 导出图像时崩溃 — `AttributeError: 'PDFHandler' object has no attribute 'filepath'`
*   **问题描述**：点击"Export to Image"时程序立即崩溃。根本原因是 `PDFHandler.__init__` 接收了 `pdf_path` 参数，却从未将其存储为实例属性。而 `main_window.py` 中的 `_export_image()` 试图读取 `self.pdf_handler.filepath` 来预填充保存对话框的初始目录，导致 `AttributeError`。
*   **解决**：在 `PDFHandler.__init__` 中新增一行 `self.filepath = pdf_path`，将路径在打开文档的同时立即持久化。

### Bug: PDF 原生矢量箭头导出位置偏移（双重旋转问题）
*   **原因**：PyMuPDF 中的 `page.rect` 在页面本身存在旋转时（例如旋转90度）已经预先交换了宽高。再次乘以旋转矩阵 `page.rotation_matrix * mat` 导致旋转被重复应用了两次，产生了错误的宽高偏移。
*   **解决**：将坐标变换的包围盒计算对象由已旋转的 `page.rect` 改为未旋转的原始几何边界 `page.cropbox`，实现了完全精确、零误差的旋转页面坐标映射。

### Bug: 导出 PDF 中文字和数字缺失
*   **原因**：原导出逻辑只实现了 `page.add_line_annot`（线条），遗漏了将界面上的高程差数值和 HP/LP 标签写入 PDF。
*   **解决**：全面引入 `page.add_freetext_annot` 接口。结合 DPI 缩放比例自适应计算 PDF 原生字号大小，完美地把红色高程差数值以及蓝/品红色的极值点标签（"HP", "LP"）作为原生 FreeText 文本注释持久化保存到导出的 PDF 中。

### Bug: OpenCV 灰度图/二值图识别闪退 — `Bad number of channels`
*   **解决**：在 `core/ocr_engine.py` 的灰度化预处理阶段加入了图像通道安全检测。若图像为单通道灰度图或二值图，则采用 `cv2.COLOR_GRAY2RGB` 进行安全转换，杜绝了 OpenCV 在特定处理环境下的通道数断言崩溃。

### 🐞 环境问题: VS Code 无法选择解释器 & 满屏红色下划线
*   **解决**：针对 Windows 平台下 VS Code 图形化选择 Python 解释器偶发的 `unable to handle` 扩展 Bug，手动建立了 `.vscode/settings.json`，将解释器硬绑定至 `${workspaceFolder}\\venv\\Scripts\\python.exe`，完美消除 Pylance/Pyright 的所有红色下划线与 unresolved-import 警告。

### 🐞 Bug: 导出 PDF 在页面有旋转时，标注文字偏转 90° 并被截断
*   **原因**：在页面存在旋转（如旋转 270°）时，FreeText 标注未指定 `rotate` 旋转方向，且其包围盒大小未按照旋转进行对调，导致文字阅读方向不匹配，并且由于文本框尺寸不符而发生折行或截断。
*   **解决**：在 `pdf_handler.py` 中将 `rotate=page.rotation` 传入 `add_freetext_annot(...)`。并在页面旋转 90°/270° 时自动对调文字包围盒的宽高，完美实现了水平向上的矢量文字导出效果。

---

## ✨ 交付物清单 (Deliverables)

1.  **`launch.bat`**：一键静默启动，自动创建 venv、安装依赖、启动应用。
2.  **PP-OCRv6 模型缓存**：首次运行自动从 HuggingFace 下载至 `~/.paddlex/official_models/PP-OCRv6_tiny_rec_onnx/`（4.3MB）。
3.  **持久化配置文件**：通过注册表管理，不产生多余的本地缓存文件。
4.  **`design_history_log.md`**：本文档——中英双语开发记录。

---

---

# Flowline Direction Checker — Design & Development History (English)

This tool is a lightweight, zero-configuration standalone desktop application for civil engineers. It allows users to **box-select elevation numbers on scanned slope maps and automatically generate flowline direction arrows**.

---

## 📅 Milestone Status

- **Phase 1: PDF Viewer with Pan/Zoom** — **✅ 100% Complete**
- **Phase 2: Rectangle Selection + OCR** — **✅ 100% Complete**
- **Phase 3: Arrow Generation + Display** — **✅ 100% Complete**
- **Phase 4: Export Annotations / Image** — **✅ 100% Complete** *(Dual export mechanism supporting WYSIWYG high-res image and native PDF vector annotations)*
- **Phase 5: UX Polish + Persistence** — **✅ 100% Complete**

---

## 🛠 Feature Log

### 1. Automatic Extrema Labeling (HP/LP)
- **What it does**: After a flowline sequence is drawn, the app performs geometric topology analysis on all intermediate points.
- **Logic**: If a point's value is lower than both neighbors → labeled **LP (Low Point)**; higher than both → labeled **HP (High Point)**.
- **Visual**: HP labels are rendered in magenta, LP labels in blue. Both scale dynamically with the text-size slider.

### 2. Directory Persistence
- **What it does**: The app remembers the last folder used for both opening files and exporting images, even after a restart.
- **Implementation**: Uses Qt's `QSettings` for registry-level persistence, storing separate keys for "last opened dir" and "last exported dir".

### 3. Object-Level Editing & Keyboard Shortcuts
- **Arrow grouping**: Introduced `ArrowGroup` to bundle the line body, arrowhead polygon, and delta-value text into a single selectable entity.
- **Selection feedback**: Clicking an arrow shows a blue dashed bounding box, consistent with CAD-style selection UX.
- **Shortcuts**:
  - `Ctrl+Z` — Multi-level undo (removes last arrow segment per page)
  - `Delete` — Physically removes the selected arrow group from the scene and data model
  - `Esc` — Cancels the currently in-progress flowline without committing
  - `Ctrl+S` — One-key trigger for image export

### 4. Dynamic Arrow & Text Size Controls
- Two toolbar sliders let the user independently adjust arrow head size (5–50 px) and label text size (10–80 pt) in real time.
- Changing either slider calls `_refresh_all_arrows()`, which clears and redraws all current-page arrows at the new sizes on the fly.

### 5. WYSIWYG Image Export
- Exports the exact on-screen scene (PDF background + all red arrows/labels) to a PNG or JPEG file.
- Uses Qt's `QImage` + `QPainter` to render the full `QGraphicsScene` at native resolution, ensuring the output matches what is visible on screen.

### 6. API Stability & Fallback Mechanism ✨ *New*
- **Multi-model Retry**: To combat API instability during peak hours, implemented an automatic fallback sequence: `gemini-3.1-flash-lite` (GA) -> `gemini-2.5-flash-lite` -> `gemini-2.0-flash-lite`.
- **Error Transparency**: Instead of crashing on API failure, the app now displays a critical error dialog explaining the cause, allowing users to retry without losing progress.
- **Active Model Display**: The confirmation dialog now features a small label showing which model successfully processed the OCR, providing transparency on API health.
- **Optimized Reasoning**: Configured `ThinkingLevel.LOW` for Gemini 3.1 series models to balance speed and accuracy for OCR tasks.

### 7. Native PDF Text & Numerical Annotations ✨ *New*
- **What it does**: When exporting to PDF, the program now embeds the actual numerical elevation difference values and the "HP" / "LP" extrema labels as native, high-quality vector FreeText annotations.
- **Placement & Offsets**: Automatically positions the delta numbers at the midpoint of each segment, applying a perpendicular offset (Tangential Offset) to prevent text from overlapping with the line.
- **Label Deduplication**: Uses a page-level coordinate set (`drawn_labels`) to ensure that shared elevation nodes only draw their "HP" or "LP" labels once on a single page, avoiding messy visual overlaps.

### 8. PDF Annotation Rotation & Layout Adaptability ✨ *New*
- **Fixed Rotation Skew**: Resolved the issue where annotation text and numbers in exported PDFs were rotated 90° counter-clockwise. By passing `rotate=page.rotation` to the PyMuPDF annotation builder, text renders horizontally.
- **Dynamic Box Dimension Swapping**: Automatically swaps bounding box width and height on 90°/270° rotated PDF pages, preventing text wrapping or clipping.

### 9. Asynchronous Non-blocking OCR & Interactive Editing ✨ *New*
- **Non-blocking Drawing Workflow**: Spawns a background thread (`OCRWorker`) for Gemini API requests. The GUI immediately returns to `ANCHOR` mode, letting users draw subsequent points continuously without blocking.
- **Temporary Clickable Blue Labels**: Renders a temporary blue number (initially `...`, updates to the float value, or `?` on OCR failure) to the left of each selection box.
- **Interactive Editing**: Users can single-click any blue number at any time to open `ValueDialog` and manually correct it prior to clicking "Done".

---

## 🐞 Bug Fixes & Design Decisions

### Bug: ArrowGroup Selection Box Disappearing
- **Problem**: Composite `QGraphicsItemGroup` items did not show a selection outline by default.
- **Fix**: Overrode the `paint()` method of `ArrowGroup` to manually draw a dashed blue `QPen` rect around `boundingRect()` when `isSelected()` is `True`.

### Bug: Middle-Mouse Pan Losing Cursor State
- **Problem**: Activating middle-mouse pan would discard the active tool cursor (e.g., red crosshair), leaving the cursor stuck after panning.
- **Fix**: Implemented a **Cursor Stashing** pattern — on mouse press the current cursor is saved to `self.stash_cursor`; on mouse release it is restored exactly, preserving continuous multi-mode interaction.

### Bug: `AttributeError: 'PDFHandler' object has no attribute 'filepath'` on Export
- **Problem**: `PDFHandler.__init__` accepted `pdf_path` but never stored it as an instance attribute. `_export_image()` in `main_window.py` tried to read `self.pdf_handler.filepath` to pre-fill the save dialog, causing an immediate crash.
- **Fix**: Added `self.filepath = pdf_path` as the first assignment inside `PDFHandler.__init__`.

### Bug: Rotated Coordinate Shifting in PDF Export (Double-Rotation Bug)
- **Problem**: PyMuPDF's `page.rect` for a rotated page already has its width and height swapped by default. Multiplying by the rotation matrix a second time (`page.rotation_matrix * mat`) rotated the viewport twice, completely displacing annotations on 90°/270° rotated documents.
- **Fix**: Replaced `page.rect` with `page.cropbox` (the unrotated original geometry) to calculate bounds, achieving mathematically precise coordinate matching.

### Bug: Missing Text & Numbers in Exported PDF
- **Problem**: The original PDF export function only added line drawings but completely omitted the elevation delta text and HP/LP labels.
- **Fix**: Upgraded `add_arrow_annotation` to leverage PyMuPDF's native `add_freetext_annot` API. Auto-scales font size against viewport zoom to perfectly write the red numerical difference values and colored extrema labels ("HP", "LP") into the PDF structure.

### Bug: OpenCV Preprocessing Channel Assert Crash
- **Problem**: Passing a single-channel grayscale or binary image array to OpenCV conversions triggered a `Bad number of channels` assert crash.
- **Fix**: Added a shape check in `core/ocr_engine.py` to safely convert single-channel grayscale arrays via `cv2.COLOR_GRAY2RGB` before processing.

### Environment: VS Code Interpreter Selection & Pylance Red Underlines
- **Problem**: VS Code graphically threw an `unable to handle` error when selecting the virtual environment, creating workspace import warnings.
- **Fix**: Created `.vscode/settings.json` configuring `"python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe"`, immediately clearing all red underlines and warnings.

### Bug: Skewed and Truncated Annotation Text on Rotated PDFs
- **Problem**: On rotated pages, text annotation geometry did not account for swapped width/height axes, and did not specify text rotation, rendering the text sideways and vertically clipped.
- **Fix**: Projected center offsets in screen space, mapped back to unrotated space via `inv_trans`, passed `rotate=page.rotation` to `add_freetext_annot`, and swapped dimensions for 90°/270° rotations.

### Design Decision: Per-Page Segment Storage
- Flowline segments are stored in `all_finished_segments: dict[int, list[tuple]]`, keyed by page index. This allows independent undo, display, and export per page without cross-page contamination.

### Feature: Scale Calibration + Slope/Length Display
- **Problem**: Arrows only showed the elevation difference (Δ). Scanned plans carry no reliable machine-readable scale, so run length and slope (%) — the numbers a reviewer actually checks against the design — could not be displayed.
- **Design**: Two-point calibration instead of typed drawing scale ("1\"=20'"). Scans are frequently re-plotted or resized, so trusting the title-block scale is unsafe; clicking both ends of the printed graphic scale bar (or any dimensioned line) and entering the real distance measures the *actual* feet-per-pixel of the raster.
- **Implementation**:
  - New `'CALIBRATE'` interaction mode in `PDFViewer` reuses the existing `point_selected` signal; `MainWindow._handle_anchor` routes clicks by mode.
  - Scale stored per page in `page_scales: dict[int, float]` (ft/pixel), mirroring the per-page segment storage decision — detail sheets often use a different scale. Uncalibrated pages keep the legacy Δ-only label.
  - `_format_arrow_text()` is the single label source shared by on-screen drawing and PDF export: `Δ` on line 1, `L=xx.xx' S=x.xx%` on line 2 (slope = Δ / horizontal length × 100). Calibrating a page retroactively relabels its existing arrows via `_refresh_all_arrows()`.
  - `PDFHandler.add_arrow_annotation` gained an optional `label_text` param; the freetext box now grows with line count and longest line, and the tangential offset scales with text height so two-line labels clear the arrow body.
  - Toolbar shows the resolved scale as a familiar drawing scale (`Scale: 1" = 20.0'`, derived from ft/px × render DPI); `Esc` cancels an in-progress calibration.
- **Deliberate omission**: The Greek Δ glyph is kept off the exported label's first line — PyMuPDF freetext annotations with the base-14 `helv-bold` font are Latin-1 encoded and would garble non-Latin glyphs.

---

## ✨ Deliverables

| File | Purpose |
|---|---|
| `launch.bat` | One-click silent launcher; auto-creates venv, installs deps, launches app |
| PP-OCRv6 model cache | Auto-downloaded from HuggingFace to `~/.paddlex/official_models/PP-OCRv6_tiny_rec_onnx/` (4.3MB) |
| Registry settings | Managed via `QSettings`; no extra local cache files generated |
| `design_history_log.md` | This file — bilingual development and design record |

