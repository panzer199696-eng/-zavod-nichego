"""Контент-срез Акта 1 (данными из CONCEPT.md, Часть IV/V).

Герой Стажёр, его карты, 3 обычных врага и босс «Квартальный Отчёт».
Числа — канон из концепта. Всё описано данными поверх движка.
"""

from __future__ import annotations

from engine import effects as fx
from engine.combat import (
    attack_intent,
    block_intent,
    new_enemy,
    skip_intent,
)
from engine.models import Card, CardType, Enemy, Hero, Rarity
from engine.statuses import STATUS

# ============================ КАРТЫ СТАЖЁРА ============================


def make_udar() -> Card:
    """Удар по столу — Атака, 1 энергии, 6 урона."""
    return Card(
        id="udar_po_stolu",
        name="Удар по столу",
        card_type=CardType.ATTACK,
        cost=1,
        effects=[fx.deal_damage(6)],
        description="6 урона",
    )


def make_otpiska() -> Card:
    """Отписка — Защита, 1 энергии, 5 брони."""
    return Card(
        id="otpiska",
        name="Отписка",
        card_type=CardType.DEFENSE,
        cost=1,
        effects=[fx.gain_block(5)],
        description="5 брони",
    )


def make_begotnya() -> Card:
    """Беготня — Действие, 0 энергии, тянуть 1, +1 Запал."""
    return Card(
        id="begotnya",
        name="Беготня",
        card_type=CardType.ACTION,
        cost=0,
        effects=[fx.draw_cards(1)],
        description="Тянуть 1 карту. (+1 Запал — от дешевизны)",
    )


def make_avral() -> Card:
    """Аврал — Атака, 1 энергии, 3 × Запал урона, макс 24 (кэп Запал≤8).

    Финишер: тратит Запал, сам его не начисляет.
    """
    return Card(
        id="avral",
        name="Аврал",
        card_type=CardType.ATTACK,
        cost=1,
        effects=[
            fx.scale_damage_from_status(
                STATUS.ZAPAL, multiplier=3, cap=24, consume=True
            )
        ],
        no_zapal=True,
        description="3 урона × Запал (макс 24), тратит весь Запал",
    )


def make_kofe_dlya_vseh() -> Card:
    """Кофе для всех — Схема, 0 энергии, +2 брони, +1 Запал, изгнать."""
    return Card(
        id="kofe_dlya_vseh",
        name="Кофе для всех",
        card_type=CardType.SCHEME,
        cost=0,
        effects=[fx.gain_block(2)],
        exhaust=True,
        description="+2 брони, +1 Запал, изгнать",
    )


# --- Классовые / наградные карты Стажёра (CONCEPT Часть IV/V) ---


def make_prinesi_poday() -> Card:
    """Принеси-подай — Действие, 0 энергии, 4 урона, при 3+ картах за ход — тянуть 1."""
    return Card(
        id="prinesi_poday",
        name="Принеси-подай",
        card_type=CardType.ACTION,
        cost=0,
        effects=[fx.deal_damage(4), fx.draw_if_cards_played(1, threshold=3)],
        description="4 урона. При 3+ картах за ход — тянуть 1. (+1 Запал)",
    )


def make_entuziazm() -> Card:
    """Энтузиазм — Действие, 1 энергии, следующие карты −1 энергии (Согласовано×3)."""
    return Card(
        id="entuziazm",
        name="Энтузиазм",
        card_type=CardType.ACTION,
        cost=1,
        effects=[fx.gain_status_self(STATUS.APPROVED, 3)],
        description="Следующие 3 карты стоят 0 энергии",
    )


def make_pererabotka() -> Card:
    """Переработка по-молодому — Действие, 2 энергии, 2 урона × число карт за ход."""
    return Card(
        id="pererabotka",
        name="Переработка по-молодому",
        card_type=CardType.ACTION,
        cost=2,
        effects=[fx.scale_damage_from_cards_played(2)],
        no_zapal=True,
        description="2 урона × число сыгранных карт за ход",
    )


def make_sluzhebnaya() -> Card:
    """Служебная записка — Атака, 2 энергии, 10 урона + Простой 1 врагу.

    Рефактор Этапа 3: Бюрократия на враге механически мертва (ход врага не
    тратит энергию), поэтому записка теперь вешает Простой — реальный дебаф атаки.
    """
    return Card(
        id="sluzhebnaya_zapiska",
        name="Служебная записка",
        card_type=CardType.ATTACK,
        cost=2,
        effects=[fx.deal_damage(10), fx.apply_status(STATUS.WEAKEN, 1)],
        rarity=Rarity.UNCOMMON,
        no_zapal=True,
        description="10 урона + Простой 1 (враг бьёт слабее)",
    )


