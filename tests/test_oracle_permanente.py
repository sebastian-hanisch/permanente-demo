"""Orakel (ORACLE-PLAYBOOK): unabhängige Gegenrechnungen und bekannte Zahlen gegen die ganze Demo.

* Die vier Permanenten-Verfahren (Brute Force, Ryser, Glynn, Bitmasken-DP) und ein fünftes, rekursives in diesem Test stimmen auf Tausenden 0/1-Matrizen überein.
* Sätze: |det| ≤ per und det ≡ per (mod 2) an **allen** 4 × 4-Matrizen; Existenz (augmentierende Wege) genau dann, wenn per > 0.
* Bekannte Zahlen: Derangements über die Rekursion D_n = (n − 1)(D_{n−1} + D_{n−2}), Blöcke 2^k, Domino-Pflasterungen aller Gitter aus einem unabhängigen Zählverfahren (Randprofil), Kasteleyn-Vorzeichen.
* Pólya: alle Vorzeichenmuster von J3 und J4 mit einer zweiten Determinante (Bareiss in ganzen Zahlen statt numpy).
* Schätzer: Erwartungswert **exakt** durch Aufzählung aller Vorzeichen, Varianz der Blöcke 2^k − 1 durch Aufzählung für k = 1 bis 4.
* Die Auswertung (`prn_evaluation`) läuft über ein Raster von Einstellungen ohne Prüffehler."""

import itertools
import math
from fractions import Fraction
from functools import lru_cache

import numpy as np
import pytest

import prn_algorithm as A
import prn_constants as C
import prn_evaluation as ev
from prn_rng import SplitMix64
from prn_scenario import random01


def _per_recursive(m):
    """Fünfte Fassung: Rekursion über die Zeilen mit den benutzten Spalten als Menge (Gedächtnis), ganz ohne Bitmasken-Arrays."""
    n = len(m)

    @lru_cache(maxsize=None)
    def go(row, used):
        if row == n:
            return 1
        return sum(go(row + 1, used | 1 << j) for j in range(n) if m[row][j] and not used >> j & 1)

    return go(0, 0)


def _all_matrices(n):
    for bits in itertools.product((0, 1), repeat=n * n):
        yield tuple(tuple(bits[i * n:(i + 1) * n]) for i in range(n))


def test_all_per_methods_agree_on_every_3x3_matrix():
    for m in _all_matrices(3):
        expected = A.per_brute(m)[0]
        assert A.per_ryser(m)[0] == A.per_glynn(m)[0] == A.per_dp(m) == _per_recursive(m) == expected, m


def test_all_per_methods_agree_on_random_matrices_of_every_density_and_size():
    rng = SplitMix64(2024)
    checked = 0
    for n, count in ((4, 600), (5, 150), (6, 60), (7, 15), (8, 5)):
        for i in range(count):
            m = random01(n, 10 + 10 * (i % 9), rng)
            expected = A.per_brute(m)[0]
            assert A.per_ryser(m)[0] == A.per_glynn(m)[0] == A.per_dp(m) == _per_recursive(m) == expected, m
            checked += 1
    assert checked == 830


def test_dp_glynn_and_recursion_agree_up_to_n_12():
    rng = SplitMix64(7)
    for n in (9, 10, 11, 12):
        for dens in (30, 60, 90):
            m = random01(n, dens, rng)
            assert A.per_glynn(m)[0] == A.per_dp(m) == _per_recursive(m)


def test_theorems_on_every_4x4_matrix():
    """|det| ≤ per, det ≡ per (mod 2), Existenz genau bei per > 0: an allen 65.536 Matrizen; Bareiss gegen numpy an jeder 997. Matrix."""
    n = 4
    for m in _all_matrices(n):
        per = _per_recursive(m)
        det = A.det_bareiss(m)[0]
        assert abs(det) <= per and (per - det) % 2 == 0, m
        assert A.has_perfect_matching(m) == (per > 0), m
    for m in itertools.islice(_all_matrices(n), 0, 65536, 997):
        assert A.det_bareiss(m)[0] == round(np.linalg.det(np.array(m, dtype=float)))


def test_derangements_follow_the_recurrence():
    d = {0: 1, 1: 0}
    for n in range(2, 13):
        d[n] = (n - 1) * (d[n - 1] + d[n - 2])
    for n in range(2, 13):
        j_minus_i = tuple(tuple(int(i != j) for j in range(n)) for i in range(n))
        assert A.per_dp(j_minus_i) == d[n]
    assert d[7] == 1854 and d[12] == 176_214_841


