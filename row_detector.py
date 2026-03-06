"""OCR 결과를 참가자 '행' 단위로 그룹핑하는 모듈."""

from typing import Optional


def group_text_into_rows(
    ocr_results: list[dict],
    y_tolerance: float = 25.0,
) -> list[dict]:
    """OCR 결과를 y좌표 기준으로 그룹핑하여 참가자 행으로 병합한다.

    같은 행에 학번과 이름이 별도로 인식되는 경우를 처리한다.

    Args:
        ocr_results: OCRReader.read_frame()의 반환값
        y_tolerance: 같은 행으로 판단하는 y좌표 차이 허용치 (px)

    Returns:
        병합된 참가자 행 리스트:
        - text: 병합된 텍스트 (예: "20201212 김도군")
        - y_center: 행의 y축 중심
        - y_height: 행의 높이 (px)
        - confidence: 평균 신뢰도
    """
    if not ocr_results:
        return []

    # y좌표 순으로 정렬
    sorted_results = sorted(ocr_results, key=lambda x: x["y_center"])

    rows = []
    current_group = [sorted_results[0]]

    for i in range(1, len(sorted_results)):
        # 현재 그룹의 평균 y와 비교
        group_y_mean = sum(t["y_center"] for t in current_group) / len(current_group)

        if abs(sorted_results[i]["y_center"] - group_y_mean) <= y_tolerance:
            current_group.append(sorted_results[i])
        else:
            rows.append(_merge_row(current_group))
            current_group = [sorted_results[i]]

    if current_group:
        rows.append(_merge_row(current_group))

    return rows


def _merge_row(texts: list[dict]) -> dict:
    """같은 행의 여러 텍스트 검출 결과를 하나로 병합한다."""
    # x좌표(왼→오) 순으로 정렬해서 텍스트 합치기
    sorted_texts = sorted(texts, key=lambda t: t["bbox"][0][0])
    merged_text = " ".join(t["text"] for t in sorted_texts)

    # y 범위 계산
    all_y = []
    for t in texts:
        all_y.append(t["bbox"][0][1])  # top-left y
        all_y.append(t["bbox"][2][1])  # bottom-right y

    y_center = sum(t["y_center"] for t in texts) / len(texts)
    y_height = max(all_y) - min(all_y) if all_y else 30
    y_height = max(y_height, 30)  # 최소 높이 보장

    avg_conf = sum(t["confidence"] for t in texts) / len(texts)

    return {
        "text": merged_text,
        "y_center": y_center,
        "y_height": y_height,
        "confidence": avg_conf,
    }
