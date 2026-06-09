"""Прогон играбельности Акта 1: старт → 4 боя → элита → босс — победа.

Headless. Использует компетентного авто-пилота (как человек): тратит энергию
на урон, держит финишер «Аврал» до Запала≥4, ставит броню при крупной входящей
атаке, в награду берёт прямые урон-карты. Цель — доказать, что срез проходим
от меню до босса А1, а не оценить ИИ.
"""

from engine.combat import Combat
from engine.content import all_relics
from engine.statuses import STATUS
from game_state.map import NODE_BOSS, NODE_ELITE, build_act1_map
from game_state.run import RunState

# Карты, которые компетентный игрок берёт в награду: усиливают, а не разбавляют
# колоду. Слабые/ситуативные (КМ-2 без брони, Чёрная метка, Служебная записка
# 5 урона/энергию < базового Удара) игрок скипает, держа колоду плотной —
# иначе средний урон на руку падает ниже стартового и босс не пробивается.
STRONG_PICKS = (
    "fors_mazhor",  # 22 урона + 8 брони — явный апгрейд
    "prinesi_poday",  # 0 энергии, 4 урона + добор
    "reglament_5_2",  # 4 брони + добор (циклит колоду)
    "entuziazm",  # энейблер 0-стоимости
    "iniciativnaya",  # 0 энергии добор + Запал
)


def _pick_reward(choices):
    """Компетентный выбор: берём сильнейший апгрейд, иначе СКИП (None)."""
    strong = [c for c in choices if c.id in STRONG_PICKS]
    return strong[0] if strong else None


def _play_turn(cb: Combat) -> None:
    """Один ход: тратим энергию разумно (как игрок)."""
    guard = 0
    while not cb.is_over() and guard < 60:
        guard += 1
        playable = [c for c in cb.hand if cb.can_play(c)]
        if not playable:
            break
        incoming = cb.enemy.current_intent()
        # сколько брони реально не хватает под входящую атаку
        threat = incoming.value if incoming.kind == "attack" else 0
        need_block = max(0, threat - cb.hero.block)
        zapal = cb.hero.get_status(STATUS.ZAPAL)

        def priority(card):
            t = card.card_type.value
            # держим Аврал-финишер, пока Запал не накоплен
            if card.no_zapal and "Запал" in card.description and zapal < 4:
                return 9
            if t in ("Действие", "Схема"):
                return 0  # добор/ресурсы/Запал — раньше
            if t == "Защита":
                # блок не только на грани смерти, а под любую ощутимую угрозу
                return 1 if need_block > 2 else 7
            if t == "Атака":
                # КМ-2 (урон от брони) бесполезна без брони — в конец
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


def _simulate_run(seed: int):
    run = RunState.new_stazher(seed=seed)
    history = []
    for node in build_act1_map():
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
        history.append((node.title, cb.result, run.hero.hp))
        if cb.result != "victory":
            return False, history
        # награда — компетентный игрок берёт апгрейд или скипает мусор
        run.gain_currency(node.currency_reward)
        pick = _pick_reward(run.roll_reward(3))
        if pick is not None:
            run.add_card(pick)
        if node.kind in (NODE_ELITE, NODE_BOSS):
            _grant_relic(run)
        run.node_index += 1
    return True, history


def test_act1_is_winnable_from_start_to_boss():
    """Срез проходится компетентным игроком на ЗДОРОВОЙ доле сидов.

    Не «хотя бы раз» (это прошло бы и при кривом балансе), а ≥4/12 ≈ 33% —
    Акт 1 проходим, но не тривиален. Текущий баланс даёт ~6/12.
    """
    results = [_simulate_run(seed)[0] for seed in range(12)]
    wins = sum(results)
    assert wins >= 4, f"Акт 1 слишком жёсткий: {wins}/12 побед (ожидалось ≥4)"


def test_each_normal_fight_winnable():
    """Каждый обычный бой Акта 1 проходится авто-пилотом на старте."""
    from game_state.map import NODE_FIGHT

    for node in build_act1_map():
        if node.kind != NODE_FIGHT:
            continue
        run = RunState.new_stazher(seed=3)
        run.hero.starting_deck = run.battle_deck()
        cb = Combat(hero=run.hero, enemy=node.enemy_factory(), rng_seed=3)
        cb.start_combat()
        steps = 0
        while not cb.is_over() and steps < 200:
            steps += 1
            _play_turn(cb)
            if cb.is_over():
                break
            cb.end_turn()
        assert cb.result == "victory", f"{node.title} не пройден на старте"
