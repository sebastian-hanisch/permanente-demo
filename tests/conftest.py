"""Gemeinsame Fixtures: Mini-Matrizen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Handwerte (per = Permanente = Zahl der perfekten Paarungen, det = Determinante):
* J2 = ((1, 1), (1, 1)): per = 1 · 1 + 1 · 1 = 2, det = 1 · 1 − 1 · 1 = 0.
* T2 = ((1, 1), (0, 1)): nur die Identität zählt (0 · 1 = 0 für die Vertauschung): per = 1, det = 1.
* J3: per = 3! = 6, det = 0 (gleiche Zeilen). Obere Dreiecksmatrix U3 (Einsen auf und über der Diagonale): per = det = 1.
* C3 = ((1, 1, 0), (0, 1, 1), (1, 0, 1)) (Einheitsmatrix plus Kreis der Länge 3): zwei Permutationen (id und der Dreierkreis, gerade): per = 2, det = 2.
* C4 (dasselbe mit 4): id und der Viererkreis (ungerade): per = 2, det = 1 − 1 = 0.
* J − I: Derangements 2, 9, 44 für n = 3, 4, 5; det(J − I) = (−1)^(n − 1) (n − 1): 2, −3, 4."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def ones(n):
    return tuple(tuple(1 for _ in range(n)) for _ in range(n))


def j_minus_i(n):
    return tuple(tuple(int(i != j) for j in range(n)) for i in range(n))


def cycle_plus_identity(n):
    return tuple(tuple(int(j == i or j == (i + 1) % n) for j in range(n)) for i in range(n))


def blocks(k):
    n = 2 * k
    return tuple(tuple(int(i // 2 == j // 2) for j in range(n)) for i in range(n))


@pytest.fixture
def mini():
    return {
        "J2": ((1, 1), (1, 1)),
        "T2": ((1, 1), (0, 1)),
        "J3": ones(3),
        "U3": ((1, 1, 1), (0, 1, 1), (0, 0, 1)),
        "C3": cycle_plus_identity(3),
        "C4": cycle_plus_identity(4),
        "Z2": ((0, 0), (0, 0)),
        "ROW0": ((1, 1), (0, 0)),
    }
