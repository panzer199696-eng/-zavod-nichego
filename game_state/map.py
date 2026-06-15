"""Линейная карта этажей (Акт 1 и Акт 2).

Минимальный вертикальный путь акта: бой → бой → бой → бой → элита → босс.
Каждый узел знает тип, фабрику врага и валюту-награду. UI рисует столбик узлов
и подсвечивает текущий/пройденные. `build_full_map()` склеивает оба акта.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from engine.content import (
    new_avtnadzor,
    new_dedlayn,
    new_gosexpertiza,
    new_kurator,
    new_kvartalnyy_otchet,
    new_prorab,
    new_profsoyuz,
    new_sdacha_obyekta,
    new_smetchik,
    new_soglasovanie,
    new_subpodryadchik,
    new_tehnadzor,
)
from engine.models import Enemy
from game_state.run import (
    CURRENCY_PER_BOSS,
    CURRENCY_PER_ELITE,
    CURRENCY_PER_FIGHT,
)

NODE_FIGHT = "fight"
NODE_ELITE = "elite"
NODE_BOSS = "boss"


@dataclass
class MapNode:
    """Узел карты этажей."""

    kind: str  # NODE_FIGHT | NODE_ELITE | NODE_BOSS
    title: str
    enemy_factory: Callable[[], Enemy]
    currency_reward: int
    icon: str  # символ для UI (⚔ 💀 🏆)


def build_act1_map() -> list[MapNode]:
    """Путь Акта 1: 3 обычных боя → элита → босс."""
    return [
        MapNode(NODE_FIGHT, "Прораб-самодур", new_prorab, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(
            NODE_FIGHT,
            "Вечный Субподрядчик",
            new_subpodryadchik,
            CURRENCY_PER_FIGHT,
            "⚔",
        ),
        MapNode(NODE_FIGHT, "Согласование", new_soglasovanie, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(NODE_FIGHT, "Дедлайн", new_dedlayn, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(
            NODE_ELITE, "Технадзор-выездной", new_tehnadzor, CURRENCY_PER_ELITE, "💀"
        ),
        MapNode(
            NODE_BOSS,
            "Квартальный Отчёт",
            new_kvartalnyy_otchet,
            CURRENCY_PER_BOSS,
            "🏆",
        ),
    ]


def build_act2_map() -> list[MapNode]:
    """Путь Акта 2: 4 обычных боя → элита → босс (жёстче Акта 1)."""
    return [
        MapNode(NODE_FIGHT, "Сметчик-зануда", new_smetchik, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(NODE_FIGHT, "Авторский надзор", new_avtnadzor, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(NODE_FIGHT, "Госэкспертиза", new_gosexpertiza, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(NODE_FIGHT, "Профсоюз", new_profsoyuz, CURRENCY_PER_FIGHT, "⚔"),
        MapNode(NODE_ELITE, "Куратор стройки", new_kurator, CURRENCY_PER_ELITE, "💀"),
        MapNode(
            NODE_BOSS,
            "Приёмочная комиссия",
            new_sdacha_obyekta,
            CURRENCY_PER_BOSS,
            "🏆",
        ),
    ]


def build_full_map() -> list[MapNode]:
    """Полный забег: Акт 1 + Акт 2 одной вертикалью узлов."""
    return build_act1_map() + build_act2_map()
