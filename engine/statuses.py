"""Реестр статус-эффектов и их поведение (тики, кэпы, спадание).

Data-driven: каждый статус описан декларативно через ``StatusSpec``.
Новые статусы добавляются записью в ``_SPECS`` без правки боевого движка.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class STATUS(str, Enum):
    """Идентификаторы статусов. Значение — машинное имя (для сериализации/JSON)."""

    BLOCK = "block"  # Броня (особый: хранится в .block, не в общем словаре)
    BUREAUCRACY = "bureaucracy"  # Бюрократия: -1 энергии в начале хода за стак
    APPROVED = "approved"  # Согласовано: следующая карта = 0 энергии
    FROZEN = "frozen"  # Заморожено: враг пропускает атаку (стак = N ходов)
    DOUBT = "doubt"  # Сомнение (Философ)
    FROSTBITE = "frostbite"  # Промерзание: +1 к стоимости карт за стак
    AGENDA = "agenda"  # Повестка (Менеджер)
    ZAPAL = "zapal"  # Запал (Стажёр): обнуляется в конце хода
    DELEGATED = "delegated"  # Поручено (Директор)
    VOID = "void"  # Пустота: внутрибоевой ресурс, кэп 10
    WEAKEN = "weaken"  # Простой: -3 к урону атаки врага за стак (контроль-дебаф)


@dataclass(frozen=True)
class StatusSpec:
    """Декларативное описание статуса.

    cap: максимум стаков (None — без лимита).
    reset_on_turn_end: обнуляется в конце хода владельца (Запал).
    decay_per_turn: на сколько спадает в начале хода владельца.
    """

    key: STATUS
    cap: Optional[int] = None
    reset_on_turn_end: bool = False
    decay_per_turn: int = 0  # спад в начале хода владельца
    decay_on_turn_end: int = 0  # спад в конце хода владельца (после действий)


_SPECS: dict[STATUS, StatusSpec] = {
    # Бюрократия: −1 энергии/стак, но это ДАВЛЕНИЕ, а не спираль смерти —
    # кэп 3 и спад 1/ход не дают энергии залочиться в ноль навсегда
    # (иначе Согласование, вешая +1 каждый ход, гарантированно убивает).
    STATUS.BUREAUCRACY: StatusSpec(STATUS.BUREAUCRACY, cap=3, decay_per_turn=1),
    STATUS.APPROVED: StatusSpec(STATUS.APPROVED),
    STATUS.FROZEN: StatusSpec(STATUS.FROZEN),
    STATUS.DOUBT: StatusSpec(STATUS.DOUBT, cap=99),
    STATUS.FROSTBITE: StatusSpec(STATUS.FROSTBITE),
    STATUS.AGENDA: StatusSpec(STATUS.AGENDA, decay_per_turn=1),
    STATUS.ZAPAL: StatusSpec(STATUS.ZAPAL, reset_on_turn_end=True),
    STATUS.DELEGATED: StatusSpec(STATUS.DELEGATED),
    STATUS.VOID: StatusSpec(STATUS.VOID, cap=10),
    # Простой: висит на враге, спадает на 1 в конце ЕГО хода (decay тикает
    # в _enemy_turn). cap 3 → максимум -9 к атаке за ход.
    STATUS.WEAKEN: StatusSpec(STATUS.WEAKEN, cap=3, decay_on_turn_end=1),
}

# Урон, который снимает один стак Простоя с атаки врага.
WEAKEN_DAMAGE_REDUCTION = 3


def spec_for(key: STATUS) -> StatusSpec:
    return _SPECS.get(key, StatusSpec(key))


def clamp_status(key: STATUS, value: int) -> int:
    """Применяет кэп и нижнюю границу 0."""
    value = max(0, value)
    spec = spec_for(key)
    if spec.cap is not None:
        value = min(value, spec.cap)
    return value
