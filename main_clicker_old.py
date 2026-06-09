import pygame
import sys
import random
import math
import json
import time
import os
import traceback
import datetime
from pathlib import Path

# ─── Android-совместимость ────────────────────────────────────────────────────
_IS_ANDROID = "ANDROID_ARGUMENT" in os.environ

# Путь к сохранению: на Android — в приватный каталог приложения
try:
    from android.storage import app_storage_path as _asp  # noqa: F401

    _SAVE_DIR = Path(_asp())
except Exception:
    _SAVE_DIR = Path(__file__).parent

# ─── Константы ───────────────────────────────────────────────────────────────
W, H = 360, 640
FPS = 60
FONT_PATH = Path(__file__).parent / "fonts" / "PressStart2P-Regular.ttf"
SAVE_PATH = _SAVE_DIR / "save.json"

HEADER_H = 78
STATS_H = 18
FACTORY_Y = HEADER_H + STATS_H  # 96
FACTORY_H = 260
PANEL_Y = FACTORY_Y + FACTORY_H  # 356
TAB_H = 36
LIST_Y = PANEL_Y + TAB_H  # 392

# ─── Палитра ─────────────────────────────────────────────────────────────────
C = {
    "bg": (15, 12, 35),
    "bg2": (25, 22, 55),
    "panel": (30, 28, 65),
    "yellow": (255, 220, 50),
    "pink": (255, 100, 160),
    "cyan": (70, 220, 200),
    "orange": (255, 160, 50),
    "green": (80, 220, 120),
    "red": (220, 70, 70),
    "white": (255, 255, 255),
    "gray": (130, 130, 160),
    "purple": (180, 90, 230),
    "dark": (10, 8, 25),
    "button": (50, 45, 100),
    "btnhov": (70, 65, 130),
    "gold": (255, 200, 0),
}

# ─── Работники ────────────────────────────────────────────────────────────────
WORKERS = [
    {
        "id": "intern",
        "name": "Стажёр по Ничему",
        "desc": "Ничего не делает\nпрофессионально",
        "rate": 1,
        "base_cost": 15,
        "color": "green",
    },
    {
        "id": "manager",
        "name": "Менеджер по Пустоте",
        "desc": "Совещания о природе\nничего",
        "rate": 8,
        "base_cost": 100,
        "color": "cyan",
    },
    {
        "id": "director",
        "name": "Директор Отсутствия",
        "desc": "Его кабинет\nвсегда пуст",
        "rate": 50,
        "base_cost": 1_100,
        "color": "orange",
    },
    {
        "id": "philosopher",
        "name": "Философ-консультант",
        "desc": "Доказал что ничего\nне существует",
        "rate": 260,
        "base_cost": 12_000,
        "color": "pink",
    },
    {
        "id": "ai",
        "name": "ИИ (тоже не понял)",
        "desc": "Отчёты о полной\nбессмысленности",
        "rate": 1_400,
        "base_cost": 130_000,
        "color": "purple",
    },
    {
        "id": "quantum",
        "name": "Квантовый сотрудник",
        "desc": "Существует и нет\nодновременно",
        "rate": 8_500,
        "base_cost": 2_000_000,
        "color": "cyan",
    },
    {
        "id": "consult2",
        "name": "Консультант-консультант",
        "desc": "Консультирует\nконсультантов",
        "rate": 55_000,
        "base_cost": 25_000_000,
        "color": "yellow",
    },
    {
        "id": "committee",
        "name": "Комитет по Комитетам",
        "desc": "Утверждает регламент\nдругих комитетов",
        "rate": 450_000,
        "base_cost": 300_000_000,
        "color": "orange",
    },
    {
        "id": "restructuring",
        "name": "Отдел Реструктуризации",
        "desc": "Реструктурирует\nсам себя",
        "rate": 3_500_000,
        "base_cost": 4_000_000_000,
        "color": "red",
    },
    {
        "id": "ceo",
        "name": "Сингулярный СЕО",
        "desc": "Поглощает любой смысл\nв радиусе парсека",
        "rate": 25_000_000,
        "base_cost": 50_000_000_000,
        "color": "purple",
    },
]

# ─── Апгрейды ────────────────────────────────────────────────────────────────
UPGRADES = [
    {
        "id": "click2",
        "name": "Улучшенная Пустота",
        "desc": "Клик x2",
        "cost": 50,
        "target": "click",
        "mult": 2,
        "color": "yellow",
    },
    {
        "id": "int2",
        "name": "Курс Эффект. Лени",
        "desc": "Стажёры x2",
        "cost": 500,
        "target": "intern",
        "mult": 2,
        "color": "green",
    },
    {
        "id": "click3",
        "name": "НаноПустота™",
        "desc": "Клик x3",
        "cost": 5_000,
        "target": "click",
        "mult": 3,
        "color": "purple",
    },
    {
        "id": "mgr2",
        "name": "Тренинг по Пустоте",
        "desc": "Менеджеры x2",
        "cost": 10_000,
        "target": "manager",
        "mult": 2,
        "color": "cyan",
    },
    {
        "id": "dir2",
        "name": "MBA по Отсутствию",
        "desc": "Директора x2",
        "cost": 55_000,
        "target": "director",
        "mult": 2,
        "color": "orange",
    },
    {
        "id": "click5",
        "name": "Квантовая Пустота",
        "desc": "Клик x5",
        "cost": 100_000,
        "target": "click",
        "mult": 5,
        "color": "pink",
    },
    {
        "id": "phi2",
        "name": "Нобелевка за Ничего",
        "desc": "Философы x2",
        "cost": 500_000,
        "target": "philosopher",
        "mult": 2,
        "color": "pink",
    },
    {
        "id": "ai2",
        "name": "AGI Бессмысленности",
        "desc": "ИИ x2",
        "cost": 5_000_000,
        "target": "ai",
        "mult": 2,
        "color": "purple",
    },
    {
        "id": "quantum2",
        "name": "Суперпозиция эффект.",
        "desc": "Квантовые x2",
        "cost": 80_000_000,
        "target": "quantum",
        "mult": 2,
        "color": "cyan",
    },
    {
        "id": "consult2x",
        "name": "Метаконсалтинг",
        "desc": "Консультанты x2",
        "cost": 1_000_000_000,
        "target": "consult2",
        "mult": 2,
        "color": "yellow",
    },
    {
        "id": "committee2",
        "name": "Регламент регламента",
        "desc": "Комитеты x2",
        "cost": 12_000_000_000,
        "target": "committee",
        "mult": 2,
        "color": "orange",
    },
]

# ─── События ─────────────────────────────────────────────────────────────────
EVENTS = [
    ("Возврат товара", "Клиент вернул пустоту.\nСказал — слишком полная."),
    ("Профсоюз требует", "8-часовой рабочий день\nничегонеделания.\nМы согласились."),
    ("Инвестиции", "Инвестор вложил 0 ₽.\nОжидает возврат 0 ₽.\nСчитает это успехом."),
    ("Проверка", "Пожарная инспекция:\nогня нет.\nПроверяющий тоже исчез."),
    (
        "Регуляторы",
        "Роспотребнадзор запретил\nвоздух без лицензии.\nПереименован в\n«Атмосферный продукт»",
    ),
    (
        "Открытие науки",
        "Учёные доказали:\nничего не существует.\nАкции выросли на 300%.",
    ),
    (
        "HR-отдел",
        "Новый сотрудник спросил:\n«в чём смысл работы?»\nУволен. Некомпетентность.",
    ),
    (
        "Грант получен",
        "Грант на изучение\nпричин отсутствия причин.\nСумма гранта: ничего.",
    ),
    ("Суд", "Конкурент выпустил\n«Пустоту Плюс».\nМы подали в суд за плагиат."),
    ("Итоги квартала", "Индекс счастья\nсотрудников: ∅\nЛучший результат в истории!"),
    ("Курьерская служба", "Заказ 1000 единиц тишины.\nПосылка потерялась.\nТихо."),
    ("Совещание", "Обсудили повестку дня.\nПовестки не было.\nВсе довольны."),
    (
        "Дисциплина",
        "Стажёр случайно\nсделал что-то полезное.\nДисциплинарное взыскание.",
    ),
    ("Forbes", "Мы в топ-100 компаний,\nкоторых не существует."),
    ("Жалоба", "Жалоба: тишина\nслишком громкая.\nВозврат невозможен."),
    (
        "Новый продукт",
        "Отдел разработки предложил\nпроизводить «смысл».\nИдея отклонена.",
    ),
    ("IT-безопасность", "Хакеры украли базу.\nОна была пустой.\nМы победили."),
    ("Маркетинг", "Слоган года:\n«Ничего — это всё».\nПремия за оксюморон."),
    # Производственные травмы
    (
        "Травма от пустоты",
        "Работник споткнулся об\nотсутствие смысла на лестнице.\nБольничный: экзистенциальный\nкризис. 2 недели.",
    ),
    (
        "Ожог ничем",
        "Менеджер обжёгся\nледяной пустотой у кулера.\nКомпенсация: дырка от бублика.\nОн счастлив.",
    ),
    (
        "Перелом мотивации",
        "Стажёр уронил на себя\nпустой годовой отчёт.\nДиагноз: перелом\nкарьерных амбиций.",
    ),
    (
        "Проф. слепота",
        "Философ вгляделся в бездну.\nБездна выписала ему\nпремию за внимание.\nЗрение не вернулось.",
    ),
    # KPI-отчёты
    (
        "Перевыполнение плана",
        "Произведено на 150% меньше\nничего, чем вчера.\nАкционеры требуют\nотрицательных дивидендов.",
    ),
    (
        "Оптимизация метрик",
        "Введён KPI: количество\nнепроведённых встреч.\nМенеджеры избегают\nдруг друга профессионально.",
    ),
    (
        "Нулевой баланс",
        "Дебет сошёлся с кредитом.\nВезде ноль.\nАудиторы плакали от\nидеальной симметрии.",
    ),
    (
        "Индекс конверсии",
        "Конверсия пустоты\nв абсолютный вакуум: 0%.\nЭто абсолютный\nрекорд отрасли.",
    ),
    # Тимбилдинг
    (
        "Верёвочный курс",
        "Строили мост из\nневидимых верёвок.\nДвое упали в воображаемую\nпропасть. HR доволен.",
    ),
    (
        "Мозговой штурм",
        "Искали идеи 8 часов.\nПридумали закрыть глаза.\nИдея немедленно\nотправлена в продакшн.",
    ),
    (
        "Квест-комната",
        "Заперли в пустой\nкомнате без дверей.\nВышли победителями: комнаты\nне существует.",
    ),
    # Корпоратив
    (
        "Банкет",
        "На столах — пустые тарелки.\nТосты произносились мысленно.\nВсем было стыдно\nза то, чего не было.",
    ),
    (
        "Секретный Санта",
        "Все подарили друг другу\nничего в красивой упаковке.\nБюджет сэкономлен.\nРадость симулирована.",
    ),
    (
        "Конкурс костюмов",
        "Победил Директор Отсутствия,\nкоторый не пришёл.\nКостюм признан шедевром\nминимализма.",
    ),
    # Философские кризисы
    (
        "Синдром самозванца",
        "Стажёр понял, что\nничего не умеет.\nКризис миновал:\nон идеально нам подходит.",
    ),
    (
        "Солипсизм",
        "Главбух решил, что завода\nне существует вне сознания.\nОштрафован за попытку\nудалить реальность из 1С.",
    ),
    (
        "ИИ завис",
        "ИИ завис, вычисляя смысл\nсвоего отсутствия.\nПерезагружен кувалдой.\nОтчёт потерян навсегда.",
    ),
    (
        "Экзист. тупик",
        "Менеджер осознал: любое\nрешение бессмысленно.\nПовышен до советника по\nбессмысленным решениям.",
    ),
    # Технические сбои
    (
        "Поломка конвейера",
        "Лента остановилась:\nне могла везти пустоту\nбыстрее скорости света.\nВызвали мастера.",
    ),
    (
        "Сбой серверов",
        "Серверы упали.\nТак как там ничего не хранилось,\nпосле падения работают\nна 20% быстрее.",
    ),
    (
        "Замыкание в сети",
        "Перегорела лампочка.\nТотальная темнота дополнила\nконцепцию бренда.\nРемонт официально отменён.",
    ),
    (
        "Ошибка 404",
        "Здание исчезло с карт города.\nЛогистика не пострадала:\nмы всё равно ничего\nне отгружаем.",
    ),
    (
        "Отчёт о недост.",
        "Цель «Ничего не делать»\nпровалена: попытка была\nзасчитана как действие.\nПремия всё равно выдана.",
    ),
    (
        "Деконструкция кулера",
        "Разобрали кулер для\nпоиска источника воды.\nНашли философскую жажду.\nОформлен патент.",
    ),
    (
        "Мастер-класс",
        "Учились дышать вакуумом.\nТрое уснули.\nКоуч похвалил за глубокое\nпогружение в материал.",
    ),
]

