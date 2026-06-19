"""
PP-OCRv6 tiny_rec 本地离线 OCR 引擎（替换 Gemini API）

安装依赖:
  pip install paddleocr onnxruntime pillow opencv-python numpy

模型文件首次运行时自动下载缓存:
  ~/.paddlex/official_models/PP-OCRv6_tiny_rec_onnx/  (4.3MB)

完全离线运行，零 API 费用，零延迟。
"""

import os
import cv2
import numpy as np
from paddleocr import TextRecognition


class OCREngine:
    """本地离线 OCR 引擎 (PP-OCRv6 tiny_rec + ONNX Runtime)"""

    # 全局共享模型实例（进程内单例）
    _model = None

    def __init__(self):
        self._init_model()

    @classmethod
    def _init_model(cls):
        """懒初始化模型（首次使用时加载）"""
        if cls._model is None:
            # 抑制 paddlex 的连接检查提示
            os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
            print("[OCR] Loading PP-OCRv6 tiny_rec (local ONNX)...")
            cls._model = TextRecognition(
                model_name="PP-OCRv6_tiny_rec",
                engine="onnxruntime",
            )
            print("[OCR] Model loaded successfully!")

    @classmethod
    def preprocess_for_ocr(cls, img_path_or_array):
        """
        保留原接口的图像预处理。
        对 PP-OCRv6 而言 paddleocr 内部已做预处理，
        此处只做基本的质量增强，不改变颜色空间/尺寸。

        参数:
            img_path_or_array: str (文件路径) 或 numpy.ndarray (HWC, BGR)
        返回:
            numpy.ndarray, 增强后的图像 (RGB, uint8)
        """
        if isinstance(img_path_or_array, str):
            image = cv2.imread(img_path_or_array)
        else:
            image = img_path_or_array

        # 确保 3 通道 BGR
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # 小图放大（扫面版图纸上数字可能很小）
        h, w = image.shape[:2]
        if h < 64:
            scale = max(2, 96 // h)
            image = cv2.resize(image, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        # 可选: CLAHE 增强对比度（对扫描件有帮助）
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        # 返回 RGB uint8 (paddleocr 内部会处理颜色通道)
        return cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)

    def recognize_elevation(self, image_array):
        """
        识别标高数字。

        参数:
            image_array: numpy.ndarray, RGB uint8, 任意尺寸

        返回:
            (value, raw_text, model_name)
              value: float | None
              raw_text: str (如 "31.95 FS")
              model_name: str (固定 "PP-OCRv6_tiny_rec")
        """
        try:
            value, raw_text, _ = self._recognize_with_local(image_array)
            return value, raw_text, "PP-OCRv6_tiny_rec"
        except Exception as e:
            return None, f"LOCAL_ERROR: {str(e)}", "Error"

    def _recognize_with_local(self, image_array: np.ndarray):
        """实际调用 PP-OCRv6 进行识别，自动处理旋转。"""
        # 尝试 4 个旋转角度，取置信度最高的结果
        candidates = []
        for angle in [0, 90, 180, 270]:
            if angle == 0:
                rotated = image_array
            else:
                rotated = self._rotate_image(image_array, angle)

            result = self._model.predict(input=rotated)

            if isinstance(result[0], dict):
                raw_text = result[0].get("rec_text", "")
                score = result[0].get("rec_score", 0.0)
            else:
                raw_text = getattr(result[0], "rec_text", "")
                score = getattr(result[0], "rec_score", 0.0)

            raw_text = raw_text.strip()
            candidates.append((raw_text, score, angle))

        # 按置信度排序，取最高分
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_text, best_score, best_angle = candidates[0]

        # 低置信度过滤
        if not best_text or best_score < 0.5:
            return None, best_text if best_text else "NULL", best_score

        # 提取数值
        value = self._extract_elevation_value(best_text)
        return value, best_text, best_score

    @staticmethod
    def _rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
        """将图像旋转 90/180/270 度。"""
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return image

    @staticmethod
    def _extract_elevation_value(text: str):
        """从 OCR 文本中提取浮点数值"""
        import re
        clean = text.strip()

        # 去掉前缀: "EL 42.30" -> "42.30"
        clean = re.sub(r'^(EL|EL\.|ELEV|TOP|BOT)[.\s]*', '', clean, flags=re.IGNORECASE).strip()
        # 去掉后缀: "31.95 FS" -> "31.95"
        clean = re.sub(r'[.\s]*(FS|EL|EL\.|ELEV|TOP|BOT)\s*$', '', clean, flags=re.IGNORECASE).strip()

        try:
            return float(clean)
        except ValueError:
            return None
