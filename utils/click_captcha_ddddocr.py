# ========================================
# 点字类验证码：ddddocr 检测框 + 分类 + 按题目顺序得到点击中心点
# ========================================
# 逻辑与项目根目录 test.py 中实验代码一致，供 Page/用例复用。
# ========================================

from __future__ import annotations

import io
import re
from typing import Optional

import ddddocr
from PIL import Image


def classify_crop(image_bytes: bytes, pool: str | None) -> str:
    """先在小字符集内识别；若为空再退回全量字符集（beta 模型）。"""
    ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    if pool:
        ocr.set_ranges(pool)
        out = ocr.classification(image_bytes)
        if out:
            return out
    ocr2 = ddddocr.DdddOcr(show_ad=False, beta=True)
    return ocr2.classification(image_bytes)


def detect_and_classify_items(image_bytes: bytes, char_pool: str | None) -> list[dict]:
    """
    返回每个检测框：{"text": str, "bbox": [x1,y1,x2,y2]}（坐标相对传入的整图）。
    """
    det = ddddocr.DdddOcr(det=True, ocr=False)
    pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    bboxes = det.detection(image_bytes)
    items: list[dict] = []
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        box = [int(x1), int(y1), int(x2), int(y2)]
        crop = pil.crop((x1, y1, x2, y2))
        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        text = classify_crop(buf.getvalue(), char_pool or None)
        items.append({"text": text, "bbox": box})
    return items


def parse_instruction_target_chars(instruction_text: str) -> list[str]:
    """
    从「请依次点击：骋 捕 颁」类文案中抽出目标汉字顺序。
    """
    s = instruction_text.strip()
    for sep in ("：", ":"):
        if sep in s:
            s = s.split(sep, 1)[-1]
            break
    chars = re.findall(r"[\u4e00-\u9fff]", s)
    return chars


def centers_for_click_order(
    target_chars: list[str],
    items: list[dict],
) -> list[tuple[float, float]]:
    """
    按题目顺序，为每个目标字匹配一个检测框，返回该框中心点在图内的坐标。
    匹配策略：未使用的框中，优先 text == c 或 c in text。
    """
    unused = list(items)
    centers: list[tuple[float, float]] = []
    for ch in target_chars:
        chosen: Optional[dict] = None
        for it in unused:
            t = it.get("text") or ""
            if ch == t or (len(t) == 1 and t == ch):
                chosen = it
                break
            if ch in t:
                chosen = it
                break
        if chosen is None:
            for it in unused:
                if it.get("text"):
                    chosen = it
                    break
        if chosen is None:
            raise ValueError(f"无法为题目字 {ch!r} 匹配检测框，识别结果: {items!r}")
        unused.remove(chosen)
        x1, y1, x2, y2 = chosen["bbox"]
        centers.append(((x1 + x2) / 2.0, (y1 + y2) / 2.0))
    return centers


def ordered_click_centers_from_image(
    image_bytes: bytes,
    instruction_text: str,
    char_pool: str | None = None,
) -> list[tuple[float, float]]:
    """
    整图 PNG 字节 + 题目整段文案 -> 按顺序的点击中心（相对该图左上角，单位像素）。
    char_pool 建议为题目候选字拼接；未传则使用「题目中的字」拼接作为 pool。
    """
    targets = parse_instruction_target_chars(instruction_text)
    if not targets:
        raise ValueError(f"无法从题目解析目标字: {instruction_text!r}")
    pool = char_pool if (char_pool and char_pool.strip()) else "".join(targets)
    items = detect_and_classify_items(image_bytes, pool)
    return centers_for_click_order(targets, items)
