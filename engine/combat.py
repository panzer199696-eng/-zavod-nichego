"""Боевой движок: энергия, рука, стопки, ходы игрока/врага, урон, win/lose.

Headless, без UI. Логирует ход боя в ``log`` (список строк) для sim.py/тестов.
"""

from __future__ import annotations

import random
from typing import Optional

from engine.models import Card, Combatant, Enemy, EnemyIntent, Hero
from engine.statuses import (
    CEITNOT_DAMAGE_MULT,
    STATUS,
    WEAKEN_DAMAGE_REDUCTION,
    spec_for,
)

ENERGY_PER_TURN = 3
HAND_SIZE = 5

# Пассив Стажёра: каждая 3-я карта за ход даёт +1 энергии.
STAZHER_PASSIVE_EVERY = 3


# --- удобные конструкторы намерений/врагов (реэкспорт для тестов/контента) ---
def attack_intent(value: int, label: str = "") -> EnemyIntent:
    return EnemyIntent(kind="attack", value=value, label=label or f"⚔ {value}")


def block_intent(value: int) -> EnemyIntent:
    return EnemyIntent(kind="block", value=value, label=f"🛡 {value}")


def skip_intent() -> EnemyIntent:
    return EnemyIntent(kind="skip", label="…")


def debuff_intent(status: STATUS, amount: int) -> EnemyIntent:
    return EnemyIntent(
        kind="debuff", status=status, status_amount=amount, label=f"💀 {status.value}"
    )


def new_enemy(hp: int, intents: list[EnemyIntent], name: str = "Враг", **kw) -> Enemy:
    return Enemy(name=name, max_hp=hp, hp=hp, intents=list(intents), **kw)


