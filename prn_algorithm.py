"""Kern: Permanente (Brute Force, Ryser, Glynn, Bitmasken-DP) und Determinante (Bareiss) auf 0/1-Matrizen, Existenz einer perfekten Paarung, Vorzeichenmuster, Gitter-Matrizen und der Godsil–Gutman-Schätzer.

Jede Einheit ist eine Funktion (DEMO-PLAYBOOK §1b). Gezählt werden **Multiplikationen** (ein Produkt von n Faktoren kostet n − 1), nie Sekunden. Alle Anzahlen sind ganze Zahlen (exakt), Anteile Brüche.

Die Permanente einer 0/1-Matrix ist die Zahl der perfekten Paarungen des bipartiten Graphen (Zeilen gegen Spalten): per(A) = Σ_π Π_i a_{i,π(i)}. Die Determinante hat dieselbe Summe mit dem Vorzeichen sgn(π)."""

import itertools
import math
from collections import Counter

import numpy as np

PER_N_MAX = 20            # per ≤ n! < 2^63 für n ≤ 20: Bitmasken-DP mit int64


def _check_square(a) -> int:
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("a muss eine nichtleere quadratische Matrix sein")
    return n


# --- Kosten (Multiplikationen, geschlossene Formeln) -------------------------------------------------------------------------------------------


def mults_brute(n: int) -> int:
    """n! Permutationen, je ein Produkt aus n Faktoren (n − 1 Multiplikationen)."""
    return math.factorial(n) * (n - 1)


def mults_ryser(n: int) -> int:
    """2^n − 1 nichtleere Spaltenteilmengen, je ein Produkt aus n Zeilensummen."""
    return (2 ** n - 1) * (n - 1)


def mults_glynn(n: int) -> int:
    """2^(n − 1) Vorzeichenvektoren (Gray-Code), je ein Produkt aus n Zeilensummen."""
    return 2 ** (n - 1) * (n - 1)


def mults_det(n: int) -> int:
    """Bareiss ohne vorzeitiges Ende: Schritt k aktualisiert (n − 1 − k)^2 Einträge mit je zwei Multiplikationen: 2 · Σ m^2 für m = 1 … n − 1."""
    return (n - 1) * n * (2 * n - 1) // 3


# --- Permanente ----------------------------------------------------------------------------------------------------------------------------


