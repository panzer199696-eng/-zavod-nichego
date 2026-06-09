"""Сцена боя — ядро UI. Оборачивает headless-движок Combat.

Раскладка (портрет 360×640):
  верх        — назад/название боя
  y36–220     — враг: спрайт, HP, намерение, статусы
  y220–360    — герой: спрайт, HP, броня, статусы
  y360–395    — ресурсы: энергия, Запал, колода/сброс
  y395–560    — рука карт (веер)
  y560–600    — кнопка «Завершить ход»
Ход врага проигрывается с задержкой (анимация), всплывают числа урона/брони.
"""

from __future__ import annotations

import math

import pygame

from engine.combat import Combat
from engine.statuses import STATUS
from scenes.base import Scene
from ui.assets import get_background, get_sprite
from ui.theme import (
    BG_DEEP,
    CYAN,
    LEGEND,
    ORANGE,
    OUTLINE,
    RED,
    SCREEN_H,
    SCREEN_W,
    TEXT,
    TEXT_DIM,
    YELLOW,
    get_font,
)
from ui.widgets import (
    CARD_H,
    CARD_W,
    Button,
    FloatingNumber,
    draw_card,
    draw_hp_bar,
    draw_intent,
    draw_status_icons,
    spawn_burst,
)

ENEMY_SLOT = (140, 175)
HERO_SLOT = (110, 138)