def test_blocks():
    for k in range(1, 8):
        m = tuple(tuple(int(i // 2 == j // 2) for j in range(2 * k)) for i in range(2 * k))
        assert A.per_dp(m) == 2 ** k


def _tilings(rows, cols):
    """Unabhängige Zählung der Domino-Pflasterungen: Zelle für Zelle mit einer Randmaske der nächsten `cols` Zellen (Broken-Profile-DP)."""
    @lru_cache(maxsize=None)
    def go(pos, mask):
        if pos == rows * cols:
            return int(mask == 0)
        if mask & 1:
            return go(pos + 1, mask >> 1)
        total = 0
        r, c = divmod(pos, cols)
        if c + 1 < cols and not mask >> 1 & 1:
            total += go(pos + 1, (mask >> 1) | 1)                           # waagerecht: die Nachbarzelle ist mit belegt
        if r + 1 < rows:
            total += go(pos + 1, (mask >> 1) | 1 << (cols - 1))              # senkrecht: die Zelle darunter wird belegt
        return total

    return go(0, 0)


def test_the_independent_tiling_counter_knows_the_classic_numbers():
    assert [_tilings(2, n) for n in range(1, 9)] == [1, 2, 3, 5, 8, 13, 21, 34] and _tilings(4, 4) == 36 and _tilings(6, 6) == 6728 and _tilings(8, 8) == 12_988_816


@pytest.mark.parametrize("n", sorted(C.GRID_SHAPES))
def test_every_grid_shape_gives_n_black_and_n_white_cells_and_the_right_count(n):
    rows, cols = C.GRID_SHAPES[n]
    matrix, black, white = A.grid_biadjacency(rows, cols)
    assert len(black) == len(white) == n and rows * cols == 2 * n
    assert A.per_dp(matrix) == _tilings(rows, cols)
    assert abs(A.det_bareiss(A.kasteleyn_signed(rows, cols))[0]) == _tilings(rows, cols)


def test_kasteleyn_shapes_all_work():
    for rows, cols in ev.KASTELEYN_SHAPES:
        assert abs(A.det_bareiss(A.kasteleyn_signed(rows, cols))[0]) == _tilings(rows, cols)


def test_polya_patterns_of_j3_and_j4_with_a_second_determinant():
    for n, expected in ((3, {0: 320, 4: 192}), (4, {0: 43264, 8: 21504, 16: 768})):
        counts = {}
        for signs in itertools.product((1, -1), repeat=n * n):
            m = [list(signs[i * n:(i + 1) * n]) for i in range(n)]
            d = abs(A.det_bareiss(m)[0])
            counts[d] = counts.get(d, 0) + 1
        assert dict(sorted(counts.items())) == expected and A.sign_pattern_counts(tuple((1,) * n for _ in range(n))) == expected
        assert math.factorial(n) not in counts                                                # nie |det| = n!


def _moments(m):
    """Exakter Erwartungswert und Varianz von X = det(A ∘ S)^2 über alle Vorzeichen S auf den Einsen."""
    dets = A.all_sign_dets(m)
    xs = [int(d) ** 2 for d in dets]
    mean = Fraction(sum(xs), len(xs))
    var = Fraction(sum(x * x for x in xs), len(xs)) - mean ** 2
    return mean, var


@pytest.mark.parametrize("m", [((1, 1), (1, 1)), ((1,) * 3,) * 3, ((1,) * 4,) * 4, ((1, 1, 0), (0, 1, 1), (1, 0, 1)), ((1, 1, 0, 0), (1, 1, 1, 0), (0, 1, 1, 1), (0, 0, 1, 1)),
                               ((1, 0, 1, 1), (1, 1, 0, 0), (0, 1, 1, 1), (1, 0, 1, 0))])
def test_the_estimator_is_exactly_unbiased(m):
    mean, _ = _moments(m)
    assert mean == A.per_dp(m) == A.per_brute(m)[0]


@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_block_variance_by_exhaustion(k):
    m = tuple(tuple(int(i // 2 == j // 2) for j in range(2 * k)) for i in range(2 * k))
    mean, var = _moments(m)
    assert mean == 2 ** k and var / mean ** 2 == A.block_variance(k) == 2 ** k - 1


def test_random_estimates_scatter_around_the_permanent_within_six_standard_errors():
    for name, m in (("J3", ((1,) * 3,) * 3), ("C3", ((1, 1, 0), (0, 1, 1), (1, 0, 1))), ("J2", ((1, 1), (1, 1)))):
        e = ev.estimate(m, 20000, 99)
        assert abs(float(e.mean) - A.per_dp(m)) <= 6 * e.std_error, name


def test_the_evaluation_runs_over_a_grid_without_validation_errors():
    for kind in C.KINDS:
        for n in (2, 3, 5, 8, 12, 14):
            for dens in (20, 50, 80):
                a = ev.analyse(ev.Settings(n=n, seed=100 + n + dens, kind=kind, dens=dens, samples=100))
                assert ev.validation_errors(a) == [], (kind, n, dens)
                assert ev.verdict_main(a)[0] in ("info", "success", "warning")


def test_the_full_sweeps_hold_the_theorems():
    rows = ev.sweep_det()
    assert all(r["bound_all"] and r["parity_all"] for r in rows) and ev.verdict_det_sweep(rows)[0] == "info"
    assert ev.verdict_polya(ev.polya_rows())[0] == "info" and ev.verdict_kasteleyn(ev.kasteleyn_rows())[0] == "success"
