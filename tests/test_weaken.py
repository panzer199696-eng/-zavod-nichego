"""Тесты статуса «Простой» (WEAKEN): режет урон атаки врага и спадает.

Простой — единственный рабочий дебаф атаки врага (Бюрократия на враге мертва:
ход врага не тратит энергию). На него завязан контроль-архетип Этапа 3.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import build_stazher
from engine.statuses import STATUS, WEAKEN_DAMAGE_REDUCTION


def _combat(enemy, seed=1):
    cb = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    cb.start_combat()
    return cb


def test_weaken_reduces_enemy_attack():
    enemy = new_enemy(hp=100, intents=[attack_intent(10)])
    cb = _combat(enemy)
    cb.enemy.add_status(STATUS.WEAKEN, 2)  # -6 к атаке
    hp0 = cb.hero.hp
    cb.end_turn()  # враг бьёт 10 - 2*3 = 4
    expected = 10 - WEAKEN_DAMAGE_REDUCTION * 2
    assert cb.hero.hp == hp0 - expected


def test_weaken_cannot_make_negative_damage():
    enemy = new_enemy(hp=100, intents=[attack_intent(4)])
    cb = _combat(enemy)
    cb.enemy.add_status(STATUS.WEAKEN, 3)  # -9, но урон не уходит ниже 0
    hp0 = cb.hero.hp
    cb.end_turn()
    assert cb.hero.hp == hp0  # 4 - 9 -> 0 урона


def test_weaken_decays_each_enemy_turn():
    enemy = new_enemy(hp=100, intents=[attack_intent(0)])
    cb = _combat(enemy)
    cb.enemy.add_status(STATUS.WEAKEN, 3)
    cb.end_turn()  # конец хода врага: спад 1
    assert cb.enemy.get_status(STATUS.WEAKEN) == 2
    cb.end_turn()
    assert cb.enemy.get_status(STATUS.WEAKEN) == 1


def test_weaken_capped_at_three():
    enemy = new_enemy(hp=100, intents=[attack_intent(0)])
    cb = _combat(enemy)
    cb.enemy.add_status(STATUS.WEAKEN, 99)
    assert cb.enemy.get_status(STATUS.WEAKEN) == 3
