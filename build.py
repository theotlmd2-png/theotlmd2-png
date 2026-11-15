"""Génère l'en-tête du profil GitHub en deux thèmes (clair et sombre), DA du portfolio v2 :
fond clair, encre noire, un seul accent bleu, et le trait avec la flèche qui souligne
« Toulemonde » puis pointe vers sa traduction.

Tout le texte est converti en tracés (Archivo, via HarfBuzz) : GitHub affiche les SVG en <img>,
sans police web, donc c'est la seule façon d'avoir un rendu identique partout et un trait
calé au pixel sous le mot.

Usage : python3 -m pip install fonttools uharfbuzz && python3 build.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
FONT_FILE = ROOT / "fonts" / "Archivo.ttf"
W, H = 1280, 400


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    ink: str
    muted: str
    accent: str


THEMES = (
    Theme("light", "#FAFAFA", "#0A0A0B", "#52525B", "#1F4BFF"),
    Theme("dark", "#0D1117", "#F0F6FC", "#9198A1", "#6E8BFF"),
)


class Typesetter:
    """Met en forme une ligne avec HarfBuzz (crénage compris) et renvoie un tracé SVG."""

    def __init__(self, path: Path) -> None:
        self.blob = hb.Blob.from_file_path(str(path))
        self.path = path
        self._fonts: dict[int, TTFont] = {}

    def _static(self, weight: int) -> TTFont:
        if weight not in self._fonts:
            self._fonts[weight] = instantiateVariableFont(TTFont(self.path), {"wght": weight, "wdth": 100})
        return self._fonts[weight]

    def line(self, text: str, size: float, weight: int, x: float, y: float, tracking: float = 0) -> tuple[str, float]:
        face = hb.Face(self.blob)
        font = hb.Font(face)
        font.set_variations({"wght": weight, "wdth": 100})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})

        static = self._static(weight)
        glyphs = static.getGlyphSet()
        order = static.getGlyphOrder()
        scale = size / static["head"].unitsPerEm
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        cursor = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gx = x + (cursor + pos.x_offset) * scale
            gy = y - pos.y_offset * scale
            glyphs[order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
            cursor += pos.x_advance + tracking / scale
        width = cursor * scale - tracking
        return pen.getCommands(), width


def arrow_head(tip: tuple[float, float], ctrl: tuple[float, float], length: float = 20, spread: float = 0.5) -> str:
    """Pointe en V orientée selon la tangente de fin de la courbe (dernier point de contrôle → pointe)."""
    angle = math.atan2(tip[1] - ctrl[1], tip[0] - ctrl[0])
    left = (tip[0] - length * math.cos(angle - spread), tip[1] - length * math.sin(angle - spread))
    right = (tip[0] - length * math.cos(angle + spread), tip[1] - length * math.sin(angle + spread))
    return f"M {left[0]:.1f} {left[1]:.1f} L {tip[0]:.1f} {tip[1]:.1f} L {right[0]:.1f} {right[1]:.1f}"


def compose(ts: Typesetter) -> dict[str, str]:
    x0 = 72
    first, _ = ts.line("Théophile", 96, 800, x0, 150, tracking=-2.5)
    last, last_w = ts.line("Toulemonde", 96, 800, x0, 254, tracking=-2.5)
    tagline, _ = ts.line("Low-code builder  ·  AI agents  ·  iOS apps  ·  CRMs  ·  growth", 22, 450, x0 + 2, 342)

    note_x = round(x0 + last_w + 190)
    everyone, _ = ts.line("“everyone”", 40, 750, note_x, 158, tracking=-0.5)
    french, _ = ts.line("in French.", 22, 450, note_x + 2, 192)
    fit1, _ = ts.line("Fitting: I build tools", 22, 500, note_x + 2, 242)
    fit2, _ = ts.line("anyone can use.", 22, 500, note_x + 2, 272)

    # Trait : souligne le mot avec un léger galbe de main, puis repart vers « everyone ».
    end_x = x0 + last_w
    tip = (note_x - 18, 150.0)
    ctrl = (note_x - 70, 196.0)
    trait = (
        f"M {x0 + 2} 274 "
        f"C {x0 + last_w * 0.35:.1f} 280, {x0 + last_w * 0.7:.1f} 279, {end_x:.1f} 272 "
        f"C {end_x + 0.3 * last_w:.1f} 265, {ctrl[0]:.1f} {ctrl[1]:.1f}, {tip[0]:.1f} {tip[1]:.1f}"
    )
    return {
        "first": first, "last": last, "tagline": tagline, "everyone": everyone,
        "french": french, "fit1": fit1, "fit2": fit2,
        "trait": trait, "arrow": arrow_head(tip, ctrl),
    }


def header(t: Theme, p: dict[str, str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Théophile Toulemonde</title>
  <desc id="d">Théophile Toulemonde. Toulemonde means everyone in French, fitting for a builder who ships tools anyone can use by piloting AI agents.</desc>
  <style>
    .rise {{ opacity: 0; transform: translateY(14px); animation: rise .7s cubic-bezier(.22,1,.36,1) forwards; }}
    .r1 {{ animation-delay: .05s; }} .r2 {{ animation-delay: .18s; }} .r3 {{ animation-delay: .4s; }}
    .trait {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1.3s cubic-bezier(.65,0,.35,1) .6s forwards; }}
    .arrow {{ opacity: 0; animation: pop .25s ease-out 1.85s forwards; }}
    .n1 {{ animation-delay: 1.9s; }} .n2 {{ animation-delay: 2.05s; }} .n3 {{ animation-delay: 2.3s; }}
    @keyframes rise {{ to {{ opacity: 1; transform: none; }} }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes pop {{ to {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .rise, .arrow {{ animation: none; opacity: 1; transform: none; }}
      .trait {{ animation: none; stroke-dashoffset: 0; }}
    }}
  </style>
  <rect width="{W}" height="{H}" rx="20" fill="{t.bg}"/>
  <path class="rise r1" fill="{t.ink}" d="{p['first']}"/>
  <path class="rise r2" fill="{t.ink}" d="{p['last']}"/>
  <path class="rise r3" fill="{t.muted}" d="{p['tagline']}"/>
  <path class="trait" pathLength="1" d="{p['trait']}" fill="none" stroke="{t.accent}" stroke-width="5" stroke-linecap="round"/>
  <path class="arrow" d="{p['arrow']}" fill="none" stroke="{t.accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <path class="rise n1" fill="{t.accent}" d="{p['everyone']}"/>
  <path class="rise n2" fill="{t.muted}" d="{p['french']}"/>
  <path class="rise n3" fill="{t.ink}" d="{p['fit1']} {p['fit2']}"/>
</svg>
"""


def main() -> None:
    if not FONT_FILE.exists():
        raise SystemExit(f"[ÉCHEC] police introuvable : {FONT_FILE}")
    ASSETS.mkdir(exist_ok=True)
    parts = compose(Typesetter(FONT_FILE))
    for theme in THEMES:
        out = ASSETS / f"header-{theme.name}.svg"
        out.write_text(header(theme, parts), encoding="utf-8")
        print(f"[OK] {out} ({out.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
