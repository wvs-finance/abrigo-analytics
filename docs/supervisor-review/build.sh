#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex
bibtex main || echo "bibtex returned non-zero (typically benign at placeholder stage with no \\cite{} calls); continuing"
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
if [[ -f main.pdf ]]; then
    mv main.pdf 2026-05-06-empirical-record-letter.pdf
    echo "PDF: $(pwd)/2026-05-06-empirical-record-letter.pdf"
else
    echo "FATAL: main.pdf not produced; check main.log"
    exit 1
fi