class Combat:
    """Состояние одного боя и его API.

    Жизненный цикл:
        start_combat() -> [play_card_instance(...) ...] -> end_turn() -> ...
    end_turn() проводит ход врага и сразу начинает следующий ход игрока,
    пока бой не окончен (is_over()).
    """

    def __init__(
        self,
        hero: Hero,
        enemy: Enemy,
        rng_seed: Optional[int] = None,
        relics: Optional[list] = None,
    ):
        self.hero = hero
        self.enemy = enemy
        self.rng = random.Random(rng_seed)
        # Реликвии: объекты с опц. методами on_combat_start(combat) /
        # on_turn_start(combat). Пассивы применяются движком в нужных точках.
        self.relics: list = list(relics) if relics else []

        self.draw_pile: list[Card] = []
        self.hand: list[Card] = []
        self.discard_pile: list[Card] = []
        self.exhaust_pile: list[Card] = []

        self.energy = 0
        self.turn = 0  # номер хода игрока (1-based после start_combat)
        self.enemy_turns = 0  # сколько ходов сделал враг
        self.cards_played_this_turn = 0
        self.result: Optional[str] = None  # "victory" | "defeat" | None
        self.log: list[str] = []

    # ---------------------------------------------------------------- log
    def _log(self, msg: str) -> None:
        self.log.append(msg)

    # ------------------------------------------------------------- setup
    def start_combat(self) -> None:
        # Combat берёт hero по ссылке из RunState и переиспользуется между боями.
        # Статусы и броня — внутрибоевые: чистим их, иначе Промерзание/Согласовано/
        # Заморозка/Запал утекают в следующий бой (вплоть до мёртвых рук у босса).
        self.hero.statuses.clear()
        self.hero.block = 0
        self.draw_pile = [c.copy() for c in self.hero.starting_deck]
        self.rng.shuffle(self.draw_pile)
        self.hand.clear()
        self.discard_pile.clear()
        self.exhaust_pile.clear()
        self._log(
            f"=== Бой: {self.hero.name} (HP {self.hero.hp}) "
            f"против {self.enemy.name} (HP {self.enemy.hp}) ==="
        )
        self._apply_relics("on_combat_start")
        self._start_player_turn()

    def _apply_relics(self, hook: str) -> None:
        """Вызвать одноимённый хук у всех реликвий, у кого он определён."""
        for relic in self.relics:
            fn = getattr(relic, hook, None)
            if callable(fn):
                fn(self)

    # ------------------------------------------------------- player turn
    def _start_player_turn(self) -> None:
        if self.is_over():
            return
        self.turn += 1
        self.cards_played_this_turn = 0
        self.hero.reset_block_for_turn()

        # Реликвии, влияющие на сам расчёт энергии (снятие Бюрократии), —
        # ДО вычисления энергии, иначе штраф текущего хода всё равно проходит.
        self._apply_relics("on_turn_pre_energy")

        # энергия с учётом Бюрократии
        self.energy = ENERGY_PER_TURN
        bureaucracy = self.hero.get_status(STATUS.BUREAUCRACY)
        if bureaucracy:
            self.energy = max(0, self.energy - bureaucracy)
            self._log(f"Бюрократия -{bureaucracy} энергии (стало {self.energy})")

        self._tick_turn_start(self.hero)
        self.draw(HAND_SIZE)
        self._apply_relics("on_turn_start")
        self._log(
            f"-- Ход {self.turn}: энергия {self.energy}, рука {len(self.hand)} --"
        )

    def _tick_turn_start(self, who: Combatant) -> None:
        """Спадание статусов с decay в начале хода владельца."""
        for key in list(who.statuses.keys()):
            spec = spec_for(key)
            if spec.decay_per_turn:
                who.add_status(key, -spec.decay_per_turn)

    # ----------------------------------------------------------- drawing
    def draw(self, n: int) -> int:
        """Добор n карт с перемешиванием discard->draw при опустошении.

        Возвращает фактически добранное число.
        """
        drawn = 0
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard_pile:
                    break  # карт нет нигде
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
                self._log("Сброс перемешан в колоду")
            self.hand.append(self.draw_pile.pop())
            drawn += 1
        return drawn

    # ------------------------------------------------------- play a card
    def card_cost(self, card: Card) -> int:
        """Итоговая стоимость с учётом Согласовано/Промерзания."""
        if self.hero.get_status(STATUS.APPROVED) > 0:
            return 0
        cost = card.cost + self.hero.get_status(STATUS.FROSTBITE)
        return max(0, cost)

    def can_play(self, card: Card) -> bool:
        return not self.is_over() and self.card_cost(card) <= self.energy

    def play_card_instance(self, card: Card) -> None:
        """Разыграть конкретный экземпляр карты (если в руке — убрать из руки)."""
        if self.is_over():
            return
        cost = self.card_cost(card)
        if cost > self.energy:
            raise ValueError(
                f"Недостаточно энергии для {card.name}: {cost} > {self.energy}"
            )

        if card in self.hand:
            self.hand.remove(card)

        self.energy -= cost
        if self.hero.get_status(STATUS.APPROVED) > 0:
            self.hero.add_status(STATUS.APPROVED, -1)

        # Запал Стажёра: дешёвые карты (0-1 базовой стоимости) дают +1.
        # Финишеры (no_zapal) тратят Запал и сами его не добавляют.
        if "zapal" in self.hero.passive and card.cost <= 1 and not card.no_zapal:
            self.hero.add_status(STATUS.ZAPAL, 1)

        self._log(f"Разыграна «{card.name}» (-{cost}э)")

        # выполнить эффекты
        for op in card.effects:
            op(self, self.hero, self.enemy)

        self.cards_played_this_turn += 1
        self._apply_play_passive()
        self._log(f"  → враг HP {max(self.enemy.hp, 0)}, броня героя {self.hero.block}")

        # утилизация карты
        if card.exhaust or card.one_time:
            self.exhaust_pile.append(card)
        else:
            self.discard_pile.append(card)

        self._check_end()

    def _apply_play_passive(self) -> None:
        """Пассив Стажёра «Молодой да ранний»: каждая 3-я карта +1 энергии."""
        if "stazher_energy" in self.hero.passive:
            if self.cards_played_this_turn % STAZHER_PASSIVE_EVERY == 0:
                self.energy += 1
                self._log("Пассив Стажёра: +1 энергии")

    # ------------------------------------------------------- damage util
    def deal_damage(self, source: Combatant, target: Combatant, amount: int) -> int:
        if amount <= 0:
            return 0
        through = target.take_damage(amount)
        self._check_end()
        return through

    # --------------------------------------------------------- end turn
    def end_turn(self) -> None:
        if self.is_over():
            return
        # конец хода игрока: статусы reset_on_turn_end (Запал)
        self._tick_turn_end(self.hero)
        # сброс руки
        self.discard_pile.extend(self.hand)
        self.hand.clear()

        self._enemy_turn()
        if not self.is_over():
            self._start_player_turn()

    def _tick_turn_end(self, who: Combatant) -> None:
        for key in list(who.statuses.keys()):
            spec = spec_for(key)
            if spec.reset_on_turn_end:
                who.set_status(key, 0)
            elif spec.decay_on_turn_end:
                who.add_status(key, -spec.decay_on_turn_end)

    # --------------------------------------------------------- enemy turn
    def _enemy_turn(self) -> None:
        enemy = self.enemy
        if not enemy.is_alive():
            return
        enemy.reset_block_for_turn()
        self.enemy_turns += 1

        # хук-поведение врага (рампы атаки и т.п.)
        if enemy.behavior:
            enemy.behavior(self, enemy, self.enemy_turns)

        # Заморожено: пропуск атаки, расход одного стака
        if enemy.get_status(STATUS.FROZEN) > 0:
            enemy.add_status(STATUS.FROZEN, -1)
            self._log(f"{enemy.name} заморожен — пропускает ход")
            enemy.advance_intent()
            return

        intent = enemy.current_intent()
        self._execute_intent(enemy, intent)
        enemy.advance_intent()
        # спад дебафов врага (Простой) в конце ЕГО хода
        self._tick_turn_end(enemy)

    def _execute_intent(self, enemy: Enemy, intent: EnemyIntent) -> None:
        if intent.kind == "attack":
            # Простой режет урон атаки на WEAKEN_DAMAGE_REDUCTION за стак
            weaken = enemy.get_status(STATUS.WEAKEN)
            value = max(0, intent.value - WEAKEN_DAMAGE_REDUCTION * weaken)
            # Цейтнот на герое усиливает входящий урон (×1.5). Без статуса —
            # нейтрально (множитель не применяется), поэтому Акт 1/golden целы.
            if self.hero.get_status(STATUS.CEITNOT) > 0:
                boosted = int(value * CEITNOT_DAMAGE_MULT)
                if boosted != value:
                    self._log(f"Цейтнот: входящий урон {value} → {boosted}")
                value = boosted
            dealt = self.deal_damage(enemy, self.hero, value)
            if weaken:
                self._log(f"{enemy.name}: Простой -{intent.value - value} к атаке")
            self._log(
                f"{enemy.name} атакует на {value} "
                f"(прошло {dealt}, HP героя {max(self.hero.hp, 0)})"
            )
        elif intent.kind == "block":
            enemy.gain_block(intent.value)
            self._log(f"{enemy.name} ставит блок {intent.value}")
        elif intent.kind == "debuff" and intent.status is not None:
            self.hero.add_status(intent.status, intent.status_amount)
            self._log(
                f"{enemy.name} вешает {intent.status.value} x{intent.status_amount}"
            )
        else:  # skip / buff без эффекта
            self._log(f"{enemy.name} бездействует")

    # ------------------------------------------------------------- state
    def _check_end(self) -> None:
        if self.result is not None:
            return
        if not self.enemy.is_alive():
            self.result = "victory"
            self._log(f">>> Победа: {self.enemy.name} повержен")
        elif not self.hero.is_alive():
            self.result = "defeat"
            self._log(f">>> Поражение: {self.hero.name} пал")

    def is_over(self) -> bool:
        self._check_end()
        return self.result is not None
