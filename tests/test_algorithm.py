"""Jede Einheit des Kerns an Handwerten (tests/conftest.py) und an ihren Zweigen."""

import math
from collections import Counter

import numpy as np
import pytest
from conftest import blocks, j_minus_i, ones

import prn_algorithm as A
from prn_rng import SplitMix64

ALL_PER = (A.per_brute, A.per_ryser, A.per_glynn)


# --- Kosten ----------------------------------------------------------------------------------------------------------------------------------


def test_cost_formulas_at_hand_values():
    """n = 3: Brute Force 6 Permutationen · 2 = 12; Ryser 7 Teilmengen · 2 = 14; Glynn 4 Vektoren · 2 = 8; Determinante 2 · (2^2 + 1^2) = 10."""
    assert (A.mults_brute(3), A.mults_ryser(3), A.mults_glynn(3), A.mults_det(3)) == (12, 14, 8, 10)
    assert (A.mults_brute(1), A.mults_ryser(1), A.mults_glynn(1), A.mults_det(1)) == (0, 0, 0, 0)
    assert (A.mults_brute(2), A.mults_ryser(2), A.mults_glynn(2), A.mults_det(2)) == (2, 3, 2, 2)
    assert A.mults_det(20) == 4940 and A.mults_glynn(20) == 19 * 2 ** 19 == 9_961_472 and A.mults_ryser(20) == 19 * (2 ** 20 - 1) == 19_922_925


def test_det_cost_formula_equals_the_sum_of_updates():
    for n in range(1, 25):
        assert A.mults_det(n) == 2 * sum(m * m for m in range(1, n))


# --- Permanente: Handwerte ---------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("fn", ALL_PER)
def test_permanent_hand_values(fn, mini):
    assert fn(mini["J2"])[0] == 2 and fn(mini["T2"])[0] == 1 and fn(mini["J3"])[0] == 6 and fn(mini["U3"])[0] == 1
    assert fn(mini["C3"])[0] == 2 and fn(mini["C4"])[0] == 2 and fn(mini["Z2"])[0] == 0 and fn(mini["ROW0"])[0] == 0


@pytest.mark.parametrize("fn", ALL_PER)
def test_permanent_of_ones_is_n_factorial_and_of_j_minus_i_the_derangements(fn):
    assert [fn(ones(n))[0] for n in range(1, 7)] == [1, 2, 6, 24, 120, 720]
    assert [fn(j_minus_i(n))[0] for n in range(2, 7)] == [1, 2, 9, 44, 265]


@pytest.mark.parametrize("fn", ALL_PER)
def test_permanent_of_blocks_is_two_to_the_k(fn):
    assert [fn(blocks(k))[0] for k in (1, 2, 3, 4)] == [2, 4, 8, 16]


@pytest.mark.parametrize("fn", ALL_PER)
def test_permanent_of_a_single_entry_and_the_identity(fn):
    assert fn(((1,),))[0] == 1 and fn(((0,),))[0] == 0
    assert fn(tuple(tuple(int(i == j) for j in range(5)) for i in range(5)))[0] == 1


def test_permanent_costs_are_the_formulas():
    a = ones(4)
    assert A.per_brute(a)[1] == A.mults_brute(4) and A.per_ryser(a)[1] == A.mults_ryser(4) and A.per_glynn(a)[1] == A.mults_glynn(4)


def test_permanent_rejects_non_square_and_empty():
    for fn in ALL_PER + (A.det_bareiss, A.per_dp, A.matching_size):
        with pytest.raises(ValueError):
            fn(())
        with pytest.raises(ValueError):
            fn(((1, 1), (1,)))


def test_dp_agrees_with_the_hand_values_and_has_a_size_limit(mini):
    assert A.per_dp(mini["J3"]) == 6 and A.per_dp(mini["C4"]) == 2 and A.per_dp(mini["Z2"]) == 0 and A.per_dp(j_minus_i(5)) == 44
    assert A.per_dp(ones(20)) == math.factorial(20)
    with pytest.raises(ValueError):
        A.per_dp(ones(21))


# --- Determinante -----------------------------------------------------------------------------------------------------------------------------


def test_determinant_hand_values(mini):
    assert A.det_bareiss(mini["J2"])[0] == 0 and A.det_bareiss(mini["T2"])[0] == 1 and A.det_bareiss(mini["J3"])[0] == 0
    assert A.det_bareiss(mini["U3"])[0] == 1 and A.det_bareiss(mini["C3"])[0] == 2 and A.det_bareiss(mini["C4"])[0] == 0
    assert A.det_bareiss(((3,),))[0] == 3 and A.det_bareiss(((0,),))[0] == 0
    assert [A.det_bareiss(j_minus_i(n))[0] for n in (3, 4, 5)] == [2, -3, 4]


