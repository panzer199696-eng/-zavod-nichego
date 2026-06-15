"""Мета-прогрессия между забегами (этап G) — ТОЛЬКО логика + сохранение.

«Командировочные» — мета-валюта, копится между забегами и тратится на разблокировку
карт, реликвий и старт-бонусов. UI-экран лавки — позже в Godot (GD-5). Здесь только
модель данных, гейтинг пула и сериализация в JSON, всё headless и тестируемо.

Дизайн: гейтинг ОПЦИОНАЛЕН. Без `MetaState` (meta=None) весь контент доступен —
поэтому существующие тесты/забеги не меняются. Заблокированы по умолчанию лишь
предметы из каталога ниже; всё остальное доступно всегда.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from engine.content import RELIC_REGISTRY, STAZHER_REWARD_POOL

# --- Каталог разблокировок: id -> цена в командировочных ---------------------

# Карты, закрытые по умолчанию (сильнейшие/редкие). Остальные доступны сразу.
UNLOCKABLE_CARDS: dict[str, int] = {
    "fors_mazhor": 120,
    "zamorozit_smetu": 120,
    "premiya_po_itogam": 120,
    "goret_na_rabote": 75,
}

# Реликвии, закрытые по умолчанию (постоянные пассивы этапа D).
UNLOCKABLE_RELICS: dict[str, int] = {
    "vechnyy_dedlayn": 100,
    "kaska_s_treshchinoy": 100,
    "zhurnal_zamechaniy": 100,
    "skorosshivatel": 100,
}

# Старт-бонусы: id -> (цена, описание). Эффект применяется в RunState.new_stazher.
START_BONUSES: dict[str, tuple[int, str]] = {
    "krepkoe_zdorovye": (100, "+5 к максимальному HP Стажёра"),
    "sluzhebnyy_avtomobil": (150, "Начинать забег с реликвией «Кофемашина сломана»"),
    "shirokiy_vybor": (200, "Показывать 4 карты в награду вместо 3"),
}

#: Все разблокируемые id с ценами (объединённый прайс-лист).
PRICES: dict[str, int] = {
    **UNLOCKABLE_CARDS,
    **UNLOCKABLE_RELICS,
    **{bid: cost for bid, (cost, _) in START_BONUSES.items()},
}

#: id предметов, закрытых по умолчанию (карты + реликвии). Старт-бонусы — не часть
#: пула контента, их «закрытость» проверяется отдельно через has_bonus.
_LOCKED_CONTENT: set[str] = set(UNLOCKABLE_CARDS) | set(UNLOCKABLE_RELICS)


@dataclass
class MetaState:
    """Постоянный профиль игрока между забегами: валюта + разблокировки."""

    currency: int = 0
    unlocked: set[str] = field(default_factory=set)

    # --- валюта ---
    def add_currency(self, amount: int) -> None:
        """Начислить командировочные (отрицательное игнорируется)."""
        if amount > 0:
            self.currency += amount

    # --- разблокировки ---
    def price_of(self, item_id: str) -> Optional[int]:
        """Цена предмета или None, если он не из каталога разблокировок."""
        return PRICES.get(item_id)

    def is_unlockable(self, item_id: str) -> bool:
        return item_id in PRICES

    def is_unlocked(self, item_id: str) -> bool:
        """True, если предмет уже разблокирован ИЛИ не требует разблокировки."""
        if item_id not in PRICES:
            return True  # не из каталога — доступен всегда
        return item_id in self.unlocked

    def can_unlock(self, item_id: str) -> bool:
        """Можно ли купить: предмет из каталога, ещё не куплен, хватает валюты."""
        price = PRICES.get(item_id)
        if price is None or item_id in self.unlocked:
            return False
        return self.currency >= price

    def unlock(self, item_id: str) -> bool:
        """Купить разблокировку. Возвращает True при успехе (списав валюту)."""
        if not self.can_unlock(item_id):
            return False
        self.currency -= PRICES[item_id]
        self.unlocked.add(item_id)
        return True

    def has_bonus(self, bonus_id: str) -> bool:
        """Активен ли старт-бонус (куплен)."""
        return bonus_id in START_BONUSES and bonus_id in self.unlocked

    # --- сериализация ---
    def to_dict(self) -> dict:
        return {"currency": self.currency, "unlocked": sorted(self.unlocked)}

    @classmethod
    def from_dict(cls, data: dict) -> "MetaState":
        return cls(
            currency=int(data.get("currency", 0)),
            unlocked=set(data.get("unlocked", [])),
        )

    def save(self, path: Union[str, Path]) -> None:
        """Записать профиль в JSON (UTF-8, человекочитаемо)."""
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Union[str, Path]) -> "MetaState":
        """Прочитать профиль из JSON. Нет файла/битый — свежий профиль (без падения)."""
        p = Path(path)
        if not p.exists():
            return cls()
        try:
            return cls.from_dict(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError, TypeError):
            return cls()


# --- Гейтинг пула контента по мете -----------------------------------------


def _is_available(item_id: str, meta: Optional[MetaState]) -> bool:
    """Доступен ли предмет при данной мете.

    Без меты (meta=None) гейтинга нет — доступно всё (поведение «как раньше»).
    С метой: заблокированный по умолчанию контент доступен только после покупки.
    """
    if meta is None:
        return True
    if item_id not in _LOCKED_CONTENT:
        return True
    return item_id in meta.unlocked


def available_card_factories(meta: Optional[MetaState]) -> list:
    """Фабрики карт наградного пула, доступные при данной мете.

    meta=None → весь пул (поведение без мета-системы, как раньше).
    """
    return [f for f in STAZHER_REWARD_POOL if _is_available(f().id, meta)]


def available_relic_classes(meta: Optional[MetaState]) -> list:
    """Классы реликвий, доступные при данной мете. meta=None → весь реестр."""
    return [cls for cls in RELIC_REGISTRY if _is_available(cls.id, meta)]
