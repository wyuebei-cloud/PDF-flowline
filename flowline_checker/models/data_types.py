from dataclasses import dataclass
from typing import Optional

@dataclass
class ElevationPoint:
    value: float
    x: float  # X coordinate in screen space (relative to pixmap)
    y: float  # Y coordinate in screen space (relative to pixmap)
    pdf_x: float = 0.0  # X coordinate in PDF page space
    pdf_y: float = 0.0  # Y coordinate in PDF page space
    confidence: float = 0.0
    confirmed: bool = False
    label: Optional[str] = None

@dataclass
class FlowArrow:
    start_point: ElevationPoint
    end_point: ElevationPoint
    delta: float = 0.0
    id: str = ""
