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

### 4. 动态箭头与字号调节 (Dynamic Arrow & Text Size Controls)
*   **功能描述**：工具栏配备两个独立滑动条，支持用户实时调整箭头大小（5–50 px）与标注字号（10–80 pt）。
*   **实时重绘机制**：拖动任一滑动条会触发 `_refresh_all_arrows()`，清空当前页面所有已绘制的箭头并以新尺寸瞬间重新渲染。

### 5. 所见即所得图像导出 (WYSIWYG Image Export)
*   **功能描述**：将屏幕当前场景（PDF 底图 + 所有红色箭头与高差标注）以高分辨率导出为 PNG 或 JPEG 图像。
*   **高保真渲染**：利用 Qt 的 `QImage` + `QPainter` 对完整的 `QGraphicsScene` 按原生分辨率进行离屏渲染，保证导出成果与屏幕显示完全一致。

### 6. API 稳定性与后备机制 (API Stability & Fallback) (历史记录)
*   **多模型轮询**：针对早先云端 API 高峰期不稳定的问题，曾引入自动重试机制（依次尝试 `gemini-3.1-flash-lite` -> `gemini-2.5-flash-lite` -> `gemini-2.0-flash-lite`）。现已由本地离线 OCR 全面替代。
*   **透明化报错**：若模型失效，程序弹出详细错误窗口告知原因，不发生闪退。
*   **模型标识展示**：对话框中显示模型来源，方便监控服务状态。

### 7. 原生 PDF 矢量文本与数字导出 (Native PDF Text & Numerical Annotations) ✨ *New*
*   **功能描述**：在导出 PDF 标注时，除了红色水流箭头，程序现在还会以原生矢量 PDF 注释形式，导出高程差数字和“HP/LP”文字标注。
*   **数学排版与偏置**：高程差数字会自动放置在线段几何中点，并沿着垂直于箭线的法线方向自动进行微调偏置（Tangential Offset），以避免文字与线条重叠。
*   **极值点标签去重**：在多段流线共享同一个高程节点时，通过页面级坐标哈希去重（`drawn_labels`），确保同一个高低点标签在 PDF 文件中只绘制一次，绝不发生文字重合重叠。

### 8. PDF 标注旋转与排版自适应 (PDF Annotation Rotation & Dynamic Sizing) ✨ *New*
*   **解决旋转偏转**：修复了在旋转 PDF 页面中导出文字与数字时逆时针偏转的问题。通过传递当前页面的 `page.rotation` 旋转参数，确保导出的 FreeText 原生注释水平直立、无裁剪、不换行。
*   **动态宽高对调**：在 90° 或 270° 旋转的页面中，自动对调文字包围盒的宽度与高度，彻底杜绝了因空间受限导致的文本折行与截断。

### 9. 异步非阻塞后台 OCR 与可点击编辑数字 (Asynchronous Background OCR & Interactive Editing) ✨ *New*
*   **后台并发处理**：引入 `OCRWorker` 线程，将 OCR 请求剥离主线程。框选数字后，界面立即恢复红十字光标，用户可连续快速绘制下一个点。
*   **暂存状态反馈**：框选区域左侧会立即生成蓝色的暂存数字（初始为 `...`，解析完毕显示数字，识别错误显示 `?`）。
*   **直接单击修改**：支持用户在点击 "Done" 完成计算前，随时单击任意蓝色数字唤起输入框进行手动修改和二次确认，大幅缩短流线校对时间。

