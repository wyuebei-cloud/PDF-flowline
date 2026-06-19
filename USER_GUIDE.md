# Flowline Direction Checker - User Guide / 用户指南

---

## 🇺🇸 English Version

### 🚀 Quick Start (For Standalone EXE Users)
If you are using the pre-compiled **`FlowlineChecker.exe`**, **no installation or environment setup is required!**
1. **Launch**: Locate `FlowlineChecker.exe` and double-click to run.
2. **Open PDF**: Click **Open PDF** and select your grading plan.

> **No API key needed.** OCR runs entirely offline using Baidu PP-OCRv6 tiny_rec (local ONNX Runtime). The 4.3MB model is embedded in the EXE — no internet connection required, no usage fees, zero configuration.

---

### 💻 Developer Guide: Running from Source Code
If you are running the project from the raw source code instead of the compiled EXE, you will need to set up a Python environment:

1. **How to open PowerShell in the project folder**:
   * **Address Bar Method (Easiest)**: Click the File Explorer address bar at the top of the project folder window, type `powershell` and press **Enter**.
   * **Shift + Right-Click Method**: Hold the `Shift` key, **right-click** on any empty space inside the project folder, and select **"Open PowerShell window here"** (or **"Open in Terminal"** on Windows 11).
2. **Environment Setup**: Run the following "Magic Command" in PowerShell to set up the virtual environment and install all dependencies:
   ```powershell
   python -m venv venv; .\venv\Scripts\activate; pip install paddleocr onnxruntime opencv-python pillow numpy PyQt6 pymupdf
   ```
   > PP-OCRv6 tiny_rec ONNX model (~4.3MB) downloads automatically on first launch. No API key needed.
3. **Launch from Source**: Double-click **`launch.bat`** in the project root folder.

---

### 🛠 Basic Workflow
1. **Enable Mode**: Click **Draw Flowline** on the toolbar. Your cursor will turn into a red crosshair.
2. **Select Physical Position**: Click the exact location on the plan where the elevation is measured.
3. **Box the Number**: Immediately after, draw a box around the corresponding elevation text (e.g., "31.95 FS").
4. **Asynchronous Processing**: A temporary blue label (initially `...`) will appear to the left of the box. The app immediately returns to drawing mode so you can click the next physical point and box the next number without waiting!
5. **Edit Values (Optional)**: If you notice a typo or if the OCR failed (showing `?`), single-click the blue number at any time to open the edit dialog and correct it.
6. **Finish**: Click **Done** to finalize the sequence. The tool will automatically calculate flow directions and label HP (High Point) / LP (Low Point) extrema.

### 🎨 Styling & Controls
* **Arrow Size Slider**: Adjust the thickness and arrowhead scale of all arrows globally in real time.
* **Text Size Slider**: Adjust the size of the Delta (Δ) and HP/LP labels globally in real time.
* **Pan/Zoom**: Use the **Middle Mouse Button (Wheel)** to pan (drag) and the **Scroll Wheel** to zoom.

### ✏️ Editing & Deleting
* **Select**: Click any existing arrow, number, or arrowhead. A **blue dashed box** will appear to indicate selection.
* **Delete**: Press the **`Delete`** key to remove selected items.
* **Undo**: Press **`Ctrl + Z`** to undo the last action.
* **Cancel**: Press **`Esc`** to abandon the current unfinished segment without exiting drawing mode.

### 💾 Exporting
* **To Image** (`Ctrl+S`): Save a high-resolution, scale-accurate PNG/JPG screenshot of your current view — WYSIWYG.
* **To PDF** (`Ctrl+E`): Export a **native PDF** with vector annotations. Red flow arrows, elevation delta labels, and HP/LP extrema labels are embedded as actual PDF vector annotations — fully editable in Adobe Acrobat or AutoCAD. The source PDF background is preserved.

### ⌨️ Shortcuts Summary
| Shortcut | Action |
| :--- | :--- |
| **Ctrl + Z** | Undo last action |
| **Ctrl + S** | Export annotated image |
| **Ctrl + E** | Export annotated PDF (vector) |
| **Delete** | Delete selected object |
| **Esc** | Cancel current segment |
| **Middle Drag** | Pan paper |

---

## 🇨🇳 中文版手册

### 🚀 快速开始（独立免安装 EXE 用户）
如果您使用的是打包好的 **`FlowlineChecker.exe`**，**不需要配置任何 Python 或安装运行环境！**
1. **启动**：直接双击运行 **`FlowlineChecker.exe`**。
2. **打开图纸**：点击 **Open PDF** 选择您的工程 PDF 文件。

