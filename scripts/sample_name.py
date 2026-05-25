#!/usr/bin/env python3
"""Sampler del generador de nombres para creación de personaje.

Devuelve (nombre, sobrenombre|None, apellido) según género.
Apodo emerge con 50% de probabilidad.

Uso CLI:
    python3 scripts/sample_name.py [m|f] [N]
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOMBRES_DIR = ROOT / "resources" / "nombres"
APODO_PROB = 0.5


def _load_pairs(path: Path) -> list[tuple[str, str]]:
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        nombre, _, apodo = line.partition("|")
        pairs.append((nombre.strip(), apodo.strip()))
    return pairs


def _load_list(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def sample(genero: str, rng: random.Random | None = None) -> dict[str, str | None]:
    """Devuelve {nombre, sobrenombre, apellido}. genero ∈ {'m', 'f'}."""
    rng = rng or random.Random()
    if genero not in ("m", "f"):
        raise ValueError(f"genero debe ser 'm' o 'f', no {genero!r}")
    fname = "nombres_m.txt" if genero == "m" else "nombres_f.txt"
    nombre, apodo = rng.choice(_load_pairs(NOMBRES_DIR / fname))
    sobrenombre = apodo if rng.random() < APODO_PROB else None
    apellido = rng.choice(_load_list(NOMBRES_DIR / "apellidos.txt"))
    return {"nombre": nombre, "sobrenombre": sobrenombre, "apellido": apellido}


if __name__ == "__main__":
    genero = sys.argv[1] if len(sys.argv) > 1 else "m"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for _ in range(n):
        s = sample(genero)
        apodo = f' "{s["sobrenombre"]}"' if s["sobrenombre"] else ""
        print(f'{s["nombre"]}{apodo} {s["apellido"]}')