### 10. 本地离线 OCR 引擎——PP-OCRv6 tiny_rec (Local Offline OCR Engine) ✨ *New*
*   **功能描述**：彻底替换了原有的 Google Gemini API OCR 方案，改用百度 PP-OCRv6 tiny_rec 本地 ONNX 推理。用户不再需要申请 API Key、不再依赖网络连接、不再承担 API 调用费用。
*   **模型选择**：PP-OCRv6 是百度 PaddleOCR 于 2026.6.11 发布的第六代 OCR 系统，tiny_rec 档仅 1.1M 参数 + 4.3MB ONNX 模型文件，在标高数字（含 "FS"、"EL" 后缀）和 HP/LP 标签上达到 94%-99.99% 的识别置信度。
*   **推理引擎**：ONNX Runtime CPU 后端，无需 CUDA/GPU，无需 PaddlePaddle 框架。
*   **旋转自适应**：由于 PP-OCRv6 为水平文字设计，引入了 4 角度轮询机制（0°→90°→180°→270°），对框选区域在 4 个方向上各推理一次（总计 ~8ms），自动选取置信度最高的结果，确保旋转 PDF 页面中的数字同样可识别。
*   **实现细节**：
    *   `core/ocr_engine.py` 完全重写，去掉 `google-genai` 依赖
    *   新增 `_rotate_image()` 静态方法：利用 `cv2.rotate` 实现 90/180/270 度旋转
    *   `_recognize_with_local()` 改为多角度轮询 + 置信度排序
    *   `ui/main_window.py`：去掉 API Key 加载逻辑和设置按钮，替换为 "OCR Engine: Local PP-OCRv6" 提示
    *   `launch.bat`：自动安装 `paddleocr` + `onnxruntime`，首次启动时自动下载并缓存模型

### 11. PDF 浏览器反色护眼模式 (PDF Viewer Invert Mode) ✨ *New*
*   **功能描述**：针对工程师长时间查看白底黑字图纸容易眼疲劳的问题，新增了独立的黑底白线反色浏览模式。
*   **毫秒级平滑渲染**：在 `PDFViewer` 中调用 Qt 底层硬件加速的 `QImage.invertPixels(QImage.InvertMode.InvertRgb)`，平滑高效，视口周围区域同步变为舒适深灰色（`#1e1e1e`）。
*   **隔离保护机制**：
    *   **OCR 识别零干扰**：底层始终保留未经反色的原始高精度渲染图（`self._raw_pixmap`）。无论在何种显示模式下框选，送入 PP-OCRv6 的始终是正色白底切图，识别精度不受任何影响。
    *   **导出 PDF/图片零干扰**：导出 PDF 依然通过 PyMuPDF 直接对矢量层进行标准标注，导出的成品文件依然是标准的白底黑字工程图；导出图片在渲染前临时切回原色，确保交付文件符合规范。
*   **快捷操作与偏好记忆**：工具栏配置纯英文 `Invert Mode` 按钮，绑定快捷键 `Ctrl+I`，并通过 `QSettings` 持久化保存用户的反色模式偏好。

### 12. 绘制中单点撤销与连通性保持 (Point-by-Point Undo During Drawing) ✨ *New*
*   **功能描述**：大幅优化了流线绘制过程中的撤销交互体验。在尚未点击 "Done" 完成流线时，按 `Ctrl+Z` 不再粗暴清空整条在建流线，而是精准回退上一个点。
*   **状态与图元精准拆解**：
    *   将每个点的物理黄色锚点标记（`_marker`）、前向连接虚线（`_line_to_prev`）、标高识别文本框（`_text_item`）以及后台 `OCRWorker` 线程精确绑定到 `ElevationPoint` 实例上。
    *   当处于等待框选数字的锚点状态（`temp_anchor` 存在）时，按 `Ctrl+Z` 仅清除当前黄色锚点，允许用户重新点选物理位置。
    *   当已添加若干完整标高点时，按 `Ctrl+Z` 仅弹出并清除末尾点及其视觉元素与 OCR 线程，**前面已绘制的节点、连接虚线和识别结果完全保留**。
*   **无缝续画与全局放弃**：撤销后界面与光标无缝维持在 `ANCHOR` 准备状态，用户可直接点击新位置继续添加后续点。若需一次性放弃整条在建流线，依然可通过键盘 `Esc` 键一键全局重置。