# центры спрайтов (для эмиттеров частиц и выпадов)
ENEMY_CENTER = (SCREEN_W // 2, 115)
HERO_CENTER = (75, 305)

HERO_LUNGE_DUR = 0.26  # рывок героя при атаке
ENEMY_FADE_DUR = 0.5  # затухание врага при смерти
SHAKE_DUR = 0.3  # длительность тряски экрана


class BattleScene(Scene):
    def __init__(self, manager, node):
        super().__init__(manager)
        self.node = node

    def on_enter(self) -> None:
        run = self.manager.run_state
        self.combat = Combat(
            hero=run.hero,
            enemy=self.node.enemy_factory(),
            relics=run.relics,
        )
        # боевая колода = копия мета-колоды (мету не мутируем)
        self.combat.hero.starting_deck = run.battle_deck()
        # восстановить HP-героя из меты (между боями HP сохраняется)
        self.combat.start_combat()

        self.end_btn = Button((90, 600, 180, 36), "Завершить ход")
        self.floats: list[FloatingNumber] = []
        self.particles: list = []  # ui.widgets.Particle
        self.selected_idx = None  # выбранная карта, ждущая цель
        self.enemy_anim = 0.0  # таймер хода врага
        self.enemy_phase = None  # None | "running"
        self._prev_hero_hp = self.combat.hero.hp
        self._prev_enemy_hp = self.combat.enemy.hp
        self.message = ""
        # таймеры анимаций
        self.hero_lunge = 0.0  # рывок героя при розыгрыше атаки
        self.shake_t = 0.0  # остаток тряски экрана
        self.shake_mag = 0.0  # амплитуда тряски
        self.enemy_fade = 0.0  # прогресс затухания врага при смерти
        self._death_burst = False  # разлёт бумаг при смерти — однократно

    # --------------------------------------------------------- events
    def handle_event(self, event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.combat.is_over():
            self._leave_after_result()
            return
        if self.enemy_phase == "running":
            return  # ввод заблокирован на ходу врага

        # клик по карте руки
        card_idx = self._card_at(event.pos)
        if card_idx is not None:
            self._click_card(card_idx)
            return
        # клик по врагу (если выбрана карта-атака, ждущая цель)
        if self.selected_idx is not None and self._enemy_clicked(event.pos):
            self._play_selected()
            return
        # кнопка завершения хода
        if self.end_btn.hit(event.pos):
            self._start_enemy_turn()
            return
        # клик в пустоту — отменяем выбранную атаку (иначе выбор «залипал»)
        if self.selected_idx is not None:
            self.selected_idx = None
            self.message = ""

    def _click_card(self, idx: int) -> None:
        card = self.combat.hand[idx]
        if not self.combat.can_play(card):
            self.message = "Недостаточно энергии"
            return
        if self._needs_target(card):
            self.selected_idx = idx  # ждём клик по врагу
            self.message = "Выбери цель"
        else:
            self.selected_idx = idx
            self._play_selected()

    def _play_selected(self) -> None:
        if self.selected_idx is None:
            return
        idx = self.selected_idx
        if idx >= len(self.combat.hand):
            self.selected_idx = None
            return
        card = self.combat.hand[idx]
        if self.combat.can_play(card):
            is_attack = card.card_type.value == "Атака"
            self.combat.play_card_instance(card)
            if is_attack:
                self.hero_lunge = HERO_LUNGE_DUR  # рывок к врагу
            self._spawn_deltas()
        self.selected_idx = None
        self.message = ""

    def _needs_target(self, card) -> bool:
        return card.card_type.value == "Атака"

    # ------------------------------------------------ enemy turn / anim
    def _start_enemy_turn(self) -> None:
        self.selected_idx = None
        self.enemy_phase = "running"
        self.enemy_anim = 0.0

    def update(self, dt: float) -> None:
        for f in self.floats:
            f.update(dt)
        self.floats = [f for f in self.floats if f.alive()]

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        # спад таймеров анимаций
        if self.hero_lunge > 0:
            self.hero_lunge = max(0.0, self.hero_lunge - dt)
        if self.shake_t > 0:
            self.shake_t = max(0.0, self.shake_t - dt)

        # затухание поверженного врага + разовый разлёт бумаг
        if self.combat.result == "victory":
            if not self._death_burst:
                self._death_burst = True
                self.particles += spawn_burst(
                    *ENEMY_CENTER,
                    TEXT,
                    n=20,
                    speed=140,
                    size=6,
                    life=0.9,
                    rng=self.combat.rng,
                )
                self.particles += spawn_burst(
                    *ENEMY_CENTER, YELLOW, n=12, speed=160, rng=self.combat.rng
                )
            if self.enemy_fade < 1.0:
                self.enemy_fade = min(1.0, self.enemy_fade + dt / ENEMY_FADE_DUR)

        if self.enemy_phase == "running":
            self.enemy_anim += dt
            if self.enemy_anim >= 0.6:  # задержка-анимация хода врага
                self.combat.end_turn()
                self._spawn_deltas()
                self.enemy_phase = None
                if self.combat.is_over():
                    self.message = (
                        "ПОБЕДА!" if self.combat.result == "victory" else "ПОРАЖЕНИЕ"
                    )

    def _spawn_deltas(self) -> None:
        """Числа + частицы по изменению HP героя/врага с прошлого замера."""
        ehp = self.combat.enemy.hp
        if ehp < self._prev_enemy_hp:
            dmg = self._prev_enemy_hp - ehp
            self.floats.append(FloatingNumber(SCREEN_W // 2, 70, dmg, YELLOW))
            # удар по врагу: жёлто-оранжевые искры + светлые обрывки бумаг
            n = min(24, 8 + dmg)
            self.particles += spawn_burst(
                *ENEMY_CENTER, YELLOW, n=n, rng=self.combat.rng
            )
            self.particles += spawn_burst(
                *ENEMY_CENTER, ORANGE, n=n // 2, speed=90, rng=self.combat.rng
            )
            self.particles += spawn_burst(
                *ENEMY_CENTER,
                TEXT,
                n=4,
                speed=70,
                size=5,
                life=0.7,
                rng=self.combat.rng,
            )
        self._prev_enemy_hp = ehp
        hhp = self.combat.hero.hp
        if hhp < self._prev_hero_hp:
            dmg = self._prev_hero_hp - hhp
            self.floats.append(FloatingNumber(SCREEN_W // 2, 250, dmg, RED))
            self.particles += spawn_burst(
                *HERO_CENTER, RED, n=min(20, 6 + dmg), rng=self.combat.rng
            )
            # крупный удар по герою — тряска экрана пропорционально урону
            if dmg >= 8:
                self.shake_t = SHAKE_DUR
                self.shake_mag = min(10.0, 3.0 + dmg * 0.4)
        self._prev_hero_hp = hhp

    def _leave_after_result(self) -> None:
        run = self.manager.run_state
        if self.combat.result == "victory":
            run.hero.hp = self.combat.hero.hp  # перенос HP в мету
            from scenes.reward import RewardScene

            self.manager.set_scene(RewardScene(self.manager, self.node))
        else:
            from scenes.gameover import GameOverScene

            self.manager.set_scene(GameOverScene(self.manager, won=False))

    # --------------------------------------------------- hit-testing
    def _hand_rects(self):
        n = len(self.combat.hand)
        if n == 0:
            return []
        total = n * (CARD_W + 4)
        start_x = SCREEN_W // 2 - total // 2
        rects = []
        for i in range(n):
            x = start_x + i * (CARD_W + 4)
            y = 470 - (8 if i % 2 == 0 else 0)  # лёгкий веер
            rects.append(pygame.Rect(x, y, CARD_W, CARD_H))
        return rects

    def _card_at(self, pos):
        for i, r in enumerate(self._hand_rects()):
            if r.collidepoint(pos):
                return i
        return None

    def _enemy_clicked(self, pos) -> bool:
        ex = SCREEN_W // 2
        return (ex - 80 < pos[0] < ex + 80) and (40 < pos[1] < 210)

    # ------------------------------------------------ анимационные сдвиги
    def _enemy_offset(self) -> int:
        """Выпад врага вниз-к-герою на фазе атаки (sin-дуга по таймеру хода)."""
        if self.enemy_phase != "running":
            return 0
        if self.combat.enemy.current_intent().kind != "attack":
            return 0
        prog = min(self.enemy_anim / 0.5, 1.0)
        return int(math.sin(prog * math.pi) * 16)

    def _hero_offset(self) -> tuple[int, int]:
        """Рывок героя вверх-вправо к врагу при розыгрыше атаки."""
        if self.hero_lunge <= 0:
            return 0, 0
        prog = 1 - self.hero_lunge / HERO_LUNGE_DUR
        off = math.sin(prog * math.pi) * 14
        return int(off), int(-off * 0.5)

    # --------------------------------------------------------- draw
    def draw(self, surf) -> None:
        # рисуем кадр на отдельную поверхность, затем блитим со сдвигом-тряской
        frame = pygame.Surface((SCREEN_W, SCREEN_H))
        self._draw_frame(frame)

        ox = oy = 0
        if self.shake_t > 0:
            mag = self.shake_mag * (self.shake_t / SHAKE_DUR)
            ox = int(self.combat.rng.uniform(-mag, mag))
            oy = int(self.combat.rng.uniform(-mag, mag))
            surf.fill(BG_DEEP)  # скрыть зазор на краях при сдвиге
        surf.blit(frame, (ox, oy))

    def _draw_frame(self, surf) -> None:
        surf.blit(get_background(), (0, 0))
        c = self.combat

        # верхняя плашка
        ttl = get_font(12, bold=True).render(self.node.title, True, TEXT)
        surf.blit(ttl, (SCREEN_W // 2 - ttl.get_width() // 2, 8))

        # --- враг ---
        e = c.enemy
        ew, eh = ENEMY_SLOT
        spr = get_sprite(e.id, e.name, ew, eh)
        edy = self._enemy_offset()
        if self.enemy_fade > 0:  # затухание при смерти
            spr = spr.copy()
            spr.set_alpha(int(255 * (1 - self.enemy_fade)))
        surf.blit(spr, (SCREEN_W // 2 - ew // 2, 30 + edy))
        # намерение над врагом
        if not c.is_over():
            draw_intent(surf, SCREEN_W // 2 + 60, 40, e.current_intent())
        draw_hp_bar(surf, 60, 196, 240, 16, e.hp, e.max_hp, e.block)
        draw_status_icons(surf, 60, 215, e.statuses)

        # --- линия мерзлоты / разделитель ---
        pygame.draw.line(surf, OUTLINE, (0, 236), (SCREEN_W, 236), 2)

        # --- герой ---
        h = c.hero
        hw, hh = HERO_SLOT
        hspr = get_sprite("stazher", "Стажёр", hw, hh)
        hdx, hdy = self._hero_offset()
        surf.blit(hspr, (20 + hdx, 248 + hdy))
        draw_hp_bar(surf, 150, 250, 150, 16, h.hp, h.max_hp, h.block)
        draw_status_icons(surf, 150, 272, h.statuses)

        # --- частицы (поверх бойцов, под рукой/HUD) ---
        for p in self.particles:
            p.draw(surf)

        # --- ресурсы ---
        self._draw_resources(surf, c)

        # --- прицел на враге, когда выбрана атака, ждущая цель ---
        if (
            self.selected_idx is not None
            and self.selected_idx < len(c.hand)
            and self._needs_target(c.hand[self.selected_idx])
            and not c.is_over()
        ):
            self._draw_target_reticle(surf)

        # --- рука ---
        rects = self._hand_rects()
        for i, (card, rect) in enumerate(zip(c.hand, rects)):
            playable = c.can_play(card)
            if i == self.selected_idx:
                pygame.draw.rect(surf, YELLOW, rect.inflate(6, 6), border_radius=8)
            draw_card(surf, rect, card, playable, c.card_cost(card))

        # --- постоянная подсказка управления (когда ход игрока, нет сообщения) ---
        if not c.is_over() and self.enemy_phase != "running" and not self.message:
            hint = "Карта → клик по врагу для атаки · действия играются сразу"
            ht = get_font(9).render(hint, True, TEXT_DIM)
            surf.blit(ht, (SCREEN_W // 2 - ht.get_width() // 2, 420))

        # кнопка / сообщение
        if c.is_over():
            self.end_btn.label = "Далее"
        self.end_btn.enabled = self.enemy_phase != "running"
        self.end_btn.draw(surf)
        if self.message:
            mt = get_font(13, bold=True).render(self.message, True, ORANGE)
            surf.blit(mt, (SCREEN_W // 2 - mt.get_width() // 2, 440))

        for f in self.floats:
            f.draw(surf)

    def _draw_target_reticle(self, surf) -> None:
        """Пульсирующий жёлтый прицел вокруг врага + подпись «бей сюда»."""
        cx, cy = ENEMY_CENTER
        pulse = 4 + int(3 * (1 + math.sin(pygame.time.get_ticks() / 120.0)))
        pygame.draw.circle(surf, YELLOW, (cx, cy), 70 + pulse, width=3)
        # уголки-прицел
        for dx in (-70, 70):
            for dy in (-70, 70):
                pygame.draw.circle(surf, YELLOW, (cx + dx, cy + dy), 4)
        lbl = get_font(11, bold=True).render("клик — бей сюда", True, YELLOW)
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - 95))

    def _draw_resources(self, surf, c):
        y = 300
        # энергия
        pygame.draw.circle(surf, YELLOW, (28, y + 12), 16)
        pygame.draw.circle(surf, OUTLINE, (28, y + 12), 16, width=2)
        et = get_font(14, bold=True).render(str(c.energy), True, OUTLINE)
        surf.blit(et, (28 - et.get_width() // 2, y + 12 - et.get_height() // 2))
        elbl = get_font(9).render("энергия", True, TEXT_DIM)
        surf.blit(elbl, (10, y + 30))
        # Запал
        zap = c.hero.get_status(STATUS.ZAPAL)
        zt = get_font(11, bold=True).render(f"Запал: {zap}", True, ORANGE)
        surf.blit(zt, (60, y + 4))
        # колода/сброс
        dt = get_font(10).render(
            f"Колода {len(c.draw_pile)}  Сброс {len(c.discard_pile)}", True, CYAN
        )
        surf.blit(dt, (60, y + 22))
        # смета
        run = self.manager.run_state
        mt = get_font(10, bold=True).render(f"Смета {run.currency}", True, LEGEND)
        surf.blit(mt, (SCREEN_W - mt.get_width() - 10, y + 4))