# ─── Эпохи ────────────────────────────────────────────────────────────────────
EPOCHS = [
    {
        "threshold": 0,
        "name": "Гаражный стартап",
        "text": "Мы начали с пустого места.\nБуквально. Первый продукт —\nчистое неразбавленное отсутствие.\nРынок пока не готов.",
        "bg": (15, 12, 35),
    },
    {
        "threshold": 10_000,
        "name": "Бюрократическая инициатива",
        "text": "Привлечены первые инвестиции\nв пустоту. Нанят совет директоров\nдля обсуждения того, чего нет.\nПроцесс официально забюрократизирован.",
        "bg": (12, 18, 42),
    },
    {
        "threshold": 1_000_000,
        "name": "Философская монополия",
        "text": "Ничего не существует.\nМы запатентовали этот факт.\nЗавод вышел на IPO.\nМы монополисты рынка вакуума.",
        "bg": (22, 10, 42),
    },
    {
        "threshold": 100_000_000,
        "name": "Алгоритмический вакуум",
        "text": "ИИ оптимизировал процессы.\nПроизводим отсутствие\nна квантовом уровне.\nЧеловеческий фактор устранён.",
        "bg": (8, 22, 38),
    },
    {
        "threshold": 10_000_000_000,
        "name": "Сингулярность Бессмысленности",
        "text": "Завод схлопнулся в себя\nот переизбытка пустоты.\nДостигнут абсолютный ноль.\nАкционеры хотят большего.",
        "bg": (28, 5, 28),
    },
]

# ─── Достижения ───────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "intern50", "name": "Делегирование пустоты", "desc": "50 стажёров нанято"},
    {"id": "million", "name": "Клуб Семи Нулей", "desc": "Заработан 1 млн ничего"},
    {
        "id": "clicks1000",
        "name": "Имитация деятельности",
        "desc": "1000 кликов по заводу",
    },
    {
        "id": "dir10",
        "name": "Свита Без Королевства",
        "desc": "10 Директоров Отсутствия",
    },
    {"id": "phi_upg", "name": "Солипсист года", "desc": "Нобелевка за Ничего куплена"},
    {"id": "first_ai", "name": "Скайнет разочарован", "desc": "Первый ИИ нанят"},
    {
        "id": "popups50",
        "name": "Внимательный слушатель",
        "desc": "50 рассылок прочитано",
    },
    {"id": "nano", "name": "Наноскопические амбиции", "desc": "НаноПустота™ куплена"},
    {
        "id": "prestige1",
        "name": "Реструктуризация реальности",
        "desc": "Первый пресейв совершён",
    },
    {"id": "quantum1", "name": "Квантовый HR", "desc": "Первый Квантовый сотрудник"},
]


def _check_ach(ach_id: str, g) -> bool:
    if ach_id == "intern50":
        return g.worker_counts.get("intern", 0) >= 50
    if ach_id == "million":
        return g.total_earned >= 1_000_000
    if ach_id == "clicks1000":
        return g.total_clicks >= 1000
    if ach_id == "dir10":
        return g.worker_counts.get("director", 0) >= 10
    if ach_id == "phi_upg":
        return g.upgrades.get("phi2", False)
    if ach_id == "first_ai":
        return g.worker_counts.get("ai", 0) >= 1
    if ach_id == "popups50":
        return g.total_popups >= 50
    if ach_id == "nano":
        return g.upgrades.get("click3", False)
    if ach_id == "prestige1":
        return g.prestige_count >= 1
    if ach_id == "quantum1":
        return g.worker_counts.get("quantum", 0) >= 1
    return False


def fmt_num(n: float) -> str:
    if n >= 1_000_000_000_000:
        return f"{n / 1_000_000_000_000:.2f}трлн"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}млрд"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}млн"
    if n >= 1_000:
        return f"{n / 1_000:.1f}к"
    return f"{int(n)}"


# ─── Состояние игры ───────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.nothing = 0.0
        self.total_earned = 0.0
        self.total_clicks = 0
        self.total_popups = 0
        self.play_time = 0.0
        self.click_mults: dict = {}
        self.worker_counts = {w["id"]: 0 for w in WORKERS}
        self.worker_mults = {w["id"]: 1.0 for w in WORKERS}
        self.upgrades = {u["id"]: False for u in UPGRADES}
        self.last_event_t = 0.0
        self.next_event_dt = random.uniform(20, 40)
        self.epoch_idx = 0
        self.achievements_unlocked: set = set()
        self.prestige_count = 0
        self._pending_epoch: int | None = None
        self._pending_ach: list = []

    def prestige_mult(self) -> float:
        return 1.0 + self.prestige_count * 0.25

    def per_second(self) -> float:
        base = sum(
            self.worker_counts[w["id"]] * w["rate"] * self.worker_mults[w["id"]]
            for w in WORKERS
        )
        return base * self.prestige_mult()

    def click_value(self) -> float:
        base = max(1.0, self.per_second() * 0.1)
        for m in self.click_mults.values():
            base *= m
        return base

    def worker_cost(self, wid: str) -> int:
        base = next(w["base_cost"] for w in WORKERS if w["id"] == wid)
        return int(base * (1.15 ** self.worker_counts[wid]))

    def buy_worker(self, wid: str) -> bool:
        cost = self.worker_cost(wid)
        if self.nothing >= cost:
            self.nothing -= cost
            self.worker_counts[wid] += 1
            return True
        return False

    def buy_upgrade(self, uid: str) -> bool:
        upg = next(u for u in UPGRADES if u["id"] == uid)
        if self.upgrades[uid] or self.nothing < upg["cost"]:
            return False
        self.nothing -= upg["cost"]
        self.upgrades[uid] = True
        if upg["target"] == "click":
            self.click_mults[uid] = upg["mult"]
        else:
            self.worker_mults[upg["target"]] *= upg["mult"]
        return True

    def prestige_threshold(self) -> float:
        return 1_000_000_000 * (2**self.prestige_count)

    def do_prestige(self):
        self.prestige_count += 1
        self.nothing = 0.0
        self.total_earned = 0.0
        self.total_clicks = 0
        self.click_mults = {}
        self.worker_counts = {w["id"]: 0 for w in WORKERS}
        self.worker_mults = {w["id"]: 1.0 for w in WORKERS}
        self.upgrades = {u["id"]: False for u in UPGRADES}
        self.epoch_idx = 0
        self.last_event_t = 0.0
        self.next_event_dt = random.uniform(20, 40)

    def update(self, dt: float, now: float):
        self.play_time += dt
        gain = self.per_second() * dt
        self.nothing += gain
        self.total_earned += gain

        # Событие
        event_out = None
        if now - self.last_event_t > self.next_event_dt:
            self.last_event_t = now
            self.next_event_dt = random.uniform(25, 55)
            self.total_popups += 1
            event_out = random.choice(EVENTS)

        # Эпоха
        self._pending_epoch = None
        for i in range(len(EPOCHS) - 1, -1, -1):
            if self.total_earned >= EPOCHS[i]["threshold"] and i > self.epoch_idx:
                self.epoch_idx = i
                self._pending_epoch = i
                break

        # Достижения
        self._pending_ach = []
        for ach in ACHIEVEMENTS:
            if ach["id"] not in self.achievements_unlocked and _check_ach(
                ach["id"], self
            ):
                self.achievements_unlocked.add(ach["id"])
                self._pending_ach.append(ach)

        return event_out

    def do_click(self) -> float:
        v = self.click_value()
        self.nothing += v
        self.total_earned += v
        self.total_clicks += 1
        return v

    def save(self):
        SAVE_PATH.write_text(
            json.dumps(
                {
                    "nothing": self.nothing,
                    "total_earned": self.total_earned,
                    "total_clicks": self.total_clicks,
                    "total_popups": self.total_popups,
                    "play_time": self.play_time,
                    "click_mults": self.click_mults,
                    "worker_counts": self.worker_counts,
                    "worker_mults": self.worker_mults,
                    "upgrades": self.upgrades,
                    "epoch_idx": self.epoch_idx,
                    "achievements_unlocked": list(self.achievements_unlocked),
                    "prestige_count": self.prestige_count,
                    "save_time": time.time(),
                }
            )
        )

    def load(self):
        if not SAVE_PATH.exists():
            return
        try:
            d = json.loads(SAVE_PATH.read_text())
            self.nothing = d.get("nothing", 0)
            self.total_earned = d.get("total_earned", 0)
            self.total_clicks = d.get("total_clicks", 0)
            self.total_popups = d.get("total_popups", 0)
            self.play_time = d.get("play_time", 0)
            self.click_mults = d.get("click_mults", {})
            self.worker_counts = {**self.worker_counts, **d.get("worker_counts", {})}
            self.worker_mults = {**self.worker_mults, **d.get("worker_mults", {})}
            self.upgrades = {**self.upgrades, **d.get("upgrades", {})}
            self.epoch_idx = d.get("epoch_idx", 0)
            self.achievements_unlocked = set(d.get("achievements_unlocked", []))
            self.prestige_count = d.get("prestige_count", 0)
            # Офлайн-прогресс
            saved_t = d.get("save_time")
            if saved_t:
                elapsed = min(time.time() - saved_t, 28800)  # max 8 часов
                if elapsed > 5:
                    offline_gain = self.per_second() * elapsed
                    self.nothing += offline_gain
                    self.total_earned += offline_gain
                    return offline_gain
        except Exception:
            pass
        return None


