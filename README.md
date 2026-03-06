# Zoom Lecture Camera Checker 📹

Zoom 회의 참가자 목록을 녹화한 **영상** 또는 **스크린샷**을 분석하여, 카메라를 켜지 않은 참가자를 자동으로 탐지합니다.

## How It Works

```
영상/이미지 → 프레임 샘플링 → OCR(이름/학번 추출) → 카메라 아이콘 색상 분석 → 결과 집계
```

1. **프레임 샘플링** — 영상에서 1~2 FPS로 프레임을 추출 (스크롤 영상 처리)
2. **OCR** — EasyOCR로 각 참가자의 이름/학번을 인식
3. **카메라 판별** — 참가자 행 오른쪽의 카메라 아이콘 영역에서 HSV 빨간색 비율을 분석하여 ON/OFF 판정
4. **결과 집계** — 학번 기준 중복 제거 + 다수결(majority vote)로 최종 판정

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# 영상 처리 (기본 1 FPS 샘플링)
python main.py recording.mp4

# 샘플링 FPS 조절
python main.py recording.mp4 --fps 2.0

# 결과를 CSV로 저장
python main.py recording.mp4 --output result.csv

# 단일 이미지 테스트
python main.py screenshot.png --image
```

## Project Structure

| File | Description |
|---|---|
| `main.py` | CLI 메인 파이프라인 |
| `frame_sampler.py` | 영상 → 프레임 추출 (generator) |
| `ocr_reader.py` | EasyOCR 래퍼 + 아바타 텍스트 필터링 |
| `row_detector.py` | OCR 결과 → 참가자 행 그룹핑 |
| `camera_checker.py` | HSV 빨간색 비율 기반 카메라 ON/OFF 판별 |
| `aggregator.py` | 중복 제거, 다수결 집계, CSV 출력 |

## Example Output

```
  이름(OCR)                             카메라     등장    OFF비율
-----------------------------------------------------------------
  20201001 학생A                        ✅ ON      1       0%
  20210002 학생B                       ❌ OFF      1     100%
  20210003 학생C                        ✅ ON      1       0%
  20211004 학생D                        ✅ ON      1       0%
  조교(조교) (나)                         ❌ OFF      1     100%
  교수(담당교수) (호스트)                    ❌ OFF      1     100%
-----------------------------------------------------------------
  총 참가자: 6명
  카메라 OFF: 3명
```

## Requirements

- Python 3.10+
- OpenCV
- EasyOCR
- NumPy, Pillow