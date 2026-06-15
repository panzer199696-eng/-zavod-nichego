"""Этап C «Расширение пула (+6)»: каждая новая карта валидна и исполняется движком.

Карты (engine/content.py):
- Гореть на работе   — base 4 + 2×Запал, НЕ тратит Запал;
- Круговая оборона   — 7 брони + тянуть 1;
- Стоп-работа        — Заморозить врага на 1 ход, изгнать;
- Бумажная волокита  — Простой 3 врагу (кэп);
- Текучка            — тянуть 1 + энергия 1, изгнать;
- Поручение          — 5 урона, при 2+ картах за ход тянуть 1.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    STAZHER_REWARD_POOL,
    build_stazher,
    make_bumazhnaya_volokita,
    make_goret_na_rabote,
    make_krugovaya_oborona,
    make_otpiska,
    make_poruchenie,
    make_stop_rabota,
    make_tekuchka,
    reward_pool_cards,
)
from engine.statuses import STATUS


def _combat(enemy_hp=200, seed=1):
    enemy = new_enemy(hp=enemy_hp, intents=[attack_intent(0)])
    cb = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    cb.draw_pile = [c.copy() for c in cb.hero.starting_deck]
    cb.energy = 99
    cb.turn = 1
    return cb


_NEW_CARD_IDS = {
    "goret_na_rabote",
    "krugovaya_oborona",
    "stop_rabota",
    "bumazhnaya_volokita",
    "tekuchka",
    "poruchenie",
}


def test_all_six_new_cards_in_pool():
    pool_ids = {c.id for c in reward_pool_cards()}
    assert _NEW_CARD_IDS <= pool_ids


def test_pool_grew_by_six_and_ids_unique():
    ids = [c.id for c in reward_pool_cards()]
    assert len(ids) == len(set(ids))
    assert len(STAZHER_REWARD_POOL) >= 23  # было 17 + 6


def test_goret_scales_from_zapal_without_consuming():
    cb = _combat()
    cb.hero.set_status(STATUS.ZAPAL, 4)
    before = cb.enemy.hp
    cb.play_card_instance(make_goret_na_rabote())  # base 4 + 2*4 = 12
    assert before - cb.enemy.hp == 12
    assert cb.hero.get_status(STATUS.ZAPAL) == 4  # Запал НЕ потрачен


def test_goret_minimum_damage_at_zero_zapal():
    cb = _combat()
    before = cb.enemy.hp
    cb.play_card_instance(make_goret_na_rabote())  # base 4 + 0
    assert before - cb.enemy.hp == 4


def test_krugovaya_oborona_block_and_draw():
    cb = _combat()  # рука пуста, draw_pile = 10
    cb.play_card_instance(make_krugovaya_oborona())
    assert cb.hero.block == 7
    assert len(cb.hand) == 1


def test_stop_rabota_freezes_enemy():
    cb = _combat()
    cb.play_card_instance(make_stop_rabota())
    assert cb.enemy.get_status(STATUS.FROZEN) >= 1


def test_bumazhnaya_volokita_applies_weaken_three():
    cb = _combat()
    cb.play_card_instance(make_bumazhnaya_volokita())
    assert cb.enemy.get_status(STATUS.WEAKEN) == 3


def test_tekuchka_draws_and_refunds_energy():
    cb = _combat()
    cb.energy = 5
    hand_before = len(cb.hand)
    cb.play_card_instance(make_tekuchka())  # cost 0, +1 энергии, тянуть 1
    assert cb.energy == 6  # 5 - 0 + 1
    assert len(cb.hand) == hand_before + 1


def test_poruchenie_damage_and_conditional_draw():
    cb = _combat()  # рука пуста, draw_pile = 10
    cb.play_card_instance(make_otpiska())  # 1-я карта за ход
    hp0 = cb.enemy.hp
    hand_before = len(cb.hand)
    cb.play_card_instance(make_poruchenie())  # 2-я -> 5 урона + тянуть 1
    assert hp0 - cb.enemy.hp == 5
    assert len(cb.hand) == hand_before + 1


def test_poruchenie_no_draw_when_first_card():
    cb = _combat()
    hand_before = len(cb.hand)
    cb.play_card_instance(make_poruchenie())  # 1-я карта -> НЕ тянет
    assert len(cb.hand) == hand_before