def make_reglament() -> Card:
    """Регламент 5.2 — Защита, 1 энергии, 4 брони + тянуть 1."""
    return Card(
        id="reglament_5_2",
        name="Регламент 5.2",
        card_type=CardType.DEFENSE,
        cost=1,
        effects=[fx.gain_block(4), fx.draw_cards(1)],
        description="4 брони, тянуть 1 карту",
    )


def make_fors_mazhor() -> Card:
    """Форс-мажор — Атака, 3 энергии, 22 урона + 8 брони."""
    return Card(
        id="fors_mazhor",
        name="Форс-мажор",
        card_type=CardType.ATTACK,
        cost=3,
        effects=[fx.deal_damage(22), fx.gain_block(8)],
        rarity=Rarity.RARE,
        no_zapal=True,
        description="22 урона + 8 брони",
    )


def make_km2() -> Card:
    """КМ-2 — Атака, 1 энергии, урон = броня × 2 (пейофф танк-билда).

    Рефактор Этапа 3: стоимость 2→1, чтобы конвертация брони в урон была
    доступна в тот же ход, что и набор брони.
    """
    return Card(
        id="km2",
        name="КМ-2",
        card_type=CardType.ATTACK,
        cost=1,
        effects=[fx.scale_damage_from_block(2.0)],
        rarity=Rarity.UNCOMMON,
        no_zapal=True,
        description="Урон = твоя броня × 2",
    )


def make_chernaya_metka() -> Card:
    """Чёрная метка — Действие, 1 энергии, 3 урона + Простой 2 врагу.

    Рефактор Этапа 3: вместо мёртвой Бюрократии вешает Простой 2 — главный
    дешёвый контроль-инструмент (−6 к атаке врага на этот ход).
    """
    return Card(
        id="chernaya_metka",
        name="Чёрная метка",
        card_type=CardType.ACTION,
        cost=1,
        effects=[fx.deal_damage(3), fx.apply_status(STATUS.WEAKEN, 2)],
        rarity=Rarity.UNCOMMON,
        no_zapal=True,
        description="3 урона + Простой 2 (враг бьёт слабее)",
    )


def make_inicaitivnaya() -> Card:
    """Инициативная записка — Действие, 0 энергии, тянуть 1."""
    return Card(
        id="iniciativnaya",
        name="Инициативная записка",
        card_type=CardType.ACTION,
        cost=0,
        effects=[fx.draw_cards(1)],
        description="Тянуть 1 карту. (+1 Запал)",
    )


# --- Этап 3: расширение пула под архетипы (бёрст/танк/контроль/цикл) ---


def make_podpis_v_uglu() -> Card:
    """Подпись в углу — Атака, 0 энергии, 3 урона.

    Дешёвая агрессия: кормит Запал и счётчик карт за ход (Переработка/Принеси-подай).
    """
    return Card(
        id="podpis_v_uglu",
        name="Подпись в углу",
        card_type=CardType.ATTACK,
        cost=0,
        effects=[fx.deal_damage(3)],
        description="3 урона. (+1 Запал — от дешевизны)",
    )


def make_perekur() -> Card:
    """Перекур — Защита, 0 энергии, 4 брони, изгнать."""
    return Card(
        id="perekur",
        name="Перекур",
        card_type=CardType.DEFENSE,
        cost=0,
        effects=[fx.gain_block(4)],
        exhaust=True,
        description="4 брони, изгнать. (+1 Запал)",
    )


def make_soglasovat_ustno() -> Card:
    """Согласовать устно — Действие, 1 энергии, +2 Запал (enabler бёрста)."""
    return Card(
        id="soglasovat_ustno",
        name="Согласовать устно",
        card_type=CardType.ACTION,
        cost=1,
        effects=[fx.gain_status_self(STATUS.ZAPAL, 2)],
        description="+2 Запал (и ещё +1 от дешевизны)",
    )


def make_delegirovanie() -> Card:
    """Делегирование — Схема, 1 энергии, тянуть 2, изгнать (цикл-движок)."""
    return Card(
        id="delegirovanie",
        name="Делегирование",
        card_type=CardType.SCHEME,
        cost=1,
        effects=[fx.draw_cards(2)],
        rarity=Rarity.UNCOMMON,
        exhaust=True,
        description="Тянуть 2 карты, изгнать",
    )


