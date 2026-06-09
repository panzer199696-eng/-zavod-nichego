"""Тесты боевого движка: урон/броня, энергия, рука, стопки, exhaust, win/lose."""

from engine import combat as C
from engine.content import (
    build_stazher,
    make_begotnya,
    make_otpiska,
    make_udar,
    new_enemy,
)


def _combat_stazher_vs(enemy, seed=1):
    hero = build_stazher()
    return C.Combat(hero=hero, enemy=enemy, rng_seed=seed)


def test_udar_deals_6_damage():
    enemy = new_enemy(hp=50, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    cb.play_card_instance(make_udar())
    assert cb.enemy.hp == 44


def test_otpiska_gives_5_block():
    enemy = new_enemy(hp=50, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    cb.play_card_instance(make_otpiska())
    assert cb.hero.block == 5


def test_block_absorbs_then_overflow_hits_hp():
    # Враг бьёт на 8, у героя 5 брони -> 3 урона по HP.
    enemy = new_enemy(hp=50, intents=[C.attack_intent(8)])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    start_hp = cb.hero.hp
    cb.play_card_instance(make_otpiska())  # +5 брони
    cb.end_turn()  # враг бьёт 8
    assert cb.hero.hp == start_hp - 3


def test_energy_regenerates_to_3_each_turn():
    enemy = new_enemy(hp=50, intents=[C.attack_intent(0)])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    assert cb.energy == 3
    cb.play_card_instance(make_udar())  # -1
    assert cb.energy == 2
    cb.end_turn()  # ход врага -> снова ход игрока
    assert cb.energy == 3


def test_hand_draws_5():
    enemy = new_enemy(hp=50, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    assert len(cb.hand) == 5


def test_discard_reshuffles_into_draw_when_empty():
    # Колода 10, рука 5 -> draw 5. Заставим добрать больше, чем осталось в draw.
    enemy = new_enemy(hp=50, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    # сбросим руку в discard, опустошим draw добором
    cb.discard_pile.extend(cb.hand)
    cb.hand.clear()
    drawn = cb.draw(7)  # в draw только 5 -> 5, потом reshuffle discard(5) -> ещё 2
    assert drawn == 7
    assert len(cb.hand) == 7


def test_exhaust_card_goes_to_exhaust_pile():
    enemy = new_enemy(hp=50, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    begotnya = make_begotnya()  # exhaust=False по канону? Беготня не exhaust.
    # Возьмём карту с exhaust: Кофе для всех не в старте, используем флаг напрямую
    from engine.content import make_kofe_dlya_vseh

    coffee = make_kofe_dlya_vseh()
    assert coffee.exhaust is True
    cb.play_card_instance(coffee)
    assert coffee in cb.exhaust_pile
    assert coffee not in cb.discard_pile


def test_victory_when_enemy_hp_zero():
    enemy = new_enemy(hp=6, intents=[])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    cb.play_card_instance(make_udar())  # 6 урона
    assert cb.enemy.hp <= 0
    assert cb.is_over() is True
    assert cb.result == "victory"


def test_defeat_when_hero_hp_zero():
    enemy = new_enemy(hp=200, intents=[C.attack_intent(999)])
    cb = _combat_stazher_vs(enemy)
    cb.start_combat()
    cb.end_turn()  # враг бьёт смертельно
    assert cb.hero.hp <= 0
    assert cb.is_over() is True
    assert cb.result == "defeat"
