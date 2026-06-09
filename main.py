"""Entry-point игры «Ничего не построено» — Акт 1 (играбельный срез).

Окно 360×640, 60 FPS, pygame. Менеджер сцен: Меню → Карта → Бой → Награда → Босс.
Старый кликер сохранён в main_clicker_old.py.
"""

from __future__ import annotations

import sys

import pygame

from scenes.base import SceneManager
from scenes.menu import MenuScene
from ui.theme import FPS, SCREEN_H, SCREEN_W


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Ничего не построено — Акт 1")
    clock = pygame.time.Clock()

    manager = SceneManager()
    manager.set_scene(MenuScene(manager))

    while manager.running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                manager.quit()
            else:
                manager.handle_event(event)
        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
