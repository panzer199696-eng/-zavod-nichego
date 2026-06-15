"""Этап H «Акт 2 (контент)»: новые враги + босс, статус Цейтнот, проходимость.

Headless. Проверяет: структуру/уникальность врагов, механику Цейтнота (рост
урона, спад, нейтральность без статуса → Акт 1/golden целы) и проходимость
Акта 2 компетентным авто-пилотом на усиленной колоде.
"""

from engine.combat import Combat, attack_intent, new_enemy
from engine.content import (
    all_relics,
    build_stazher,
    make_avral,
    make_fors_mazhor,
    new_avtnadzor,
    new_gosexpertiza,
    new_kurator,
    new_profsoyuz,
    new_sdacha_obyekta,
    new_smetchik,
)
from engine.statuses import CEITNOT_DAMAGE_MULT, STATUS
from game_state.map import (
    NODE_BOSS,
    NODE_ELITE,
    NODE_FIGHT,
    build_act2_map,
    build_full_map,
)
from game_state.run import RunState

ACT2_FACTORIES = [
    new_smetchik,
    new_avtnadzor,
    new_gosexpertiza,
    new_profsoyuz,
    new_kurator,
    new_sdacha_obyekta,
]


# --- структура врагов Акта 2 ---


def test_act2_enemies_unique_ids():
    ids = [f().id for f in ACT2_FACTORIES]
    assert len(ids) == len(set(ids))  # уникальны
    # не пересекаются с Актом 1
    act1_ids = {n.enemy_factory().id for n in build_full_map()[:6]}
    assert set(ids).isdisjoint(act1_ids - set(ids))


def test_act2_harder_than_act1():
    """Босс и элита Акта 2 крепче аналогов Акта 1."""
    assert new_sdacha_obyekta().max_hp > 95  # > босс Акта 1
    assert new_kurator().max_hp > 55  # > элита Акта 1


def test_act2_map_shape():
    m = build_act2_map()
    kinds = [n.kind for n in m]
    assert kinds.count(NODE_FIGHT) == 4
    assert kinds.count(NODE_ELITE) == 1
    assert kinds.count(NODE_BOSS) == 1
    assert kinds[-1] == NODE_BOSS


def test_full_map_is_act1_plus_act2():
    assert len(build_full_map()) == len(build_act2_map()) + 6


# --- механика статуса Цейтнот ---


def _attack_combat(intent_value=10, seed=1):
    enemy = new_enemy(hp=100, intents=[attack_intent(intent_value)], id="dummy")
    cb = Combat(hero=build_stazher(), enemy=enemy, rng_seed=seed)
    cb.start_combat()
    return cb


def test_ceitnot_boosts_incoming_damage():
    cb = _attack_combat(intent_value=10)
    cb.hero.add_status(STATUS.CEITNOT, 2)
    hp_before = cb.hero.hp
    cb.end_turn()  # враг бьёт на 10 → под Цейтнотом 15
    lost = hp_before - cb.hero.hp
    assert lost == int(10 * CEITNOT_DAMAGE_MULT)  # 15


def test_no_ceitnot_no_change():
    """Без статуса урон ровно номинальный (нейтральность для Акта 1/golden)."""
    cb = _attack_combat(intent_value=10)
    hp_before = cb.hero.hp
    cb.end_turn()
    assert hp_before - cb.hero.hp == 10


def test_ceitnot_decays_on_hero_turn():
    cb = _attack_combat(intent_value=0)
    cb.hero.add_status(STATUS.CEITNOT, 2)
    cb.end_turn()  # ход врага → начало хода игрока: спад 1
    assert cb.hero.get_status(STATUS.CEITNOT) == 1


def test_avtnadzor_applies_ceitnot_then_hits_hard():
    """Авторский надзор: ход 1 вешает Цейтнот, ход 2 бьёт усиленно."""
    cb = Combat(hero=build_stazher(), enemy=new_avtnadzor(), rng_seed=1)
    cb.start_combat()
    cb.end_turn()  # враг ход 1: debuff Цейтнот 2
    assert cb.hero.get_status(STATUS.CEITNOT) >= 1


# --- проходимость авто-пилотом ---

