"""Сцена награды: выбор 1 из 3 карт пула Стажёра + валюта; элита даёт реликвию."""

from __future__ import annotations

import pygame

from engine.content import all_relics
from game_state.map import NODE_BOSS, NODE_ELITE
from scenes.base import Scene
from ui.theme import (
    BG_DEEP,
    CYAN,
    LEGEND,
    SCREEN_W,
    TEXT,
    TEXT_DIM,
    YELLOW,
    get_font,
)
from ui.widgets import CARD_H, CARD_W, Button, draw_card


class RewardScene(Scene):
    def __init__(self, manager, node):
        super().__init__(manager)
        self.node = node

    def on_enter(self) -> None:
        run = self.manager.run_state
        run.gain_currency(self.node.currency_reward)
        self.choices = run.roll_reward(3)
        # элита/босс дарят реликвию (если есть невыбранные)
        self.relic = None
        if self.node.kind in (NODE_ELITE, NODE_BOSS):
            owned = {type(r).__name__ for r in run.relics}
            available = [r for r in all_relics() if type(r).__name__ not in owned]
            if available:
                self.relic = run.rng.choice(available)
                run.add_relic(self.relic)
        self.skip_btn = Button(
            (110, 560, 140, 40), "Пропустить", color=TEXT_DIM, text_color=TEXT
        )
        self._card_rects()

    def _card_rects(self):
        n = len(self.choices)
        cw, ch = CARD_W + 30, CARD_H + 40
        total = n * (cw + 10)
        start_x = SCREEN_W // 2 - total // 2
        self.rects = [
            pygame.Rect(start_x + i * (cw + 10), 240, cw, ch) for i in range(n)
        ]

    def handle_event(self, event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        for i, r in enumerate(self.rects):
            if r.collidepoint(event.pos):
                self.manager.run_state.add_card(self.choices[i])
                self._advance()
                return
        if self.skip_btn.hit(event.pos):
            self._advance()

    def _advance(self) -> None:
        run = self.manager.run_state
        run.node_index += 1
        if self.node.kind == NODE_BOSS:
            from scenes.gameover import GameOverScene

            self.manager.set_scene(GameOverScene(self.manager, won=True))
        else:
            from scenes.map_scene import MapScene

            self.manager.set_scene(MapScene(self.manager))

    def draw(self, surf) -> None:
        surf.fill(BG_DEEP)
        ttl = get_font(18, bold=True).render("ПОБЕДА!", True, YELLOW)
        surf.blit(ttl, (SCREEN_W // 2 - ttl.get_width() // 2, 40))
        run = self.manager.run_state
        money = get_font(13, bold=True).render(
            f"+{self.node.currency_reward} Сметы  (всего {run.currency})", True, LEGEND
        )
        surf.blit(money, (SCREEN_W // 2 - money.get_width() // 2, 80))
        if self.relic is not None:
            rl = get_font(12, bold=True).render(
                f"Реликвия: {self.relic.name}", True, CYAN
            )
            surf.blit(rl, (SCREEN_W // 2 - rl.get_width() // 2, 110))
            rd = get_font(10).render(self.relic.description, True, TEXT_DIM)
            surf.blit(rd, (SCREEN_W // 2 - rd.get_width() // 2, 128))

        pick = get_font(13).render("Выбери карту в награду:", True, TEXT)
        surf.blit(pick, (SCREEN_W // 2 - pick.get_width() // 2, 200))
        for card, rect in zip(self.choices, self.rects):
            draw_card(surf, rect, card, playable=True, cost_display=card.cost)
        self.skip_btn.draw(surf)
