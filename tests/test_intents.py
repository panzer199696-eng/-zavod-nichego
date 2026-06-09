"""Тесты намерений врага: очередь, исполнение, спец-поведение врагов Акта 1."""

from engine import combat as C
from engine.content import (
    build_stazher,
    new_dedlayn,
    new_prorab,
    new_soglasovanie,
)
from engine.statuses import STATUS


def _vs(enemy, seed=1):
    return C.Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)


def test_intent_queue_cycles_in_order():
    enemy = C.new_enemy(hp=100, intents=[C.attack_intent(5), C.attack_intent(7)])
    cb = _vs(enemy)
    cb.start_combat()
    # текущее намерение видно
    assert cb.enemy.current_intent().value == 5
    h0 = cb.hero.hp
    cb.end_turn()
    assert h0 - cb.hero.hp == 5
    # следующий ход игрока: намерение переключилось на 7
    assert cb.enemy.current_intent().value == 7
    h1 = cb.hero.hp
    cb.end_turn()
    assert h1 - cb.hero.hp == 7
    # цикл вернулся к первому
    assert cb.enemy.current_intent().value == 5


def test_prorab_ramps_attack_every_3_turns():
    # Прораб-самодур: атака базовая, каждые 3 хода +2 к атаке.
    enemy = new_prorab()
    cb = _vs(enemy)
    cb.start_combat()
    first = cb.enemy.current_intent().value
    # после трёх ходов врага атака должна вырасти на 2
    for _ in range(3):
        cb.end_turn()
    later = cb.enemy.current_intent().value
    assert later == first + 2


def test_dedlayn_hits_every_other_turn():
    # Дедлайн: бьёт через ход (атака 12 / простой).
    enemy = new_dedlayn()
    cb = _vs(enemy)
    cb.start_combat()
    h0 = cb.hero.hp
    cb.end_turn()  # ход 1
    after1 = cb.hero.hp
    cb.end_turn()  # ход 2
    after2 = cb.hero.hp
    # ровно один из двух ходов наносит 12 урона
    dmg = [h0 - after1, after1 - after2]
    assert 12 in dmg
    assert 0 in dmg


def test_soglasovanie_pressures_energy_without_death_spiral():
    """Согласование давит Бюрократией на энергию, но не уходит в спираль смерти.

    Бюрократия вешается каждый ход, но имеет кэп и спад — энергия игрока
    снижается (давление), а стак не растёт безгранично (иначе энергия
    залочится в ноль и слабый-но-вечный враг гарантированно убивает).
    """
    from engine.combat import ENERGY_PER_TURN
    from engine.statuses import spec_for

    enemy = new_soglasovanie()
    cb = _vs(enemy)
    cb.start_combat()
    cb.end_turn()  # враг вешает Бюрократию → давит на следующий ход
    # энергия нового хода игрока снижена Бюрократией
    assert cb.energy < ENERGY_PER_TURN
    # за много ходов стак ограничен кэпом — не death spiral
    cap = spec_for(STATUS.BUREAUCRACY).cap
    for _ in range(10):
        cb.end_turn()
    assert cb.hero.get_status(STATUS.BUREAUCRACY) <= cap
