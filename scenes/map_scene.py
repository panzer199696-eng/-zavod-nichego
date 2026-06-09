"""Карта этажей Акта 1: вертикальный столбик узлов; текущий доступен для входа."""

from __future__ import annotations

import pygame

from game_state.map import NODE_BOSS, NODE_ELITE, build_act1_map
from scenes.base import Scene
from ui.theme import (
    BG_DEEP,
    BG_PANEL,
    CYAN,
    LEGEND,
    OUTLINE,
    PINK,
    SCREEN_H,
    SCREEN_W,
    TEXT,
    TEXT_DIM,
    YELLOW,
    get_font,
)


class MapScene(Scene):
    def on_enter(self) -> None:
        self.nodes = build_act1_map()
        run = self.manager.run_state
        # позиции узлов — снизу вверх (прогресс наверх)
        self.node_pos = []
        n = len(self.nodes)
        for i in range(n):
            x = SCREEN_W // 2
            y = SCREEN_H - 90 - i * ((SCREEN_H - 200) // max(1, n - 1))
            self.node_pos.append((x, y))
        # если забег пройден — финал
        self.completed = run.node_index >= len(self.nodes)

    def handle_event(self, event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        run = self.manager.run_state
        if self.completed:
            return
        idx = run.node_index
        cx, cy = self.node_pos[idx]
        if (event.pos[0] - cx) ** 2 + (event.pos[1] - cy) ** 2 <= 26**2:
            self._enter_node(idx)

    def _enter_node(self, idx: int) -> None:
        from scenes.battle import BattleScene  # локальный импорт — цикл сцен

        node = self.nodes[idx]
        self.manager.set_scene(BattleScene(self.manager, node))

    def draw(self, surf) -> None:
        surf.fill(BG_DEEP)
        title = get_font(16, bold=True).render("АКТ 1 · Открытый Офис", True, YELLOW)
        surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 14))
        run = self.manager.run_state
        money = get_font(12, bold=True).render(f"Смета: {run.currency}", True, LEGEND)
        surf.blit(money, (10, 40))
        relic_txt = get_font(11).render(f"Реликвий: {len(run.relics)}", True, CYAN)
        surf.blit(relic_txt, (SCREEN_W - relic_txt.get_width() - 10, 42))

        # линии пути
        for i in range(len(self.nodes) - 1):
            pygame.draw.line(surf, BG_PANEL, self.node_pos[i], self.node_pos[i + 1], 3)

        for i, node in enumerate(self.nodes):
            cx, cy = self.node_pos[i]
            done = i < run.node_index
            current = i == run.node_index and not self.completed
            if node.kind == NODE_BOSS:
                color = PINK
            elif node.kind == NODE_ELITE:
                color = LEGEND
            else:
                color = CYAN
            ring = YELLOW if current else (TEXT_DIM if not done else color)
            fill = color if (done or current) else BG_PANEL
            pygame.draw.circle(surf, fill, (cx, cy), 22)
            pygame.draw.circle(surf, ring, (cx, cy), 22, width=3 if current else 2)
            ic = get_font(16, bold=True).render(
                node.icon, True, OUTLINE if (done or current) else TEXT_DIM
            )
            surf.blit(ic, (cx - ic.get_width() // 2, cy - ic.get_height() // 2))
            # подпись узла
            lbl = get_font(10, bold=current).render(
                node.title, True, TEXT if current else TEXT_DIM
            )
            surf.blit(lbl, (cx + 30, cy - lbl.get_height() // 2))

        if self.completed:
            won = get_font(18, bold=True).render("АКТ 1 ПРОЙДЕН!", True, YELLOW)
            surf.blit(won, (SCREEN_W // 2 - won.get_width() // 2, SCREEN_H // 2))
        else:
            hint = get_font(11).render("Нажми на светящийся узел", True, TEXT_DIM)
            surf.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 30))
