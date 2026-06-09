"""Headless-смоук сцен: создание, рендер кадров, переходы бой→награда→карта.

Используем SDL dummy-видеодрайвер — без окна, без зависания.
"""

import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(scope="module", autouse=True)
def _pg():
    pygame.init()
    pygame.display.set_mode((360, 640))
    yield
    pygame.quit()


def _surface():
    return pygame.Surface((360, 640))


def _new_manager():
    from game_state.run import RunState
    from scenes.base import SceneManager

    return SceneManager(run_state=RunState.new_stazher(seed=1))


def test_menu_scene_renders():
    from scenes.base import SceneManager
    from scenes.menu import MenuScene

    mgr = SceneManager()
    mgr.set_scene(MenuScene(mgr))
    mgr.update(0.016)
    mgr.draw(_surface())  # не падает


def test_map_scene_renders():
    from scenes.map_scene import MapScene

    mgr = _new_manager()
    mgr.set_scene(MapScene(mgr))
    mgr.draw(_surface())


def test_battle_scene_creates_and_renders():
    from game_state.map import build_act1_map
    from scenes.battle import BattleScene

    mgr = _new_manager()
    node = build_act1_map()[0]
    scene = BattleScene(mgr, node)
    mgr.set_scene(scene)
    assert scene.combat is not None
    assert len(scene.combat.hand) == 5
    for _ in range(3):  # несколько кадров
        mgr.update(0.016)
        mgr.draw(_surface())


def test_battle_to_reward_to_map_transition():
    """Победа в бою -> RewardScene -> выбор карты -> MapScene; node_index растёт."""
    from game_state.map import build_act1_map
    from scenes.battle import BattleScene
    from scenes.map_scene import MapScene
    from scenes.reward import RewardScene

    mgr = _new_manager()
    node = build_act1_map()[0]
    scene = BattleScene(mgr, node)
    mgr.set_scene(scene)

    # форсируем победу: обнуляем HP врага и проводим завершение
    scene.combat.enemy.hp = 0
    scene.combat._check_end()
    assert scene.combat.result == "victory"

    # клик переводит из боя в награду
    scene._leave_after_result()
    assert isinstance(mgr.scene, RewardScene)
    reward = mgr.scene
    mgr.draw(_surface())

    deck_before = len(mgr.run_state.deck)
    idx_before = mgr.run_state.node_index
    # выбираем первую карту награды
    mgr.run_state.add_card(reward.choices[0])
    reward._advance()
    assert isinstance(mgr.scene, MapScene)
    assert len(mgr.run_state.deck) == deck_before + 1
    assert mgr.run_state.node_index == idx_before + 1
    mgr.draw(_surface())


def test_full_path_smoke_reaches_boss():
    """Прогон сцен по всем узлам через форс-победы: доходит до GameOver(won)."""
    from game_state.map import build_act1_map
    from scenes.battle import BattleScene
    from scenes.gameover import GameOverScene
    from scenes.map_scene import MapScene
    from scenes.reward import RewardScene

    mgr = _new_manager()
    nodes = build_act1_map()
    mgr.set_scene(MapScene(mgr))

    for node in nodes:
        battle = BattleScene(mgr, node)
        mgr.set_scene(battle)
        mgr.draw(_surface())
        battle.combat.enemy.hp = 0
        battle.combat._check_end()
        battle._leave_after_result()
        assert isinstance(mgr.scene, (RewardScene, GameOverScene))
        if isinstance(mgr.scene, GameOverScene):
            break
        reward = mgr.scene
        mgr.run_state.add_card(reward.choices[0])
        reward._advance()

    assert isinstance(mgr.scene, GameOverScene)
    assert mgr.scene.won is True
    mgr.draw(_surface())


def test_cyrillic_renders_nonempty():
    """Русский текст рендерится непустым (кириллица в Arial)."""
    from ui.theme import TEXT, get_font

    surf = get_font(16).render("Стажёр по Ничему", True, TEXT)
    assert surf.get_width() > 0
    assert surf.get_height() > 0
