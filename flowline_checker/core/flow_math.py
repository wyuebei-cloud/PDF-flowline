"""
Flowline Checker - Pure Calculation and Parsing Logic
Zero GUI, zero ML dependencies. Fast, deterministic, and easily testable.
"""

import re
from typing import Any, List, Optional, Tuple


def extract_elevation_value(text: str) -> Optional[float]:
    """从 OCR 文本中提取浮点数值"""
    if not text:
        return None
    clean = text.strip()

    # 去掉前缀: "EL 42.30" -> "42.30"
    clean = re.sub(r'^(EL|EL\.|ELEV|TOP|BOT)[.\s]*', '', clean, flags=re.IGNORECASE).strip()
    # 去掉后缀: "31.95 FS" -> "31.95"
    clean = re.sub(r'[.\s]*(FS|EL|EL\.|ELEV|TOP|BOT)\s*$', '', clean, flags=re.IGNORECASE).strip()

    # 使用正则提取有效浮点数/整数（支持正负号、括号、中括号等包裹的情况）
    match = re.search(r'[-+]?\d+(?:\.\d+)?', clean)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def format_delta_text(p1_val: float, p2_val: float) -> str:
    """计算两点高差并返回格式化文本。若高差为 0 则返回 'FLAT'。"""
    delta = abs(p1_val - p2_val)
    if delta == 0:
        return "FLAT"
    return f"{delta:.2f}"


def determine_flow_segment(p1: Any, p2: Any) -> Tuple[Any, Any, bool]:
    """
    根据两点高程判断水流方向（水往低处流）。
    返回: (start_point, end_point, is_flat)
      - start_point: 高处点（流向起点）
      - end_point: 低处点（流向终点，箭头所指处）
      - is_flat: 是否为平段（高差为 0）
    """
    is_reverse = p2.value > p1.value
    is_flat = p1.value == p2.value
    start, end = (p1, p2) if not is_reverse else (p2, p1)
    return start, end, is_flat


def compute_extrema_labels(points: List[Any]) -> None:
    """
    计算连续点序列的 HP (High Point) / LP (Low Point) 极值标签。
    仅对长度 >= 3 的序列中的中间点进行判定。
    若点高于两侧邻点，标记为 'HP'；若低于两侧邻点，标记为 'LP'。
    """
    if len(points) < 3:
        return

    for i in range(1, len(points) - 1):
        prev_val = points[i - 1].value
        curr_val = points[i].value
        next_val = points[i + 1].value

        if curr_val is None or prev_val is None or next_val is None:
            continue

        if curr_val < prev_val and curr_val < next_val:
            points[i].label = "LP"
        elif curr_val > prev_val and curr_val > next_val:
            points[i].label = "HP"
