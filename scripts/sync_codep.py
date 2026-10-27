#!/usr/bin/env python3
"""Regenerate _data/codep_presentaciones.yml from the candidate write-ups
kept in the documentos-comcom repo, instead of transcribing them by hand.

Usage: scripts/sync_codep.py [--source PATH] [--dry-run]
"""
import argparse
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT.parent / "documentos-comcom" / "CoDep"
DATA_FILE = REPO_ROOT / "_data" / "codep_presentaciones.yml"
YEAR_PAGES_DIR = REPO_ROOT / "codep" / "presentaciones"

YEAR_DIR_RE = re.compile(r"^Candidat[eo]s(\d{4})$")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def prettify(stem):
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", stem)
    return " ".join(w[0].upper() + w[1:] for w in spaced.split())


def clean_line(line):
    # A single trailing space is accidental and forces PyYAML to fall back
    # from literal block style to a quoted scalar; two-or-more is a markdown
    # hard line break and must be kept (normalized to exactly two spaces).
    if not line.strip():
        return ""
    trailing = len(line) - len(line.rstrip(" "))
    stripped = line.rstrip(" \t")
    return stripped + "  " if trailing >= 2 else stripped


def load_candidato(path):
    text = path.read_text(encoding="utf-8")
    body = FRONTMATTER_RE.sub("", text, count=1)
    lines = (clean_line(line) for line in body.strip("\n").split("\n"))
    return {
        "nombre": prettify(path.stem),
        "contenido": "\n".join(lines) + "\n",
    }


def collect(source_dir):
    presentaciones = {}
    for year_dir in sorted(source_dir.iterdir()):
        match = YEAR_DIR_RE.match(year_dir.name)
        if not year_dir.is_dir() or not match:
            continue
        year = int(match.group(1))
        candidatos = [load_candidato(p) for p in year_dir.glob("*.md")]
        candidatos.sort(key=lambda c: c["nombre"])
        presentaciones[year] = candidatos
    return dict(sorted(presentaciones.items()))


def str_presenter(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def write_data_file(presentaciones, dry_run):
    yaml.add_representer(str, str_presenter, Dumper=IndentDumper)
    text = yaml.dump(
        presentaciones,
        Dumper=IndentDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    if dry_run:
        print(f"--- would write {DATA_FILE} ---")
        print(text)
        return
    DATA_FILE.write_text(text, encoding="utf-8")
    print(f"wrote {DATA_FILE}")


def ensure_year_pages(years, dry_run):
    for year in years:
        page = YEAR_PAGES_DIR / f"{year}.md"
        if page.exists():
            continue
        content = (
            "---\n"
            "layout: codep\n"
            f'title: "Presentaciones de candidates a CoDep {year}"\n'
            f"permalink: /codep/presentaciones/{year}/\n"
            f"year: {year}\n"
            "---\n"
        )
        if dry_run:
            print(f"--- would create {page} ---")
            print(content)
            continue
        page.write_text(content, encoding="utf-8")
        print(f"created {page}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.source.is_dir():
        parser.error(f"source directory not found: {args.source}")

    presentaciones = collect(args.source)
    write_data_file(presentaciones, args.dry_run)
    ensure_year_pages(presentaciones.keys(), args.dry_run)


if __name__ == "__main__":
    main()
