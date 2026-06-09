"""Загрузка proto-спрайтов и фона с прозрачностью + плейсхолдеры.

Спрайты в assets/proto/ нарисованы на сплошном фоне #0F0C23 — делаем
set_colorkey, масштабируем под слот по высоте с сохранением пропорций.
Для отсутствующих артов (Дедлайн, Субподрядчик, босс) — цветной плейсхолдер.
"""

from __future__ import annotations

import os

import pygame

from ui.theme import (
    BG_DEEP,
    BG_PANEL,
    OUTLINE,
    SCREEN_H,
    SCREEN_W,
    SPRITE_COLORKEY,
    TEXT,
    get_font,
)

_PROTO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "proto")

# id врага/героя -> имя файла спрайта в assets/proto/
SPRITE_FILES = {
    "stazher": "stazher.png",
    "prorab": "prorab.png",
    "soglasovanie": "soglasovanie.png",
    "subpodryadchik": "subpodryadchik.png",
    "tehnadzor": "tehnadzor.png",
    "dedlayn": "deadline.png",
    "boss_kvartalnyy": "boss_otchet.png",
}

_sprite_cache: dict[tuple[str, int, int], "pygame.Surface"] = {}


def _load_raw(filename: str) -> "pygame.Surface | None":
    path = os.path.join(_PROTO_DIR, filename)
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert()
    img.set_colorkey(SPRITE_COLORKEY)
    return img


def _scale_to_slot(img: "pygame.Surface", w: int, h: int) -> "pygame.Surface":
    """Масштаб по высоте слота с сохранением пропорций; центр-кроп по ширине."""
    iw, ih = img.get_size()
    scale = h / ih
    new_w = max(1, int(iw * scale))
    scaled = pygame.transform.smoothscale(img, (new_w, h))
    if new_w <= w:
        return scaled
    # центр-кроп по ширине
    x = (new_w - w) // 2
    cropped = pygame.Surface((w, h))
    cropped.fill(SPRITE_COLORKEY)
    cropped.set_colorkey(SPRITE_COLORKEY)
    cropped.blit(scaled, (-x, 0))
    return cropped


def _placeholder(w: int, h: int, label: str) -> "pygame.Surface":
    """Цветной прямоугольник с подписью — заглушка под будущий арт."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, BG_PANEL, (0, 0, w, h), border_radius=8)
    pygame.draw.rect(surf, OUTLINE, (0, 0, w, h), width=3, border_radius=8)
    font = get_font(12, bold=True)
    words = label.split()
    y = h // 2 - (len(words) * 14) // 2
    for word in words:
        txt = font.render(word, True, TEXT)
        surf.blit(txt, (w // 2 - txt.get_width() // 2, y))
        y += 16
    return surf


def get_sprite(entity_id: str, label: str, w: int, h: int) -> "pygame.Surface":
    """Спрайт сущности под слот wxh. Нет файла -> подписанный плейсхолдер."""
    key = (entity_id, w, h)
    cached = _sprite_cache.get(key)
    if cached is not None:
        return cached
    filename = SPRITE_FILES.get(entity_id)
    surf: "pygame.Surface | None" = None
    if filename:
        raw = _load_raw(filename)
        if raw is not None:
            surf = _scale_to_slot(raw, w, h)
    if surf is None:
        surf = _placeholder(w, h, label)
    _sprite_cache[key] = surf
    return surf


_bg_cache: dict[tuple[int, int], "pygame.Surface"] = {}


def get_background(w: int = SCREEN_W, h: int = SCREEN_H) -> "pygame.Surface":
    """Фон боя: масштабированный bg_office.png или заливка #0F0C23."""
    key = (w, h)
    cached = _bg_cache.get(key)
    if cached is not None:
        return cached
    path = os.path.join(_PROTO_DIR, "bg_office.png")
    if os.path.exists(path):
        img = pygame.image.load(path).convert()
        surf = pygame.transform.smoothscale(img, (w, h))
    else:
        surf = pygame.Surface((w, h))
        surf.fill(BG_DEEP)
    _bg_cache[key] = surf
    return surf