def test_determinant_swaps_rows_when_the_pivot_is_zero():
    assert A.det_bareiss(((0, 1), (1, 0))) == (-1, 2)                     # eine Vertauschung: Vorzeichen −1, danach die übliche Aktualisierung (2 Multiplikationen)
    assert A.det_bareiss(((0, 1, 0), (0, 0, 1), (1, 0, 0)))[0] == 1       # Dreierkreis: gerade
    assert A.det_bareiss(((0, 1, 2), (1, 0, 3), (4, 5, 6)))[0] == 0 * (0 * 6 - 3 * 5) - 1 * (1 * 6 - 3 * 4) + 2 * (1 * 5 - 0 * 4)


def test_determinant_stops_when_a_column_has_no_pivot():
    value, mults = A.det_bareiss(((0, 1, 1), (0, 1, 0), (0, 0, 1)))
    assert value == 0 and mults == 0
    value, mults = A.det_bareiss(((1, 1, 1), (1, 1, 0), (1, 1, 1)))      # Schritt 0: 4 Einträge · 2 Multiplikationen; danach ist Spalte 1 unter dem Pivot leer
    assert value == 0 and mults == 8


def test_determinant_cost_equals_the_formula_when_all_pivots_exist():
    for n in range(1, 9):
        identity = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
        assert A.det_bareiss(identity) == (1, A.mults_det(n))


def test_determinant_agrees_with_numpy_on_integer_matrices():
    rng = SplitMix64(5)
    for n in range(1, 8):
        for _ in range(10):
            m = [[rng.below(5) - 2 for _ in range(n)] for _ in range(n)]
            assert A.det_bareiss(m)[0] == round(np.linalg.det(np.array(m, float)))


# --- Existenz ---------------------------------------------------------------------------------------------------------------------------------


def test_matching_size_and_existence(mini):
    assert A.matching_size(mini["J2"]) == 2 and A.has_perfect_matching(mini["T2"])
    assert A.matching_size(mini["ROW0"]) == 1 and not A.has_perfect_matching(mini["ROW0"])
    assert A.matching_size(mini["Z2"]) == 0
    assert A.matching_size(((1, 0), (1, 0))) == 1                          # beide Zeilen wollen Spalte 0
    assert A.matching_size(((1, 1, 0), (1, 0, 0), (0, 0, 0))) == 2


def test_matching_needs_an_augmenting_path():
    """Zeile 0 nimmt zuerst Spalte 0; Zeile 1 kann nur Spalte 0: der Weg muss Zeile 0 auf Spalte 1 umlenken."""
    assert A.has_perfect_matching(((1, 1), (1, 0)))
    assert A.has_perfect_matching(((1, 1, 0), (1, 0, 1), (0, 1, 0)))


# --- Vorzeichenmuster ---------------------------------------------------------------------------------------------------------------------------


def test_sign_patterns_of_j2_and_j3(mini):
    """J2: 16 Muster, bei 8 ist det = ±(1 · 1 ∓ …) = ±2 (die beiden Produkte gleich bezeichnet vorzeichenverschieden), bei 8 gleich 0."""
    assert A.sign_pattern_counts(mini["J2"]) == Counter({0: 8, 2: 8})
    assert A.sign_pattern_counts(mini["J3"]) == Counter({0: 320, 4: 192})


def test_sign_patterns_with_few_ones(mini):
    assert A.sign_pattern_counts(((1,),)) == Counter({1: 2})
    assert A.sign_pattern_counts(mini["Z2"]) == Counter({0: 1})                        # eine leere Musterliste: nur das Nullmuster
    assert A.sign_pattern_counts(mini["T2"]) == Counter({1: 8})                        # det = ±1 · 1 ∓ 0: immer ±1
    assert sorted(A.all_sign_dets(((1,),))) == [-1, 1]


def test_sign_patterns_index_order():
    """Bit i des Index = Vorzeichen der i-ten Eins (zeilenweise), gesetzt = −1. Index 0: ((+,+),(+,+)) → 1 − 1 = 0; 1: ((−,+),(+,+)) → −1 − 1 = −2; 2: ((+,−),(+,+)) → 1 + 1 = 2; 3: ((−,−),(+,+)) → −1 + 1 = 0."""
    dets = A.all_sign_dets(((1, 1), (1, 1)))
    assert list(dets[:4]) == [0, -2, 2, 0] and len(dets) == 16


def test_sign_patterns_limit():
    A.all_sign_dets(ones(4))                                                           # 16 Einsen: erlaubt
    with pytest.raises(ValueError):
        A.all_sign_dets(ones(5))                                                      # 25 Einsen: zu viele


# --- Gitter -----------------------------------------------------------------------------------------------------------------------------------