def make_prostoy_obyekta() -> Card:
    """Простой объекта — Действие, 1 энергии, Простой 2 врагу + 2 брони (контроль)."""
    return Card(
        id="prostoy_obyekta",
        name="Простой объекта",
        card_type=CardType.ACTION,
        cost=1,
        effects=[fx.apply_status(STATUS.WEAKEN, 2), fx.gain_block(2)],
        rarity=Rarity.UNCOMMON,
        no_zapal=True,
        description="Простой 2 врагу + 2 брони",
    )


def make_zamorozit_smetu() -> Card:
    """Заморозить смету — Схема, 2 энергии, Заморозить врага на 1 ход + 6 брони, изгнать."""
    return Card(
        id="zamorozit_smetu",
        name="Заморозить смету",
        card_type=CardType.SCHEME,
        cost=2,
        effects=[fx.apply_status(STATUS.FROZEN, 1), fx.gain_block(6)],
        rarity=Rarity.RARE,
        exhaust=True,
        no_zapal=True,
        description="Враг пропускает следующую атаку + 6 брони, изгнать",
    )


def make_premiya_po_itogam() -> Card:
    """Премия по итогам — Атака, 2 энергии, 14 урона + 4 брони (редкая агрессия)."""
    return Card(
        id="premiya_po_itogam",
        name="Премия по итогам",
        card_type=CardType.ATTACK,
        cost=2,
        effects=[fx.deal_damage(14), fx.gain_block(4)],
        rarity=Rarity.RARE,
        no_zapal=True,
        description="14 урона + 4 брони",
    )


# ============================== ГЕРОИ =================================


def build_stazher() -> Hero:
    """Стажёр по Ничему — HP 80, пассив Запал + «каждая 3-я карта +1 энергии».

    Стартовая колода (10): 5×Удар, 3×Отписка, 1×Беготня, 1×Аврал.
    Маркеры пассива в строке passive читает combat.py: "stazher_energy", "zapal".
    """
    deck: list[Card] = (
        [make_udar() for _ in range(5)]
        + [make_otpiska() for _ in range(3)]
        + [make_begotnya()]
        + [make_avral()]
    )
    return Hero(
        name="Стажёр по Ничему",
        id="stazher",
        max_hp=80,
        hp=80,
        passive="stazher_energy zapal",  # маркеры пассивов
        starting_deck=deck,
    )


def build_direktor() -> Hero:
    """Директор Отсутствия — HP 90, пассив «броня не спадает на 30%».

    Стартовая колода-заглушка для Этапа 0 (полный набор — Этап 1/3).
    Ключевое для движка: block_keep_ratio = 0.3.
    """
    deck = [make_udar() for _ in range(4)] + [make_otpiska() for _ in range(4)]
    hero = Hero(
        name="Директор Отсутствия",
        id="direktor",
        max_hp=90,
        hp=90,
        passive="direktor_block",
        starting_deck=deck,
    )
    hero.block_keep_ratio = 0.3
    return hero


# ============================== ВРАГИ ================================


def _prorab_behavior(combat, enemy: Enemy, turn_index: int) -> None:
    """Прораб-самодур: каждые 3 хода +2 к атаке (ко всем attack-намерениям).

    Рост на ходах врага 3, 6, 9… (срабатывает до исполнения намерения).
    """
    if turn_index % 3 == 0:
        for intent in enemy.intents:
            if intent.kind == "attack":
                intent.value += 2
                intent.label = f"⚔ {intent.value}"


def new_prorab() -> Enemy:
    """Прораб-самодур — HP 28, атака 8 (рампа +2 каждые 3 хода)."""
    return new_enemy(
        hp=28,
        name="Прораб-самодур",
        intents=[attack_intent(8)],
        id="prorab",
        behavior=_prorab_behavior,
    )


def new_dedlayn() -> Enemy:
    """Дедлайн — HP 18, бьёт через ход (12 урона / простой)."""
    return new_enemy(
        hp=18,
        name="Дедлайн",
        intents=[attack_intent(12, "⚔ 12 «нужно было вчера»"), skip_intent()],
        id="dedlayn",
    )


def new_soglasovanie() -> Enemy:
    """Согласование — HP 35, атака 3, вешает Бюрократию каждый ход.

    Намерение — видимая атака 3 (телеграфируется ⚔3, чтобы игрок понимал,
    откуда теряет HP), а Бюрократию вешает поведение каждый ход.
    """
    enemy = new_enemy(
        hp=35,
        name="Согласование",
        intents=[attack_intent(3, "⚔ 3 «согласуем» + Бюрократия")],
        id="soglasovanie",
    )

    def _behavior(combat, e: Enemy, turn_index: int) -> None:
        # каждый ход вешает Бюрократию 1 (давление на энергию)
        combat.hero.add_status(STATUS.BUREAUCRACY, 1)
        combat._log(f"{e.name}: «нужно согласовать» — Бюрократия 1")

    enemy.behavior = _behavior
    return enemy


