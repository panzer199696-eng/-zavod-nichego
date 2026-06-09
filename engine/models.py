"""Data-модели: Card, Hero, Enemy, EnemyIntent и носитель статусов Combatant.

Чистые dataclass'ы без боевой логики — её держит combat.py.
Эффекты карт лежат списком callable-операций (см. effects.py), что делает
карты декларативными и расширяемыми данными.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

from engine.statuses import STATUS, clamp_status

if TYPE_CHECKING:  # избегаем циклического импорта в рантайме
    from engine.combat import Combat


class CardType(str, Enum):
    ATTACK = "Атака"
    DEFENSE = "Защита"
    ACTION = "Действие"
    SCHEME = "Схема"
    DOCUMENT = "Документ"
    SPECIAL = "Особая"


class Rarity(str, Enum):
    COMMON = "обычная"
    UNCOMMON = "необычная"
    RARE = "редкая"


# Эффект карты — операция над боем. Возвращать ничего не обязан.
CardEffect = Callable[["Combat", "Combatant", "Combatant"], None]


@dataclass
class Card:
    """Карта. Эффекты — список компонуемых операций (effects.py)."""

    id: str
    name: str
    card_type: CardType
    cost: int
    effects: list[CardEffect] = field(default_factory=list)
    rarity: Rarity = Rarity.COMMON
    exhaust: bool = False  # уходит в изгнание после розыгрыша
    one_time: bool = False  # одноразовая (удаляется из колоды насовсем)
    no_zapal: bool = False  # финишер: не начисляет Запал Стажёру (тратит его)
    description: str = ""

    def copy(self) -> "Card":
        """Свежий экземпляр (эффекты — общие callable, состояния не несут)."""
        return Card(
            id=self.id,
            name=self.name,
            card_type=self.card_type,
            cost=self.cost,
            effects=list(self.effects),
            rarity=self.rarity,
            exhaust=self.exhaust,
            one_time=self.one_time,
            no_zapal=self.no_zapal,
            description=self.description,
        )


@dataclass
class Combatant:
    """Общий носитель HP/брони/статусов для героя и врага."""

    name: str
    max_hp: int
    hp: int
    block: int = 0
    statuses: dict[STATUS, int] = field(default_factory=dict)

    # Поведение брони при старте хода: доля сохраняемой брони (Директор = 0.3).
    block_keep_ratio: float = 0.0

    # --- статусы ---
    def get_status(self, key: STATUS) -> int:
        return self.statuses.get(key, 0)

    def set_status(self, key: STATUS, value: int) -> None:
        value = clamp_status(key, value)
        if value <= 0:
            self.statuses.pop(key, None)
        else:
            self.statuses[key] = value

    def add_status(self, key: STATUS, amount: int) -> None:
        self.set_status(key, self.get_status(key) + amount)

    def is_alive(self) -> bool:
        return self.hp > 0

    # --- урон/броня ---
    def take_damage(self, amount: int) -> int:
        """Урон с учётом брони. Возвращает фактический урон по HP."""
        if amount <= 0:
            return 0
        absorbed = min(self.block, amount)
        self.block -= absorbed
        through = amount - absorbed
        self.hp -= through
        return through

    def gain_block(self, amount: int) -> None:
        if amount > 0:
            self.block += amount

    def reset_block_for_turn(self) -> None:
        """Сброс брони в начале своего хода (Директор сохраняет долю)."""
        if self.block_keep_ratio > 0:
            self.block = int(self.block * self.block_keep_ratio)
        else:
            self.block = 0


@dataclass
class Hero(Combatant):
    """Герой. id/passive/стартовая колода — поверх Combatant."""

    id: str = ""
    passive: str = ""
    starting_deck: list[Card] = field(default_factory=list)


@dataclass
class EnemyIntent:
    """Намерение врага: что он сделает в свой ход."""

    kind: str  # "attack" | "block" | "debuff" | "skip" | "buff"
    value: int = 0
    status: Optional[STATUS] = None
    status_amount: int = 0
    label: str = ""


@dataclass
class Enemy(Combatant):
    """Враг с очередью намерений и опциональным хук-поведением.

    behavior: callable(combat, enemy, turn_index) -> None, вызывается
    перед взятием намерения (рампы атаки, чередования и т.п.).
    """

    id: str = ""
    intents: list[EnemyIntent] = field(default_factory=list)
    intent_index: int = 0
    behavior: Optional[Callable[["Combat", "Enemy", int], None]] = None

    def current_intent(self) -> EnemyIntent:
        if not self.intents:
            return EnemyIntent(kind="skip", label="ждёт")
        return self.intents[self.intent_index % len(self.intents)]

    def advance_intent(self) -> None:
        if self.intents:
            self.intent_index = (self.intent_index + 1) % len(self.intents)
