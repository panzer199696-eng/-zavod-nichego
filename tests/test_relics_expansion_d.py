"""Этап D «Реликвии (+4)»: постоянные (каждый ход) пассивы под архетипы
+ ролл реликвии-награды (элита/босс) с дедупом по уже собранным.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    RELIC_REGISTRY,
    KaskaSTreshchinoy,
    Skorosshivatel,
    VechnyyDedlayn,
    ZhurnalZamechaniy,
    all_relics,
    build_stazher,
)
from engine.statuses import STATUS
from game_state.run import RunState

_NEW_RELIC_IDS = {
    "vechnyy_dedlayn",
    "kaska_s_treshchinoy",
    "zhurnal_zamechaniy",
    "skorosshivatel",
}


def _combat(relics, enemy=None, seed=1):
    enemy = enemy or new_enemy(hp=100, intents=[attack_intent(0)])
    return Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed, relics=relics)


def test_all_new_relics_registered_and_unique():
    ids = [cls.id for cls in RELIC_REGISTRY]
    assert _NEW_RELIC_IDS <= set(ids)
    assert len(ids) == len(set(ids))  # уникальность id
    assert len(all_relics()) >= 14  # было 10 + 4


# --- пассивы: эффект на КАЖДОМ ходу, не только первом ---


def test_vechnyy_dedlayn_adds_zapal_every_turn():
    cb = _combat([VechnyyDedlayn()])
    cb.start_combat()
    assert cb.hero.get_status(STATUS.ZAPAL) == 1  # ход 1
    cb.end_turn()  # ход 2 (Запал обнулился в конце хода, реликвия даёт снова)
    assert cb.turn == 2
    assert cb.hero.get_status(STATUS.ZAPAL) == 1


def test_kaska_adds_block_every_turn():
    cb = _combat([KaskaSTreshchinoy()])
    cb.start_combat()
    assert cb.hero.block == 2  # ход 1
    cb.end_turn()  # ход 2 (броня сброшена, реликвия даёт снова)
    assert cb.hero.block == 2


def test_zhurnal_weakens_enemy_every_turn():
    cb = _combat([ZhurnalZamechaniy()])
    cb.start_combat()
    assert cb.enemy.get_status(STATUS.WEAKEN) == 1  # ход 1
    cb.end_turn()  # Простой спадает на 1 в конце хода -> 0, реликвия вешает снова
    assert cb.enemy.get_status(STATUS.WEAKEN) >= 1


def test_skorosshivatel_draws_extra_every_turn():
    cb = _combat([Skorosshivatel()])
    cb.start_combat()
    assert len(cb.hand) == 6  # обычные 5 + 1 от реликвии


def test_no_new_relic_no_effect():
    cb = _combat([])
    cb.start_combat()
    assert cb.hero.block == 0
    assert cb.hero.get_status(STATUS.ZAPAL) == 0
    assert cb.enemy.get_status(STATUS.WEAKEN) == 0


# --- ролл реликвии-награды (элита/босс) ---


def test_roll_relic_returns_relic_from_registry():
    run = RunState.new_stazher(seed=7)
    relic = run.roll_relic_reward()
    assert relic is not None
    assert relic.id in {cls.id for cls in RELIC_REGISTRY}


def test_roll_relic_excludes_owned():
    run = RunState.new_stazher(seed=3)
    # выдать игроку все реликвии, кроме одной
    keep_out = RELIC_REGISTRY[0]
    for cls in RELIC_REGISTRY[1:]:
        run.add_relic(cls())
    relic = run.roll_relic_reward()
    assert relic is not None
    assert relic.id == keep_out.id  # единственная не собранная


def test_roll_relic_returns_none_when_all_owned():
    run = RunState.new_stazher(seed=1)
    for cls in RELIC_REGISTRY:
        run.add_relic(cls())
    assert run.roll_relic_reward() is None


def test_roll_relic_deterministic_by_seed():
    a = RunState.new_stazher(seed=42).roll_relic_reward()
    b = RunState.new_stazher(seed=42).roll_relic_reward()
    assert a.id == b.id
