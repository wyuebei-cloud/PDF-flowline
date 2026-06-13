# Flowline Direction Checker - User Guide / 用户指南

---

## 🇺🇸 English Version

### 🚀 Quick Start (For Standalone EXE Users)
If you are using the pre-compiled **`FlowlineChecker.exe`**, **no installation or environment setup is required!**
1. **Launch**: Locate `FlowlineChecker.exe` (inside the `dist` folder, or wherever you copied it) and double-click to run.
2. **Setup API Key**: 
   * **Option A**: Click **Set Gemini API Key** on the toolbar, paste your Google AI API key, and click OK. The key will be saved to your system registry, so you only need to enter it once!
   * **Option B**: Create a text file named `api_key.txt` in the same directory as `FlowlineChecker.exe`, paste your key inside, and save. The app will load it automatically.
3. **Open PDF**: Click **Open PDF** and select your grading plan.

---

### 💻 Developer Guide: Running from Source Code
If you are running the project from the raw source code instead of the compiled EXE, you will need to set up a Python environment:

1. **How to open PowerShell in the project folder**:
   * **Address Bar Method (Easiest)**: Click the File Explorer address bar at the top of the project folder window, type `powershell` and press **Enter**.
   * **Shift + Right-Click Method**: Hold the `Shift` key, **right-click** on any empty space inside the project folder, and select **"Open PowerShell window here"** (or **"Open in Terminal"** on Windows 11).
2. **Environment Setup**: Run the following "Magic Command" in PowerShell to set up the virtual environment and install all dependencies:
   ```powershell
   python -m venv venv; .\venv\Scripts\activate; pip install PyQt6 pymupdf opencv-python google-genai Pillow numpy
   ```
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
* **To Image**: Click **Export to Image** (or `Ctrl + S`). This saves a high-resolution, scale-accurate PNG/JPG image of your current view. It guarantees that what you see on screen is exactly what you get in the output.

### ⌨️ Shortcuts Summary
| Shortcut | Action |
| :--- | :--- |
| **Ctrl + Z** | Undo last action |
| **Ctrl + S** | Export marked-up image |
| **Delete** | Delete selected object |
| **Esc** | Cancel current segment |
| **Middle Drag** | Pan paper |

---

## 🇨🇳 中文版手册

### 🚀 快速开始（独立免安装 EXE 用户）
如果您使用的是打包好的 **`FlowlineChecker.exe`**，**不需要配置任何 Python 或安装运行环境！**
1. **启动**：直接双击运行 `dist` 目录下的 **`FlowlineChecker.exe`**（您可以将该文件复制到电脑的任意位置运行）。
2. **设置 API Key**：
   * **方法 A**：点击工具栏上的 **Set Gemini API Key**，粘贴您的 Google AI API 密钥。该密钥会被安全地保存至 Windows 系统注册表中，以后运行无需再次输入！
   * **方法 B**：在 `FlowlineChecker.exe` 的同级目录下新建一个名为 `api_key.txt` 的文本文件，将密钥粘进去保存即可，程序启动时会自动读取。
3. **打开图纸**：点击 **Open PDF** 选择您的工程 PDF 文件。

---

### 💻 开发者指南：源码运行与环境配置
如果您是从源码运行项目（不使用打包好的 EXE），则需要配置 Python 开发环境：

1. **如何在项目文件夹中打开 PowerShell**：
   * **地址栏简易法（推荐）**：在项目文件夹窗口上方的文件资源管理器**地址栏**上点击，清空内容后输入 `powershell` 并按下 **Enter (回车键)**。
   * **Shift + 右键快捷法**：按住键盘上的 `Shift` 键，在项目文件夹空白处**右键单击**，选择 **“在此处打开 PowerShell 窗口”**（Windows 11 用户亦可选择 **“在终端中打开”**）。
2. **安装依赖**：在打开的 PowerShell 窗口中运行以下“魔法命令”以创建虚拟环境并安装所有依赖包：
   ```powershell
   python -m venv venv; .\venv\Scripts\activate; pip install PyQt6 pymupdf opencv-python google-genai Pillow numpy
   ```
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
* **导出图片**：点击 **Export to Image** (或快捷键 `Ctrl + S`)。这会将当前视图保存为高清 PNG/JPG 图片。该方案采用“所见即所得”技术，确保导出的标注位置与屏幕显示完全一致。

### ⌨️ 快捷键汇总
| 快捷键 | 对应功能 |
| :--- | :--- |
| **Ctrl + Z** | 撤销上一步 |
| **Ctrl + S** | 导出标注图 |
| **Delete** | 删除选中标注 |
| **Esc** | 取消当前线段 |
| **中键拖拽** | 平移图纸 |

---

## 📝 性能与小贴士
* **文件夹记忆**：程序会自动记忆**上次打开**和**上次导出**的文件夹路径，省去频繁寻找目录的时间。
* **多页状态保存**：在同一个 PDF 对话中翻页，各页的标注都会被自动保存，切换回来不会丢失。
