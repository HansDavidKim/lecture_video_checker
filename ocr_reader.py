"""EasyOCR 래퍼 모듈 — 프레임에서 텍스트와 위치를 추출한다."""

import easyocr
import numpy as np
from typing import Optional


class OCRReader:
    """EasyOCR를 사용하여 프레임에서 텍스트를 추출하는 클래스."""

    def __init__(self, languages: list[str] = None, use_gpu: bool = False):
        if languages is None:
            languages = ["ko", "en"]
        self.reader = easyocr.Reader(languages, gpu=use_gpu)

    def read_frame(
        self,
        frame: np.ndarray,
        confidence_threshold: float = 0.3,
    ) -> list[dict]:
        """프레임에서 텍스트를 추출한다.

        Args:
            frame: BGR 이미지 (numpy array)
            confidence_threshold: 이 값 미만의 신뢰도를 가진 결과는 제외

        Returns:
            각 텍스트 검출 결과 딕셔너리 리스트:
            - bbox: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            - text: 인식된 텍스트
            - confidence: 신뢰도 (0~1)
            - y_center: bbox의 y축 중심 좌표
        """
        results = self.reader.readtext(frame, detail=1, paragraph=False)

        # 아바타 영역(왼쪽 ~110px) 내의 텍스트는 제외
        h, w = frame.shape[:2]
        avatar_x_cutoff = min(110, w * 0.15)

        filtered = []
        for bbox, text, conf in results:
            if conf < confidence_threshold:
                continue

            text = text.strip()
            if not text:
                continue

            # bbox의 중심 x좌표가 아바타 영역 안이면 무시
            x_center = (bbox[0][0] + bbox[2][0]) / 2.0
            if x_center < avatar_x_cutoff:
                continue

            y_center = (bbox[0][1] + bbox[2][1]) / 2.0

            filtered.append(
                {
                    "bbox": bbox,
                    "text": text,
                    "confidence": conf,
                    "y_center": y_center,
                }
            )

        return filtered
