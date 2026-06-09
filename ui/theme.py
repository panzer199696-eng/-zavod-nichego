"""Палитра CONCEPT и шрифты с кириллицей.

PressStart2P не содержит кириллицы — для русского текста берём системный Arial.
Шрифты кэшируются по размеру.
"""

from __future__ import annotations

import os

import pygame

# --- размеры экрана (портрет) ---
SCREEN_W = 360
SCREEN_H = 640
FPS = 60

# --- палитра (CONCEPT Часть III) ---
BG_DEEP = (15, 12, 35)  # #0F0C23 (он же colorkey спрайтов)
BG_MID = (30, 26, 58)  # #1E1A3A
BG_PANEL = (42, 37, 80)  # #2A2550
YELLOW = (255, 220, 50)  # #FFDC32
ORANGE = (255, 160, 50)  # #FFA032
CYAN = (70, 220, 200)  # #46DCC8
PINK = (255, 100, 160)  # #FF64A0
RED = (255, 58, 58)  # #FF3A3A
TEXT = (240, 234, 248)  # #F0EAF8
TEXT_DIM = (136, 128, 168)  # #8880A8
EPIC = (176, 96, 255)  # #B060FF
LEGEND = (255, 184, 48)  # #FFB830
OUTLINE = (26, 21, 56)  # #1A1538

# colorkey спрайтов (фон артов = глубокий фон)
SPRITE_COLORKEY = (15, 12, 35)

# цвет рамки карты по типу
CARD_TYPE_COLOR = {
    "Атака": RED,
    "Защита": CYAN,
    "Действие": (90, 220, 120),
    "Схема": YELLOW,
    "Документ": TEXT_DIM,
    "Особая": EPIC,
}

_ARIAL = r"C:\Windows\Fonts\arial.ttf"
_ARIAL_BD = r"C:\Windows\Fonts\arialbd.ttf"

_font_cache: dict[tuple[int, bool], "pygame.font.Font"] = {}


def get_font(size: int, bold: bool = False) -> "pygame.font.Font":
    """Кэшированный Arial нужного размера (кириллица). Fallback — дефолт pygame."""
    key = (size, bold)
    cached = _font_cache.get(key)
    if cached is not None:
        return cached
    path = _ARIAL_BD if bold else _ARIAL
    if os.path.exists(path):
        font = pygame.font.Font(path, size)
    else:  # запасной вариант (на не-Windows) — системный/дефолтный
        font = pygame.font.SysFont("arial", size, bold=bold)
    _font_cache[key] = font
    return font
