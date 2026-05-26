#!/usr/bin/env python3
"""
Migración de slugs legibles a patentes opacas ^[A-Z0-9]{8}$.

Idempotente: si los slugs ya son patentes 8-char, no hace nada.
Aplica a: identidad.slug, aliados[].ref, nemesis[].ref,
          historial[].metadata.ref, historial[].metadata.lider_caido
"""

import re
import sys
from pathlib import Path

# Tabla de mapeo slug_legible → patente opaca
PATENTES = {
    # Confederación
    "aguirre_walter":              "WA3K9F2H",
    "sosa_horacio":                "HS7M4N1P",
    "quiroga_lisandro":            "LQ5C8D3R",
    "funes_dardo":                 "DF2T6G9X",
    "rodriguez_marcela":           "MR4B1K7S",
    "olivares_tomas":              "TO8P5H2N",
    "acosta_ruben":                "RA6N3F1M",
    "pereyra_graciela":            "GP9D7K4C",
    "mendez_ignacio":              "IM1R8T5L",
    "lugones_patricia":            "PL3X2B9K",
    "ramirez_esteban":             "ER7H6N4D",
    # Ejército Rojo
    "mansilla_ramon":              "RM5F3C8T",
    "iturra_delia":                "DI4K9M2P",
    "antinao_hector":              "HA2D7N6B",
    "calfucura_ignacio":           "IC6P1R3X",
    "carcamo_fermin":              "FC8T5H1N",
    "paine_rosa":                  "RP3N2K7M",
    "soriano_norberto":            "NS9B4D5F",
    "belenchini_esteban":          "EB1M6T3R",
    "bordon_luciano":              "LB7C8N2P",
    "maturana_claudio":            "CM4X3F9K",
    "bordagaray_sebastian":        "SB6H1D8T",
    # NPCs sintéticos
    "ricardo_sargento_postmortem": "RS0P2M7N",
    "mentor_metalurgico_bahia_blanca": "MM4B9L1X",
}

PATENTE_RE = re.compile(r'^[A-Z0-9]{8}$')
FIXTURE_DIR = Path(__file__).parent.parent / "mock" / "personajes"
REF_KEYS = {"ref", "lider_caido"}

# --- regex-based replacers (safe: only touch yaml value, not prose) ---

def replace_slug_line(line: str) -> tuple[str, int]:
    """Replace identidad.slug value. Returns (new_line, count_replaced)."""
    m = re.match(r'^(\s+slug:\s+)(\S+)(.*)$', line)
    if m:
        val = m.group(2)
        if val in PATENTES and not PATENTE_RE.match(val):
            return m.group(1) + PATENTES[val] + m.group(3) + "\n", 1
    return line, 0

def replace_ref_line(line: str) -> tuple[str, int]:
    """Replace ref: / lider_caido: values in metadata or aliados/nemesis."""
    for key in REF_KEYS:
        # matches both "    ref: value" and "  - ref: value"
        m = re.match(rf'^(\s+(?:- )?{key}:\s+)(\S+)(.*)$', line)
        if m:
            val = m.group(2)
            if val in PATENTES and not PATENTE_RE.match(val):
                return m.group(1) + PATENTES[val] + m.group(3) + "\n", 1
    return line, 0

def migrate_file(path: Path) -> int:
    """Migrate a single YAML file. Returns count of replacements made."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    new_lines = []
    count = 0
    for line in lines:
        new_line, n = replace_slug_line(line)
        if n == 0:
            new_line, n = replace_ref_line(line)
        new_lines.append(new_line)
        count += n
    if count > 0:
        path.write_text("".join(new_lines), encoding="utf-8")
    return count

def main():
    total = 0
    files = sorted(FIXTURE_DIR.rglob("*.yaml"))
    for f in files:
        n = migrate_file(f)
        if n:
            print(f"  {f.relative_to(FIXTURE_DIR.parent.parent)}: {n} reemplazos")
        total += n
    print(f"\nTotal reemplazos: {total}")
    if total == 0:
        print("(Idempotente: nada que migrar)")

if __name__ == "__main__":
    main()