### 13. 单元测试体系与核心计算解耦 (Unit Testing & Pure Logic Decoupling) ✨ *New*
*   **半自动工具的测试建立原则（Testing Principles for Semi-Automated Tools）**：
    *   **原则 1：坚决不做“全自动 UI 交互测试”（No Flaky E2E GUI Tests）**
        *   半自动工具的核心特征在于**人是验证与纠错闭环的关键一环**（人手点选物理锚点、人眼框选高程、人眼复核 OCR 识别值并在异常时单击快速修改）。
        *   若采用自动化测试模拟 Qt 鼠标点击、画框拖拽与异步线程等待，测试脚本将异常臃肿脆弱，界面微调几个像素就会频繁报错（Flaky），维护成本是业务代码的数倍，ROI 极低。界面的流畅与交互体验应由发布前的**轻量手工 Checklist** 验证。
    *   **原则 2：算法剥离，锁定强确定性（Decouple Logic to Lock Determinism）**
        *   测试应当精准瞄准“纯算法、强确定性、一旦出错破坏性大且隐蔽”的模块。
        *   将原本散落在 `ui/main_window.py` 与 `core/ocr_engine.py` 内部的标高解析、高差与平水计算、流向判断、HP/LP 极值判定彻底剥离为纯 Python 模块 `core/flow_math.py`，使核心逻辑彻底脱离 Qt 与重型依赖。
    *   **原则 3：零外部测试依赖与毫秒级即时反馈（Zero Extra Deps & Sub-Second Execution）**
        *   采用 Python 内置的 `unittest` 标准库组织测试（同时原生兼容 `pytest`），不引入任何额外的第三方测试框架。
        *   避免在核心逻辑测试中导入重型 ML 库（`paddleocr` 模块加载耗时近 8 秒）；通过独立计算模块，全套 21 个单元测试可在 **0.04 秒**内瞬间完成，为开发提供零心智负担的即时反馈。
    *   **原则 4：聚焦覆盖三大易退化（Regression-Prone）核心区域**：
        1.  **标高文本正则清洗与数值提取 (`test_elevation_parsing.py`)**：覆盖常用工程后缀（`FS`, `EL`, `TOP`, `BOT`）、前缀、负高程、括号包裹及空/噪点字符串，防止后续修改正则时造成格式退化。
        2.  **几何流向与极值拓扑 (`test_flow_math.py`)**：严格验证 V 型谷地（LP）、单峰（HP）、平水（FLAT）、单调坡度以及平台段（无误判极值）的拓扑判定；锁定水往低处流的端点自动校准逻辑。
        3.  **无头 PDF 矢量导出 (`test_pdf_export.py`)**：基于 PyMuPDF 内存虚拟单页验证原生线段箭头、差值文本、极值点 FreeText 注释的完整性，并覆盖 90° 旋转图纸的导出容错。

---

## 🐞 核心解决的问题追溯与架构决策 (Bug Fixes & Decisions)

### Bug: ArrowGroup 绘制覆盖导致的选框失踪
*   **解决**：重写了 `ArrowGroup` 的 `paint` 事件。通过计算 `boundingRect()` 并应用 `DashLine` 画笔，成功让复合图形在被选中时能显现出类似 CAD 的选择框。

### Bug: 鼠标中键平移导致的光标丢失
*   **解决**：实现了 **Cursor Stashing (光标保险柜)** 机制。在 Pan 动作触发瞬间存入当前光标状态，Release 后精准还原，确保多任务交互的光标连续性。

### Bug: 导出图像时崩溃 — `AttributeError: 'PDFHandler' object has no attribute 'filepath'`
*   **问题描述**：点击 "Export to Image" 时程序立即崩溃。根本原因是 `PDFHandler.__init__` 接收了 `pdf_path` 参数，却从未将其存储为实例属性。而 `main_window.py` 中的 `_export_image()` 试图读取 `self.pdf_handler.filepath` 来预填充保存对话框的初始目录，导致 `AttributeError`。
*   **解决**：在 `PDFHandler.__init__` 中新增一行 `self.filepath = pdf_path`，将路径在打开文档的同时立即持久化。

### Bug: PDF 原生矢量箭头导出位置偏移（双重旋转问题）
*   **原因**：PyMuPDF 中的 `page.rect` 在页面本身存在旋转时（例如旋转 90 度）已经预先交换了宽高。再次乘以旋转矩阵 `page.rotation_matrix * mat` 导致旋转被重复应用了两次，产生了错误的宽高偏移。
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

### 架构决策: 按页独立存储线段数据 (Per-Page Segment Storage)
*   **设计思路**：流线段数据统一存储在以页码为键的字典中 `all_finished_segments: dict[int, list[tuple]]`。
*   **优势**：实现了翻页浏览、独立撤销、局部刷新与按页导出等操作的完全解耦，彻底避免了跨页面的数据串扰。