def test_grid_biadjacency_2x2_and_2x3():
    matrix, black, white = A.grid_biadjacency(2, 2)
    assert black == [(0, 0), (1, 1)] and white == [(0, 1), (1, 0)] and matrix == ((1, 1), (1, 1))
    matrix, black, white = A.grid_biadjacency(2, 3)
    assert len(black) == len(white) == 3 and sum(map(sum, matrix)) == 7                      # 2 · 3 Gitter hat 7 Kanten
    assert A.per_glynn(matrix)[0] == 3


def test_grid_requires_an_even_number_of_cells():
    with pytest.raises(ValueError):
        A.grid_biadjacency(3, 3)
    with pytest.raises(ValueError):
        A.kasteleyn_signed(1, 3)


def test_kasteleyn_signs_on_the_2x2_grid():
    """Schwarz (0,0), (1,1); weiß (0,1), (1,0). Senkrecht in Spalte 1 (ungerade): Eintrag (1,1)–(0,1) wird −1."""
    assert A.kasteleyn_signed(2, 2) == ((1, 1), (-1, 1))
    assert A.det_bareiss(A.kasteleyn_signed(2, 2))[0] == 2


@pytest.mark.parametrize("rows, cols, tilings", [(2, 2, 2), (2, 3, 3), (2, 4, 5), (2, 8, 34), (3, 4, 11), (4, 4, 36), (4, 5, 95), (6, 6, 6728)])
def test_kasteleyn_signs_make_the_determinant_count_the_tilings(rows, cols, tilings):
    matrix, _, _ = A.grid_biadjacency(rows, cols)
    assert A.per_glynn(matrix)[0] == tilings
    assert abs(A.det_bareiss(A.kasteleyn_signed(rows, cols))[0]) == tilings


def test_other_sign_rules_do_not_work():
    """Dieselbe Matrix mit allen senkrechten Kanten −1 zählt nicht (2 × 8: 0 statt 34)."""
    matrix, black, white = A.grid_biadjacency(2, 8)
    every = [[-x if b[1] == w[1] else x for x, w in zip(row, white)] for row, b in zip(matrix, black)]
    assert abs(A.det_bareiss(every)[0]) != 34


# --- Schätzer ---------------------------------------------------------------------------------------------------------------------------------


def test_random_signs_follow_the_bits_of_the_stream():
    word = SplitMix64(0).next()
    signs = A.random_signs(SplitMix64(0), 1, 2)
    assert signs.shape == (1, 2, 2) and signs.dtype == np.int64
    assert [int(x) for x in signs.reshape(-1)] == [1 if word >> i & 1 else -1 for i in range(4)]


def test_random_signs_cross_the_word_boundary_and_are_deterministic():
    r = SplitMix64(3)
    words = [r.next() for _ in range(2)]
    signs = A.random_signs(SplitMix64(3), 2, 6)                                         # 72 Vorzeichen: 64 aus Wort 0, 8 aus Wort 1
    flat = [int(x) for x in signs.reshape(-1)]
    assert flat[:64] == [1 if words[0] >> i & 1 else -1 for i in range(64)] and flat[64:] == [1 if words[1] >> i & 1 else -1 for i in range(8)]
    assert np.array_equal(signs, A.random_signs(SplitMix64(3), 2, 6))
    assert set(flat) <= {-1, 1}


def test_gg_values_hand_value_on_j2(mini):
    """det((+,+),(+,−)) = −2 → X = 4; det((+,+),(+,+)) = 0 → X = 0."""
    signs = np.array([[[1, 1], [1, -1]], [[1, 1], [1, 1]]])
    assert list(A.gg_values(mini["J2"], signs)) == [4, 0]


def test_gg_values_respect_the_zero_pattern(mini):
    signs = np.array([[[-1, -1], [-1, -1]]])
    assert list(A.gg_values(mini["T2"], signs)) == [1]                                  # det((−1, −1), (0, −1)) = 1


def test_gg_limit():
    with pytest.raises(ValueError):
        A.gg_values(ones(15), np.ones((1, 15, 15), dtype=np.int64))
    assert list(A.gg_values(ones(1), np.ones((1, 1, 1), dtype=np.int64))) == [1]


def test_block_variance():
    assert [A.block_variance(k) for k in range(0, 6)] == [0, 1, 3, 7, 15, 31]
    with pytest.raises(ValueError):
        A.block_variance(-1)


def test_random_signs_word_count_is_exact_when_the_bit_count_is_one_above_a_multiple_of_64():
    """need = count · n² = 1, 65, 129 (≡ 1 mod 64): ein Wort zu wenig würde die Form brechen."""
    for count, n in ((1, 1), (65, 1), (129, 1), (1, 8), (2, 6), (13, 5)):
        signs = A.random_signs(SplitMix64(count + n), count, n)
        assert signs.shape == (count, n, n)
    assert A.random_signs(SplitMix64(0), 1, 1).tolist() == [[[1 if SplitMix64(0).next() & 1 else -1]]]
