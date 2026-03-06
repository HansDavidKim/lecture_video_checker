"""여러 프레임의 결과를 학번 기준으로 중복 제거하고 집계하는 모듈."""

import re
import csv
from typing import Optional


def extract_student_id(text: str) -> Optional[str]:
    """텍스트에서 학번(7~8자리 숫자)을 추출한다."""
    match = re.search(r"\d{7,8}", text)
    return match.group() if match else None


def aggregate_results(all_frame_results: list[list[dict]]) -> list[dict]:
    """여러 프레임의 참가자 결과를 집계하고 중복을 제거한다.

    같은 참가자가 여러 프레임에 등장할 수 있으므로, 학번 또는
    이름을 key로 사용하여 중복을 제거하고, 다수결(majority vote)로
    최종 카메라 상태를 결정한다.

    Args:
        all_frame_results: 각 프레임의 참가자 행 결과 리스트

    Returns:
        집계된 참가자 리스트:
        - key: 고유 참가자 식별자 (학번 또는 이름)
        - name: 참가자 이름 (가장 높은 신뢰도의 텍스트)
        - camera_off: 카메라 OFF 여부 (다수결)
        - camera_off_ratio: 카메라 OFF로 판정된 비율
        - appearances: 등장 프레임 수
    """
    participant_map: dict[str, dict] = {}

    for frame_results in all_frame_results:
        for row in frame_results:
            key = _get_participant_key(row["text"])
            if key is None:
                continue

            if key not in participant_map:
                participant_map[key] = {
                    "key": key,
                    "text": row["text"],
                    "camera_off_count": 0,
                    "total_count": 0,
                    "best_conf": 0.0,
                }

            participant_map[key]["total_count"] += 1

            if row.get("camera_off", False):
                participant_map[key]["camera_off_count"] += 1

            # 가장 높은 신뢰도의 텍스트를 유지
            conf = row.get("confidence", 0)
            if conf > participant_map[key]["best_conf"]:
                participant_map[key]["text"] = row["text"]
                participant_map[key]["best_conf"] = conf

    # 최종 결과 생성
    results = []
    for key, data in participant_map.items():
        total = data["total_count"]
        off_count = data["camera_off_count"]
        off_ratio = off_count / total if total > 0 else 0

        results.append(
            {
                "key": key,
                "name": data["text"],
                "camera_off": off_ratio > 0.5,  # 다수결
                "camera_off_ratio": off_ratio,
                "appearances": total,
            }
        )

    results.sort(key=lambda x: x["key"])
    return results


def save_results_csv(results: list[dict], output_path: str) -> None:
    """결과를 CSV 파일로 저장한다."""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["학번/ID", "이름(OCR)", "카메라", "OFF비율", "등장횟수"])

        for r in results:
            status = "OFF" if r["camera_off"] else "ON"
            writer.writerow(
                [
                    r["key"],
                    r["name"],
                    status,
                    f"{r['camera_off_ratio']:.2f}",
                    r["appearances"],
                ]
            )

    print(f"\n📄 결과가 {output_path}에 저장되었습니다.")


def _get_participant_key(text: str) -> Optional[str]:
    """참가자의 고유 식별 키를 생성한다.

    학번(7~8자리)이 있으면 학번을, 없으면 정제된 텍스트를 사용한다.
    """
    student_id = extract_student_id(text)
    if student_id:
        return student_id

    # 학번이 없는 경우 텍스트 정제 후 사용
    cleaned = re.sub(r"\s+", "", text).strip()
    if len(cleaned) >= 2:
        return cleaned

    return None