# ============================== БОСС ================================


def new_subpodryadchik() -> Enemy:
    """Вечный Субподрядчик — HP 22, атака 6, чередует ход иммунитета (блок)."""
    return new_enemy(
        hp=22,
        name="Вечный Субподрядчик",
        intents=[
            attack_intent(6, "⚔ 6 «мы всё сделаем»"),
            block_intent(8),
        ],
        id="subpodryadchik",
    )


def _tehnadzor_behavior(combat, enemy: Enemy, turn_index: int) -> None:
    """Технадзор: разовое Промерзание на 2-м ходу («а исполнительная есть?»).

    Промерзание (Frostbite) не имеет спада, поэтому вешаем его ОДИН раз —
    разовый налог на стоимость карт, а не вечный лок (как и Бюрократия у босса).
    """
    if turn_index == 2:
        combat.hero.add_status(STATUS.FROSTBITE, 1)
        combat._log(f"{enemy.name}: «а исполнительная есть?» — Промерзание 1")


def new_tehnadzor() -> Enemy:
    """Элита «Технадзор-выездной» — HP 55, атака 8/9, разовое Промерзание.

    Промежуточный гейт перед боссом; гарантированно даёт реликвию в награду.
    """
    return new_enemy(
        hp=55,
        name="Технадзор-выездной",
        intents=[
            attack_intent(8, "⚔ 8 «это не по СНиП»"),
            block_intent(6),
            attack_intent(9, "⚔ 9 «документация на ЭТО?»"),
        ],
        id="tehnadzor",
        behavior=_tehnadzor_behavior,
    )


# ============================== БОСС ================================


def _boss_behavior(combat, enemy: Enemy, turn_index: int) -> None:
    """Квартальный Отчёт: разовый «Баг в формуле» (Бюрократия 2) на 2-м ходу.

    Бюрократия не имеет спада, поэтому ВЕШАЕМ ЕЁ ОДИН РАЗ за бой — это разовое
    давление-«пересчёт», а не вечный энергетический лок (иначе бой Акта 1
    становится математически непроходимым). Дальше босс давит атаками/блоком.
    """
    if turn_index == 2:
        combat.hero.add_status(STATUS.BUREAUCRACY, 2)
        combat._log(f"{enemy.name}: «Баг в формуле» — Бюрократия 2")


def new_kvartalnyy_otchet() -> Enemy:
    """Босс «Квартальный Отчёт» — HP 95, фазовые намерения (атака 14 канон финала).

    Цикл: давление атаками 10/14 + блок-фаза. Разовый дебаф «Баг в формуле»
    вешается поведением (см. _boss_behavior), а не повторяется в цикле.
    """
    return new_enemy(
        hp=95,
        name="Квартальный Отчёт",
        intents=[
            attack_intent(10, "⚔ 10 «цифры не сходятся»"),
            block_intent(8),
            attack_intent(14, "⚔ 14 «пересчитай с нуля»"),
            attack_intent(10, "⚔ 10 «итоги квартала»"),
        ],
        id="boss_kvartalnyy",
        behavior=_boss_behavior,
    )


# ===================== ПУЛ НАГРАДНЫХ КАРТ СТАЖЁРА =====================

# Карты, выпадающие в награду за бой (вне стартовой колоды-дублей).
STAZHER_REWARD_POOL: list = [
    # обычные
    make_prinesi_poday,
    make_kofe_dlya_vseh,
    make_entuziazm,
    make_reglament,
    make_inicaitivnaya,
    make_podpis_v_uglu,
    make_perekur,
    make_soglasovat_ustno,
    make_pererabotka,
    # необычные
    make_sluzhebnaya,
    make_km2,
    make_chernaya_metka,
    make_delegirovanie,
    make_prostoy_obyekta,
    # редкие
    make_fors_mazhor,
    make_zamorozit_smetu,
    make_premiya_po_itogam,
]


def reward_pool_cards() -> list[Card]:
    """Свежие экземпляры всех наградных карт пула Стажёра."""
    return [factory() for factory in STAZHER_REWARD_POOL]


# ============================ РЕЛИКВИИ ===============================


