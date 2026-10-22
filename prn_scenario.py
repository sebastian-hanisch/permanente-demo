"""Szenario: 0/1-Matrizen (zufällig, alle Einsen, J − I, Blöcke, Gitter) mit eigenem Zufallsgenerator (SplitMix64, wörtliche Kopie in prn_rng.py), damit alle Instanzen auf jeder Plattform gleich sind.

Eine Matrix ist ein Tupel von Zeilen-Tupeln aus 0 und 1: Zeile = Aufgabe, Spalte = Ressource, 1 = erlaubt; die Permanente zählt die möglichen Zuordnungen (perfekte Paarungen)."""

import prn_algorithm as A
import prn_constants as C
from prn_rng import SplitMix64


def random01(n: int, dens: int, rng: SplitMix64) -> tuple:
    """Jeder Eintrag ist 1 mit Wahrscheinlichkeit dens / 100 (ganzzahlige Prozent: `below(100) < dens`); zeilenweise gezogen."""
    return tuple(tuple(int(rng.below(100) < dens) for _ in range(n)) for _ in range(n))


def full(n: int) -> tuple:
    return tuple((1,) * n for _ in range(n))


def derange(n: int) -> tuple:
    return tuple(tuple(int(i != j) for j in range(n)) for i in range(n))


def blocks(n: int) -> tuple:
    """Blockdiagonale aus n // 2 Blöcken J2; bei ungeradem n steht am Ende ein Block (1)."""
    return tuple(tuple(int(i // 2 == j // 2) for j in range(n)) for i in range(n))


def grid(n: int) -> tuple:
    rows, cols = C.GRID_SHAPES[n]
    return A.grid_biadjacency(rows, cols)[0]


def make_matrix(kind: str, n: int, dens: int, seed: int) -> tuple:
    """Deterministisch aus (Art, n, Dichte, Zufalls-Seed); nur die Art „zufällig“ benutzt Dichte und Seed."""
    if kind == "random":
        return random01(n, dens, SplitMix64(seed))
    if kind == "full":
        return full(n)
    if kind == "derange":
        return derange(n)
    if kind == "blocks":
        return blocks(n)
    if kind == "grid":
        return grid(n)
    raise ValueError(f"unbekannte Matrixart: {kind}")
