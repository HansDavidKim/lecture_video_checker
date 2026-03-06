"""Zoom 강의 참가자 카메라 ON/OFF 자동 체크 시스템.

참가자 목록을 녹화한 영상 또는 스크린샷을 입력받아,
각 참가자의 카메라 ON/OFF 상태를 판별하고 결과를 출력한다.

Usage:
    # 영상 처리
    python main.py video.mp4
    python main.py video.mp4 --fps 2.0 --output results.csv

    # 단일 이미지 테스트
    python main.py dataset/image.png --image
"""

import argparse
import sys

import cv2

from frame_sampler import sample_frames
from ocr_reader import OCRReader
from row_detector import group_text_into_rows
from camera_checker import check_camera_status
from aggregator import aggregate_results, save_results_csv


def print_results(results: list[dict]) -> None:
    """결과를 테이블 형태로 콘솔에 출력한다."""
    print("\n" + "=" * 65)
    print("  결과")
    print("=" * 65)
    print(f"  {'이름(OCR)':<30} {'카메라':>8} {'등장':>6} {'OFF비율':>8}")
    print("-" * 65)

    camera_off_list = []
    for r in results:
        status = "❌ OFF" if r["camera_off"] else "✅ ON"
        ratio_str = f"{r['camera_off_ratio']:.0%}"
        print(
            f"  {r['name']:<30} {status:>8} {r['appearances']:>6} {ratio_str:>8}"
        )
        if r["camera_off"]:
            camera_off_list.append(r["name"])

    print("-" * 65)
    print(f"  총 참가자: {len(results)}명")
    print(f"  카메라 OFF: {len(camera_off_list)}명")

    if camera_off_list:
        print("\n  ⚠️  카메라를 끈 참가자:")
        for name in camera_off_list:
            print(f"    • {name}")

    print()


def process_video(
    video_path: str,
    sample_fps: float = 1.0,
    confidence_threshold: float = 0.3,
    output_csv: str = None,
) -> list[dict]:
    """영상을 처리하여 참가자 카메라 상태를 판별한다."""
    print(f"🎬 영상 처리 시작: {video_path}")
    print(f"   샘플링 FPS: {sample_fps}")

    reader = OCRReader(languages=["ko", "en"], use_gpu=False)
    all_frame_results = []

    for frame_idx, frame in sample_frames(video_path, sample_fps):
        print(f"\r  프레임 #{frame_idx} 처리 중...", end="", flush=True)

        # OCR로 텍스트 추출
        ocr_results = reader.read_frame(frame, confidence_threshold)

        # 참가자 행으로 그룹핑
        rows = group_text_into_rows(ocr_results)

        # 각 행의 카메라 상태 판별
        for row in rows:
            row["camera_off"] = check_camera_status(
                frame, row["y_center"], row["y_height"]
            )

        all_frame_results.append(rows)

    print()  # newline after \r

    # 중복 제거 및 집계
    results = aggregate_results(all_frame_results)

    # 결과 출력
    print_results(results)

    # CSV 저장
    if output_csv:
        save_results_csv(results, output_csv)

    return results


def process_image(
    image_path: str,
    confidence_threshold: float = 0.3,
    output_csv: str = None,
) -> list[dict]:
    """단일 이미지를 처리하여 참가자 카메라 상태를 판별한다."""
    print(f"🖼️  이미지 처리: {image_path}")

    reader = OCRReader(languages=["ko", "en"], use_gpu=False)

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ 이미지를 읽을 수 없습니다: {image_path}")
        sys.exit(1)

    # OCR
    ocr_results = reader.read_frame(frame, confidence_threshold)

    # 행 그룹핑
    rows = group_text_into_rows(ocr_results)

    # 카메라 상태 판별
    for row in rows:
        row["camera_off"] = check_camera_status(
            frame, row["y_center"], row["y_height"]
        )

    # 집계 (단일 프레임이므로 중복 없음)
    results = aggregate_results([rows])

    print_results(results)

    if output_csv:
        save_results_csv(results, output_csv)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Zoom 강의 참가자 카메라 ON/OFF 체크 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py recording.mp4                    # 영상 처리 (1 FPS)
  python main.py recording.mp4 --fps 2.0          # 영상 처리 (2 FPS)
  python main.py recording.mp4 --output result.csv # CSV 저장
  python main.py screenshot.png --image            # 단일 이미지 테스트
        """,
    )
    parser.add_argument("input", help="영상 파일 또는 이미지 경로")
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="영상 샘플링 FPS (기본: 1.0, 높을수록 정밀하지만 느림)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.3,
        help="OCR 신뢰도 임계값 (기본: 0.3)",
    )
    parser.add_argument(
        "--image",
        action="store_true",
        help="단일 이미지로 처리",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="결과를 저장할 CSV 파일 경로",
    )

    args = parser.parse_args()

    if args.image:
        process_image(args.input, args.confidence, args.output)
    else:
        process_video(args.input, args.fps, args.confidence, args.output)


if __name__ == "__main__":
    main()