class Relic:
    """Реликвия с пассивом. Хуки on_combat_start / on_turn_start —
    опциональные методы, которые вызывает движок боя (combat._apply_relics).
    """

    id: str = ""
    name: str = ""
    description: str = ""


class PechatSoglasovano(Relic):
    """Печать «согласовано» — первая карта каждого хода стоит 0 энергии."""

    id = "pechat_soglasovano"
    name = "Печать «согласовано»"
    description = "Первая карта каждого хода стоит 0 энергии"

    def on_turn_start(self, combat) -> None:
        combat.hero.add_status(STATUS.APPROVED, 1)


class DressKod(Relic):
    """Корпоративный дресс-код — броня не спадает (копится весь бой)."""

    id = "dress_kod"
    name = "Корпоративный дресс-код"
    description = "Броня не спадает между ходами (копится)"

    def on_combat_start(self, combat) -> None:
        combat.hero.block_keep_ratio = 1.0


class KofemashinaSlomana(Relic):
    """Кофемашина сломана — +3 брони в начале боя (первый ход).

    Бронь даётся в on_turn_start первого хода — ПОСЛЕ сброса брони
    reset_block_for_turn(), иначе её сразу обнулит начало хода.
    """

    id = "kofemashina"
    name = "Кофемашина сломана"
    description = "+3 брони в начале боя"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.hero.gain_block(3)


class BeydzhBezFoto(Relic):
    """Бейдж без фото (классовая Стажёра) — в первый ход +1 Запал и +1 энергии."""

    id = "beydzh_bez_foto"
    name = "Бейдж без фото"
    description = "В первый ход боя: +1 Запал и +1 энергии"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.hero.add_status(STATUS.ZAPAL, 1)
            combat.energy += 1


class NenormirovannyyGrafik(Relic):
    """Ненормированный график — в первый ход боя +1 энергии."""

    id = "nenormirovannyy_grafik"
    name = "Ненормированный график"
    description = "В первый ход боя +1 энергии"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.energy += 1


class KorporativnayaKruzhka(Relic):
    """Корпоративная кружка — в первый ход боя +2 Запал (опора бёрст-билда)."""

    id = "korporativnaya_kruzhka"
    name = "Корпоративная кружка"
    description = "В первый ход боя +2 Запал"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.hero.add_status(STATUS.ZAPAL, 2)


class TolstayaPapka(Relic):
    """Толстая папка с допусками — в первый ход боя +6 брони (опора танк-билда)."""

    id = "tolstaya_papka"
    name = "Толстая папка с допусками"
    description = "В первый ход боя +6 брони"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.hero.gain_block(6)


class ChernyySpisok(Relic):
    """Чёрный список — в начале боя вешает Простой 2 на врага (опора контроль-билда)."""

    id = "chernyy_spisok"
    name = "Чёрный список"
    description = "В начале боя враг получает Простой 2"

    def on_combat_start(self, combat) -> None:
        combat.enemy.add_status(STATUS.WEAKEN, 2)


class VtorayaSmena(Relic):
    """Вторая смена — в первый ход боя тянуть +2 карты (опора цикл-билда)."""

    id = "vtoraya_smena"
    name = "Вторая смена"
    description = "В первый ход боя тянуть +2 карты"

    def on_turn_start(self, combat) -> None:
        if combat.turn == 1:
            combat.draw(2)


class ByurokraticheskiyImmunitet(Relic):
    """Бюрократический иммунитет — каждый ход снимает Бюрократию с героя.

    Снимаем в on_turn_pre_energy — ДО расчёта энергии в _start_player_turn,
    поэтому штраф не проходит даже в заражённый ход и реликвия реально
    защищает от Согласования (которое вешает Бюрократию каждый ход).
    """

    id = "byurokraticheskiy_immunitet"
    name = "Бюрократический иммунитет"
    description = "Иммунитет к Бюрократии: снимает её каждый ход"

    def on_turn_pre_energy(self, combat) -> None:
        combat.hero.set_status(STATUS.BUREAUCRACY, 0)


# Реестр доступных реликвий (фабрики — каждый забег свежий экземпляр).
RELIC_REGISTRY: list = [
    PechatSoglasovano,
    DressKod,
    KofemashinaSlomana,
    BeydzhBezFoto,
    NenormirovannyyGrafik,
    KorporativnayaKruzhka,
    TolstayaPapka,
    ChernyySpisok,
    VtorayaSmena,
    ByurokraticheskiyImmunitet,
]


def all_relics() -> list:
    """Свежие экземпляры всех реликвий."""
    return [cls() for cls in RELIC_REGISTRY]
