"""Génère l'en-tête du profil GitHub en deux thèmes (clair et sombre), DA du portfolio v2 :
fond clair, encre noire, un seul accent bleu, et le trait avec la flèche qui a un rôle précis
(il souligne « Toulemonde » puis pointe vers sa traduction).

Usage : python3 build.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
FONT = "Archivo, Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    ink: str
    muted: str
    accent: str


THEMES = (
    Theme("light", "#FAFAFA", "#0A0A0B", "#52525B", "#1F4BFF"),
    Theme("dark", "#0A0A0B", "#FAFAFA", "#A1A1AA", "#6E8BFF"),
)

# Le trait : sous « Toulemonde », puis remonte vers l'annotation de droite.
TRAIT = "M 74 262 C 260 274, 470 270, 640 258 C 760 249, 812 214, 846 162"
ARROW = "M 830 176 L 848 158 L 852 184"


def header(t: Theme) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="380" viewBox="0 0 1280 380" role="img" aria-labelledby="t d">
  <title id="t">Théophile Toulemonde</title>
  <desc id="d">Théophile Toulemonde. Toulemonde means everyone in French, fitting for a low-code builder who ships tools anyone can use by piloting AI agents.</desc>
  <style>
    .trait {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1.6s cubic-bezier(.65,0,.35,1) .3s forwards; }}
    .arrow, .note {{ opacity: 0; animation: show .4s ease-out 1.8s forwards; }}
    .note2 {{ opacity: 0; animation: show .4s ease-out 2.1s forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes show {{ to {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .trait {{ animation: none; stroke-dashoffset: 0; }}
      .arrow, .note, .note2 {{ animation: none; opacity: 1; }}
    }}
  </style>
  <rect width="1280" height="380" rx="20" fill="{t.bg}"/>
  <g font-family="{FONT}" fill="{t.ink}">
    <text x="68" y="136" font-size="84" font-weight="800" letter-spacing="-2.5">Théophile</text>
    <text x="68" y="238" font-size="84" font-weight="800" letter-spacing="-2.5">Toulemonde</text>
    <text x="72" y="330" font-size="22" fill="{t.muted}">Low-code builder · AI agents · iOS apps · CRMs · growth</text>
  </g>
  <path class="trait" pathLength="1" d="{TRAIT}" fill="none" stroke="{t.accent}" stroke-width="5" stroke-linecap="round"/>
  <path class="arrow" d="{ARROW}" fill="none" stroke="{t.accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <g font-family="{FONT}">
    <text class="note" x="870" y="150" font-size="34" font-weight="700" fill="{t.accent}">“everyone”</text>
    <text class="note" x="870" y="184" font-size="22" fill="{t.muted}">in French.</text>
    <text class="note2" x="870" y="232" font-size="22" fill="{t.ink}">Fitting: I build tools</text>
    <text class="note2" x="870" y="262" font-size="22" fill="{t.ink}">anyone can use.</text>
  </g>
</svg>
"""


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        out = ASSETS / f"header-{theme.name}.svg"
        out.write_text(header(theme), encoding="utf-8")
        print(f"[OK] {out}")


if __name__ == "__main__":
    main()
