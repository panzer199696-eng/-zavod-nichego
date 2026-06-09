"""Компонуемые операции-эффекты карт.

Каждая фабрика возвращает callable ``(combat, source, target) -> None``.
Карта собирается декларативно из списка таких операций — новые карты
описываются данными, без правки движка.
"""

from __future__ import annotations

from typing import Optional

from engine.statuses import STATUS


def deal_damage(amount: int):
    """Нанести фиксированный урон цели (с учётом её брони)."""

    def _op(combat, source, target):
        combat.deal_damage(source, target, amount)

    return _op


def gain_block(amount: int):
    """Дать броню источнику."""

    def _op(combat, source, target):
        source.gain_block(amount)

    return _op


def apply_status(key: STATUS, amount: int, to_target: bool = True):
    """Наложить статус на цель (по умолчанию) или на источник."""

    def _op(combat, source, target):
        who = target if to_target else source
        who.add_status(key, amount)

    return _op


def draw_cards(n: int):
    def _op(combat, source, target):
        combat.draw(n)

    return _op


def gain_energy(n: int):
    def _op(combat, source, target):
        combat.energy += n

    return _op


def gain_status_self(key: STATUS, amount: int):
    """Дать статус самому источнику (Запал, Пустота, Сомнение себе и т.п.)."""

    def _op(combat, source, target):
        source.add_status(key, amount)

    return _op


def draw_if_cards_played(n_draw: int, threshold: int):
    """Добрать n_draw карт, если эта карта — threshold-я за ход или позже.

    «Принеси-подай»: при 3+ картах за ход — тянуть 1.
    На момент эффекта текущая карта ещё НЕ учтена в cards_played_this_turn
    (инкремент в combat.play_card_instance идёт после эффектов), поэтому
    сравниваем с threshold-1 — итог включает текущую карту.
    """

    def _op(combat, source, target):
        if combat.cards_played_this_turn + 1 >= threshold:
            combat.draw(n_draw)

    return _op


def scale_damage_from_cards_played(multiplier: int):
    """Урон = multiplier × число сыгранных за ход карт (включая эту).

    «Переработка по-молодому»: 2 урона × число карт за ход.
    """

    def _op(combat, source, target):
        dmg = multiplier * (combat.cards_played_this_turn + 1)
        combat.deal_damage(source, target, dmg)

    return _op


def scale_damage_from_status(
    key: STATUS,
    multiplier: int,
    cap: Optional[int] = None,
    consume: bool = False,
):
    """Урон = multiplier × стаки статуса источника (с опц. кэпом).

    Используется для «Аврала» (3 × Запал, макс 24).
    consume=True обнуляет статус после применения.
    """

    def _op(combat, source, target):
        stacks = source.get_status(key)
        dmg = multiplier * stacks
        if cap is not None:
            dmg = min(dmg, cap)
        combat.deal_damage(source, target, dmg)
        if consume:
            source.set_status(key, 0)

    return _op


def scale_damage_from_block(multiplier: float):
    """Урон = броня источника × multiplier (КМ-2 / Спрос с подчинённых)."""

    def _op(combat, source, target):
        dmg = int(source.block * multiplier)
        combat.deal_damage(source, target, dmg)

    return _op
