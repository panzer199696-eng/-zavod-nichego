"""Этап G «Мета-прогрессия»: валюта, разблокировки, старт-бонусы, save/load,
гейтинг пула наград. Всё headless — без UI.
"""

import json

from engine.content import KofemashinaSlomana
from game_state.meta import (
    PRICES,
    UNLOCKABLE_CARDS,
    UNLOCKABLE_RELICS,
    MetaState,
    available_card_factories,
    available_relic_classes,
)
from game_state.run import RunState


# --- валюта и покупки ---


def test_add_currency_ignores_nonpositive():
    m = MetaState()
    m.add_currency(50)
    m.add_currency(-10)
    m.add_currency(0)
    assert m.currency == 50


def test_unlock_spends_currency_and_marks_unlocked():
    m = MetaState(currency=200)
    price = PRICES["goret_na_rabote"]
    assert m.can_unlock("goret_na_rabote")
    assert m.unlock("goret_na_rabote") is True
    assert m.currency == 200 - price
    assert m.is_unlocked("goret_na_rabote")


def test_unlock_denied_without_enough_currency():
    m = MetaState(currency=10)
    assert m.can_unlock("fors_mazhor") is False
    assert m.unlock("fors_mazhor") is False
    assert m.currency == 10
    assert not m.is_unlocked("fors_mazhor")


def test_cannot_unlock_twice():
    m = MetaState(currency=1000)
    assert m.unlock("vechnyy_dedlayn") is True
    spent = 1000 - m.currency
    assert m.unlock("vechnyy_dedlayn") is False  # повторно нельзя
    assert 1000 - m.currency == spent  # валюта не списана второй раз


def test_non_catalog_item_is_always_unlocked():
    m = MetaState()
    assert m.is_unlocked("udar_po_stolu")  # обычная карта вне каталога
    assert m.is_unlockable("udar_po_stolu") is False


def test_has_bonus_only_when_purchased():
    m = MetaState(currency=1000)
    assert m.has_bonus("krepkoe_zdorovye") is False
    m.unlock("krepkoe_zdorovye")
    assert m.has_bonus("krepkoe_zdorovye") is True


# --- сериализация ---


def test_to_from_dict_roundtrip():
    m = MetaState(currency=130, unlocked={"goret_na_rabote", "skorosshivatel"})
    restored = MetaState.from_dict(m.to_dict())
    assert restored.currency == 130
    assert restored.unlocked == {"goret_na_rabote", "skorosshivatel"}


def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "meta.json"
    m = MetaState(currency=75, unlocked={"fors_mazhor"})
    m.save(path)
    loaded = MetaState.load(path)
    assert loaded.currency == 75
    assert loaded.unlocked == {"fors_mazhor"}
    # файл — валидный человекочитаемый JSON
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["currency"] == 75
    assert data["unlocked"] == ["fors_mazhor"]


def test_load_missing_file_returns_fresh(tmp_path):
    loaded = MetaState.load(tmp_path / "nope.json")
    assert loaded.currency == 0
    assert loaded.unlocked == set()


def test_load_corrupt_file_returns_fresh(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ это не json", encoding="utf-8")
    loaded = MetaState.load(path)
    assert loaded.currency == 0


# --- гейтинг пула ---


def test_locked_cards_excluded_without_unlock():
    pool_ids = {f().id for f in available_card_factories(MetaState())}
    for cid in UNLOCKABLE_CARDS:
        assert cid not in pool_ids
    # обычная карта остаётся доступной
    assert "podpis_v_uglu" in pool_ids


def test_unlocked_card_appears_in_pool():
    m = MetaState(unlocked={"fors_mazhor"})
    pool_ids = {f().id for f in available_card_factories(m)}
    assert "fors_mazhor" in pool_ids
    assert "zamorozit_smetu" not in pool_ids  # другая редкая всё ещё закрыта


def test_meta_none_means_full_pool():
    full = {f().id for f in available_card_factories(None)}
    for cid in UNLOCKABLE_CARDS:
        assert cid in full  # без меты гейтинга нет


def test_locked_relics_excluded_without_unlock():
    ids = {cls.id for cls in available_relic_classes(MetaState())}
    for rid in UNLOCKABLE_RELICS:
        assert rid not in ids
    assert "pechat_soglasovano" in ids  # базовая реликвия доступна


# --- интеграция в RunState ---


def test_run_reward_pool_respects_meta_lock():
    run = RunState.new_stazher(seed=1, meta=MetaState())
    # за много роллов заблокированные карты не должны выпасть
    seen = set()
    for _ in range(100):
        for c in run.roll_reward():
            seen.add(c.id)
    assert seen.isdisjoint(set(UNLOCKABLE_CARDS))


def test_run_relic_reward_respects_meta_lock():
    run = RunState.new_stazher(seed=1, meta=MetaState())
    seen = set()
    for _ in range(100):
        r = run.roll_relic_reward()
        if r:
            seen.add(r.id)
    assert seen.isdisjoint(set(UNLOCKABLE_RELICS))


def test_start_bonus_extra_hp():
    m = MetaState(unlocked={"krepkoe_zdorovye"})
    run = RunState.new_stazher(seed=1, meta=m)
    assert run.hero.max_hp == 85  # 80 + 5
    assert run.hero.hp == 85


def test_start_bonus_starting_relic():
    m = MetaState(unlocked={"sluzhebnyy_avtomobil"})
    run = RunState.new_stazher(seed=1, meta=m)
    assert any(isinstance(r, KofemashinaSlomana) for r in run.relics)


def test_start_bonus_fourth_reward_choice():
    m = MetaState(unlocked={"shirokiy_vybor"})
    run = RunState.new_stazher(seed=1, meta=m)
    assert run.reward_choice_count() == 4
    assert len(run.roll_reward()) == 4


def test_default_run_has_three_choices_and_no_bonuses():
    run = RunState.new_stazher(seed=1)
    assert run.reward_choice_count() == 3
    assert run.hero.max_hp == 80
    assert run.relics == []


def test_bank_currency_to_meta_transfers_and_resets():
    m = MetaState(currency=10)
    run = RunState.new_stazher(seed=1, meta=m)
    run.gain_currency(60)
    moved = run.bank_currency_to_meta()
    assert moved == 60
    assert run.currency == 0
    assert m.currency == 70


def test_bank_currency_without_meta_is_noop():
    run = RunState.new_stazher(seed=1)
    run.gain_currency(40)
    assert run.bank_currency_to_meta() == 0
    assert run.currency == 40  # не тронуто