# ─── Частицы ─────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, text, color):
        self.x, self.y = float(x), float(y)
        self.vy = -random.uniform(50, 110)
        self.vx = random.uniform(-30, 30)
        self.life = 1.4
        self.text = text
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 50 * dt
        self.life -= dt
        return self.life > 0


# ─── Пиксельные иконки работников ────────────────────────────────────────────
def draw_worker_icon(surf, x, y, worker_id, color):
    c = color

    if worker_id == "intern":
        pygame.draw.rect(surf, c, (x + 10, y + 4, 16, 14), border_radius=3)
        pygame.draw.rect(surf, C["dark"], (x + 14, y + 8, 4, 4))
        pygame.draw.rect(surf, C["dark"], (x + 20, y + 8, 4, 4))
        pygame.draw.rect(surf, c, (x + 12, y + 18, 12, 14), border_radius=2)
        pygame.draw.rect(surf, C["white"], (x + 16, y + 6, 4, 2))
        pygame.draw.rect(surf, C["white"], (x + 18, y + 8, 2, 4))
        pygame.draw.rect(surf, C["white"], (x + 16, y + 12, 2, 2))

    elif worker_id == "manager":
        pygame.draw.rect(surf, c, (x + 10, y + 4, 16, 14), border_radius=3)
        pygame.draw.rect(surf, C["dark"], (x + 13, y + 8, 4, 4))
        pygame.draw.rect(surf, C["dark"], (x + 19, y + 8, 4, 4))
        pygame.draw.rect(surf, c, (x + 12, y + 18, 12, 14), border_radius=2)
        pygame.draw.polygon(
            surf,
            C["yellow"],
            [(x + 17, y + 18), (x + 15, y + 24), (x + 18, y + 30), (x + 21, y + 24)],
        )

    elif worker_id == "director":
        pygame.draw.rect(surf, c, (x + 6, y + 16, 24, 14), border_radius=2)
        pygame.draw.rect(surf, c, (x + 6, y + 4, 24, 14), border_radius=2)
        pygame.draw.rect(surf, c, (x + 6, y + 28, 4, 8))
        pygame.draw.rect(surf, c, (x + 26, y + 28, 4, 8))
        pygame.draw.ellipse(surf, C["dark"], (x + 12, y + 18, 12, 8))

    elif worker_id == "philosopher":
        pygame.draw.rect(surf, c, (x + 10, y + 4, 16, 14), border_radius=3)
        pygame.draw.rect(surf, C["dark"], (x + 13, y + 8, 4, 4))
        pygame.draw.rect(surf, C["dark"], (x + 20, y + 8, 4, 4))
        pygame.draw.rect(surf, c, (x + 12, y + 18, 12, 14), border_radius=2)
        pygame.draw.rect(surf, c, (x + 4, y + 20, 12, 4))
        pygame.draw.rect(surf, c, (x + 4, y + 14, 4, 8))
        pygame.draw.circle(surf, C["white"], (x + 28, y + 8), 3)
        pygame.draw.circle(surf, C["white"], (x + 32, y + 5), 4)
        pygame.draw.circle(surf, C["white"], (x + 28, y + 3), 3)

    elif worker_id == "ai":
        pygame.draw.rect(surf, c, (x + 8, y + 8, 20, 20), border_radius=2)
        pygame.draw.rect(surf, C["dark"], (x + 11, y + 11, 14, 14))
        for i in range(3):
            pygame.draw.rect(surf, c, (x + 11 + i * 5, y + 4, 3, 5))
            pygame.draw.rect(surf, c, (x + 11 + i * 5, y + 27, 3, 5))
            pygame.draw.rect(surf, c, (x + 4, y + 11 + i * 5, 5, 3))
            pygame.draw.rect(surf, c, (x + 27, y + 11 + i * 5, 5, 3))
        pygame.draw.circle(surf, C["cyan"], (x + 18, y + 18), 4)
        pygame.draw.circle(surf, C["dark"], (x + 18, y + 18), 2)

    elif worker_id == "quantum":
        # Пунктирный силуэт человека (существует/не существует)
        for i in range(0, 14, 4):
            pygame.draw.rect(surf, c, (x + 10 + i, y + 4, 2, 14))  # пунктир головы
        pygame.draw.rect(surf, c, (x + 12, y + 18, 12, 14), border_radius=2)
        pygame.draw.circle(surf, C["white"], (x + 30, y + 6), 5)  # символ ∞ упрощённый
        pygame.draw.circle(surf, C["white"], (x + 30, y + 6), 3)
        pygame.draw.rect(surf, C["dark"], (x + 28, y + 4, 4, 4))

    elif worker_id == "consult2":
        # Человек с указкой у флипчарта
        pygame.draw.rect(surf, c, (x + 2, y + 4, 14, 12), border_radius=2)  # флипчарт
        pygame.draw.rect(surf, C["dark"], (x + 3, y + 5, 12, 9))  # экран
        pygame.draw.line(
            surf, c, (x + 9, y + 16), (x + 9, y + 20), 2
        )  # ножка флипчарта
        pygame.draw.rect(surf, c, (x + 22, y + 6, 10, 10), border_radius=2)  # голова
        pygame.draw.rect(surf, c, (x + 20, y + 16, 12, 10), border_radius=2)  # тело
        pygame.draw.line(
            surf, C["yellow"], (x + 16, y + 14), (x + 21, y + 10), 2
        )  # указка

    elif worker_id == "committee":
        # Круглый стол + пустые кресла (только контуры)
        pygame.draw.ellipse(surf, c, (x + 8, y + 12, 20, 12))
        pygame.draw.ellipse(surf, C["dark"], (x + 10, y + 14, 16, 8))
        for i, (cx2, cy2) in enumerate(
            [(x + 4, y + 6), (x + 18, y + 4), (x + 28, y + 8)]
        ):
            pygame.draw.rect(surf, c, (cx2, cy2, 8, 10), 1, border_radius=2)
        pygame.draw.rect(surf, c, (x + 10, y + 24, 4, 8))
        pygame.draw.rect(surf, c, (x + 22, y + 24, 4, 8))

    elif worker_id == "restructuring":
        # Уроборос из стрелок-оргсхемы
        cx2, cy2, r = x + 18, y + 18, 12
        for i in range(4):
            a = i * math.pi / 2
            px = int(cx2 + math.cos(a) * r)
            py = int(cy2 + math.sin(a) * r)
            pygame.draw.rect(surf, c, (px - 3, py - 3, 6, 6), border_radius=1)
        for i in range(4):
            a1 = i * math.pi / 2 + 0.3
            a2 = a1 + math.pi / 2 - 0.6
            p1 = (int(cx2 + math.cos(a1) * r), int(cy2 + math.sin(a1) * r))
            p2 = (int(cx2 + math.cos(a2) * r), int(cy2 + math.sin(a2) * r))
            pygame.draw.line(surf, c, p1, p2, 2)
        pygame.draw.circle(surf, C["dark"], (cx2, cy2), 4)

    elif worker_id == "ceo":
        # Чёрная дыра с ореолом + цилиндр
        cx2, cy2 = x + 18, y + 20
        pygame.draw.circle(surf, c, (cx2, cy2), 12)
        pygame.draw.circle(surf, (0, 0, 0), (cx2, cy2), 8)
        # цилиндр-шляпа
        pygame.draw.rect(surf, c, (cx2 - 6, y + 4, 12, 8), border_radius=1)
        pygame.draw.rect(surf, c, (cx2 - 8, y + 10, 16, 3))