def per_brute(a) -> tuple:
    """Definition: Summe über alle n! Permutationen; Rückgabe (Wert, Multiplikationen)."""
    n = _check_square(a)
    total = sum(math.prod(a[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))
    return total, mults_brute(n)


def per_ryser(a) -> tuple:
    """Ryser: per = (−1)^n Σ_{S ⊆ Spalten, S ≠ ∅} (−1)^|S| Π_i Σ_{j ∈ S} a_ij; Rückgabe (Wert, Multiplikationen)."""
    n = _check_square(a)
    total = 0
    for mask in range(1, 1 << n):
        cols = [j for j in range(n) if mask >> j & 1]
        prod = 1
        for i in range(n):
            prod *= sum(a[i][j] for j in cols)
        total += (-1) ** len(cols) * prod
    return (-1) ** n * total, mults_ryser(n)


def per_glynn(a) -> tuple:
    """Glynn: per = 2^(−(n − 1)) Σ_δ (Π_k δ_k) Π_i Σ_j δ_j a_ij über δ ∈ {±1}^n mit δ_n = +1. Die 2^(n − 1) Vektoren werden im Gray-Code durchlaufen (je Schritt kippt ein Vorzeichen, die
    Zeilensummen ändern sich um ± 2 a_ij). Rückgabe (Wert, Multiplikationen)."""
    n = _check_square(a)
    delta = [1] * n
    sums = [sum(row) for row in a]
    total = math.prod(sums)
    sign = 1
    for k in range(1, 1 << (n - 1)):
        j = (k & -k).bit_length() - 1
        delta[j] = -delta[j]
        for i in range(n):
            sums[i] += 2 * delta[j] * a[i][j]
        sign = -sign
        total += sign * math.prod(sums)
    value, rest = divmod(total, 1 << (n - 1))
    if rest:
        raise ArithmeticError("Glynn-Summe nicht durch 2^(n − 1) teilbar")
    return value, mults_glynn(n)


def per_dp(a) -> int:
    """Drittes, unabhängiges Verfahren: Bitmasken-DP über die Zeilen (dp[S] = Zahl der Zuordnungen der ersten |S| Zeilen auf die Spaltenmenge S). Mit numpy (int64, per ≤ n! < 2^63 für n ≤ 20)."""
    n = _check_square(a)
    if n > PER_N_MAX:
        raise ValueError(f"n muss höchstens {PER_N_MAX} sein")
    dp = np.zeros(1 << n, dtype=np.int64)
    dp[0] = 1
    for i in range(n):
        new = np.zeros(1 << n, dtype=np.int64)
        for j in range(n):
            if a[i][j]:
                src = dp.reshape(-1, 2, 1 << j)[:, 0, :]
                new.reshape(-1, 2, 1 << j)[:, 1, :] += src
        dp = new
    return int(dp[(1 << n) - 1])


# --- Determinante ---------------------------------------------------------------------------------------------------------------------------


def det_bareiss(a) -> tuple:
    """Determinante in ganzen Zahlen (Bareiss, ohne Brüche); Rückgabe (Wert, Multiplikationen). Findet sich in einer Spalte kein Pivot, ist die Determinante 0 und das Verfahren endet dort."""
    n = _check_square(a)
    m = [list(row) for row in a]
    sign, prev, mults = 1, 1, 0
    for k in range(n - 1):
        if m[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if m[r][k] != 0), None)
            if swap is None:
                return 0, mults
            m[k], m[swap] = m[swap], m[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
                mults += 2
        prev = m[k][k]
    return sign * m[n - 1][n - 1], mults


# --- Existenz -------------------------------------------------------------------------------------------------------------------------------


def matching_size(a) -> int:
    """Größe einer größten Paarung (augmentierende Wege nach Kuhn): Existenz ohne Zählen, polynomiell."""
    n = _check_square(a)
    match = [-1] * n

    def augment(i, seen):
        for j in range(n):
            if a[i][j] and not seen[j]:
                seen[j] = True
                if match[j] == -1 or augment(match[j], seen):
                    match[j] = i
                    return True
        return False

    return sum(augment(i, [False] * n) for i in range(n))


def has_perfect_matching(a) -> bool:
    return matching_size(a) == len(a)


# --- Vorzeichen: kann man die Permanente in eine Determinante verwandeln? (Pólya) ------------------------------------------------------------

SIGN_ONES_MAX = 16        # höchstens 2^16 Vorzeichenmuster


def all_sign_dets(a) -> np.ndarray:
    """Determinanten (ganzzahlig, mit Vorzeichen) aller 2^e Matrizen, die aus a entstehen, wenn jede der e Einsen +1 oder −1 wird; Reihenfolge: Bit i des Index = Vorzeichen der i-ten Eins
    (zeilenweise), gesetzt = −1. Gleitkomma-Determinante, auf ganze Zahlen gerundet (bei höchstens 16 Einsen exakt)."""
    n = _check_square(a)
    ones = [(i, j) for i in range(n) for j in range(n) if a[i][j]]
    e = len(ones)
    if e > SIGN_ONES_MAX:
        raise ValueError(f"höchstens {SIGN_ONES_MAX} Einsen, gefunden {e}")
    idx = np.arange(1 << e, dtype=np.int64)
    signs = 1.0 - 2.0 * ((idx[:, None] >> np.arange(e, dtype=np.int64)) & 1)
    mats = np.zeros((1 << e, n, n))
    if e:
        mats[:, [i for i, _ in ones], [j for _, j in ones]] = signs
    dets = np.linalg.det(mats)
    rounded = np.rint(dets)
    if np.max(np.abs(dets - rounded)) > 1e-6:
        raise ArithmeticError("Determinante nicht ganzzahlig genug")
    return rounded.astype(np.int64)


def sign_pattern_counts(a) -> Counter:
    """Wie oft kommt jeder Betrag |det| unter allen Vorzeichenmustern vor?"""
    return Counter(int(abs(d)) for d in all_sign_dets(a))


# --- Gitter (Domino-Pflasterungen) -----------------------------------------------------------------------------------------------------------


def grid_biadjacency(rows: int, cols: int) -> tuple:
    """Biadjazenzmatrix des Gitters rows × cols (schwarze Zellen gegen weiße, Zellen mit gerader Koordinatensumme sind schwarz): ein Eintrag 1 je Paar benachbarter Zellen = ein Domino; die Permanente zählt
    die Pflasterungen. Rückgabe (Matrix, schwarze Zellen, weiße Zellen); rows · cols muss gerade sein."""
    if rows * cols % 2:
        raise ValueError("rows · cols muss gerade sein")
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    black = [x for x in cells if sum(x) % 2 == 0]
    white = [x for x in cells if sum(x) % 2 == 1]
    matrix = tuple(tuple(int(abs(b[0] - w[0]) + abs(b[1] - w[1]) == 1) for w in white) for b in black)
    return matrix, black, white


def kasteleyn_signed(rows: int, cols: int) -> tuple:
    """Dieselbe Matrix mit Vorzeichen −1 an den **senkrechten** Kanten in ungeraden Spalten (Zählung der Spalten ab 0). Auf Gittern ist dann |det| = per (Kasteleyn-Vorzeichen für Gitter)."""
    matrix, black, white = grid_biadjacency(rows, cols)
    out = []
    for i, b in enumerate(black):
        row = []
        for j, w in enumerate(white):
            vertical = b[1] == w[1]
            row.append(-matrix[i][j] if vertical and b[1] % 2 == 1 else matrix[i][j])
        out.append(tuple(row))
    return tuple(out)


# --- Godsil–Gutman-Schätzer --------------------------------------------------------------------------------------------------------------------

EST_N_MAX = 14            # Hadamard-Schranke 14^7 ≈ 1,05 · 10^8: die Gleitkomma-Determinante ist auf ganze Zahlen genau


def random_signs(rng, count: int, n: int) -> np.ndarray:
    """count Vorzeichenmatrizen n × n aus dem Strom des Generators: je 64-Bit-Wort 64 Vorzeichen, Bit i (niedrigstes zuerst) gesetzt = +1, sonst −1; die Matrizen werden zeilenweise nacheinander befüllt."""
    need = count * n * n
    words = np.array([rng.next() for _ in range((need + 63) // 64)], dtype=np.uint64)
    bits = ((words[:, None] >> np.arange(64, dtype=np.uint64)) & np.uint64(1)).reshape(-1)[:need].astype(np.int64)
    return (2 * bits - 1).reshape(count, n, n)


def gg_values(a, signs) -> np.ndarray:
    """Die Stichprobenwerte X = det(A ∘ S)^2 (ganze Zahlen) für die Vorzeichenmatrizen S: E[X] = per(A) (Godsil und Gutman)."""
    n = _check_square(a)
    if n > EST_N_MAX:
        raise ValueError(f"n muss höchstens {EST_N_MAX} sein")
    dets = np.linalg.det(signs * np.array(a, dtype=np.int64))
    rounded = np.rint(dets)
    if np.max(np.abs(dets - rounded)) > 1e-3:
        raise ArithmeticError("Determinante nicht ganzzahlig genug")
    d = rounded.astype(np.int64)
    return d * d


def block_variance(k: int) -> int:
    """Blockdiagonale aus k Blöcken J_2 (alle Einsen, 2 × 2): per = 2^k und Var(X) / per^2 = 2^k − 1 (jeder Block: X_b ∈ {0, 4} gleich wahrscheinlich, E = 2, E[X_b^2] = 8, Verhältnis 2; Blöcke unabhängig)."""
    if k < 0:
        raise ValueError("k muss >= 0 sein")
    return 2 ** k - 1