> **无需 API Key。** OCR 使用百度 PP-OCRv6 tiny_rec 完全离线本地运行（ONNX Runtime），模型已打包进 EXE。无需网络、无需付费、零配置。

---

### 💻 开发者指南：源码运行与环境配置
如果您是从源码运行项目（不使用打包好的 EXE），则需要配置 Python 开发环境：

1. **如何在项目文件夹中打开 PowerShell**：
   * **地址栏简易法（推荐）**：在项目文件夹窗口上方的文件资源管理器**地址栏**上点击，清空内容后输入 `powershell` 并按下 **Enter (回车键)**。
   * **Shift + 右键快捷法**：按住键盘上的 `Shift` 键，在项目文件夹空白处**右键单击**，选择 **“在此处打开 PowerShell 窗口”**（Windows 11 用户亦可选择 **“在终端中打开”**）。
2. **安装依赖**：在打开的 PowerShell 窗口中运行以下"魔法命令"以创建虚拟环境并安装所有依赖包：
   ```powershell
   python -m venv venv; .\venv\Scripts\activate; pip install paddleocr onnxruntime opencv-python pillow numpy PyQt6 pymupdf
   ```
   > PP-OCRv6 tiny_rec 模型（~4.3MB）首次启动时自动下载，无需 API Key。
3. **启动运行**：双击项目根目录下的 **`launch.bat`**。

---

### 🛠 基础操作流程
1. **进入模式**：点击 **Draw Flowline**。光标会变成红色十字准星。
2. **定位物理位置**：点击图纸上高程测点的实际物理位置。
3. **框选数字**：紧接着，框选该点对应的数字文字（如 "31.95 FS"）。
4. **异步识别**：框选区域左侧会立即生成蓝色的暂存数字（初始为 `...` 代表识别中）。此时界面已切回定位模式，您可以直接点击下一个物理点和框选数字，无需等待。
5. **修改数值（可选）**：如果识别有误或显示为 `?`，您可以随时**单击**屏幕上的任意蓝色数字，在弹出的对话框中进行手动修改。
6. **结算**：点击 **Done** 结束这一组连线。程序会自动清除蓝色数字并生成流向箭头、计算高差，并识别 HP/LP 极值点。

### 🎨 样式与控制
* **Arrow Size 滑动条**：全局实时调节所有箭头的粗细和箭头帽的大小。
* **Text Size 滑动条**：全局实时调节高差数字 (Δ) 以及 HP/LP 标签的大小。
* **平移/缩放**：按住 **鼠标中键（滚轮）** 即可拖动图纸，滚动 **滚轮** 即可放大缩小。

### ✏️ 编辑与删除
* **选择**：点击任何已生成的箭头、数字或箭头帽。被选中对象会出现**蓝色虚线框**。
* **删除**：按下键盘上的 **`Delete`** 键即可删除选中的标注。
* **撤销**：按下 **`Ctrl + Z`** 可撤销上一步操作（支持多级撤销）。
* **取消**：按下 **`Esc`** 可直接放弃当前画到一半的线段，无需退出模式。

### 💾 导出成果
* **导出图片** (`Ctrl+S`)：将当前视图保存为高清 PNG/JPG 图片——所见即所得，标注位置与屏幕显示完全一致。
* **导出 PDF** (`Ctrl+E`)：导出**原生 PDF 矢量标注**文件。红色流向箭头、高差数字、HP/LP 极值标签均以 PDF 矢量注释形式嵌入，可在 Adobe Acrobat 或 AutoCAD 中直接编辑和查看，原始 PDF 底图完整保留。

### ⌨️ 快捷键汇总
| 快捷键 | 对应功能 |
| :--- | :--- |
| **Ctrl + Z** | 撤销上一步 |
| **Ctrl + S** | 导出标注图 |
| **Ctrl + E** | 导出 PDF 矢量标注 |
| **Delete** | 删除选中标注 |
| **Esc** | 取消当前线段 |
| **中键拖拽** | 平移图纸 |

---

## 📝 性能与小贴士
* **文件夹记忆**：程序会自动记忆**上次打开**和**上次导出**的文件夹路径，省去频繁寻找目录的时间。
* **多页状态保存**：在同一个 PDF 对话中翻页，各页的标注都会被自动保存，切换回来不会丢失。