### 功能探索与移除: 比例尺校准与坡度/长度显示 (Scale Calibration & Slope Display - Removed)
*   **功能描述**：曾新增 "Calibrate Scale" 工具模式——点击图上两个已知实际距离的点（如图形比例尺两端），输入真实距离，按页存储 ft/像素比例；校准后每个箭头标签显示两行：高差 + `L=xx.xx' S=x.xx%`（坡度 = 高差 ÷ 水平长度 × 100%）。屏幕与 PDF 导出共用同一格式化函数，保证所见即所得。
*   **移除原因**：实测发现扫描 PDF 上无法可靠获取流线的真实长度——流线很少是两点间的直线，点选位置近似的是标注文字的锚点而非实际排水路径，由此推算的坡度"看似精确、实则不可信"。**在扫描图上，高差 (Δ) 仍是唯一可靠的信号。** 该功能整体撤下。
*   **保留的副产品**：`_finish_flowline` 布尔返回值及翻页/导出阻断、`label_text` 必填参数、共享偏移函数 `label_offset_distance`、实测文字框宽度、FLAT 平坡段渲染。
*   **教训**：用不可靠的测量值算出一个"看起来很精确"的数字，比不显示这个数字更糟——应先在实际场景中验证测量本身可信，再在其上构建显示功能。

### 🐞 Bug: 校准状态在上下文切换时泄漏（代码评审修复，随功能一并移除）
*   **问题**：代码评审确认了 4 个状态机漏洞：翻页不取消进行中的校准（两次校准点击可跨页、把错误比例存到新页）；校准中按 `Ctrl+Z` 误删已完成的箭头；OCR 未完成时切换校准模式导致半成品流线孤儿化；导出图片时把绿色校准标记点烤进成品。
*   **解决**：建立统一收口 `_cancel_calibration()`，在翻页、Undo、两种导出、Esc 处统一释放校准模式；进入校准前先校验流线确实收尾成功。
*   **教训**：可勾选的工具模式是一种有生命周期的资源——所有切换页面、文档或输出上下文的操作都必须显式释放它，而不能假设用户已手动关闭。

### 🐞 Bug: `_finish_flowline` 被挡下时调用方毫不知情（master 遗留问题）
*   **问题**：OCR 未完成或数值无效时 `_finish_flowline` 弹出警告后提前返回，但没有返回值，调用方无从判断成败：(1) 翻页照常执行 `current_page ± 1`，待定的点之后被归档到**错误的页码**下——箭头画错位置、标注导出到错误的 PDF 页；(2) 导出 PDF 照常进行并弹出 "Success"，刚画的流线被静默丢弃。
*   **解决**：`_finish_flowline` 现在返回 True/False；翻页与两种导出在收尾被挡时**中止**上下文切换，停留在原页并在状态栏提示。

### 清理: 标签几何与内容的唯一所有权（代码评审项）
*   `add_arrow_annotation` 的 `label_text` 改为**必填参数**，删除了内部重复实现高差格式化的死代码回退——标签内容只有 `MainWindow._format_arrow_text` 一个所有者。
*   标签的切向偏移公式从两个渲染器中的复制粘贴提取为共享函数 `label_offset_distance()`（`core/pdf_handler.py`），屏幕排版与 PDF 导出排版不再可能漂移。
*   导出文字框宽度改用 `fitz.get_text_length()` 按 Helvetica-Bold **实测**字符串宽度（支持多行），替代 `0.62 × 字符数` 的猜测值——今后修改标签格式不会静默裁字。

### 🐞 Bug: 相邻高程相等时画出方向随机的箭头（FLAT 平坡段）
*   **问题**：`is_reverse = p2.value > p1.value` 在两值相等时为 False，平坡段会按**点击顺序**画 p1→p2 箭头——方向毫无依据，却与真实流向以同样的"权威性"呈现。
*   **解决**：高差为 0 的段只画连线、不画箭头帽，标签显示 `FLAT`；PDF 导出同步处理（仅当高程不同时才设置箭头线端样式）。HP/LP 判定本就使用严格大小比较，相等的邻点不会被误标极值。

---

