"""Процедурные UI-виджеты: HP-бар, иконки статусов/намерения, кнопка, карта, числа, частицы."""

from __future__ import annotations

import math
import random

import pygame

from engine.statuses import STATUS
from ui.theme import (
    BG_PANEL,
    CARD_TYPE_COLOR,
    CYAN,
    ORANGE,
    OUTLINE,
    RED,
    TEXT,
    TEXT_DIM,
    YELLOW,
    get_font,
)

# короткие буквы статусов для иконок-примитивов
STATUS_LETTER = {
    STATUS.BUREAUCRACY: "Б",
    STATUS.APPROVED: "С",
    STATUS.FROZEN: "❄",
    STATUS.DOUBT: "?",
    STATUS.FROSTBITE: "*",
    STATUS.AGENDA: "П",
    STATUS.ZAPAL: "З",
    STATUS.DELEGATED: "Д",
    STATUS.VOID: "0",
    STATUS.WEAKEN: "▼",
}

STATUS_COLOR = {
    STATUS.BUREAUCRACY: TEXT_DIM,
    STATUS.APPROVED: YELLOW,
    STATUS.FROZEN: CYAN,
    STATUS.FROSTBITE: CYAN,
    STATUS.ZAPAL: ORANGE,
    STATUS.WEAKEN: CYAN,
}


