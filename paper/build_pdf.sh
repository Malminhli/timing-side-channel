#!/usr/bin/env bash
# Build paper/paper.pdf from paper/paper.md with pandoc + xelatex.
#
#   ./paper/build_pdf.sh            (from anywhere)
#
# Figures are read from ../results/ (relative to paper/). If a figure is
# missing, a placeholder box is printed instead, so the PDF can be built
# before the experiments have been run. Re-run this script once results/
# contains exp1_leakage.png and exp2_tvla.png.
#
# Needs: pandoc (>= 2.11), xelatex (TeX Live with fontspec, unicode-math,
# titlesec, fancyhdr, xurl, microtype, booktabs) and an installed serif font.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"   # image paths in paper.md (../results/...) are relative to paper/

# Pick the first installed font from each list (fc-list or TeX Live tree).
have_font() {
  fc-list : family 2>/dev/null | tr ',' '\n' | grep -qx "$1" && return 0
  case "$1" in
    "TeX Gyre Pagella")      kpsewhich texgyrepagella-regular.otf >/dev/null 2>&1 ;;
    "TeX Gyre Pagella Math") kpsewhich texgyrepagella-math.otf    >/dev/null 2>&1 ;;
    "Latin Modern Math")     kpsewhich latinmodern-math.otf       >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}
pick_font() {
  for f in "$@"; do
    if have_font "$f"; then echo "$f"; return 0; fi
  done
  return 1
}

MAINFONT="$(pick_font "TeX Gyre Pagella" "Libertinus Serif" "TeX Gyre Termes" \
            "DejaVu Serif" "Latin Modern Roman")" || { echo "No serif font found" >&2; exit 1; }
MATHFONT="$(pick_font "TeX Gyre Pagella Math" "Libertinus Math" "Latin Modern Math" \
            "DejaVu Math TeX Gyre")" || MATHFONT=""
MONOFONT="$(pick_font "DejaVu Sans Mono" "Liberation Mono" "Latin Modern Mono")" || MONOFONT=""

for fig in ../results/exp1_leakage.png ../results/exp2_tvla.png; do
  [ -f "$fig" ] || echo "note: $fig not found, a placeholder will be used" >&2
done

args=(
  paper.md
  --from=markdown+autolink_bare_uris-implicit_figures
  --to=pdf
  --pdf-engine=xelatex
  --shift-heading-level-by=-1
  --lua-filter=latex/paper-filter.lua
  --include-in-header=latex/header.tex
  -V documentclass=article
  -V papersize=a4
  -V fontsize=11pt
  -V geometry:margin=1in
  -V geometry:headsep=0.3in
  -V linestretch=1.08
  -V colorlinks=true
  -V linkcolor=linkblue
  -V urlcolor=linkblue
  -V citecolor=linkblue
  -V "mainfont=$MAINFONT"
  --output=paper.pdf
)
[ -n "$MATHFONT" ] && args+=(-V "mathfont=$MATHFONT")
[ -n "$MONOFONT" ] && args+=(-V "monofont=$MONOFONT" -V "monofontoptions=Scale=0.88" -V "monofontoptions=HyphenChar=None")

pandoc "${args[@]}"
echo "Built $HERE/paper.pdf (main font: $MAINFONT${MATHFONT:+, math: $MATHFONT})"
