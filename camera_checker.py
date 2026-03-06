"""카메라 아이콘 영역의 빨간색 비율을 분석하여 카메라 ON/OFF를 판별하는 모듈."""

import cv2
import numpy as np


def check_camera_status(
    frame: np.ndarray,
    y_center: float,
    y_height: float,
    icon_width: int = 50,
    margin_right: int = 5,
    red_threshold: float = 0.08,
) -> bool:
    """카메라 아이콘이 빨간색(OFF)인지 판별한다.

    참가자 행의 오른쪽 끝 영역에서 빨간색 비율을 계산한다.
    Zoom의 카메라 OFF 아이콘은 빨간색 사선이 그어진 형태이므로,
    해당 영역에 빨간 픽셀이 일정 비율 이상이면 카메라 OFF로 판정한다.

    Args:
        frame: BGR 이미지
        y_center: 참가자 행의 y축 중심 좌표
        y_height: 참가자 행의 높이
        icon_width: 카메라 아이콘 영역의 너비 (px)
        margin_right: 오른쪽 여백 (px)
        red_threshold: 빨간색 비율 임계값

    Returns:
        True이면 카메라 OFF (빨간색 감지), False이면 카메라 ON
    """
    h, w = frame.shape[:2]

    # ROI 좌표 계산: 프레임 오른쪽 끝 영역
    pad = max(y_height * 0.4, 20)
    y_start = max(0, int(y_center - pad))
    y_end = min(h, int(y_center + pad))
    x_start = max(0, w - icon_width - margin_right)
    x_end = max(x_start + 1, w - margin_right)

    roi = frame[y_start:y_end, x_start:x_end]
    if roi.size == 0:
        return False

    # BGR → HSV 변환
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 빨간색은 HSV에서 H=0 부근과 H=180 부근 두 영역에 걸침
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([15, 255, 255])

    lower_red2 = np.array([160, 70, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 | mask2

    red_ratio = cv2.countNonZero(red_mask) / red_mask.size

    return red_ratio > red_threshold
