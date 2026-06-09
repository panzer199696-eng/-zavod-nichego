"""Тесты системы частиц (UI-полировка боя). Headless, без окна."""

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from ui.widgets import Particle, spawn_burst


def test_particle_moves_by_velocity():
    p = Particle(10, 20, vx=100, vy=-50, color=(255, 0, 0), size=4, life=1.0)
    p.update(0.1)
    assert p.x == 10 + 100 * 0.1
    # вертикаль: скорость + гравитация (gravity=0 по умолчанию)
    assert p.y == 20 - 50 * 0.1


def test_particle_gravity_pulls_down():
    p = Particle(0, 0, vx=0, vy=0, color=(1, 2, 3), size=3, life=1.0, gravity=200)
    p.update(0.5)  # шаг 1: позиция по скорости (0), затем гравитация разгоняет vy
    assert p.vy > 0  # гравитация разогнала вниз
    p.update(0.5)  # шаг 2: набранная vy уже двигает вниз
    assert p.y > 0


def test_particle_dies_after_lifetime():
    p = Particle(0, 0, 0, 0, (1, 1, 1), 3, life=0.3)
    assert p.alive()
    p.update(0.2)
    assert p.alive()
    p.update(0.2)
    assert not p.alive()  # 0.4 > 0.3


def test_spawn_burst_count_and_alive():
    parts = spawn_burst(100, 100, (255, 220, 50), n=15, rng=random.Random(1))
    assert len(parts) == 15
    assert all(p.alive() for p in parts)


def test_spawn_burst_deterministic_with_seed():
    a = spawn_burst(0, 0, (1, 2, 3), n=8, rng=random.Random(42))
    b = spawn_burst(0, 0, (1, 2, 3), n=8, rng=random.Random(42))
    assert [(p.vx, p.vy, p.life) for p in a] == [(p.vx, p.vy, p.life) for p in b]


def test_burst_all_dead_after_enough_time():
    parts = spawn_burst(0, 0, (9, 9, 9), n=10, life=0.5, rng=random.Random(7))
    for _ in range(60):  # ~1с при 60 fps
        for p in parts:
            p.update(1 / 60)
    assert not any(p.alive() for p in parts)


def test_particle_draw_does_not_crash():
    pygame.init()
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    p = Particle(25, 25, 0, 0, (255, 100, 0), 6, life=1.0)
    p.draw(surf)  # не должно бросать
    pygame.quit()
