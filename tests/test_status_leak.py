"""Регресс-тесты на утечку внутрибоевых статусов между боями (БАГ-1/2/3).

Combat берёт hero по ссылке из RunState и переиспользуется между боями —
статусы и броня НЕ должны переживать конец боя.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import build_stazher
from engine.statuses import STATUS


def _combat(hero, seed=1):
    enemy = new_enemy(hp=100, intents=[attack_intent(0)])
    return Combat(hero=hero, enemy=enemy, rng_seed=seed)


def test_frostbite_does_not_leak_into_next_combat():
    hero = build_stazher()
    cb1 = _combat(hero)
    cb1.start_combat()
    hero.add_status(STATUS.FROSTBITE, 2)  # враг «заразил» промерзанием
    assert hero.get_status(STATUS.FROSTBITE) == 2

    # следующий бой тем же героем
    cb2 = _combat(hero)
    cb2.start_combat()
    assert hero.get_status(STATUS.FROSTBITE) == 0


def test_all_statuses_cleared_on_new_combat():
    hero = build_stazher()
    cb1 = _combat(hero)
    cb1.start_combat()
    hero.add_status(STATUS.FROZEN, 3)
    hero.add_status(STATUS.APPROVED, 1)
    hero.add_status(STATUS.ZAPAL, 5)
    hero.add_status(STATUS.BUREAUCRACY, 2)

    cb2 = _combat(hero)
    cb2.start_combat()
    assert hero.statuses.get(STATUS.FROZEN, 0) == 0
    assert hero.statuses.get(STATUS.APPROVED, 0) == 0
    assert hero.statuses.get(STATUS.ZAPAL, 0) == 0
    assert hero.statuses.get(STATUS.BUREAUCRACY, 0) == 0


def test_block_does_not_leak_into_next_combat():
    hero = build_stazher()
    cb1 = _combat(hero)
    cb1.start_combat()
    hero.gain_block(20)

    cb2 = _combat(hero)
    cb2.start_combat()
    # на старте боя броня героя сброшена (могла появиться лишь от реликвий)
    assert hero.block == 0


def test_hp_carries_over_between_combats():
    """Контроль: HP, в отличие от статусов, переносится между боями."""
    hero = build_stazher()
    cb1 = _combat(hero)
    cb1.start_combat()
    hero.hp -= 13
    hurt = hero.hp

    cb2 = _combat(hero)
    cb2.start_combat()
    assert hero.hp == hurt
