"""Этап B «Баланс мёртвых карт»: ни одна карта не наносит 0 эффекта в типовой
ситуации.

Покрывает три карты-трупа из ROADMAP:
- КМ-2 — при 0 брони раньше давала 0 урона;
- Аврал — при 0 Запала давал 0 (а он в стартовой колоде Стажёра);
- Переработка — при малом числе сыгранных карт давала мало/0.

Числа после правки (см. engine/effects.py):
- КМ-2:        base 3 + броня×2  → при 0 брони 3, при 5 броне 13.
- Аврал:       base 3 + Запал×3 (cap 27) → при 0 Запала 3, при 8 Запала 27.
- Переработка: base 2 + карты×2  → при 1 сыгранной карте (она сама) 4.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    build_stazher,
    make_avral,
    make_km2,
    make_otpiska,
    make_pererabotka,
)
from engine.statuses import STATUS


def _combat(enemy_hp=500, seed=1):
    enemy = new_enemy(hp=enemy_hp, intents=[attack_intent(0)])
    cb = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    cb.draw_pile = [c.copy() for c in cb.hero.starting_deck]
    cb.energy = 99
    cb.turn = 1
    return cb


# ----------------------------- КМ-2 -----------------------------


def test_km2_not_dead_at_zero_block():
    """КМ-2 при 0 брони наносит минимум урона, а не 0."""
    cb = _combat()
    hp0 = cb.enemy.hp
    assert cb.hero.block == 0
    cb.play_card_instance(make_km2())
    assert hp0 - cb.enemy.hp == 3, "КМ-2 при 0 брони должна давать base 3 урона"


def test_km2_scales_with_block():
    """КМ-2 с бронёй: base 3 + броня×2."""
    cb = _combat()
    cb.play_card_instance(make_otpiska())  # 5 брони
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_km2())
    assert hp0 - cb.enemy.hp == 3 + 5 * 2  # 13


# ----------------------------- Аврал ----------------------------


def test_avral_not_dead_at_zero_zapal():
    """Аврал при 0 Запала наносит минимум урона (он в стартовой колоде)."""
    cb = _combat()
    assert cb.hero.get_status(STATUS.ZAPAL) == 0
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_avral())
    assert hp0 - cb.enemy.hp == 3, "Аврал при 0 Запала должен давать base 3"


def test_avral_scales_and_consumes_zapal():
    """Аврал: base 3 + 3×Запал, тратит Запал."""
    cb = _combat()
    cb.hero.set_status(STATUS.ZAPAL, 4)
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_avral())
    assert hp0 - cb.enemy.hp == 3 + 3 * 4  # 15
    assert cb.hero.get_status(STATUS.ZAPAL) == 0


def test_avral_cap_at_max_zapal():
    """Аврал на максимуме Запала (8): 3 + 24 = 27, кэп 27."""
    cb = _combat()
    cb.hero.set_status(STATUS.ZAPAL, 8)
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_avral())
    assert hp0 - cb.enemy.hp == 27


# -------------------------- Переработка -------------------------


def test_pererabotka_not_dead_when_first_card():
    """Переработка как первая карта хода: base 2 + 2×1 = 4 урона, не труп."""
    cb = _combat()
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_pererabotka())  # 1-я карта за ход
    assert hp0 - cb.enemy.hp == 2 + 2 * 1  # 4


def test_pererabotka_scales_with_cards_played():
    """Переработка 3-й картой: base 2 + 2×3 = 8 урона."""
    cb = _combat()
    cb.play_card_instance(make_otpiska())
    cb.play_card_instance(make_otpiska())
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_pererabotka())  # 3-я карта
    assert hp0 - cb.enemy.hp == 2 + 2 * 3  # 8


# --------------------- общий инвариант этапа B ------------------


def test_no_starter_or_scaler_card_deals_zero_in_typical_situation():
    """Три бывшие карты-трупа дают ненулевой урон в нулевой ситуации."""
    for factory in (make_km2, make_avral, make_pererabotka):
        cb = _combat()
        hp0 = cb.enemy.hp
        cb.play_card_instance(factory())
        assert hp0 - cb.enemy.hp > 0, f"{factory.__name__} нанесла 0 урона"
