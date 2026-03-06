"""영상에서 지정된 FPS로 프레임을 샘플링하는 모듈."""

import cv2
import numpy as np
from typing import Generator


def sample_frames(
    video_path: str,
    sample_fps: float = 1.0,
) -> Generator[tuple[int, np.ndarray], None, None]:
    """영상 파일에서 프레임을 일정 간격으로 추출한다.

    Args:
        video_path: 영상 파일 경로
        sample_fps: 초당 추출할 프레임 수 (기본: 1.0)

    Yields:
        (frame_index, frame) 튜플
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"영상을 열 수 없습니다: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0

    # 샘플링 간격 (프레임 단위)
    frame_interval = max(1, int(video_fps / sample_fps))

    print(f"  영상 정보: {video_fps:.1f} FPS, {total_frames} frames, {duration:.1f}초")
    print(f"  샘플링: {frame_interval} 프레임마다 1개 추출 (≈ {sample_fps} FPS)")

    frame_idx = 0
    sampled_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            sampled_count += 1
            yield frame_idx, frame

        frame_idx += 1

    cap.release()
    print(f"  총 {sampled_count}개 프레임 추출 완료")