# ─── Завод ────────────────────────────────────────────────────────────────────
class Factory:
    # Детерминированные позиции — генерируются один раз, не мерцают
    _STARS = [
        (
            int(s * 7919) % 348 + 6,
            int(s * 4001) % 110 + 4,
            (s * 0.618033) % (math.pi * 2),
        )
        for s in range(48)
    ]
    _GRASS = [(int(g * 2903) % 338 + 11, 4 + (g * 17) % 7) for g in range(55)]
    _FENCE_POSTS = list(range(6, 354, 22))

    def __init__(self):
        self.smoke = []
        self.t = 0.0
        self.shake = 0.0
        self.squash = 0.0
        self.conveyor_x = 0.0
        self.kpi_val = random.uniform(40, 80)
        self.kpi_dir = -1
        self.glitch = 0.0

    def click_fx(self):
        self.shake = 0.22
        self.squash = 1.0

    def epoch_glitch(self):
        self.glitch = 0.4

    def update(self, dt, ps: float, epoch_idx: int):
        self.t += dt
        self.shake = max(0.0, self.shake - dt * 4)
        self.squash = max(0.0, self.squash - dt * 6)
        self.glitch = max(0.0, self.glitch - dt * 2)

        # Конвейер
        speed = min(80, 10 + ps * 0.005)
        self.conveyor_x = (self.conveyor_x + speed * dt) % 60

        # KPI ползёт вниз, иногда делает ложный скачок вверх
        self.kpi_val += self.kpi_dir * dt * 3
        if self.kpi_val < 2:
            self.kpi_val = random.uniform(35, 70)  # ложный отскок
        if random.random() < 0.003:
            self.kpi_val = min(98, self.kpi_val + random.uniform(10, 30))

        # Дым
        rate = min(12, 0.5 + ps * 0.04)
        if random.random() < rate * dt:
            # выбираем одну из трёх труб: x=62+9, x=115+12, x=235+9
            pipe_cx = random.choice([71, 127, 244])
            self.smoke.append(
                [
                    float(pipe_cx + random.uniform(-4, 4)),
                    float(FACTORY_Y + 28),
                    random.randint(4, 9),
                    255,
                    random.uniform(-28, -52),
                ]
            )
        new = []
        for s in self.smoke:
            s[1] += s[4] * dt
            s[3] -= 180 * dt
            s[2] += 2.5 * dt
            if s[3] > 0:
                new.append(s)
        self.smoke = new

    def draw(self, surf, ps: float, epoch_idx: int):
        y0 = FACTORY_Y
        sq = self.squash * 0.08
        ox = int(math.sin(self.t * 22) * 3 * self.shake)
        fw, fh = 360, FACTORY_H  # полная ширина экрана

        fsuf = pygame.Surface((fw, fh), pygame.SRCALPHA)
        t = self.t

        # ── 1. Ночное небо ────────────────────────────────────────────────────
        sky_top = [(8, 6, 32), (10, 7, 40), (12, 10, 55), (20, 6, 45), (35, 5, 55)][
            min(epoch_idx, 4)
        ]
        sky_bot = [(28, 18, 62), (22, 26, 70), (42, 14, 72), (18, 28, 65), (55, 8, 60)][
            min(epoch_idx, 4)
        ]
        sky_h = 115  # высота неба над зданием
        for row in range(sky_h):
            k = row / sky_h
            rc = tuple(
                int(sky_top[i] + (sky_bot[i] - sky_top[i]) * k) for i in range(3)
            )
            pygame.draw.line(fsuf, rc, (0, row), (fw, row))

        # Луна
        moon_x, moon_y = 310, 28
        glow_s = pygame.Surface((56, 56), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (255, 240, 180, 35), (28, 28), 28)
        pygame.draw.circle(glow_s, (255, 240, 180, 50), (28, 28), 20)
        fsuf.blit(glow_s, (moon_x - 28, moon_y - 28))
        pygame.draw.circle(fsuf, (235, 228, 180), (moon_x, moon_y), 14)
        # кратеры
        pygame.draw.circle(fsuf, (210, 200, 155), (moon_x - 4, moon_y - 3), 4)
        pygame.draw.circle(fsuf, (210, 200, 155), (moon_x + 5, moon_y + 4), 3)
        pygame.draw.circle(fsuf, (220, 212, 170), (moon_x - 2, moon_y + 6), 2)

        # Звёзды (мерцание по фазе)
        for sx, sy, phase in self._STARS:
            if sy >= sky_h:
                continue
            bright = int(160 + 95 * math.sin(t * 1.3 + phase))
            r_s = 1 if (int(phase * 7) % 3 == 0) else 2
            tmp_s = pygame.Surface((r_s * 2, r_s * 2), pygame.SRCALPHA)
            pygame.draw.circle(tmp_s, (bright, bright, bright, bright), (r_s, r_s), r_s)
            fsuf.blit(tmp_s, (sx - r_s, sy - r_s))

        # ── 2. Силуэты деревьев на горизонте ──────────────────────────────────
        tree_col = (18, 14, 40)
        for tx2 in range(0, fw, 28):
            th2 = 24 + (tx2 * 17) % 20
            # ствол
            pygame.draw.rect(fsuf, tree_col, (tx2 + 11, sky_h - th2 + 14, 6, th2))
            # крона — 3 треугольника
            for ti in range(3):
                base = 20 - ti * 4
                top_y = sky_h - th2 - ti * 9 + 14
                pts_t = [
                    (tx2 + 14, top_y),
                    (tx2 + 14 - base, top_y + 14),
                    (tx2 + 14 + base, top_y + 14),
                ]
                pygame.draw.polygon(fsuf, tree_col, pts_t)

        # ── 3. Трубы с кирпичной текстурой ────────────────────────────────────
        pipe_defs = [(62, 18, 85), (115, 24, 98), (235, 19, 72)]
        pipe_base_cols = [
            [(100, 58, 52), (78, 42, 38)],  # epoch 0-1: терракота
            [(85, 52, 100), (65, 38, 78)],  # epoch 2-3: пурпурный
            [(140, 40, 160), (105, 28, 120)],  # epoch 4+: неон
        ]
        pidx = 0 if epoch_idx < 2 else (1 if epoch_idx < 4 else 2)
        for px2, pw2, ph2 in pipe_defs:
            py2_base = sky_h - ph2
            pc_main = pipe_base_cols[pidx][0]
            pc_dark = pipe_base_cols[pidx][1]
            # тело трубы
            pygame.draw.rect(fsuf, pc_main, (px2, py2_base, pw2, ph2))
            # кирпичные полосы
            for bi in range(ph2 // 7):
                stripe_y = py2_base + bi * 7 + (1 if bi % 2 == 0 else 4)
                pygame.draw.rect(fsuf, pc_dark, (px2, stripe_y, pw2, 2))
            # световые блик (левый край)
            pygame.draw.rect(
                fsuf, tuple(min(255, c + 40) for c in pc_main), (px2, py2_base, 3, ph2)
            )
            # тень (правый край)
            pygame.draw.rect(
                fsuf,
                tuple(max(0, c - 30) for c in pc_dark),
                (px2 + pw2 - 3, py2_base, 3, ph2),
            )
            # металлическое кольцо-ободок внизу трубы
            ring_y = py2_base + ph2 - 10
            pygame.draw.rect(
                fsuf, (80, 78, 88), (px2 - 4, ring_y, pw2 + 8, 8), border_radius=2
            )
            pygame.draw.rect(
                fsuf, (110, 108, 118), (px2 - 4, ring_y, pw2 + 8, 3), border_radius=2
            )
            # шапка трубы
            pygame.draw.rect(
                fsuf,
                (60, 58, 70),
                (px2 - 5, py2_base - 6, pw2 + 10, 7),
                border_radius=1,
            )
            pygame.draw.rect(
                fsuf,
                (90, 88, 100),
                (px2 - 5, py2_base - 6, pw2 + 10, 3),
                border_radius=1,
            )

        # ── 4. Крыша и зубцы ──────────────────────────────────────────────────
        roof_y = sky_h
        roof_col = (55, 50, 38)  # тёмно-коричневая черепица
        roof_dark = (38, 34, 25)
        pygame.draw.rect(fsuf, roof_dark, (28, roof_y, 304, 14))  # навес
        pygame.draw.rect(fsuf, roof_col, (28, roof_y, 304, 10))
        pygame.draw.rect(fsuf, (75, 68, 52), (28, roof_y, 304, 3))  # бликовая линия
        # Зубцы (мерлоны)
        for mx in range(36, 320, 20):
            pygame.draw.rect(fsuf, roof_col, (mx, roof_y - 10, 12, 12))
            pygame.draw.rect(fsuf, (75, 68, 52), (mx, roof_y - 10, 12, 2))

        # ── 5. Стены здания с кирпичным паттерном ─────────────────────────────
        wall_y = roof_y + 14
        wall_h = 130
        wall_cols = [
            (72, 55, 48),  # тёплая кирпичная кладка
            (60, 48, 72),  # фиолетовая кирпичная кладка
            (80, 40, 56),  # алая кирпичная кладка
            (45, 55, 80),  # синеватая кирпичная кладка
            (90, 25, 90),  # пурпурно-неоновая
        ]
        brick_col = wall_cols[min(epoch_idx, 4)]
        brick_dark = tuple(max(0, c - 22) for c in brick_col)
        brick_hi = tuple(min(255, c + 18) for c in brick_col)
        pygame.draw.rect(fsuf, brick_col, (28, wall_y, 304, wall_h))
        # кирпичи рядами
        bh = 10  # высота ряда
        for row in range(wall_h // bh + 1):
            ry = wall_y + row * bh
            offset_x = 15 if row % 2 == 0 else 0
            pygame.draw.line(fsuf, brick_dark, (28, ry), (332, ry), 1)
            for cx3 in range(28 - offset_x, 332, 30):
                pygame.draw.line(
                    fsuf,
                    brick_dark,
                    (cx3, max(wall_y, ry)),
                    (cx3, min(wall_y + wall_h, ry + bh)),
                    1,
                )
            pygame.draw.line(fsuf, brick_hi, (28, ry + 1), (332, ry + 1), 1)
        # Тень от крыши на стене
        shadow = pygame.Surface((304, 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        fsuf.blit(shadow, (28, wall_y))
        # Боковые тени
        shade_l = pygame.Surface((6, wall_h), pygame.SRCALPHA)
        shade_l.fill((0, 0, 0, 55))
        shade_r = pygame.Surface((6, wall_h), pygame.SRCALPHA)
        shade_r.fill((0, 0, 0, 40))
        fsuf.blit(shade_l, (28, wall_y))
        fsuf.blit(shade_r, (326, wall_y))

        # ── 6. Флаг на флагштоке ──────────────────────────────────────────────
        pole_x, pole_y = 50, roof_y - 38
        pygame.draw.line(fsuf, (150, 148, 140), (pole_x, pole_y), (pole_x, roof_y), 2)
        flag_colors = [C["yellow"], C["cyan"], C["orange"], C["pink"], C["purple"]]
        fc = flag_colors[min(epoch_idx, 4)]
        # Волнистый флаг (полигон с sin-смещением точек)
        flag_pts = []
        flen = 38
        for fi in range(flen + 1):
            wave = math.sin(t * 4 + fi * 0.28) * 4 * (fi / flen)
            flag_pts.append((pole_x + 1 + fi, pole_y + wave))
        for fi in range(flen, -1, -1):
            wave = math.sin(t * 4 + fi * 0.28) * 4 * (fi / flen)
            flag_pts.append((pole_x + 1 + fi, pole_y + 10 + wave))
        pygame.draw.polygon(fsuf, fc, flag_pts)
        # полоска на флаге
        flag_stripe = []
        for fi in range(flen + 1):
            wave = math.sin(t * 4 + fi * 0.28) * 4 * (fi / flen) + 4
            flag_stripe.append((pole_x + 1 + fi, pole_y + wave))
        if len(flag_stripe) >= 2:
            pygame.draw.lines(
                fsuf, tuple(max(0, c - 60) for c in fc), False, flag_stripe, 1
            )

        # ── 7. Антенна с мигающим огнём ───────────────────────────────────────
        ant_x = 290
        pygame.draw.line(
            fsuf, (120, 118, 130), (ant_x, roof_y - 42), (ant_x, roof_y), 2
        )
        pygame.draw.line(
            fsuf, (100, 98, 110), (ant_x - 8, roof_y - 30), (ant_x + 8, roof_y - 30), 1
        )
        pygame.draw.line(
            fsuf, (100, 98, 110), (ant_x - 5, roof_y - 20), (ant_x + 5, roof_y - 20), 1
        )
        # мигающий красный огонь
        if int(t * 2) % 2 == 0:
            glow_a = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_a, (255, 60, 60, 120), (6, 6), 6)
            fsuf.blit(glow_a, (ant_x - 6, roof_y - 48))
            pygame.draw.circle(fsuf, (255, 80, 80), (ant_x, roof_y - 42), 2)

        # ── 8. Две шестерёнки на крыше ────────────────────────────────────────
        def draw_gear(suf, gx4, gy4, gr4, teeth, speed, col4):
            pygame.draw.circle(suf, col4, (gx4, gy4), gr4)
            inner_col = tuple(max(0, c - 35) for c in col4)
            pygame.draw.circle(suf, inner_col, (gx4, gy4), gr4 - 4)
            pygame.draw.circle(suf, col4, (gx4, gy4), gr4 - 8)
            pygame.draw.circle(suf, (10, 8, 25), (gx4, gy4), 3)
            for i in range(teeth):
                a4 = t * speed + i * (math.pi * 2 / teeth)
                tx4 = int(gx4 + math.cos(a4) * gr4)
                ty4 = int(gy4 + math.sin(a4) * gr4)
                pygame.draw.circle(suf, col4, (tx4, ty4), 4)

        gear_col = (95, 92, 108) if epoch_idx < 4 else (140, 60, 200)
        draw_gear(fsuf, 178, roof_y - 4, 14, 7, 1.1, gear_col)
        draw_gear(fsuf, 204, roof_y - 4, 10, 5, -1.54, gear_col)

        # ── 9. Вывеска (3D-тень + лампочки) ───────────────────────────────────
        sign_x, sign_y = 55, wall_y + 8
        sign_w, sign_h = 190, 24
        # 3D-тень
        pygame.draw.rect(
            fsuf, (10, 8, 20), (sign_x + 4, sign_y + 4, sign_w, sign_h), border_radius=4
        )
        sign_bg = [
            (40, 28, 14),
            (30, 22, 48),
            (48, 14, 30),
            (20, 32, 50),
            (55, 10, 55),
        ][min(epoch_idx, 4)]
        pygame.draw.rect(
            fsuf, sign_bg, (sign_x, sign_y, sign_w, sign_h), border_radius=4
        )
        border_sc = [C["yellow"], C["cyan"], C["orange"], C["pink"], C["purple"]][
            min(epoch_idx, 4)
        ]
        pygame.draw.rect(
            fsuf, border_sc, (sign_x, sign_y, sign_w, sign_h), 2, border_radius=4
        )
        # лампочки по нижнему краю вывески
        bulb_cols = [C["yellow"], C["white"], C["cyan"], C["orange"]]
        for bi2, bx2 in enumerate(range(sign_x + 8, sign_x + sign_w - 4, 16)):
            on = (int(t * 3) + bi2) % 4 != 0
            bc = bulb_cols[bi2 % 4] if on else (40, 40, 40)
            pygame.draw.circle(fsuf, bc, (bx2, sign_y + sign_h - 4), 3)
            if on:
                glow_b = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_b, (*bc, 60), (5, 5), 5)
                fsuf.blit(glow_b, (bx2 - 5, sign_y + sign_h - 9))

        # ── 10. Пять окон с рамками и сценами ─────────────────────────────────
        win_defs = [
            (68, wall_y + 28, "paper"),
            (120, wall_y + 28, "headdesk"),
            (178, wall_y + 28, "blink"),
            (240, wall_y + 28, "stare"),
            (95, wall_y + 76, "sleep"),
        ]
        win_glow_cols = [C["yellow"], C["cyan"], C["orange"], C["pink"], C["yellow"]]
        for wi, (wx3, wy3, scene) in enumerate(win_defs):
            ww3, wh3 = 34, 28
            # внешнее свечение
            glow_wnd = pygame.Surface((ww3 + 12, wh3 + 12), pygame.SRCALPHA)
            pulse3 = abs(math.sin(t * 1.8 + wi * 1.1)) * 0.4 + 0.6
            gc = win_glow_cols[wi]
            ga = int(60 * pulse3)
            pygame.draw.rect(
                glow_wnd, (*gc, ga), (0, 0, ww3 + 12, wh3 + 12), border_radius=6
            )
            fsuf.blit(glow_wnd, (wx3 - 6, wy3 - 6))
            # деревянная рама
            pygame.draw.rect(
                fsuf,
                (82, 52, 28),
                (wx3 - 3, wy3 - 3, ww3 + 6, wh3 + 6),
                border_radius=3,
            )
            # стекло (тёмный фон)
            glass_col = tuple(int(c * 0.25 + pulse3 * 20) for c in gc)
            pygame.draw.rect(fsuf, glass_col, (wx3, wy3, ww3, wh3))
            # диагональный блик на стекле
            pygame.draw.line(
                fsuf, (200, 220, 255), (wx3 + 2, wy3 + 2), (wx3 + 10, wy3 + 10), 1
            )
            pygame.draw.line(
                fsuf, (180, 200, 240), (wx3 + 14, wy3 + 2), (wx3 + 18, wy3 + 6), 1
            )
            # перекрестье рамы
            pygame.draw.line(
                fsuf,
                (82, 52, 28),
                (wx3 + ww3 // 2, wy3),
                (wx3 + ww3 // 2, wy3 + wh3),
                1,
            )
            pygame.draw.line(
                fsuf,
                (82, 52, 28),
                (wx3, wy3 + wh3 // 2),
                (wx3 + ww3, wy3 + wh3 // 2),
                1,
            )
            # сцена внутри
            self._draw_window_scene(fsuf, wx3, wy3, scene)

        # ── 11. Дверь с панелями и ручкой ─────────────────────────────────────
        door_x, door_y = 152, wall_y + wall_h - 44
        # деревянная рама двери
        pygame.draw.rect(
            fsuf, (62, 38, 18), (door_x - 4, door_y, 44, 44), border_radius=2
        )
        # левая панель
        pygame.draw.rect(
            fsuf, (30, 22, 10), (door_x, door_y + 2, 18, 20), border_radius=1
        )
        pygame.draw.rect(
            fsuf, (45, 32, 15), (door_x, door_y + 2, 18, 20), 1, border_radius=1
        )
        # правая панель
        pygame.draw.rect(
            fsuf, (30, 22, 10), (door_x + 20, door_y + 2, 16, 20), border_radius=1
        )
        pygame.draw.rect(
            fsuf, (45, 32, 15), (door_x + 20, door_y + 2, 16, 20), 1, border_radius=1
        )
        # нижняя панель на всю ширину
        pygame.draw.rect(
            fsuf, (30, 22, 10), (door_x, door_y + 24, 36, 18), border_radius=1
        )
        # золотая ручка
        pygame.draw.circle(fsuf, C["gold"], (door_x + 32, door_y + 16), 3)
        pygame.draw.circle(fsuf, (200, 160, 0), (door_x + 32, door_y + 16), 2)
        # пятно света от двери на земле
        light_patch = pygame.Surface((40, 8), pygame.SRCALPHA)
        light_patch.fill((255, 230, 150, 30))
        fsuf.blit(light_patch, (door_x - 2, wall_y + wall_h - 6))

        # ── 12. KPI-табло ──────────────────────────────────────────────────────
        self._draw_kpi(fsuf, 204, wall_y + 66)

        # ── 13. Конвейер ──────────────────────────────────────────────────────
        conv_y = wall_y + wall_h
        self._draw_conveyor(fsuf, 28, conv_y, 304, epoch_idx)

        # ── 14. Земля + трава ─────────────────────────────────────────────────
        ground_y = conv_y + 12
        pygame.draw.rect(fsuf, (35, 50, 28), (0, ground_y, fw, fh - ground_y))
        pygame.draw.rect(fsuf, (48, 68, 34), (0, ground_y, fw, 5))
        # травинки
        for gx5, gh5 in self._GRASS:
            pygame.draw.line(
                fsuf,
                (60, 85, 40),
                (gx5, ground_y + 4),
                (gx5 + 1, ground_y + 4 - gh5),
                1,
            )

        # ── 15. Деревянный забор ──────────────────────────────────────────────
        fence_y = ground_y + 2
        # горизонтальные планки
        pygame.draw.rect(fsuf, (95, 62, 32), (0, fence_y + 6, fw, 4))
        pygame.draw.rect(fsuf, (110, 74, 38), (0, fence_y + 6, fw, 1))
        pygame.draw.rect(fsuf, (95, 62, 32), (0, fence_y + 13, fw, 4))
        pygame.draw.rect(fsuf, (110, 74, 38), (0, fence_y + 13, fw, 1))
        # столбики с заострённым верхом
        for fp in self._FENCE_POSTS:
            # столбик
            pygame.draw.rect(fsuf, (80, 50, 24), (fp, fence_y, 8, 22))
            # блик
            pygame.draw.rect(fsuf, (115, 76, 40), (fp, fence_y, 2, 22))
            # тень
            pygame.draw.rect(fsuf, (60, 36, 16), (fp + 6, fence_y, 2, 22))
            # заострённый верх (треугольник)
            pygame.draw.polygon(
                fsuf,
                (95, 62, 32),
                [(fp + 4, fence_y - 6), (fp, fence_y + 2), (fp + 8, fence_y + 2)],
            )
            pygame.draw.polygon(
                fsuf,
                (110, 74, 38),
                [(fp + 4, fence_y - 6), (fp, fence_y + 2), (fp + 2, fence_y + 2)],
            )

        # ── 16. Маленькая табличка у входа ────────────────────────────────────
        smx, smy = door_x - 30, wall_y + wall_h - 18
        pygame.draw.rect(fsuf, (42, 30, 14), (smx, smy, 24, 12), border_radius=1)
        pygame.draw.rect(fsuf, C["yellow"], (smx, smy, 24, 12), 1, border_radius=1)
        pygame.draw.rect(fsuf, C["yellow"], (smx + 3, smy + 3, 18, 2))
        pygame.draw.rect(fsuf, C["yellow"], (smx + 3, smy + 7, 12, 2))

        # ── 17. Squash & stretch + shake ──────────────────────────────────────
        if sq > 0.005:
            new_w = int(fw * (1 + sq))
            new_h = int(fh * (1 - sq * 0.6))
            scaled = pygame.transform.scale(fsuf, (new_w, new_h))
            surf.blit(scaled, (ox + (fw - new_w) // 2, y0 + (fh - new_h)))
        else:
            surf.blit(fsuf, (ox, y0))

        # ── 18. Глитч (эпоха 4+) ──────────────────────────────────────────────
        if self.glitch > 0.1 and epoch_idx >= 4:
            glitch_surf = pygame.Surface((W, 5), pygame.SRCALPHA)
            glitch_surf.fill((*C["purple"], 90))
            for _ in range(4):
                gy_g = random.randint(y0, y0 + fh)
                surf.blit(glitch_surf, (random.randint(-10, 10), gy_g))

        # ── 19. Многослойный дым ──────────────────────────────────────────────
        smoke_palettes = [
            [(210, 210, 225), (180, 185, 200), (160, 165, 180)],
            [(190, 185, 220), (155, 150, 190), (120, 115, 160)],
            [(200, 160, 230), (160, 110, 200), (120, 70, 170)],
            [(100, 180, 230), (70, 140, 200), (50, 100, 160)],
            [(230, 80, 230), (180, 40, 200), (140, 20, 170)],
        ]
        sp = smoke_palettes[min(epoch_idx, 4)]
        for s in self.smoke:
            alpha = max(0, int(s[3]))
            r = max(1, int(s[2]))
            # три слоя дыма (смещённые)
            for li, (lox, loy, lsc, la_mul) in enumerate(
                [(0, 0, 1.0, 1.0), (-2, -1, 0.75, 0.6), (2, -2, 0.6, 0.4)]
            ):
                la = int(alpha * la_mul)
                lr = max(1, int(r * lsc))
                tmp2 = pygame.Surface((lr * 2, lr * 2), pygame.SRCALPHA)
                sc = sp[li]
                pygame.draw.circle(tmp2, (*sc, la), (lr, lr), lr)
                surf.blit(tmp2, (int(s[0]) + lox - lr, int(s[1]) + loy - lr))

    def _draw_conveyor(self, surf, x, y, w, epoch_idx):
        # Рамки конвейера
        belt_col = (48, 44, 36) if epoch_idx < 4 else (60, 18, 65)
        pygame.draw.rect(surf, (28, 26, 20), (x, y, w, 13))  # тень под конвейером
        pygame.draw.rect(surf, belt_col, (x, y, w, 11), border_radius=1)
        # Засечки-зубья ленты
        for ix in range(x, x + w - 4, 8):
            pygame.draw.rect(
                surf,
                tuple(max(0, c + 15) for c in belt_col),
                (ix + int(self.conveyor_x) % 8, y + 1, 4, 3),
            )
        pygame.draw.rect(
            surf,
            (90, 85, 72) if epoch_idx < 4 else (110, 45, 110),
            (x, y, w, 11),
            1,
            border_radius=1,
        )
        # Металлические ролики по краям
        for rx2 in [x + 4, x + w - 8]:
            pygame.draw.circle(surf, (110, 108, 120), (rx2, y + 5), 5)
            pygame.draw.circle(surf, (80, 78, 90), (rx2, y + 5), 3)
        # Коробки с крышками
        box_cols = [C["yellow"], C["cyan"], C["orange"], C["pink"], C["green"]]
        for i in range(6):
            bx = int(x + 12 + (self.conveyor_x * 1.2 + i * 48) % (w - 24))
            if bx + 14 < x + w - 2:
                bc2 = box_cols[i % len(box_cols)]
                pygame.draw.rect(surf, bc2, (bx, y - 11, 14, 11), border_radius=1)
                pygame.draw.rect(
                    surf,
                    tuple(max(0, c - 50) for c in bc2),
                    (bx, y - 11, 14, 11),
                    1,
                    border_radius=1,
                )
                # крышка
                pygame.draw.rect(
                    surf, tuple(min(255, c + 30) for c in bc2), (bx - 1, y - 13, 16, 4)
                )
                # блик на коробке
                pygame.draw.line(
                    surf,
                    tuple(min(255, c + 60) for c in bc2),
                    (bx + 2, y - 10),
                    (bx + 2, y - 3),
                    1,
                )

    def _draw_kpi(self, surf, x, y):
        pygame.draw.rect(surf, (10, 8, 20), (x + 3, y + 3, 82, 50))  # тень
        pygame.draw.rect(surf, (18, 16, 36), (x, y, 82, 50), border_radius=3)
        pygame.draw.rect(surf, C["cyan"], (x, y, 82, 50), 1, border_radius=3)
        # заголовок
        pygame.draw.rect(surf, (0, 60, 55), (x + 1, y + 1, 80, 8), border_radius=2)
        # График KPI
        pts = []
        for i in range(10):
            px3 = x + 4 + i * 7
            raw_y = self.kpi_val * (1 - i / 12) + math.sin(self.t * 2.5 + i * 0.8) * 5
            py3 = y + 38 - int(raw_y * 0.22)
            py3 = max(y + 12, min(y + 38, py3))
            pts.append((px3, py3))
        if len(pts) >= 2:
            # заливка под линией
            fill_pts = pts + [(pts[-1][0], y + 40), (pts[0][0], y + 40)]
            fill_s = pygame.Surface((82, 50), pygame.SRCALPHA)
            fill_pts_l = [(p[0] - x, p[1] - y) for p in fill_pts]
            pygame.draw.polygon(fill_s, (*C["green"], 40), fill_pts_l)
            surf.blit(fill_s, (x, y))
            pygame.draw.lines(surf, C["green"], False, pts, 2)
            # точки на перегибах
            for p in pts[::3]:
                pygame.draw.circle(surf, C["green"], p, 2)
        # Прогресс-бар (никогда не доходит до конца)
        bar_w = min(int((self.kpi_val / 100) * 74), 68)
        pygame.draw.rect(surf, (30, 55, 30), (x + 4, y + 42, 74, 5))
        pygame.draw.rect(surf, C["green"], (x + 4, y + 42, bar_w, 5))
        pygame.draw.rect(
            surf, tuple(min(255, c + 60) for c in C["green"]), (x + 4, y + 42, bar_w, 2)
        )

    def _draw_window_scene(self, surf, wx, wy, scene):
        t = self.t
        # Фигурки в окнах — упрощённые пиксельные формы
        if scene == "paper":
            hand_x = wx + 5 + int(abs(math.sin(t * 1.5)) * 16)
            pygame.draw.rect(surf, (220, 210, 190), (hand_x, wy + 17, 8, 4))
            pygame.draw.line(
                surf, (200, 190, 170), (wx + 16, wy + 10), (hand_x + 4, wy + 17), 1
            )
            # голова
            pygame.draw.circle(surf, (230, 195, 160), (wx + 16, wy + 8), 4)
        elif scene == "headdesk":
            head_y = wy + 9 + int(abs(math.sin(t * 2.8)) * 9)
            pygame.draw.circle(surf, (230, 195, 160), (wx + 16, head_y), 5)
            pygame.draw.rect(surf, (90, 70, 50), (wx + 4, wy + 20, 26, 3))
        elif scene == "blink":
            frm = int(t * 60) % 90
            pygame.draw.circle(surf, (230, 195, 160), (wx + 16, wy + 10), 5)
            if frm < 80:  # глаза открыты
                pygame.draw.circle(surf, (30, 30, 60), (wx + 13, wy + 9), 2)
                pygame.draw.circle(surf, (30, 30, 60), (wx + 19, wy + 9), 2)
            pygame.draw.rect(
                surf, (180, 50, 50), (wx + 4, wy + 14, 8, 8)
            )  # тело (рубашка)
        elif scene == "stare":
            pygame.draw.circle(surf, (230, 195, 160), (wx + 16, wy + 10), 5)
            pygame.draw.circle(surf, (20, 20, 50), (wx + 14, wy + 9), 2)
            pygame.draw.circle(surf, (20, 20, 50), (wx + 20, wy + 9), 2)
            pygame.draw.rect(surf, (50, 80, 130), (wx + 4, wy + 14, 8, 8))
        elif scene == "sleep":
            pygame.draw.circle(surf, (230, 195, 160), (wx + 16, wy + 18), 5)
            # Zz
            if int(t * 1.5) % 2 == 0:
                pygame.draw.line(
                    surf, C["gray"], (wx + 21, wy + 5), (wx + 26, wy + 5), 1
                )
                pygame.draw.line(
                    surf, C["gray"], (wx + 26, wy + 5), (wx + 21, wy + 9), 1
                )
                pygame.draw.line(
                    surf, C["gray"], (wx + 21, wy + 9), (wx + 26, wy + 9), 1
                )
            else:
                pygame.draw.line(
                    surf, C["gray"], (wx + 24, wy + 3), (wx + 28, wy + 3), 1
                )
                pygame.draw.line(
                    surf, C["gray"], (wx + 28, wy + 3), (wx + 24, wy + 6), 1
                )
                pygame.draw.line(
                    surf, C["gray"], (wx + 24, wy + 6), (wx + 28, wy + 6), 1
                )

    def _draw_binary_line(self, surf, x, y, w):
        bits = "10110010100110100110"
        offset = int(self.t * 15) % len(bits)
        for i in range(min(w // 8, len(bits))):
            bit = bits[(offset + i) % len(bits)]
            col = C["cyan"] if bit == "1" else (30, 30, 60)
            pygame.draw.rect(surf, col, (x + i * 8, y, 6, 3))


# ─── Кнопка ───────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, color_key="button", font_key="sm"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color_key = color_key
        self.font_key = font_key

    def draw(self, surf, fonts, mouse_pos, _=False):
        hov = self.rect.collidepoint(mouse_pos)
        col = C["btnhov"] if hov else C[self.color_key]
        pygame.draw.rect(surf, col, self.rect, border_radius=4)
        pygame.draw.rect(surf, C["white"], self.rect, 1, border_radius=4)
        txt = fonts[self.font_key].render(self.text, False, C["white"])
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event, pos=None):
        p = pos if pos is not None else event.pos
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(p)
        )


# ─── Попап события ────────────────────────────────────────────────────────────
class EventPopup:
    def __init__(self, title, body, border_color="yellow"):
        self.title = title
        self.body = body
        self.border_color = border_color
        self.life = 7.0
        self.button = Button((W // 2 - 50, H // 2 + 90, 100, 32), "OK", "green", "sm")

    def update(self, dt):
        self.life -= dt

    def draw(self, surf, fonts, mp=(0, 0)):
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        surf.blit(dim, (0, 0))

        box = pygame.Rect(20, H // 2 - 155, W - 40, 310)
        pygame.draw.rect(surf, C["panel"], box, border_radius=8)
        pygame.draw.rect(surf, C[self.border_color], box, 2, border_radius=8)

        t = fonts["sm"].render(self.title, False, C[self.border_color])
        surf.blit(t, t.get_rect(centerx=W // 2, y=box.y + 12))
        pygame.draw.line(
            surf, C["gray"], (box.x + 10, box.y + 38), (box.right - 10, box.y + 38)
        )

        y = box.y + 52
        for line in self.body.split("\n"):
            lt = fonts["xs"].render(line, False, C["white"])
            surf.blit(lt, lt.get_rect(centerx=W // 2, y=y))
            y += 22

        self.button.draw(surf, fonts, mp)

    def handle(self, event, vpos=None):
        return self.button.is_clicked(event, vpos)


class EpochPopup(EventPopup):
    def __init__(self, epoch: dict):
        super().__init__(f"ЭПОХА: {epoch['name']}", epoch["text"], "gold")
        self.life = 9.0


class PrestigeConfirmPopup:
    def __init__(self, prestige_count: int):
        self.pc = prestige_count
        self.btn_yes = Button(
            (W // 2 - 110, H // 2 + 70, 100, 34), "ДА, СБРОС", "red", "xs"
        )
        self.btn_no = Button(
            (W // 2 + 10, H // 2 + 70, 100, 34), "ОТМЕНА", "button", "xs"
        )
        self.result = None

    def draw(self, surf, fonts, mp=(0, 0)):
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 200))
        surf.blit(dim, (0, 0))

        box = pygame.Rect(20, H // 2 - 160, W - 40, 270)
        pygame.draw.rect(surf, C["panel"], box, border_radius=8)
        pygame.draw.rect(surf, C["gold"], box, 2, border_radius=8)

        lines = [
            "ФИКТИВНОЕ БАНКРОТСТВО",
            "",
            "Совет директоров решил",
            "обанкротить завод.",
            "Весь прогресс будет",
            "сброшен.",
            "",
            "Бонус: +25% навсегда",
            f"(уже {self.pc} пресейв(а))",
        ]
        y = box.y + 14
        for line in lines:
            col = (
                C["gold"]
                if line == "ФИКТИВНОЕ БАНКРОТСТВО"
                else C["white"]
                if line
                else C["panel"]
            )
            lt = fonts["xs"].render(line, False, col)
            surf.blit(lt, lt.get_rect(centerx=W // 2, y=y))
            y += 20

        self.btn_yes.draw(surf, fonts, mp)
        self.btn_no.draw(surf, fonts, mp)

    def handle(self, event, vpos=None):
        if self.btn_yes.is_clicked(event, vpos):
            self.result = True
        if self.btn_no.is_clicked(event, vpos):
            self.result = False


# ─── Баннер достижения ────────────────────────────────────────────────────────
class AchievementBanner:
    def __init__(self, ach: dict):
        self.name = ach["name"]
        self.desc = ach["desc"]
        self.life = 3.5

    def draw(self, surf, fonts):
        a = min(1.0, self.life / 0.5) * min(1.0, (self.life) / 0.3)
        alpha = int(min(220, self.life / 3.5 * 220))
        bw, bh = 320, 46
        bx, by = (W - bw) // 2, H - LIST_Y - bh - 4 + LIST_Y
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((30, 60, 30, alpha))
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, C["green"], (bx, by, bw, bh), 1, border_radius=4)
        nt = fonts["xs"].render(f"ДОСТИЖЕНИЕ: {self.name}", False, C["green"])
        dt = fonts["xs"].render(self.desc, False, C["gray"])
        surf.blit(nt, nt.get_rect(centerx=W // 2, y=by + 6))
        surf.blit(dt, dt.get_rect(centerx=W // 2, y=by + 24))

    def update(self, dt):
        self.life -= dt
        return self.life > 0


# ─── Главный класс ────────────────────────────────────────────────────────────
class App:
    def __init__(self):
        pygame.init()
        # Звука в игре нет — отключаем mixer. На Android SDL2_mixer падает в SIGSEGV
        # если аудиоустройство занято или не инициализировано системой.
        try:
            pygame.mixer.quit()
        except Exception:
            pass

        # FULLSCREEN | SCALED: pygame использует SDL_RenderSetLogicalSize → НЕ меняет
        # аппаратное разрешение → нет SIGSEGV. Координаты event.pos автоматически
        # масштабируются в пространство W×H (не нужна ручная трансформация).
        _SCALED = getattr(pygame, "SCALED", 0)
        if _IS_ANDROID:
            flags = pygame.FULLSCREEN | (_SCALED or 0)
        else:
            flags = _SCALED or 0
        self.screen = pygame.display.set_mode((W, H), flags)
        self._game_surf = None  # SCALED обрабатывает масштабирование нативно
        self._vscale = 1.0
        self._vox = self._voy = 0

        pygame.display.set_caption("ЗАВОД НИЧЕГО")
        self.clock = pygame.time.Clock()

        # Загрузка шрифта с fallback на системный
        _font_src = str(FONT_PATH) if FONT_PATH.exists() else None
        self.fonts = {
            "lg": pygame.font.Font(_font_src, 20),
            "md": pygame.font.Font(_font_src, 11),
            "sm": pygame.font.Font(_font_src, 9),
            "xs": pygame.font.Font(_font_src, 7),
        }

        self.game = Game()
        offline_gain = self.game.load()

        self.factory = Factory()
        self.particles: list[Particle] = []
        self.popup: EventPopup | None = None
        self.prestige_popup: PrestigeConfirmPopup | None = None
        self.ach_banners: list[AchievementBanner] = []
        self.tab = "workers"
        self.scroll = 0
        self.save_t = 0.0

        # Три вкладки
        self.tab_w = Button(
            (4, PANEL_Y + 3, 114, TAB_H - 6), "РАБОТНИКИ", "button", "xs"
        )
        self.tab_u = Button(
            (122, PANEL_Y + 3, 114, TAB_H - 6), "АПГРЕЙДЫ", "button", "xs"
        )
        self.tab_p = Button(
            (240, PANEL_Y + 3, 116, TAB_H - 6), "ПРОГРЕСС", "button", "xs"
        )

        self.factory_rect = pygame.Rect(0, FACTORY_Y, W, FACTORY_H)

        # Офлайн-попап
        if offline_gain and offline_gain > 1:
            self.popup = EventPopup(
                "Офлайн-прогресс",
                f"Пока вас не было,\nзавод усердно ничего\nне делал.\n\nПроизведено:\n+{fmt_num(offline_gain)} ничего",
            )

    def _virt_pos(self, pos):
        """Physical screen coords → virtual 360×640 game coords."""
        if not self._game_surf or self._vscale == 0:
            return pos
        return (
            (pos[0] - self._vox) / self._vscale,
            (pos[1] - self._voy) / self._vscale,
        )

    def run(self):
        prev = time.time()
        while True:
            now = time.time()
            dt = min(now - prev, 0.1)
            prev = now

            for event in pygame.event.get():
                self.handle(event)

            ev = self.game.update(dt, now)

            # Новое событие
            if ev and not self.popup and not self.prestige_popup:
                self.popup = EventPopup(*ev)

            # Новая эпоха
            if (
                self.game._pending_epoch is not None
                and not self.popup
                and not self.prestige_popup
            ):
                self.popup = EpochPopup(EPOCHS[self.game._pending_epoch])
                self.factory.epoch_glitch()
                self.game._pending_epoch = None

            # Достижения
            for ach in self.game._pending_ach:
                self.ach_banners.append(AchievementBanner(ach))
            self.game._pending_ach = []

            self.factory.update(dt, self.game.per_second(), self.game.epoch_idx)
            self.particles = [p for p in self.particles if p.update(dt)]
            self.ach_banners = [b for b in self.ach_banners if b.update(dt)]

            if self.popup:
                self.popup.update(dt)
                if self.popup.life <= 0:
                    self.popup = None

            self.save_t += dt
            if self.save_t > 30:
                self.game.save()
                self.save_t = 0

            self.draw()
            self.clock.tick(FPS)

    def handle(self, event):
        if event.type == pygame.QUIT:
            self.game.save()
            sys.exit()

        # Трансформируем физические координаты касания → виртуальные игровые
        vpos = self._virt_pos(event.pos) if hasattr(event, "pos") else None

        # Пресейв-попап приоритетнее
        if self.prestige_popup:
            self.prestige_popup.handle(event, vpos)
            if self.prestige_popup.result is True:
                self.game.do_prestige()
                self.prestige_popup = None
                self.scroll = 0
                self.tab = "workers"
            elif self.prestige_popup.result is False:
                self.prestige_popup = None
            return

        if self.popup:
            if self.popup.handle(event, vpos):
                self.popup = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            p = vpos or event.pos
            if self.factory_rect.collidepoint(p):
                v = self.game.do_click()
                self.factory.click_fx()
                col = random.choice([C["yellow"], C["cyan"], C["pink"], C["orange"]])
                self.particles.append(Particle(p[0], p[1], f"+{fmt_num(v)}", col))
                return

            if self.tab_w.is_clicked(event, p):
                self.tab, self.scroll = "workers", 0
            if self.tab_u.is_clicked(event, p):
                self.tab, self.scroll = "upgrades", 0
            if self.tab_p.is_clicked(event, p):
                self.tab, self.scroll = "progress", 0

            if self.tab == "workers":
                for btn, wid in getattr(self, "_wbtns", []):
                    if btn.is_clicked(event, p):
                        self.game.buy_worker(wid)

            if self.tab == "upgrades":
                for btn, uid in getattr(self, "_ubtns", []):
                    if btn.is_clicked(event, p):
                        self.game.buy_upgrade(uid)

            if self.tab == "progress":
                pb = getattr(self, "_prestige_btn", None)
                if pb and pb.is_clicked(event, p):
                    self.prestige_popup = PrestigeConfirmPopup(self.game.prestige_count)

        _MOUSEWHEEL = getattr(pygame, "MOUSEWHEEL", None)
        if _MOUSEWHEEL and event.type == _MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y * 40)

        # Android touch scroll (FINGERMOTION): dy нормализован 0-1 по высоте экрана
        _FINGERMOTION = getattr(pygame, "FINGERMOTION", None)
        if _FINGERMOTION and event.type == _FINGERMOTION:
            _, sh = self.screen.get_size()
            self.scroll = max(0, self.scroll - event.dy * sh)

    def draw(self):
        # Рисуем в виртуальный Surface (fallback) или напрямую в экран
        surf = self._game_surf if self._game_surf else self.screen

        # Фон эпохи
        bg = EPOCHS[min(self.game.epoch_idx, len(EPOCHS) - 1)]["bg"]
        surf.fill(bg)

        # ── Шапка ─────────────────────────────────────────────────────────
        pygame.draw.rect(surf, C["panel"], (0, 0, W, HEADER_H))

        title = self.fonts["xs"].render("ЗАВОД  НИЧЕГО", False, C["yellow"])
        surf.blit(title, title.get_rect(centerx=W // 2, y=6))

        val = self.fonts["lg"].render(fmt_num(self.game.nothing), False, C["white"])
        surf.blit(val, val.get_rect(centerx=W // 2, y=22))

        sub = self.fonts["xs"].render("единиц ничего", False, C["gray"])
        surf.blit(sub, sub.get_rect(centerx=W // 2, y=56))

        if self.game.prestige_count > 0:
            pt = self.fonts["xs"].render(
                f"x{1 + self.game.prestige_count * 0.25:.2f} пресейв", False, C["gold"]
            )
            surf.blit(pt, (W - pt.get_width() - 4, 6))

        # ── Статистика ────────────────────────────────────────────────────
        ps = self.game.per_second()
        cv = self.game.click_value()
        ps_t = self.fonts["xs"].render(f"+{fmt_num(ps)}/сек", False, C["cyan"])
        cl_t = self.fonts["xs"].render(f"клик {fmt_num(cv)}", False, C["orange"])
        surf.blit(ps_t, (8, HEADER_H + 2))
        surf.blit(cl_t, (W - cl_t.get_width() - 8, HEADER_H + 2))

        # ── Завод ─────────────────────────────────────────────────────────
        self.factory.draw(surf, ps, self.game.epoch_idx)

        if self.game.total_earned < 5:
            hint = self.fonts["xs"].render(">> нажми на завод <<", False, C["gray"])
            surf.blit(hint, hint.get_rect(centerx=W // 2, y=FACTORY_Y + FACTORY_H - 20))

        # ── Частицы ───────────────────────────────────────────────────────
        for p in self.particles:
            a = max(0.0, min(1.0, p.life / 1.4))
            co = tuple(int(ch * a) for ch in p.color)
            t = self.fonts["sm"].render(p.text, False, co)
            surf.blit(t, (int(p.x) - t.get_width() // 2, int(p.y)))

        # ── Нижняя панель ─────────────────────────────────────────────────
        pygame.draw.rect(surf, C["panel"], (0, PANEL_Y, W, H - PANEL_Y))
        pygame.draw.line(surf, C["gray"], (0, PANEL_Y), (W, PANEL_Y), 1)

        self.tab_w.color_key = "yellow" if self.tab == "workers" else "button"
        self.tab_u.color_key = "yellow" if self.tab == "upgrades" else "button"
        self.tab_p.color_key = "yellow" if self.tab == "progress" else "button"
        mp = self._virt_pos(pygame.mouse.get_pos())
        self.tab_w.draw(surf, self.fonts, mp)
        self.tab_u.draw(surf, self.fonts, mp)
        self.tab_p.draw(surf, self.fonts, mp)

        list_rect = pygame.Rect(0, LIST_Y, W, H - LIST_Y)

        if self.tab == "workers":
            self._draw_workers_tab(surf, list_rect)
        elif self.tab == "upgrades":
            self._draw_upgrades_tab(surf, list_rect)
        elif self.tab == "progress":
            self._draw_progress_tab(surf, list_rect, mp)

        # ── Баннеры достижений ────────────────────────────────────────────
        for b in self.ach_banners[:1]:
            b.draw(surf, self.fonts)

        # ── Попапы ────────────────────────────────────────────────────────
        if self.prestige_popup:
            self.prestige_popup.draw(surf, self.fonts, mp)
        elif self.popup:
            self.popup.draw(surf, self.fonts, mp)

        # Если рисовали в виртуальный Surface — масштабируем на физический экран
        if self._game_surf:
            sw, sh = self.screen.get_size()
            scale = min(sw / W, sh / H)
            nw, nh = int(W * scale), int(H * scale)
            scaled = pygame.transform.scale(self._game_surf, (nw, nh))
            self.screen.fill((0, 0, 0))
            self.screen.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))

        pygame.display.flip()

    def _draw_workers_tab(self, surf, list_rect):
        self._wbtns = []
        lsuf = pygame.Surface((W, len(WORKERS) * 64 + 10), pygame.SRCALPHA)
        y = 0
        for w in WORKERS:
            cost = self.game.worker_cost(w["id"])
            cnt = self.game.worker_counts[w["id"]]
            can = self.game.nothing >= cost
            self._draw_worker_row(lsuf, y, w, cost, cnt, can)
            bc = "green" if can else "button"
            btn_vis = Button((W - 82, y + 10, 74, 34), fmt_num(cost), bc, "xs")
            btn_vis.draw(lsuf, self.fonts, (-999, -999))
            self._wbtns.append(
                (
                    Button(
                        (
                            list_rect.x + W - 82,
                            list_rect.y + y + 10 - self.scroll,
                            74,
                            34,
                        ),
                        "",
                        bc,
                    ),
                    w["id"],
                )
            )
            y += 64
        total_h = len(WORKERS) * 64
        self.scroll = min(self.scroll, max(0, total_h - list_rect.height))
        surf.blit(
            lsuf, (list_rect.x, list_rect.y), (0, self.scroll, W, list_rect.height)
        )

    def _draw_upgrades_tab(self, surf, list_rect):
        self._ubtns = []
        lsuf = pygame.Surface((W, len(UPGRADES) * 64 + 10), pygame.SRCALPHA)
        y = 0
        for u in UPGRADES:
            bought = self.game.upgrades[u["id"]]
            can = not bought and self.game.nothing >= u["cost"]
            self._draw_upgrade_row(lsuf, y, u, can, bought)
            if not bought:
                bc = "green" if can else "button"
                btn_vis = Button((W - 82, y + 10, 74, 34), fmt_num(u["cost"]), bc, "xs")
                btn_vis.draw(lsuf, self.fonts, (-999, -999))
                self._ubtns.append(
                    (
                        Button(
                            (
                                list_rect.x + W - 82,
                                list_rect.y + y + 10 - self.scroll,
                                74,
                                34,
                            ),
                            "",
                            bc,
                        ),
                        u["id"],
                    )
                )
            y += 64
        total_h = len(UPGRADES) * 64
        self.scroll = min(self.scroll, max(0, total_h - list_rect.height))
        surf.blit(
            lsuf, (list_rect.x, list_rect.y), (0, self.scroll, W, list_rect.height)
        )

    def _draw_progress_tab(self, surf, list_rect, mp=(0, 0)):
        self._prestige_btn = None
        y = list_rect.y + 6

        # ─ Текущая эпоха
        epoch = EPOCHS[self.game.epoch_idx]
        ep_box = pygame.Rect(8, y, W - 16, 52)
        pygame.draw.rect(surf, (30, 30, 70), ep_box, border_radius=4)
        pygame.draw.rect(surf, C["gold"], ep_box, 1, border_radius=4)
        et = self.fonts["xs"].render(
            f"ЭПОХА {self.game.epoch_idx + 1}: {epoch['name']}", False, C["gold"]
        )
        surf.blit(et, et.get_rect(centerx=W // 2, y=y + 6))
        # Прогресс до следующей эпохи
        if self.game.epoch_idx < len(EPOCHS) - 1:
            nxt = EPOCHS[self.game.epoch_idx + 1]["threshold"]
            prog = min(1.0, self.game.total_earned / nxt)
            pygame.draw.rect(
                surf, (40, 40, 80), (16, y + 30, W - 32, 8), border_radius=3
            )
            pygame.draw.rect(
                surf, C["cyan"], (16, y + 30, int((W - 32) * prog), 8), border_radius=3
            )
            pt = self.fonts["xs"].render(
                f"{fmt_num(self.game.total_earned)}/{fmt_num(nxt)}", False, C["gray"]
            )
            surf.blit(pt, pt.get_rect(centerx=W // 2, y=y + 42))
        else:
            mt = self.fonts["xs"].render("МАКСИМАЛЬНАЯ ЭПОХА", False, C["cyan"])
            surf.blit(mt, mt.get_rect(centerx=W // 2, y=y + 34))
        y += 62

        # ─ Достижения
        dt = self.fonts["xs"].render("ДОСТИЖЕНИЯ", False, C["white"])
        surf.blit(dt, (12, y))
        y += 16
        unlocked = self.game.achievements_unlocked
        cols = 2
        for i, ach in enumerate(ACHIEVEMENTS):
            ax = 8 + (i % cols) * ((W - 16) // cols)
            ay = y + (i // cols) * 28
            done = ach["id"] in unlocked
            col_b = (20, 45, 25) if done else (22, 22, 50)
            col_border = C["green"] if done else C["gray"]
            pygame.draw.rect(
                surf, col_b, (ax, ay, (W - 20) // cols, 24), border_radius=3
            )
            pygame.draw.rect(
                surf, col_border, (ax, ay, (W - 20) // cols, 24), 1, border_radius=3
            )
            nt = self.fonts["xs"].render(
                ach["name"][:14], False, C["white"] if done else C["gray"]
            )
            surf.blit(nt, (ax + 4, ay + 4))
            if done:
                chk = self.fonts["xs"].render("v", False, C["green"])
                surf.blit(chk, (ax + (W - 20) // cols - 14, ay + 4))
        y += (len(ACHIEVEMENTS) // cols + 1) * 28 + 8

        # ─ Пресейв
        threshold = self.game.prestige_threshold()
        can_prestige = self.game.total_earned >= threshold
        pb_col = "gold" if can_prestige else "button"
        pb_text = "БАНКРОТСТВО" if can_prestige else f"нужно {fmt_num(threshold)}"
        pb = Button((8, y, W - 16, 36), pb_text, pb_col, "xs")
        pb.draw(surf, self.fonts, mp)
        self._prestige_btn = pb
        y += 44
        info = self.fonts["xs"].render(
            f"Пресейвов: {self.game.prestige_count}  Бонус: x{self.game.prestige_mult():.2f}",
            False,
            C["gray"],
        )
        surf.blit(info, info.get_rect(centerx=W // 2, y=y))

    def _draw_worker_row(self, surf, y, w, cost, cnt, can):
        alpha = 255 if can else 140
        row = pygame.Surface((W - 10, 60), pygame.SRCALPHA)
        col_bg = (38, 35, 78, alpha) if can else (22, 20, 50, alpha)
        pygame.draw.rect(row, col_bg, (0, 0, W - 10, 60), border_radius=4)
        pygame.draw.rect(
            row, (*C["gray"], alpha), (0, 0, W - 10, 60), 1, border_radius=4
        )
        surf.blit(row, (5, y + 2))

        ic_col = C[w["color"]]
        ic_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(ic_surf, (*ic_col, alpha), (0, 0, 36, 36), border_radius=3)
        draw_worker_icon(ic_surf, 0, 0, w["id"], C["dark"])
        surf.blit(ic_surf, (12, y + 12))

        nm = self.fonts["xs"].render(w["name"], False, C["white"] if can else C["gray"])
        surf.blit(nm, (56, y + 12))
        ct = self.fonts["sm"].render(f"x{cnt}", False, ic_col)
        surf.blit(ct, (56, y + 34))
        rate = w["rate"] * self.game.worker_mults[w["id"]]
        rt = self.fonts["xs"].render(f"{fmt_num(rate)}/сек", False, C["gray"])
        surf.blit(rt, (120, y + 34))

    def _draw_upgrade_row(self, surf, y, u, can, bought):
        col_bg = (20, 45, 28) if bought else (42, 38, 25) if can else (20, 20, 44)
        pygame.draw.rect(surf, col_bg, (5, y + 2, W - 10, 60), border_radius=4)
        border = C["green"] if bought else (C["yellow"] if can else C["gray"])
        pygame.draw.rect(surf, border, (5, y + 2, W - 10, 60), 1, border_radius=4)
        ic_col = C[u["color"]]
        pygame.draw.rect(surf, ic_col, (12, y + 12, 36, 36), border_radius=3)
        lbl = self.fonts["sm"].render("v" if bought else "*", False, C["dark"])
        surf.blit(lbl, lbl.get_rect(center=(30, y + 30)))
        nm = self.fonts["xs"].render(
            u["name"], False, C["white"] if can or bought else C["gray"]
        )
        dsc = self.fonts["xs"].render(u["desc"], False, C["gray"])
        surf.blit(nm, (56, y + 12))
        surf.blit(dsc, (56, y + 34))
        if bought:
            gt = self.fonts["xs"].render("КУПЛЕНО", False, C["green"])
            surf.blit(gt, gt.get_rect(right=W - 12, y=y + 28))


if __name__ == "__main__":
    try:
        App().run()
    except SystemExit:
        pass
    except Exception:
        log_path = _SAVE_DIR / "crash.log"
        try:
            with open(log_path, "a") as _f:
                _f.write(f"\n=== {datetime.datetime.now()} ===\n")
                traceback.print_exc(file=_f)
        except Exception:
            pass
        raise
