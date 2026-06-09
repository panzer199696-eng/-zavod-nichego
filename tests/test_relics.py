"""Тесты реликвий: пассивы применяются на старте боя/хода, числа сходятся."""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    BeydzhBezFoto,
    ByurokraticheskiyImmunitet,
    ChernyySpisok,
    DressKod,
    KofemashinaSlomana,
    KorporativnayaKruzhka,
    NenormirovannyyGrafik,
    PechatSoglasovano,
    TolstayaPapka,
    VtorayaSmena,
    all_relics,
    build_stazher,
    make_udar,
)
from engine.statuses import STATUS


def _combat(relics, enemy=None, seed=1):
    enemy = enemy or new_enemy(hp=100, intents=[attack_intent(0)])
    return Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed, relics=relics)


def test_kofemashina_gives_3_block_at_combat_start():
    cb = _combat([KofemashinaSlomana()])
    cb.start_combat()
    assert cb.hero.block == 3


def test_dress_kod_keeps_block_between_turns():
    cb = _combat([DressKod()], enemy=new_enemy(hp=100, intents=[attack_intent(0)]))
    cb.start_combat()
    cb.hero.gain_block(7)
    cb.end_turn()  # враг бьёт 0 -> новый ход игрока
    # без реликвии броня бы сбросилась в 0; с дресс-кодом сохраняется
    assert cb.hero.block == 7


def test_pechat_soglasovano_makes_first_card_free():
    cb = _combat([PechatSoglasovano()])
    cb.start_combat()
    assert cb.hero.get_status(STATUS.APPROVED) >= 1
    # первая карта стоит 0
    assert cb.card_cost(make_udar()) == 0
    energy_before = cb.energy
    cb.play_card_instance(make_udar())
    assert cb.energy == energy_before  # энергия не потрачена


def test_beydzh_first_turn_bonus():
    cb = _combat([BeydzhBezFoto()])
    cb.start_combat()
    # +1 энергии в первый ход (3 -> 4) и +1 Запал
    assert cb.energy == 4
    assert cb.hero.get_status(STATUS.ZAPAL) == 1


def test_beydzh_only_first_turn():
    cb = _combat([BeydzhBezFoto()], enemy=new_enemy(hp=100, intents=[attack_intent(0)]))
    cb.start_combat()
    cb.end_turn()  # переход на ход 2
    assert cb.turn == 2
    assert cb.energy == 3  # без бонуса


def test_no_relics_no_effect():
    cb = _combat([])
    cb.start_combat()
    assert cb.hero.block == 0
    assert cb.energy == 3


def test_all_relics_factory_returns_unique_instances():
    relics = all_relics()
    assert len(relics) >= 10
    ids = {r.id for r in relics}
    assert len(ids) == len(relics)  # все id уникальны


# --- Этап 3: новые реликвии под архетипы ---


def test_nenormirovannyy_grafik_first_turn_energy():
    cb = _combat([NenormirovannyyGrafik()])
    cb.start_combat()
    assert cb.energy == 4  # 3 + 1
    cb.end_turn()
    assert cb.energy == 3  # только первый ход


def test_korporativnaya_kruzhka_first_turn_zapal():
    cb = _combat([KorporativnayaKruzhka()])
    cb.start_combat()
    assert cb.hero.get_status(STATUS.ZAPAL) == 2


def test_tolstaya_papka_first_turn_block():
    cb = _combat([TolstayaPapka()])
    cb.start_combat()
    assert cb.hero.block == 6


def test_chernyy_spisok_weakens_enemy_at_start():
    cb = _combat([ChernyySpisok()])
    cb.start_combat()
    assert cb.enemy.get_status(STATUS.WEAKEN) == 2


def test_vtoraya_smena_draws_two_extra_first_turn():
    cb = _combat([VtorayaSmena()])
    cb.start_combat()
    # обычная рука 5 + 2 от реликвии = 7
    assert len(cb.hand) == 7


def test_byurokraticheskiy_immunitet_clears_bureaucracy():
    cb = _combat([ByurokraticheskiyImmunitet()])
    cb.start_combat()
    cb.hero.add_status(STATUS.BUREAUCRACY, 3)
    cb.end_turn()  # начало след. хода: иммунитет снимает Бюрократию
    assert cb.hero.get_status(STATUS.BUREAUCRACY) == 0


def test_byurokraticheskiy_immunitet_keeps_energy_full_same_turn():
    """Иммунитет снимает Бюрократию ДО расчёта энергии — штраф не проходит."""
    cb = _combat([ByurokraticheskiyImmunitet()])
    cb.start_combat()
    cb.hero.add_status(STATUS.BUREAUCRACY, 2)  # «заразили» в конце прошлого хода
    cb.end_turn()
    assert cb.energy == 3  # полная энергия, штраф -2 не прошёл
