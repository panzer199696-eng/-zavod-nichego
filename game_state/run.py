"""RunState — мета-состояние одного забега (вне боя).

Колода героя, реликвии, валюта «Смета», прогресс по карте этажей.
Логика наград (3 карты без повторов) живёт здесь — она headless и тестируема
отдельно от UI.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from engine.content import KofemashinaSlomana, build_stazher
from engine.models import Card, Hero, Rarity
from game_state.meta import (
    MetaState,
    available_card_factories,
    available_relic_classes,
)

# Сколько карт показывать в награду и валюта за обычный бой.
REWARD_CHOICES = 3
CURRENCY_PER_FIGHT = 25
CURRENCY_PER_ELITE = 60
CURRENCY_PER_BOSS = 120

# Веса выпадения по редкости (примерно как в StS): обычные доминируют,
# редкие — приятная находка. Выборка взвешенная, без повторов id.
RARITY_WEIGHTS: dict[Rarity, float] = {
    Rarity.COMMON: 0.65,
    Rarity.UNCOMMON: 0.28,
    Rarity.RARE: 0.07,
}


def reward_choices(pool: list[Card], count: int, rng: random.Random) -> list[Card]:
    """Выбрать ``count`` РАЗНЫХ по id карт из пула с учётом редкости.

    Выборка без повторов и взвешенная: чем реже карта, тем меньше шанс. Внутри
    одной редкости карты равновероятны. Возвращает свежие экземпляры. Если в
    пуле меньше уникальных id, чем count, вернёт сколько есть (без падения).
    """
    by_id: dict[str, Card] = {}
    for card in pool:
        by_id.setdefault(card.id, card)
    remaining = list(by_id.values())

    chosen: list[Card] = []
    for _ in range(min(count, len(remaining))):
        weights = [RARITY_WEIGHTS.get(c.rarity, 0.65) for c in remaining]
        pick = rng.choices(remaining, weights=weights, k=1)[0]
        chosen.append(pick)
        remaining.remove(pick)
    return [c.copy() for c in chosen]


@dataclass
class RunState:
    """Состояние забега: герой, колода, реликвии, валюта, позиция на карте."""

    hero: Hero
    deck: list[Card] = field(default_factory=list)
    relics: list = field(default_factory=list)
    currency: int = 0
    node_index: int = 0  # текущий узел карты этажей
    rng: random.Random = field(default_factory=random.Random)
    meta: Optional[MetaState] = None  # профиль мета-прогрессии (этап G), опционален

    @classmethod
    def new_stazher(
        cls, seed: Optional[int] = None, meta: Optional[MetaState] = None
    ) -> "RunState":
        """Свежий забег Стажёром: стартовая колода (10) + старт-бонусы из меты.

        Если передан `meta`, применяются купленные старт-бонусы (доп. HP,
        стартовая реликвия). Без меты — поведение как раньше (всё доступно).
        """
        hero = build_stazher()
        relics: list = []
        if meta is not None:
            if meta.has_bonus("krepkoe_zdorovye"):
                hero.max_hp += 5
                hero.hp += 5
            if meta.has_bonus("sluzhebnyy_avtomobil"):
                relics.append(KofemashinaSlomana())
        return cls(
            hero=hero,
            deck=[c.copy() for c in hero.starting_deck],
            relics=relics,
            currency=0,
            rng=random.Random(seed),
            meta=meta,
        )

    # --- награды ---
    def reward_choice_count(self) -> int:
        """Сколько карт показывать в награду (старт-бонус «Широкий выбор» → 4)."""
        if self.meta is not None and self.meta.has_bonus("shirokiy_vybor"):
            return 4
        return REWARD_CHOICES

    def roll_reward(self, count: Optional[int] = None) -> list[Card]:
        """Сгенерировать варианты награды (без повторов) из доступного пула.

        Пул фильтруется по мете (заблокированные карты не выпадают, пока не
        разблокированы). count по умолчанию — из reward_choice_count().
        """
        if count is None:
            count = self.reward_choice_count()
        pool = [factory() for factory in available_card_factories(self.meta)]
        return reward_choices(pool, count, self.rng)

    def add_card(self, card: Card) -> None:
        """Добавить выбранную карту в колоду (свежий экземпляр)."""
        self.deck.append(card.copy())

    def gain_currency(self, amount: int) -> None:
        if amount > 0:
            self.currency += amount

    def add_relic(self, relic) -> None:
        self.relics.append(relic)

    def roll_relic_reward(self):
        """Выдать реликвию-награду (элита/босс): случайную из ДОСТУПНЫХ (по мете),
        которой ещё нет у игрока. Детерминирована по rng. None — если выбора нет.
        """
        owned = {r.id for r in self.relics}
        available = [
            cls for cls in available_relic_classes(self.meta) if cls.id not in owned
        ]
        if not available:
            return None
        return self.rng.choice(available)()

    def bank_currency_to_meta(self) -> int:
        """Перенести валюту забега в командировочные меты (конец забега).

        Возвращает сумму перенесённого. Без меты — ничего не делает (0).
        """
        if self.meta is None or self.currency <= 0:
            return 0
        amount = self.currency
        self.meta.add_currency(amount)
        self.currency = 0
        return amount

    # --- удобство для боя ---
    def battle_deck(self) -> list[Card]:
        """Копия колоды для боевого героя (бой не должен мутировать мету)."""
        return [c.copy() for c in self.deck]
