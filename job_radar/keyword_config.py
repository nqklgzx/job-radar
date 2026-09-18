"""补抓关键词配置。

关键词型招聘接口（如字节、腾讯、京东、国聘）默认排序可能漏掉目标方向。
这里从 config/role_keywords.json 读取统一关键词，避免每个 adapter 各写一份。
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Iterable, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "role_keywords.json")

_DEFAULTS = {'intern': ['嵌入式实习', '硬件实习'], 'data_algo': ['嵌入式', '固件', 'MCU', 'STM32', 'BSP', '驱动开发'], 'product': ['医疗电子', '硬件研发', '电子研发'], 'decision': ['FPGA', 'DSP', '医学信号处理'], 'campus_cycle': ['2027届 嵌入式', '2028届 嵌入式', '校招 硬件', '实习 固件'], 'iguopin_extra': ['医疗器械研发']}


@lru_cache(maxsize=1)
def load_keywords() -> dict:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        data = {}
    out = dict(_DEFAULTS)
    for k, v in data.items():
        if isinstance(v, list):
            out[k] = [str(x).strip() for x in v if str(x).strip()]
    return out


def keywords(*groups: str) -> List[str]:
    cfg = load_keywords()
    out: List[str] = []
    for g in groups:
        vals: Iterable[str] = cfg.get(g, [])
        for v in vals:
            if v and v not in out:
                out.append(v)
    return out


def role_focus_keywords() -> List[str]:
    return keywords("data_algo", "product", "decision", "intern")


def iguopin_keywords() -> List[str]:
    return keywords("data_algo", "product", "decision", "intern", "campus_cycle", "iguopin_extra")
