"""Смоук-скрины сцены боя (Акт 1) с новыми спрайтами и частицами. Headless.

Прогоняет сцену через настоящие методы (розыгрыш атаки → частицы → update),
чтобы в кадре были искры/обрывки. Делает скрин для нескольких узлов.

    python make_battle_screenshot.py            # узел 0 (Прораб) -> battle.png
    python make_battle_screenshot.py 4 elite    # элита Технадзор -> elite.png
"""

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).parent))

from game_state.map import build_act1_map
from game_state.run import RunState
from scenes.base import SceneManager
from scenes.battle import BattleScene
from ui.theme import SCREEN_H, SCREEN_W


def shot(node_index: int, out_name: str) -> None:
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    run = RunState.new_stazher(seed=7)
    manager = SceneManager(run_state=run)
    node = build_act1_map()[node_index]
    scene = BattleScene(manager, node)
    manager.set_scene(scene)

    # разыграть первую доступную атаку «как из UI»: рывок + урон + частицы
    cb = scene.combat
    for i, card in enumerate(list(cb.hand)):
        if card.card_type.value == "Атака" and cb.can_play(card):
            scene._click_card(i)  # ставит цель/играет, спавнит частицы и рывок
            if scene.selected_idx is not None:
                scene._play_selected()
            break

    # продвинуть анимацию: частицы разлетелись, но ещё живы; рывок в пике
    for _ in range(6):
        scene.update(1 / 60)

    scene.draw(surf)
    out = Path(__file__).parent / out_name
    pygame.image.save(surf, str(out))
    print(f"{out_name} сохранён: {out}")


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((SCREEN_W, SCREEN_H))  # для .convert()
    if len(sys.argv) >= 3:
        shot(int(sys.argv[1]), f"{sys.argv[2]}.png")
    else:
        shot(0, "battle.png")  # Прораб
        shot(4, "elite.png")  # Технадзор-выездной (элита)
    pygame.quit()