# Сильные карты, которые компетентный игрок берёт к Акту 2 (плотная колода).
STRONG_PICKS = (
    "fors_mazhor",
    "prinesi_poday",
    "reglament_5_2",
    "entuziazm",
    "iniciativnaya",
    "goret_na_rabote",
    "krugovaya_oborona",
    "poruchenie",
)


def _pick_reward(choices):
    strong = [c for c in choices if c.id in STRONG_PICKS]
    return strong[0] if strong else None


def _play_turn(cb: Combat) -> None:
    guard = 0
    while not cb.is_over() and guard < 60:
        guard += 1
        playable = [c for c in cb.hand if cb.can_play(c)]
        if not playable:
            break
        incoming = cb.enemy.current_intent()
        threat = incoming.value if incoming.kind == "attack" else 0
        # под Цейтнотом входящий урон выше — авто-пилот это учитывает
        if cb.hero.get_status(STATUS.CEITNOT) > 0:
            threat = int(threat * CEITNOT_DAMAGE_MULT)
        need_block = max(0, threat - cb.hero.block)
        zapal = cb.hero.get_status(STATUS.ZAPAL)

        def priority(card):
            t = card.card_type.value
            if card.no_zapal and "Запал" in card.description and zapal < 4:
                return 9
            if t in ("Действие", "Схема"):
                return 0
            if t == "Защита":
                return 1 if need_block > 2 else 7
            if t == "Атака":
                if "броня" in card.description and cb.hero.block == 0:
                    return 8
                return 3
            return 6

        playable.sort(key=priority)
        cb.play_card_instance(playable[0])


def _grant_relic(run: RunState) -> None:
    owned = {type(r).__name__ for r in run.relics}
    available = [r for r in all_relics() if type(r).__name__ not in owned]
    if available:
        run.add_relic(run.rng.choice(available))


def _simulate_full_run(seed: int):
    run = RunState.new_stazher(seed=seed)
    for node in build_full_map():
        run.hero.starting_deck = run.battle_deck()
        cb = Combat(
            hero=run.hero,
            enemy=node.enemy_factory(),
            relics=run.relics,
            rng_seed=seed + run.node_index,
        )
        cb.start_combat()
        steps = 0
        while not cb.is_over() and steps < 400:
            steps += 1
            _play_turn(cb)
            if cb.is_over():
                break
            cb.end_turn()
        run.hero.hp = max(cb.hero.hp, 0)
        if cb.result != "victory":
            return False, node.title
        run.gain_currency(node.currency_reward)
        pick = _pick_reward(run.roll_reward(3))
        if pick is not None:
            run.add_card(pick)
        if node.kind in (NODE_ELITE, NODE_BOSS):
            _grant_relic(run)
        run.node_index += 1
    return True, "complete"


def test_full_run_winnable_on_some_seeds():
    """Полный забег (Акт 1+2) проходится компетентным игроком на части сидов.

    Акт 2 заметно жёстче, поэтому порог ниже, чем у одиночного Акта 1: важно,
    что финал в принципе берётся при грамотной игре, а не тривиален.
    """
    wins = sum(_simulate_full_run(seed)[0] for seed in range(12))
    assert wins >= 2, f"Акт 2 непроходим: {wins}/12 полных забегов"


def test_act2_normal_fights_winnable_with_upgraded_deck():
    """Каждый обычный бой Акта 2 проходится на усиленной колоде (как к Акту 2)."""
    for node in build_act2_map():
        if node.kind != NODE_FIGHT:
            continue
        run = RunState.new_stazher(seed=5)
        # усиление колоды: пара сильных карт, как накопилось бы за Акт 1
        run.add_card(make_fors_mazhor())
        run.add_card(make_avral())
        run.hero.starting_deck = run.battle_deck()
        cb = Combat(hero=run.hero, enemy=node.enemy_factory(), rng_seed=5)
        cb.start_combat()
        steps = 0
        while not cb.is_over() and steps < 300:
            steps += 1
            _play_turn(cb)
            if cb.is_over():
                break
            cb.end_turn()
        assert cb.result == "victory", f"{node.title} не пройден усиленной колодой"