## ✨ 交付物清单 (Deliverables)

1.  **`launch.bat`**：一键静默启动，自动创建 venv、安装依赖、启动应用。
2.  **PP-OCRv6 模型缓存**：首次运行自动从 HuggingFace 下载至 `~/.paddlex/official_models/PP-OCRv6_tiny_rec_onnx/`（4.3MB）。
3.  **持久化配置文件**：通过注册表管理，不产生多余的本地缓存文件。
4.  **`flowline_checker/core/flow_math.py`**：纯计算与正则解析模块，剥离业务逻辑与 GUI。
5.  **`tests/`**：轻量单元测试套件（21 个用例，0.04s 运行时间，零额外测试依赖）。
6.  **`.github/workflows/test.yml`**：GitHub Actions CI 自动化测试流水线。
7.  **`design_history_log.md`**：本文档——中英双语开发记录。

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

### 1. Automatic Extrema Labeling (HP/LP) ✨ *New*
- **What it does**: After a flowline sequence is drawn, the app performs geometric topology analysis on all intermediate points.
- **Logic**: If a point's value is lower than both neighbors → labeled **LP (Low Point)**; higher than both → labeled **HP (High Point)**.
- **Visual**: HP labels are rendered in magenta, LP labels in blue. Both scale dynamically with the text-size slider.

### 2. Directory Persistence ✨ *New*
- **What it does**: The app remembers the last folder used for both opening files and exporting images, even after a restart.
- **Implementation**: Uses Qt's `QSettings` for registry-level persistence, storing separate keys for "last opened dir" and "last exported dir".

### 3. Object-Level Editing & Keyboard Shortcuts ✨ *New*
- **Arrow grouping**: Introduced `ArrowGroup` to bundle the line body, arrowhead polygon, and delta-value text into a single selectable entity.
- **Selection feedback**: Clicking an arrow shows a blue dashed bounding box, consistent with CAD-style selection UX.
- **Shortcuts**:
  - `Ctrl+Z` — Multi-level undo (removes last arrow segment per page)
  - `Delete` — Physically removes the selected arrow group from the scene and data model
  - `Esc` — Cancels the currently in-progress flowline without committing
  - `Ctrl+S` — One-key trigger for image export

### 4. Dynamic Arrow & Text Size Controls
- **What it does**: Two toolbar sliders let the user independently adjust arrowhead size (5–50 px) and label text size (10–80 pt) in real time.
- **Real-Time Redraw**: Changing either slider calls `_refresh_all_arrows()`, which clears and redraws all current-page arrows at the new sizes on the fly.

### 5. WYSIWYG Image Export
- **What it does**: Exports the exact on-screen scene (PDF background + all red arrows/labels) to a PNG or JPEG file.
- **High-Fidelity Rendering**: Uses Qt's `QImage` + `QPainter` to render the full `QGraphicsScene` at native resolution, ensuring the deliverable strictly matches what is visible on screen.

### 6. API Stability & Fallback Mechanism (Legacy)
- **Multi-Model Retry**: To combat earlier cloud API instability during peak hours, implemented an automatic fallback sequence (`gemini-3.1-flash-lite` -> `gemini-2.5-flash-lite` -> `gemini-2.0-flash-lite`). Now superseded by the local offline OCR engine.
- **Error Transparency**: Displays clear error dialogs explaining failure causes without crashing.
- **Model Display**: Displayed active model origin in the confirmation dialog.

### 7. Native PDF Text & Numerical Annotations ✨ *New*
- **What it does**: When exporting to PDF, the program now embeds the actual numerical elevation difference values and the "HP" / "LP" extrema labels as native, high-quality vector FreeText annotations.
- **Placement & Offsets**: Automatically positions the delta numbers at the midpoint of each segment, applying a perpendicular offset (Tangential Offset) to prevent text from overlapping with the line.
- **Label Deduplication**: Uses a page-level coordinate set (`drawn_labels`) to ensure that shared elevation nodes only draw their "HP" or "LP" labels once on a single page, avoiding messy visual overlaps.

