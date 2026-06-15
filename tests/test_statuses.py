"""Тесты статусов: Бюрократия, Заморожено, Запал+Аврал кэп, броня Директора 30%."""

from engine import combat as C
from engine.content import (
    build_direktor,
    build_stazher,
    make_avral,
    make_begotnya,
    make_otpiska,
    make_udar,
    new_enemy,
)
from engine.statuses import STATUS


def _stazher_vs(enemy, seed=1):
    return C.Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)


def test_byurokratiya_drains_energy_at_turn_start():
    enemy = new_enemy(hp=50, intents=[C.attack_intent(0)])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.hero.add_status(STATUS.BUREAUCRACY, 1)
    cb.end_turn()  # враг ходит, затем начало нового хода игрока
    # старт хода: энергия 3, Бюрократия 1 снимает 1 -> 2
    assert cb.energy == 2


def test_frozen_enemy_skips_attack():
    enemy = new_enemy(hp=50, intents=[C.attack_intent(15)])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.enemy.add_status(STATUS.FROZEN, 1)
    start_hp = cb.hero.hp
    cb.end_turn()  # враг должен пропустить атаку
    assert cb.hero.hp == start_hp


def test_zapal_grows_from_cheap_cards():
    enemy = new_enemy(hp=200, intents=[])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    assert cb.hero.get_status(STATUS.ZAPAL) == 0
    cb.play_card_instance(make_udar())  # 1 энергии -> +1 Запал
    cb.play_card_instance(make_otpiska())  # 1 энергии -> +1 Запал
    cb.play_card_instance(make_begotnya())  # 0 энергии -> +1 Запал (+саму карту даёт)
    assert cb.hero.get_status(STATUS.ZAPAL) == 3


def test_avral_scales_with_zapal():
    enemy = new_enemy(hp=200, intents=[])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.hero.set_status(STATUS.ZAPAL, 4)
    before = cb.enemy.hp
    cb.play_card_instance(make_avral())  # base 3 + 3 * 4 = 15
    assert before - cb.enemy.hp == 15


def test_avral_capped_at_27():
    enemy = new_enemy(hp=500, intents=[])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.hero.set_status(STATUS.ZAPAL, 20)  # base 3 + 3*20=63, но кэп 27
    before = cb.enemy.hp
    cb.play_card_instance(make_avral())
    assert before - cb.enemy.hp == 27


def test_zapal_resets_at_end_of_turn():
    enemy = new_enemy(hp=200, intents=[C.attack_intent(0)])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.hero.set_status(STATUS.ZAPAL, 5)
    cb.end_turn()
    assert cb.hero.get_status(STATUS.ZAPAL) == 0


def test_void_capped_at_10():
    enemy = new_enemy(hp=50, intents=[])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.hero.add_status(STATUS.VOID, 50)
    assert cb.hero.get_status(STATUS.VOID) == 10


def test_block_fully_resets_for_normal_hero():
    enemy = new_enemy(hp=50, intents=[C.attack_intent(0)])
    cb = _stazher_vs(enemy)
    cb.start_combat()
    cb.play_card_instance(make_otpiska())  # 5 брони
    assert cb.hero.block == 5
    cb.end_turn()  # начало нового хода -> броня сбрасывается полностью
    assert cb.hero.block == 0


def test_direktor_keeps_30_percent_block():
    enemy = new_enemy(hp=50, intents=[C.attack_intent(0)])
    hero = build_direktor()
    cb = C.Combat(hero=hero, enemy=enemy, rng_seed=1)
    cb.start_combat()
    cb.hero.block = 10
    cb.end_turn()  # начало нового хода: сохраняется 30% от 10 = 3
    assert cb.hero.block == 3