def draw_hp_bar(surf, x, y, w, h, hp, max_hp, block=0):
    """Полоса HP с числом и (опц.) бронёй слева отдельной плашкой."""
    hp = max(0, hp)
    pygame.draw.rect(surf, (40, 20, 30), (x, y, w, h), border_radius=4)
    frac = hp / max_hp if max_hp else 0
    if frac > 0:
        pygame.draw.rect(surf, RED, (x, y, int(w * frac), h), border_radius=4)
    pygame.draw.rect(surf, OUTLINE, (x, y, w, h), width=2, border_radius=4)
    font = get_font(11, bold=True)
    txt = font.render(f"{hp}/{max_hp}", True, TEXT)
    surf.blit(
        txt, (x + w // 2 - txt.get_width() // 2, y + h // 2 - txt.get_height() // 2)
    )
    if block > 0:
        bx = x - 26
        pygame.draw.circle(surf, CYAN, (bx + 10, y + h // 2), 11)
        pygame.draw.circle(surf, OUTLINE, (bx + 10, y + h // 2), 11, width=2)
        bt = get_font(11, bold=True).render(str(block), True, OUTLINE)
        surf.blit(
            bt, (bx + 10 - bt.get_width() // 2, y + h // 2 - bt.get_height() // 2)
        )


def draw_status_icons(surf, x, y, statuses: dict):
    """Иконки статусов: кружок + буква/стак. Возвращает x после последней иконки."""
    cx = x
    for key, val in statuses.items():
        if val <= 0:
            continue
        color = STATUS_COLOR.get(key, TEXT_DIM)
        pygame.draw.circle(surf, color, (cx + 9, y + 9), 9)
        pygame.draw.circle(surf, OUTLINE, (cx + 9, y + 9), 9, width=2)
        letter = STATUS_LETTER.get(key, "•")
        lt = get_font(9, bold=True).render(f"{letter}{val}", True, OUTLINE)
        surf.blit(lt, (cx + 9 - lt.get_width() // 2, y + 9 - lt.get_height() // 2))
        cx += 22
    return cx


def draw_intent(surf, cx, y, intent):
    """Иконка намерения врага: символ + число над врагом."""
    if intent is None:
        return
    kind = intent.kind
    if kind == "attack":
        sym, color, num = "⚔", RED, str(intent.value)
    elif kind == "block":
        sym, color, num = "🛡", CYAN, str(intent.value)
    elif kind == "debuff":
        sym, color, num = "💀", ORANGE, ""
    else:
        sym, color, num = "…", TEXT_DIM, ""
    pygame.draw.circle(surf, BG_PANEL, (cx, y), 16)
    pygame.draw.circle(surf, color, (cx, y), 16, width=2)
    label = f"{sym}{num}"
    ft = get_font(13, bold=True).render(label, True, color)
    surf.blit(ft, (cx - ft.get_width() // 2, y - ft.get_height() // 2))


class Button:
    """Простая кнопка с подписью и hit-test."""

    def __init__(self, rect, label, color=YELLOW, text_color=OUTLINE):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.text_color = text_color
        self.enabled = True

    def draw(self, surf):
        col = self.color if self.enabled else BG_PANEL
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, OUTLINE, self.rect, width=2, border_radius=8)
        tc = self.text_color if self.enabled else TEXT_DIM
        ft = get_font(14, bold=True).render(self.label, True, tc)
        surf.blit(
            ft,
            (
                self.rect.centerx - ft.get_width() // 2,
                self.rect.centery - ft.get_height() // 2,
            ),
        )

    def hit(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


CARD_W = 62
CARD_H = 88


def draw_card(surf, rect, card, playable: bool, cost_display: int):
    """Карта в руке: рамка по типу, стоимость, имя, описание. Тусклая если недоступна."""
    rect = pygame.Rect(rect)
    type_color = CARD_TYPE_COLOR.get(card.card_type.value, TEXT_DIM)
    body = BG_PANEL if playable else (30, 26, 48)
    pygame.draw.rect(surf, body, rect, border_radius=6)
    pygame.draw.rect(surf, type_color, rect, width=3, border_radius=6)
    # круг стоимости
    pygame.draw.circle(
        surf, YELLOW if playable else TEXT_DIM, (rect.x + 11, rect.y + 11), 10
    )
    pygame.draw.circle(surf, OUTLINE, (rect.x + 11, rect.y + 11), 10, width=2)
    ct = get_font(11, bold=True).render(str(cost_display), True, OUTLINE)
    surf.blit(
        ct, (rect.x + 11 - ct.get_width() // 2, rect.y + 11 - ct.get_height() // 2)
    )
    # имя (перенос в 2 строки по словам)
    name_color = TEXT if playable else TEXT_DIM
    _blit_wrapped(
        surf,
        card.name,
        get_font(9, bold=True),
        name_color,
        rect.x + 3,
        rect.y + 24,
        rect.w - 6,
        max_lines=2,
    )
    # описание мелким
    _blit_wrapped(
        surf,
        card.description,
        get_font(8),
        TEXT_DIM,
        rect.x + 3,
        rect.y + 50,
        rect.w - 6,
        max_lines=4,
    )


def _blit_wrapped(surf, text, font, color, x, y, max_w, max_lines=3):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
        if len(lines) >= max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    for i, line in enumerate(lines[:max_lines]):
        surf.blit(font.render(line, True, color), (x, y + i * (font.get_height() - 1)))


class FloatingNumber:
    """Всплывающее число урона/брони (поднимается и затухает)."""

    def __init__(self, x, y, value, color):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.life = 0.0
        self.duration = 0.7

    def update(self, dt):
        self.life += dt
        self.y -= 30 * dt

    def alive(self) -> bool:
        return self.life < self.duration

    def draw(self, surf):
        alpha = max(0, 255 - int(255 * self.life / self.duration))
        ft = get_font(16, bold=True).render(str(self.value), True, self.color)
        ft.set_alpha(alpha)
        surf.blit(ft, (self.x - ft.get_width() // 2, int(self.y)))


class Particle:
    """Лёгкая частица: летит по скорости, тяжелеет от гравитации, затухает.

    Прямоугольный «осколок» (искра/обрывок бумаги) — дёшево и читаемо мелким.
    """

    __slots__ = ("x", "y", "vx", "vy", "color", "size", "life", "max_life", "gravity")

    def __init__(self, x, y, vx, vy, color, size, life, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = float(size)
        self.life = float(life)
        self.max_life = float(life)
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt

    def alive(self) -> bool:
        return self.life > 0

    def draw(self, surf):
        frac = max(0.0, self.life / self.max_life) if self.max_life else 0.0
        s = max(1, int(self.size * (0.4 + 0.6 * frac)))
        chip = pygame.Surface((s, s), pygame.SRCALPHA)
        r, g, b = self.color[:3]
        chip.fill((r, g, b, int(255 * frac)))
        surf.blit(chip, (int(self.x - s / 2), int(self.y - s / 2)))


def spawn_burst(
    x,
    y,
    color,
    n=12,
    speed=130,
    size=4,
    life=0.5,
    gravity=160,
    upward=20,
    rng=random,
):
    """Радиальный всплеск из n частиц от точки (x, y).

    upward — добавочный импульс вверх (искры взлетают перед падением).
    Возвращает список Particle (вызывающий копит и обновляет их сам).
    """
    parts = []
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        spd = speed * rng.uniform(0.35, 1.0)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd - upward
        parts.append(
            Particle(
                x,
                y,
                vx,
                vy,
                color,
                rng.uniform(size * 0.6, size),
                life * rng.uniform(0.6, 1.0),
                gravity,
            )
        )
    return parts
