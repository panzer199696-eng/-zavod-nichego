"""Тесты логики наград: 3 карты из пула без повторов, попадают в колоду, валюта."""

import random

from engine.content import reward_pool_cards
from game_state.run import RunState, reward_choices


def test_reward_returns_three_cards():
    pool = reward_pool_cards()
    choices = reward_choices(pool, 3, random.Random(1))
    assert len(choices) == 3


def test_reward_has_no_duplicate_ids():
    pool = reward_pool_cards()
    for seed in range(30):
        choices = reward_choices(pool, 3, random.Random(seed))
        ids = [c.id for c in choices]
        assert len(ids) == len(set(ids)), f"дубль в наградах seed={seed}: {ids}"


def test_reward_cards_come_from_pool():
    pool = reward_pool_cards()
    pool_ids = {c.id for c in pool}
    choices = reward_choices(pool, 3, random.Random(5))
    assert all(c.id in pool_ids for c in choices)


def test_chosen_reward_card_added_to_deck():
    run = RunState.new_stazher(seed=3)
    deck_size = len(run.deck)
    choices = run.roll_reward()
    picked = choices[0]
    run.add_card(picked)
    assert len(run.deck) == deck_size + 1
    assert run.deck[-1].id == picked.id


def test_added_card_is_independent_copy():
    run = RunState.new_stazher(seed=3)
    choices = run.roll_reward()
    picked = choices[0]
    run.add_card(picked)
    # мутация исходного экземпляра не должна затрагивать копию в колоде
    in_deck = run.deck[-1]
    assert in_deck is not picked


def test_gain_currency():
    run = RunState.new_stazher(seed=1)
    run.gain_currency(25)
    run.gain_currency(60)
    assert run.currency == 85
    run.gain_currency(-10)  # отрицательное игнорируется
    assert run.currency == 85


def test_starting_deck_has_ten_cards():
    run = RunState.new_stazher(seed=1)
    assert len(run.deck) == 10


# --- Этап 3: редкости и взвешивание ---


def test_pool_has_all_three_rarities():
    from engine.models import Rarity

    rarities = {c.rarity for c in reward_pool_cards()}
    assert Rarity.COMMON in rarities
    assert Rarity.UNCOMMON in rarities
    assert Rarity.RARE in rarities


def test_common_cards_outweigh_rare_over_many_rolls():
    """Статистика: обычные карты выпадают намного чаще редких (веса работают)."""
    from collections import Counter

    from engine.models import Rarity

    counts: Counter = Counter()
    rng = random.Random(123)
    for _ in range(2000):
        for card in reward_choices(reward_pool_cards(), 1, rng):
            counts[card.rarity] += 1
    assert counts[Rarity.COMMON] > counts[Rarity.UNCOMMON] > counts[Rarity.RARE]


def test_weighted_choice_still_no_duplicates():
    pool = reward_pool_cards()
    for seed in range(50):
        choices = reward_choices(pool, 3, random.Random(seed))
        ids = [c.id for c in choices]
        assert len(ids) == len(set(ids))
