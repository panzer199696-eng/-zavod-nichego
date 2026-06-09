"""Экран финала забега: победа над боссом А1 или поражение. Возврат в меню."""

from __future__ import annotations

import pygame

from scenes.base import Scene
from ui.theme import BG_DEEP, PINK, SCREEN_W, TEXT_DIM, YELLOW, get_font
from ui.widgets import Button


class GameOverScene(Scene):
    def __init__(self, manager, won: bool):
        super().__init__(manager)
        self.won = won

    def on_enter(self) -> None:
        self.menu_btn = Button((80, 460, 200, 50), "В меню")

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu_btn.hit(event.pos):
            from scenes.menu import MenuScene

            self.manager.set_scene(MenuScene(self.manager))

    def draw(self, surf) -> None:
        surf.fill(BG_DEEP)
        if self.won:
            t1 = get_font(24, bold=True).render("АКТ 1 ПРОЙДЕН", True, YELLOW)
            t2 = get_font(13).render("Квартальный Отчёт повержен.", True, TEXT_DIM)
            t3 = get_font(11).render("Дальше — Акт 2 (в разработке).", True, TEXT_DIM)
        else:
            t1 = get_font(24, bold=True).render("УВОЛЕН", True, PINK)
            t2 = get_font(13).render("Рабочие нервы кончились.", True, TEXT_DIM)
            t3 = get_font(11).render("Ничего так и не построено.", True, TEXT_DIM)
        surf.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, 180))
        surf.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, 230))
        surf.blit(t3, (SCREEN_W // 2 - t3.get_width() // 2, 252))
        run = self.manager.run_state
        if run:
            stats = get_font(11).render(
                f"Карт в колоде: {len(run.deck)} · Реликвий: {len(run.relics)}",
                True,
                TEXT_DIM,
            )
            surf.blit(stats, (SCREEN_W // 2 - stats.get_width() // 2, 300))
        self.menu_btn.draw(surf)