### 8. PDF Annotation Rotation & Layout Adaptability ✨ *New*
- **Fixed Rotation Skew**: Resolved the issue where annotation text and numbers in exported PDFs were rotated 90° counter-clockwise. By passing `rotate=page.rotation` to the PyMuPDF annotation builder, text renders horizontally.
- **Dynamic Box Dimension Swapping**: Automatically swaps bounding box width and height on 90°/270° rotated PDF pages, preventing text wrapping or clipping.

### 9. Asynchronous Non-blocking OCR & Interactive Editing ✨ *New*
- **Non-blocking Drawing Workflow**: Spawns a background thread (`OCRWorker`) for OCR processing. The GUI immediately returns to `ANCHOR` mode, letting users draw subsequent points continuously without waiting.
- **Temporary Clickable Blue Labels**: Renders a temporary blue number (initially `...`, updates to the float value, or `?` on OCR failure) to the left of each selection box.
- **Interactive Editing**: Users can single-click any blue number at any time to open `ValueDialog` and manually correct it prior to clicking "Done".

### 10. Local Offline OCR Engine — PP-OCRv6 tiny_rec ✨ *New*
- **What it does**: Completely replaces the cloud-based Google Gemini API with Baidu's local offline PP-OCRv6 tiny_rec model running on ONNX Runtime CPU. Zero API key configuration, zero cloud network dependency, zero API cost.
- **Model Rationale**: PP-OCRv6 tiny_rec (Baidu PaddleOCR, released 2026.6.11) is an ultra-lightweight text recognition model with only 1.1M parameters and a 4.3MB ONNX model file. Achieves 94%–99.99% confidence on engineering elevation numbers (including "FS", "EL" suffixes) and HP/LP labels.
- **Inference Engine**: Runs locally via ONNX Runtime on CPU — no CUDA/GPU required, no heavy PaddlePaddle framework needed.
- **4-Angle Rotation Handling**: Since PP-OCRv6 is trained on horizontal text, an automated 4-direction polling mechanism (0° → 90° → 180° → 270°) rotates the cropped cropbox 4 times (~8ms total) and selects the candidate with the highest confidence score, ensuring rotated numbers on PDF plans are recognized reliably.
- **Implementation Details**:
  - `core/ocr_engine.py` completely rewritten, removing `google-genai` dependencies.
  - Added static method `_rotate_image()` using `cv2.rotate`.
  - `_recognize_with_local()` evaluates 4 rotations and sorts by confidence.
  - `ui/main_window.py`: Removed API key prompts and buttons, replaced with "OCR Engine: Local PP-OCRv6" status.
  - `launch.bat`: Automatically provisions dependencies and caches the model on first launch.

### 11. PDF Viewer Invert Mode (Dark Theme Eye Protection) ✨ *New*
- **What it does**: Provides a toggleable dark viewing mode (black background with white linework) to reduce eye strain when reviewing high-contrast civil engineering plans for extended periods.
- **Hardware-Accelerated Inversion**: Uses Qt's native `QImage.invertPixels(QImage.InvertMode.InvertRgb)` in `PDFViewer` for sub-millisecond page inversion. The outer viewport canvas automatically switches to dark gray (`#1e1e1e`) to eliminate white glare around the page.
- **Strict Isolation Guarantees**:
  - **OCR Accuracy Unaffected**: The original un-inverted raster is preserved in `self._raw_pixmap`. Box-selection cropping always extracts clean dark-text-on-white images for the local PP-OCRv6 engine, guaranteeing zero degradation in recognition accuracy.
  - **Export Integrity Unaffected**: Native PDF export (`Ctrl+E`) annotates the un-inverted vector document directly via PyMuPDF. Image export (`Ctrl+S`) renders from the raw pixmap, ensuring all exported deliverables strictly adhere to standard white-background engineering drafting specs.
- **UX & Persistence**: Features a dedicated `Invert Mode` toolbar button (shortcut: `Ctrl+I`). Viewport preference is persisted via `QSettings` across sessions.

