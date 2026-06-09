"""Главное меню: лого + кнопка «Новая командировка»."""

from __future__ import annotations

import pygame

from game_state.run import RunState
from scenes.base import Scene
from scenes.map_scene import MapScene
from ui.assets import get_sprite
from ui.theme import BG_DEEP, PINK, SCREEN_W, TEXT_DIM, YELLOW, get_font
from ui.widgets import Button


class MenuScene(Scene):
    def on_enter(self) -> None:
        self.start_btn = Button((60, 470, 240, 50), "Новая командировка")

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.start_btn.hit(event.pos):
            self._start_run()

    def _start_run(self) -> None:
        self.manager.run_state = RunState.new_stazher()
        self.manager.set_scene(MapScene(self.manager))

    def draw(self, surf) -> None:
        surf.fill(BG_DEEP)
        title = get_font(26, bold=True)
        l1 = title.render("НИЧЕГО НЕ", True, YELLOW)
        l2 = title.render("ПОСТРОЕНО", True, PINK)
        surf.blit(l1, (SCREEN_W // 2 - l1.get_width() // 2, 60))
        surf.blit(l2, (SCREEN_W // 2 - l2.get_width() // 2, 95))
        sub = get_font(11).render("строительный roguelike · Акт 1", True, TEXT_DIM)
        surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 135))
        # арт Стажёра по центру
        sprite = get_sprite("stazher", "Стажёр", 160, 240)
        surf.blit(sprite, (SCREEN_W // 2 - sprite.get_width() // 2, 200))
        self.start_btn.draw(surf)
