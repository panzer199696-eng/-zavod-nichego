"""Тесты расширенного пула карт Стажёра: карты валидны, эффекты исполняются движком."""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    STAZHER_REWARD_POOL,
    build_stazher,
    make_entuziazm,
    make_fors_mazhor,
    make_km2,
    make_otpiska,
    make_pererabotka,
    make_prinesi_poday,
    make_reglament,
    make_sluzhebnaya,
    reward_pool_cards,
)
from engine.models import CardType
from engine.statuses import STATUS


def _combat(seed=1, enemy_hp=200):
    """Бой со старым ходом и щедрой энергией — для проверки эффектов карт.

    Колода кладётся в draw_pile вручную, рука пуста: размер руки управляется
    тестом детерминированно (без случайного добора start_combat).
    """
    enemy = new_enemy(hp=enemy_hp, intents=[attack_intent(0)])
    cb = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    cb.draw_pile = [c.copy() for c in cb.hero.starting_deck]
    cb.energy = 99
    cb.turn = 1
    return cb


def test_pool_size_is_at_least_ten():
    assert len(STAZHER_REWARD_POOL) >= 10


def test_all_pool_cards_valid():
    for card in reward_pool_cards():
        assert card.id
        assert card.name
        assert isinstance(card.card_type, CardType)
        assert card.cost >= 0
        assert isinstance(card.effects, list)
        assert len(card.effects) >= 1


def test_all_pool_cards_have_unique_ids():
    ids = [c.id for c in reward_pool_cards()]
    assert len(ids) == len(set(ids))


def test_every_pool_card_executes_without_error():
    """Каждая карта пула должна разыгрываться движком без исключений."""
    for card in reward_pool_cards():
        cb = _combat(enemy_hp=500)
        cb.energy = 99  # хватит на любую стоимость
        cb.play_card_instance(card)


def test_sluzhebnaya_does_10_damage_and_weaken():
    cb = _combat(enemy_hp=200)
    cb.energy = 99
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_sluzhebnaya())
    assert cb.enemy.hp == hp0 - 10
    assert cb.enemy.get_status(STATUS.WEAKEN) == 1


def test_reglament_block_and_draw():
    cb = _combat()  # рука пуста, draw_pile = 10
    cb.play_card_instance(make_reglament())  # 4 брони + тянуть 1
    assert cb.hero.block == 4
    assert len(cb.hand) == 1  # добрана 1 карта (играем карту вне руки)


def test_fors_mazhor_22_damage_8_block():
    cb = _combat(enemy_hp=200)
    cb.energy = 99
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_fors_mazhor())
    assert cb.enemy.hp == hp0 - 22
    assert cb.hero.block == 8


def test_km2_scales_from_block():
    cb = _combat(enemy_hp=200)
    cb.energy = 99
    cb.play_card_instance(make_otpiska())  # 5 брони
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_km2())  # урон = 5 * 2 = 10
    assert cb.enemy.hp == hp0 - 10


def test_pererabotka_scales_with_cards_played():
    cb = _combat(enemy_hp=200)
    cb.energy = 99
    # сыграем 2 дешёвые карты, затем переработку (она 3-я) -> 2*3 = 6
    cb.play_card_instance(make_otpiska())
    cb.play_card_instance(make_otpiska())
    hp0 = cb.enemy.hp
    cb.play_card_instance(make_pererabotka())
    assert cb.enemy.hp == hp0 - 6


def test_prinesi_poday_draws_on_third_card():
    cb = _combat(enemy_hp=200)  # рука пуста, draw_pile = 10
    cb.play_card_instance(make_otpiska())  # 1-я
    cb.play_card_instance(make_otpiska())  # 2-я
    hand_before = len(cb.hand)  # = 0 (играем карты вне руки)
    cb.play_card_instance(make_prinesi_poday())  # 3-я -> тянет 1
    assert len(cb.hand) == hand_before + 1


def test_prinesi_poday_no_draw_when_early():
    cb = _combat(enemy_hp=200)  # рука пуста, draw_pile = 10
    cb.play_card_instance(make_prinesi_poday())  # 1-я -> НЕ тянет
    assert len(cb.hand) == 0


def test_entuziazm_grants_approved_stacks():
    cb = _combat()
    cb.play_card_instance(make_entuziazm())
    assert cb.hero.get_status(STATUS.APPROVED) >= 1
