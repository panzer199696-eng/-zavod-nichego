# -*- coding: utf-8 -*-
"""
gen_assets.py — генерация артов игры «Ничего не построено» через Nano Banana.
ЕДИНЫЙ СТИЛЬ: каждый промпт = PER-ASSET описание + общий STYLE-суффикс (style bible).
Это гарантия строго единого визуального стиля (требование заказчика).

Запуск одного ассета (чтобы параллелить и проверять по очереди):
    cd C:\\Users\\user\\Desktop\\Разработка на питоне\\game
    python gen_assets.py stazher
    python gen_assets.py --list
"""

from __future__ import annotations
import sys
import pathlib

# подключаем библиотечный генератор pto-worker
sys.path.insert(0, r"C:\Users\user\pto-worker")
from nano_banana import generate  # noqa: E402

OUT_DIR = pathlib.Path(__file__).parent / "assets" / "proto"
MODEL = "pro"  # для прототипа стиля — лучший контроль; потом можно nb2

# ───────────────────────── STYLE BIBLE (единый суффикс) ─────────────────────────
STYLE = (
    "ART STYLE (strict, identical across all assets): hand-drawn vector cartoon, "
    "flat colors with simple two-tone cell-shading, thick dark indigo outline color #1A1538 "
    "(3-4px on characters), rounded exaggerated shapes, soft light from the top-left. "
    "MOOD: absurdist corporate-bureaucracy satire meets a grim arctic Chukotka construction site; "
    "gloomy indigo atmosphere with a few vivid accent colors. "
    "STRICT COLOR PALETTE only: backgrounds #0F0C23 and #1E1A3A, panels #2A2550, "
    "primary yellow #FFDC32, warm orange #FFA032, cold cyan #46DCC8, accent pink #FF64A0, "
    "danger red #FF3A3A, light text/highlights #F0EAF8. "
    "Mobile deckbuilder game asset, clean, high contrast, readable as a small sprite. "
    "No text, no words, no letters, no logos, no UI frames."
)
CHAR = (
    " Single full-body character, centered, facing forward, isolated on a flat #0F0C23 background. "
    + STYLE
)
BG = (
    " Vertical mobile battle background scene, empty center stage for characters. "
    + STYLE
)

ASSETS: dict[str, tuple[str, str | None]] = {
    # ── ГЕРОЙ ──
    "stazher": (
        "A cartoon young male office intern, the hero of the game. Skinny, slightly hunched, "
        "oversized round glasses, a yellow hard hat slipping off one ear, baggy grey work overalls "
        "over a shirt and tie, clutching an enormous wobbling stack of paper documents taller than "
        "himself. Cute, absurd, anxious-but-determined expression." + CHAR,
        None,
    ),
    # ── ВРАГИ Акт 1 ──
    "prorab": (
        "A cartoon construction foreman enemy, the bully. Big barrel-chested stocky man, red angry "
        "face, thick moustache, orange dirty safety vest, a yellow hard hat, fists on hips, shouting. "
        "Comedic but intimidating." + CHAR,
        None,
    ),
    "soglasovanie": (
        "A cartoon bureaucratic ghost enemy: a translucent pale spectre made of stacked paper "
        "documents and rubber stamps, hollow eyes, floating, holding an approval stamp. Eerie, "
        "absurd, melancholic." + CHAR,
        None,
    ),
    "deadline": (
        "A cartoon embodiment of a burning deadline, an enemy. A round wall clock with a cracked "
        "screaming panicked face, clock hands spinning wildly, small orange flames flickering on top "
        "of it, sweat drops flying, standing on thin twitchy spider legs. Frantic, comedic dread."
        + CHAR,
        None,
    ),
    "subpodryadchik": (
        "A cartoon shifty subcontractor enemy who never finishes anything. A wiry sleazy man with a "
        "sly grin and shifty eyes, cheap mismatched work clothes and an open hi-vis vest, holding an "
        "endless unrolling scroll of unfinished to-do lists in one hand, half-hiding behind a crooked "
        "barricade of unfinished construction junk — stacked bricks, a bag of cement, tangled rebar "
        "and a leaning shovel. Eternally promising, never delivering. Comedic, evasive."
        + CHAR,
        None,
    ),
    "tehnadzor": (
        "An intimidating cartoon construction-supervision inspector enemy (technical-supervision "
        "elite), standing upright and facing the viewer head-on. A tall gaunt strict bureaucrat in a "
        "long cold-grey coat over a hi-vis vest and white inspector hard hat, sharp icy stare through "
        "thin rectangular glasses, pursed disapproving mouth, hugging a thick heavy "
        "code-of-regulations binder against his chest with one arm, and holding a tall vertical "
        "surveyor's measuring staff upright beside him with the other hand. Light frost and a small "
        "puff of cold breath around him. Pedantic, freezing, merciless. Full standing pose, head to "
        "feet visible." + CHAR,
        None,
    ),
    # ── БОСС Акт 1 ──
    "boss_otchet": (
        "A huge intimidating boss monster called 'The Quarterly Report'. A towering teetering stack "
        "of office report binders and paper folders fused into a creature, with glowing red and "
        "orange pie-charts and bar-graphs forming an angry face, bundles of documents as tentacle "
        "arms, rubber stamps and paperclips, oppressive corporate doom looming over the viewer."
        + CHAR,
        None,
    ),
    # ── ЛОКАЦИЯ Акт 1 ──
    "bg_office": (
        "A dark cold open-plan office at night, flickering fluorescent ceiling lights, rows of "
        "cluttered desks with old monitors, a busy paper printer spitting pages, and a big window "
        "showing frozen arctic tundra with snow and a half-built bridge outside in the dark."
        + BG,
        "9:16",
    ),
}


def gen_one(key: str) -> None:
    prompt, aspect = ASSETS[key]
    out = OUT_DIR / f"{key}.png"
    print(f"→ генерирую {key} (model={MODEL}, aspect={aspect})…")
    path, cost = generate(prompt, str(out), model=MODEL, aspect=aspect)
    print(f"OK: {path}  (${cost:.4f})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("--list", "-l"):
        print("Ассеты:", ", ".join(ASSETS))
        sys.exit(0)
    if args[0] == "all":
        for k in ASSETS:
            gen_one(k)
    else:
        for k in args:
            if k not in ASSETS:
                print(
                    f"нет ассета {k!r}; доступны: {', '.join(ASSETS)}", file=sys.stderr
                )
                sys.exit(1)
            gen_one(k)