### 12. Point-by-Point Undo During In-Progress Drawing ✨ *New*
- **What it does**: Overhauls the in-progress drawing undo experience. Pressing `Ctrl+Z` before clicking "Done" no longer discards the entire polyline sequence — it now pops only the last placed point.
- **Fine-Grained Entity Binding**:
  - Each `ElevationPoint` directly tracks its yellow anchor marker (`_marker`), dashed connecting line to the previous point (`_line_to_prev`), interactive blue/cyan text item (`_text_item`), and active background `OCRWorker` thread (`_worker`).
  - If pressed right after clicking an anchor (yellow marker present, awaiting bounding box), `Ctrl+Z` simply cancels that anchor so the user can re-click the physical point.
  - If multiple points have been completed, `Ctrl+Z` pops the trailing point and cleanly tears down its text, connecting line, anchor dot, and any running OCR worker, **preserving all preceding points, dashed lines, and values**.
- **Seamless Continuity**: Leaves the cursor in `ANCHOR` crosshair mode, allowing users to immediately click a new physical location and continue extending the flowline. `Esc` remains available to abandon the entire in-progress sequence in one keystroke.

### 13. Unit Testing Architecture & Pure Logic Decoupling ✨ *New*
- **Testing Principles for Semi-Automated Engineering Tools**:
  - **Principle 1: Avoid Flaky End-to-End GUI Testing (Anti-Pattern)**:
    In semi-automated desktop tools, human eyes and manual clicks form an essential part of the closed-loop verification (pointing physical locations, box-selecting text, visually confirming OCR readings, single-click editing). Automating Qt mouse events, bounding box drags, and asynchronous worker waits creates brittle, flaky tests with prohibitive maintenance overhead and poor ROI. UI and interaction quality are best verified via a lightweight manual pre-release checklist.
  - **Principle 2: Decouple Pure Logic to Lock Determinism**:
    Tests must strictly target deterministic, high-impact business logic. Pure mathematical functions and string parsers previously embedded within `ui/main_window.py` and `core/ocr_engine.py` were extracted into a standalone, pure-Python module: `core/flow_math.py`.
  - **Principle 3: Zero Extra Dependencies & Sub-Second Execution**:
    Tests are built using Python's standard `unittest` framework (natively runnable via `python -m unittest` or `pytest`). By isolating domain math from heavy ML frameworks (`paddleocr` takes ~8 seconds to import), all 21 unit tests execute in **0.04 seconds**, offering immediate developer feedback.
  - **Principle 4: High-Value Regression Protection**:
    1. **Elevation String Cleaning & Extraction (`test_elevation_parsing.py`)**: Tests civil engineering suffixes (`FS`, `EL`, `TOP`, `BOT`), prefixes, negative elevations, bracket wrappers, and corrupt OCR noise, safeguarding regex updates.
    2. **Flow Direction & Extrema Topology (`test_flow_math.py`)**: Verifies valley (LP), peak (HP), flat (FLAT), monotonic, and plateau sequences; ensures downhill arrow direction correction (water always flows downhill).
    3. **Headless PDF Vector Export (`test_pdf_export.py`)**: Generates in-memory test PDFs to verify line annotations, closed-arrow line ends, delta freetext, and HP/LP freetext labels, including 90° rotated page support.

---

## 🐞 Bug Fixes & Architectural Decisions

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
- **Design Rationale**: Flowline segments are stored in `all_finished_segments: dict[int, list[tuple]]`, keyed by page index.
- **Benefits**: Allows independent undo, display, and export per page without cross-page data contamination.

### Feature Exploration & Removal: Scale Calibration + Slope/Length Display
- **Problem**: Arrows only showed the elevation difference (Δ). Scanned plans carry no reliable machine-readable scale, so run length and slope (%) — the numbers a reviewer actually checks against the design — could not be displayed.
- **Design Attempt**: Two-point calibration instead of typed drawing scale ("1\"=20'"). Clicking both ends of the printed graphic scale bar and entering the real distance measured the actual feet-per-pixel of the raster. Scale was stored per page in `page_scales: dict[int, float]`.
- **Outcome & Removal**: Removed after field testing on real grading plans. There is no reliable way to capture the true flowline run length on a scanned PDF — flowlines are rarely straight point-to-point, and click positions approximate text anchors rather than the actual drainage path. A slope derived from that length is precise-looking but untrustworthy. **Elevation difference (Δ) remains the only reliable signal on scanned plans.**
- **Kept from that work**: `_finish_flowline` returning True/False with page-nav/export aborting when blocked; `label_text` as a required `add_arrow_annotation` parameter; shared `label_offset_distance()` helper; measured freetext box width via `fitz.get_text_length`; and FLAT rendering for equal elevations.
- **Lesson**: A feature that computes a plausible-looking number from an unreliable measurement is worse than not showing the number — validate the measurement's trustworthiness in the field before building the display on top of it.

