"""Базовая сцена и менеджер сцен.

Менеджер headless-совместим: update/draw/handle_event можно вызывать без окна
(нужна лишь поверхность для draw). Переходы между сценами — через set_scene,
который сцены вызывают на менеджере.
"""

from __future__ import annotations

from typing import Optional


class Scene:
    """Базовая сцена. Наследники переопределяют нужные методы."""

    def __init__(self, manager: "SceneManager"):
        self.manager = manager

    def on_enter(self) -> None:
        """Вызывается при активации сцены."""

    def handle_event(self, event) -> None:
        """Обработка одного pygame-события."""

    def update(self, dt: float) -> None:
        """Логика/анимации за кадр (dt — секунды)."""

    def draw(self, surf) -> None:
        """Отрисовка на поверхность."""


class SceneManager:
    """Держит активную сцену и общий RunState; маршрутизирует кадр/события."""

    def __init__(self, run_state=None):
        self.run_state = run_state
        self.scene: Optional[Scene] = None
        self.running = True

    def set_scene(self, scene: Scene) -> None:
        self.scene = scene
        scene.on_enter()

    def handle_event(self, event) -> None:
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.scene:
            self.scene.update(dt)

    def draw(self, surf) -> None:
        if self.scene:
            self.scene.draw(surf)

    def quit(self) -> None:
        self.running = False
