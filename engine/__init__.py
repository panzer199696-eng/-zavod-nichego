"""Движок боевой логики deckbuilder'а «Ничего не построено» (Этап 0, headless).

Публичный API:
    engine.combat  — Combat, конструкторы намерений/врагов
    engine.models  — Card, Hero, Enemy, EnemyIntent, Combatant, CardType, Rarity
    engine.effects — компонуемые операции карт
    engine.statuses — STATUS, реестр статусов
    engine.content — контент-срез Акта 1 (Стажёр, карты, враги, босс)
"""

__all__ = ["combat", "models", "effects", "statuses", "content"]
