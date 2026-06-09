"""Headless-раннер одного боя с простой авто-политикой розыгрыша.

Назначение: ручная проверка боевой логики и грубого баланса Акта 1 в консоли.
Запуск:
    python sim.py                # Стажёр против Прораба-самодура
    python sim.py boss           # Стажёр против босса «Квартальный Отчёт»
    python sim.py dedlayn        # против Дедлайна
    python sim.py soglasovanie   # против Согласования
"""

from __future__ import annotations

import sys

from engine.combat import Combat
from engine.content import (
    build_stazher,
    new_dedlayn,
    new_kvartalnyy_otchet,
    new_prorab,
    new_soglasovanie,
)
from engine.models import Card, CardType
from engine.statuses import STATUS

ENEMIES = {
    "prorab": new_prorab,
    "dedlayn": new_dedlayn,
    "soglasovanie": new_soglasovanie,
    "boss": new_kvartalnyy_otchet,
}


def _card_priority(combat: Combat, card: Card) -> int:
    """Грубая эвристика порядка розыгрыша.

    1. Если враг почти мёртв — добивать атаками.
    2. Если входящая атака большая и HP героя низок — сначала броня.
    3. Иначе: добор/действия → атаки → защита.
    """
    enemy_hp = combat.enemy.hp
    incoming = combat.enemy.current_intent()
    incoming_dmg = incoming.value if incoming.kind == "attack" else 0
    low_hp = combat.hero.hp <= incoming_dmg + 5

    is_attack = card.card_type == CardType.ATTACK
    is_defense = card.card_type == CardType.DEFENSE

    if enemy_hp <= 12 and is_attack:
        return 0  # добиваем
    if low_hp and is_defense:
        return 0  # выживаем
    if card.card_type in (CardType.ACTION, CardType.SCHEME):
        return 1  # добор/ресурсы пораньше
    if is_attack:
        return 2
    return 3


def _worth_playing(combat: Combat, card: Card) -> bool:
    """Не тратить Аврал-финишер при пустом/малом Запале (копим)."""
    if card.no_zapal and combat.hero.get_status(STATUS.ZAPAL) < 3:
        # держим финишер, если он не последняя доступная карта хода
        others = [c for c in combat.hand if c is not card and combat.can_play(c)]
        return not others
    return True


def auto_play_turn(combat: Combat) -> None:
    """Разыграть руку по эвристике, пока есть энергия и доступные карты."""
    guard = 0
    while not combat.is_over():
        guard += 1
        if guard > 50:
            break
        playable = [
            c for c in combat.hand if combat.can_play(c) and _worth_playing(combat, c)
        ]
        if not playable:
            break
        playable.sort(key=lambda c: _card_priority(combat, c))
        combat.play_card_instance(playable[0])


def run(enemy_key: str = "prorab", seed: int = 7, verbose: bool = True) -> Combat:
    enemy = ENEMIES.get(enemy_key, new_prorab)()
    combat = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    combat.start_combat()

    safety = 0
    while not combat.is_over() and safety < 100:
        safety += 1
        auto_play_turn(combat)
        if combat.is_over():
            break
        combat.end_turn()

    if verbose:
        print("\n".join(combat.log))
        print("\n=== ИТОГ ===")
        print(f"Результат: {combat.result}")
        print(f"Ходов игрока: {combat.turn}, ходов врага: {combat.enemy_turns}")
        print(f"HP героя: {max(combat.hero.hp, 0)}/{combat.hero.max_hp}")
        print(f"HP врага: {max(combat.enemy.hp, 0)}/{combat.enemy.max_hp}")
    return combat


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "prorab"
    run(key)