### Bug: Calibration State Leaked Across Context Switches (Code-Review Fixes)
- **Problem**: A code review of the calibration feature found four confirmed state-machine holes: (1) page navigation did not cancel an in-progress calibration; (2) `Ctrl+Z` pressed mid-calibration fell through `_undo`'s guards and permanently deleted the last committed arrow; (3) toggling Calibrate Scale while a flowline point's OCR was pending orphaned the half-drawn flowline; (4) `Export to Image` rendered the scene with calibration markers still present.
- **Fix**: One chokepoint, `_cancel_calibration()` (uncheck the action; its `toggled(False)` handler owns teardown), invoked at every context switch: `_prev_page`/`_next_page`, `_undo`, `_export_image`, `_export_pdf`, and `_cancel_current`.
- **Lesson**: A checkable tool mode is a resource with a lifecycle — every action that changes page, document, or output context must release it explicitly, not assume the user toggled it off first.

### Bug: Blocked `_finish_flowline` Silently Ignored by Callers (Pre-Existing)
- **Problem**: `_finish_flowline` early-returns with a warning when a point's OCR is still pending or its value is invalid — but it returned nothing, so callers couldn't tell. Two consequences: (1) page navigation incremented `current_page` anyway, filing pending points under the wrong page index; (2) `Export to PDF` proceeded anyway and popped a "Success" dialog while silently omitting the flowline just drawn.
- **Fix**: `_finish_flowline` now returns `True`/`False`. Page navigation and both export paths check the result and abort the context switch when finalization is blocked, keeping the user on the page with a status-bar hint.

### Cleanup: One Owner for Label Geometry and Content (Code-Review Items)
- `label_text` is now a **required** parameter of `add_arrow_annotation`; the dead `None` fallback that re-implemented delta formatting inside `PDFHandler` is gone — `MainWindow._format_arrow_text` is the only place that knows what an arrow label says.
- The tangential label-offset formula moved to a shared module-level helper `label_offset_distance()` in `core/pdf_handler.py`, imported by the on-screen renderer — screen and PDF placement can no longer drift.
- The freetext box width is now **measured** with `fitz.get_text_length(line, fontname="hebo", ...)` instead of heuristic character counts.

### Bug: Equal Elevations Drew an Arbitrary-Direction Arrow (FLAT Segment)
- **Problem**: `is_reverse = p2.value > p1.value` is False when two elevations are equal, so a flat segment silently drew an arrow from p1 to p2 — the direction was just click order, presented with the same authority as a real flow direction.
- **Fix**: Flat segments (delta == 0) are drawn as a plain connecting line with no arrowhead, labeled `FLAT`. The PDF export mirrors this: `set_line_ends` with the closed-arrow head is only applied when the elevations differ. HP/LP detection already used strict comparisons, so equal neighbors were never mislabeled.

---

## ✨ 交付物清单 / Deliverables

| 文件/项目 (File / Folder) | 作用描述 (Purpose) |
|---|---|
| `launch.bat` | 一键静默启动脚本；自动建 venv、装依赖、启动应用 (One-click silent launcher) |
| PP-OCRv6 model cache | 首次运行自动从 HuggingFace 下载至本地的 4.3MB 离线模型 (Local offline OCR model) |
| Registry settings | 基于 `QSettings` 管理的注册表配置，零本地缓存冗余 (Managed via QSettings) |
| `flowline_checker/core/flow_math.py` | 纯计算与正则解析模块，业务与 UI 彻底解耦 (Pure calculation & parsing logic) |
| `tests/` | 单元测试套件（21 个用例，0.04s 运行时间，零额外测试依赖）(Unit test suite) |
| `.github/workflows/test.yml` | GitHub Actions CI 自动化测试流水线 (GitHub Actions CI workflow) |
| `design_history_log.md` | 本文档——中英双语开发与设计决策记录 (Bilingual development and design record) |
