"""Auswertung: Kennzahlen an Handwerten, jeder Zweig von validation_errors (mit Grenzfällen), Messreihen gegen eine unabhängige Nachrechnung."""

import itertools
import math
import statistics
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest

import prn_algorithm as A
import prn_constants as C
import prn_evaluation as ev
from prn_rng import SplitMix64
from prn_scenario import make_matrix, random01


def _base(**kw):
    return ev.analyse(ev.Settings(**kw))


def _errors(a):
    return ev.validation_errors(a)


def _has(a, part):
    return any(part in e for e in _errors(a))


# --- Kennzahlen an Handwerten --------------------------------------------------------------------------------------------------------------


def test_lehrbeispiel_j3():
    a = _base(n=3, kind="full")
    assert (a.per, a.det, a.exists, a.ones) == (6, 0, True, 9)
    assert (a.per_mults, a.ryser_mults, a.brute_mults) == (8, 14, 12) and a.ratio == 0
    assert a.det_mults == 8                                                                       # J3 ist singulär: das Verfahren endet nach Schritt 1


def test_derangements_and_blocks():
    assert [_base(n=n, kind="derange").per for n in (3, 4, 5, 7)] == [2, 9, 44, 1854]
    assert [_base(n=n, kind="derange").det for n in (3, 4, 5, 7)] == [2, -3, 4, 6]
    assert [_base(n=n, kind="blocks").per for n in (2, 4, 6, 12, 7)] == [2, 4, 8, 64, 8]


def test_a_matrix_without_a_perfect_matching():
    a = _base(n=10, dens=20)                                                                      # Standardseed: Dichte 20 % ohne perfekte Paarung
    assert not a.exists and a.per == 0 and a.ratio is None and a.estimate.mean == 0 and a.estimate.nonzero == 0
    assert _errors(a) == []


def test_ratio_is_an_exact_fraction():
    a = _base()
    assert a.ratio == Fraction(abs(a.det), a.per) and (a.per - a.det) % 2 == 0


def test_estimate_is_none_above_the_limit_and_present_at_the_limit():
    assert _base(n=C.EST_N_MAX).estimate is not None and _base(n=C.EST_N_MAX + 1).estimate is None


def test_analysis_uses_all_settings():
    a = _base(n=6, seed=7, kind="random", dens=70, samples=100)
    assert len(a.matrix) == 6 and a.matrix == make_matrix("random", 6, 70, 7) and a.estimate.samples == 100


# --- Schätzer -------------------------------------------------------------------------------------------------------------------------------


def test_estimate_is_deterministic_and_depends_on_the_seed():
    m = make_matrix("full", 4, 50, 0)
    assert ev.estimate(m, 200, 5) == ev.estimate(m, 200, 5) and ev.estimate(m, 200, 5) != ev.estimate(m, 200, 6)


def test_estimate_of_the_identity_is_exactly_one():
    identity = tuple(tuple(int(i == j) for j in range(5)) for i in range(5))
    e = ev.estimate(identity, 50, 1)
    assert e.mean == 1 and e.std_error == 0.0 and e.nonzero == 50 and e.maximum == 1


def test_estimate_of_a_single_sample_has_no_standard_error():
    e = ev.estimate(make_matrix("full", 3, 50, 0), 1, 3)
    assert e.std_error == 0.0 and e.samples == 1 and e.nonzero in (0, 1)


def test_estimate_mean_is_the_exact_sum_over_the_samples():
    m = make_matrix("full", 3, 50, 0)
    signs = A.random_signs(SplitMix64(11), 40, 3)
    values = [round(np.linalg.det(s)) ** 2 for s in signs]
    e = ev.estimate(m, 40, 11)
    assert e.mean == Fraction(sum(values), 40) and e.nonzero == sum(v > 0 for v in values) and e.maximum == max(values)
    mean = sum(values) / 40
    assert e.std_error == pytest.approx(math.sqrt(sum((v - mean) ** 2 for v in values) / 39 / 40))


# --- validation_errors: Grundfall und jeder Zweig ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kw", [{}, {"n": 2}, {"n": 3, "kind": "full"}, {"n": 12, "kind": "blocks"}, {"n": 8, "kind": "grid"}, {"n": 20, "kind": "grid"}, {"n": 9, "dens": 80}, {"n": 13}, {"n": 4, "kind": "derange"}])
def test_valid_analyses_have_no_errors(kw):
    assert _errors(_base(**kw)) == []


def test_matrix_must_be_square_zero_one():
    a = _base(n=3, kind="full")
    assert _errors(replace(a, matrix=((1, 1), (1, 1, 1)))) == ["Die Matrix ist nicht quadratisch oder nicht 0/1."]
    assert _errors(replace(a, matrix=((1, 2, 1), (1, 1, 1), (1, 1, 1)))) == ["Die Matrix ist nicht quadratisch oder nicht 0/1."]


def test_permanent_is_checked_against_the_second_route():
    a = _base()
    assert _has(replace(a, per=a.per + 1), "zweiten Rechnung") and _has(replace(a, per=a.per - 1), "zweiten Rechnung")


def test_permanent_is_checked_against_the_definition_up_to_n_8_only(monkeypatch):
    calls = []
    monkeypatch.setattr(A, "per_brute", lambda m: (calls.append(len(m)) or -1, 0))
    assert _has(_base(n=8), "Definition")
    assert _has(_base(n=3, kind="full"), "Definition")
    calls.clear()
    assert not _has(_base(n=9), "Definition") and calls == []                                       # ab n = 9 nicht aufgerufen (Grenze genau bei BRUTE_N_MAX)
    assert C.BRUTE_N_MAX == 8


def test_permanent_must_lie_in_zero_to_the_row_and_column_products():
    a = _base(n=3, kind="full")                                                                    # Zeilen- und Spaltenprodukt: 27
    assert not _has(replace(a, per=27), "außerhalb")                                              # Grenze: genau das Produkt ist (für sich) erlaubt
    assert _has(replace(a, per=28), "außerhalb") and _has(replace(a, per=-1), "außerhalb")
    b = ev.Analysis(ev.Settings(), ((1, 1, 1), (1, 1, 1), (0, 0, 0)), 6, 0, 8, 14, 12, 0, 0, False, None, None)
    assert not _has(b, "außerhalb")                                                                # Zeilenprodukt 0 = per 0: in Ordnung
    c = replace(b, matrix=((1, 0, 0), (1, 1, 1), (1, 1, 1)), per=1)                                # Spaltenprodukt 3 · 2 · 2 = 12, Zeilenprodukt 1 · 3 · 3 = 9 → min 9
    assert _has(replace(c, per=10), "außerhalb")


def test_determinant_bound_and_parity():
    a = _base()
    assert not _has(replace(a, det=a.per), "größer als die Permanente") and not _has(replace(a, det=-a.per), "größer als die Permanente")   # |det| = per erlaubt
    assert _has(replace(a, det=a.per + 2), "größer als die Permanente") and _has(replace(a, det=-a.per - 2), "größer als die Permanente")
    assert _has(replace(a, det=a.det + 1), "Parität") and not _has(replace(a, det=a.det + 2), "Parität")


def test_existence_must_match_the_permanent():
    a = _base()
    assert _has(replace(a, exists=False), "Existenz") and _has(replace(_base(n=10, dens=20), exists=True), "Existenz")


def test_determinant_is_checked_against_numpy():
    a = _base()
    assert _has(replace(a, det=a.det + 2), "numpy") and not _has(a, "numpy")
    assert _has(replace(_base(n=3, kind="full"), det=2), "numpy")


def test_cost_counts_must_match_the_formulas():
    a = _base()
    assert _has(replace(a, per_mults=a.per_mults + 1), "Multiplikationen") and _has(replace(a, ryser_mults=0), "Multiplikationen") and _has(replace(a, brute_mults=1), "Multiplikationen")
    assert _has(replace(a, det_mults=A.mults_det(8) + 1), "Multiplikationen") and _has(replace(a, det_mults=-1), "Multiplikationen")
    assert not _has(replace(a, det_mults=A.mults_det(8)), "Multiplikationen") and not _has(replace(a, det_mults=0), "Multiplikationen")      # beide Grenzen erlaubt


def test_estimate_must_not_be_negative_or_nonzero_for_permanent_zero():
    a = _base(n=3, kind="full")
    assert _has(replace(a, estimate=replace(a.estimate, mean=Fraction(-1))), "negativ")
    z = _base(n=10, dens=20)
    assert _has(replace(z, estimate=replace(z.estimate, mean=Fraction(1, 1000))), "negativ oder von null")
    assert not _has(replace(z, estimate=replace(z.estimate, mean=Fraction(0))), "negativ")
    assert not _has(replace(a, estimate=replace(a.estimate, mean=Fraction(0))), "negativ")      # Mittel 0 bei per > 0 ist möglich (nur eine Stichprobe)


def test_estimate_is_checked_against_the_enumeration_for_up_to_sixteen_ones():
    j4 = _base(n=4, kind="full")                                                                    # genau 16 Einsen: aufgezählt
    assert j4.ones == A.SIGN_ONES_MAX
    assert _has(replace(j4, estimate=replace(j4.estimate, maximum=7)), "aufgezählten")
    assert not _has(j4, "aufgezählten") and not _has(j4, "Erwartungswert")
    assert _has(replace(j4, per=23), "Erwartungswert")
    big = _base(n=5, kind="full")                                                                   # 25 Einsen: nicht aufgezählt
    assert not _has(replace(big, estimate=replace(big.estimate, maximum=7)), "aufgezählten")


# --- Messreihen gegen eine unabhängige Nachrechnung -------------------------------------------------------------------------------------------


def _per_by_definition(m):
    n = len(m)
    return sum(math.prod(m[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))


def _det_by_fractions(m):
    """Gauß mit Brüchen (zweite Determinante)."""
    n = len(m)
    a = [[Fraction(x) for x in row] for row in m]
    det = Fraction(1)
    for c in range(n):
        piv = next((r for r in range(c, n) if a[r][c] != 0), None)
        if piv is None:
            return 0
        if piv != c:
            a[c], a[piv] = a[piv], a[c]
            det = -det
        det *= a[c][c]
        for r in range(c + 1, n):
            f = a[r][c] / a[c][c]
            a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return int(det)


def test_cost_rows_are_the_formulas_and_the_counted_determinant():
    rows = ev.cost_rows(range(2, 7))
    assert [r["n"] for r in rows] == [2, 3, 4, 5, 6]
    assert rows[1] == {"n": 3, "brute": 12, "ryser": 14, "glynn": 8, "det": 10, "det_counted": A.det_bareiss(random01(3, 50, SplitMix64(C.COST_SEED + 3)))[1]}
    assert all(r["det_counted"] <= r["det"] for r in rows) and len(ev.cost_rows()) == C.N_MAX - C.N_MIN + 1


def test_sweep_det_matches_a_recount_with_the_definition():
    rows = ev.sweep_det(sizes=(3, 5), dens_list=(30, 70), count=15, seed=77)
    assert [(r["n"], r["dens"]) for r in rows] == [(3, 30), (3, 70), (5, 30), (5, 70)]
    for r in rows:
        rng = SplitMix64(77 + 1000 * r["dens"] + r["n"])
        ratios, zero = [], 0
        for _ in range(15):
            m = random01(r["n"], r["dens"], rng)
            per, det = _per_by_definition(m), _det_by_fractions(m)
            assert abs(det) <= per and (per - det) % 2 == 0
            if per:
                ratios.append(Fraction(abs(det), per))
                zero += det == 0
        assert r["with_pm"] == len(ratios) and r["det_zero"] == zero and r["count"] == 15 and r["parity_all"] and r["bound_all"]
        if ratios:
            assert r["mean"] == sum(ratios) / len(ratios) and r["median"] == statistics.median(ratios)


def test_sweep_det_handles_a_cell_without_any_perfect_matching():
    rows = ev.sweep_det(sizes=(2,), dens_list=(0,), count=5, seed=1)                                  # Dichte 0: nur Nullmatrizen
    assert rows[0]["with_pm"] == 0 and rows[0]["mean"] is None and rows[0]["median"] is None and rows[0]["det_zero"] == 0


def test_polya_rows_against_a_recount_by_exhaustion():
    rows = {r["name"]: r for r in ev.polya_rows()}
    assert set(rows) == set(C.POLYA_CASES)
    assert rows["J2"]["counts"] == {0: 8, 2: 8} and rows["J2"]["hits"] == 8 and rows["J2"]["per"] == 2
    assert rows["J3"]["counts"] == {0: 320, 4: 192} and rows["J3"]["hits"] == 0 and rows["J3"]["patterns"] == 512
    assert rows["J4"]["counts"] == {0: 43264, 8: 21504, 16: 768} and rows["J4"]["hits"] == 0 and rows["J4"]["patterns"] == 65536
    for name, shape in (("Gitter 2 × 3", (2, 3)), ("Gitter 2 × 4", (2, 4))):
        m = A.grid_biadjacency(*shape)[0]
        ones = [(i, j) for i, row in enumerate(m) for j, x in enumerate(row) if x]
        hits, counts = 0, {}
        for signs in itertools.product((1, -1), repeat=len(ones)):
            s = [list(r) for r in m]
            for (i, j), sg in zip(ones, signs):
                s[i][j] = sg
            d = abs(_det_by_fractions(s))
            counts[d] = counts.get(d, 0) + 1
            hits += d == _per_by_definition(m)
        assert rows[name]["hits"] == hits and rows[name]["counts"] == dict(sorted(counts.items())) and rows[name]["patterns"] == 2 ** len(ones)


def test_kasteleyn_rows_agree_with_known_tiling_numbers():
    rows = {(r["rows"], r["cols"]): r for r in ev.kasteleyn_rows()}
    known = {(2, 2): 2, (2, 3): 3, (2, 4): 5, (3, 4): 11, (4, 4): 36, (4, 5): 95, (4, 6): 281, (5, 6): 1183, (6, 6): 6728, (5, 8): 14824}
    assert {k: v["per"] for k, v in rows.items()} == known
    assert all(v["det_signed"] == v["per"] for v in rows.values()) and all(v["det_plain"] != v["per"] for v in rows.values())
    assert rows[(5, 8)]["n"] == 20 and rows[(4, 4)]["det_plain"] == 0


def _exact_estimator_value(m, sg):
    s = [list(r) for r in m]
    return _det_by_fractions([[x * sg[i][j] for j, x in enumerate(row)] for i, row in enumerate(s)]) ** 2


def test_sweep_estimator_matches_a_recount_with_exact_determinants():
    res = ev.sweep_estimator(sizes=(4,), matrices=3, reps=4, samples=30, blocks=(2,), seed=9)
    assert res["samples"] == 30 and res["reps"] == 4 and len(res["random"]) == 1
    rels, used = [], 0
    for i in range(3):
        m = random01(4, 50, SplitMix64(9 + 400 + i))
        per = _per_by_definition(m)
        if per == 0:
            continue
        used += 1
        rng = SplitMix64(9 + 28 + i)
        ests = []
        for _ in range(4):
            signs = A.random_signs(rng, 30, 4)
            ests.append(Fraction(sum(_exact_estimator_value(m, [[int(x) for x in row] for row in s]) for s in signs), 30))
        mean = sum(ests) / 4
        rels.append(math.sqrt(float(sum((e - mean) ** 2 for e in ests) / 3)) / per)
    row = res["random"][0]
    assert row["n"] == 4 and row["matrices"] == used and row["skipped"] == 3 - used
    assert row["mean_rel"] == pytest.approx(sum(rels) / len(rels)) and row["max_rel"] == pytest.approx(max(rels))
    block = res["blocks"][0]
    assert (block["k"], block["n"], block["per"], block["variance"], block["needed"]) == (2, 4, 4, 3, 300) and block["predicted"] == pytest.approx(math.sqrt(3 / 30))


def test_sweep_estimator_skips_matrices_without_a_perfect_matching():
    res = ev.sweep_estimator(sizes=(4,), matrices=6, reps=2, samples=10, blocks=(1,), seed=3)
    r = res["random"][0]
    assert r["matrices"] + r["skipped"] == 6 and r["matrices"] >= 1


def test_estimate_standard_error_uses_n_minus_one_from_two_samples_on():
    m = make_matrix("full", 3, 50, 0)
    def values_for(seed):
        return [round(np.linalg.det(s)) ** 2 for s in A.random_signs(SplitMix64(seed), 2, 3)]

    seed = next(sd for sd in range(200) if values_for(sd)[0] != values_for(sd)[1])               # ein Paar mit verschiedenen Werten (0 und 16)
    values = values_for(seed)
    e = ev.estimate(m, 2, seed)
    expected = math.sqrt(((values[0] - values[1]) ** 2 / 2) / 2)                                 # Stichprobenvarianz (n − 1) geteilt durch N
    assert e.std_error == pytest.approx(expected) and e.std_error > 0 and values[0] != values[1]


def test_sweep_det_flags_violations_of_the_theorems(monkeypatch):
    real = A.det_bareiss
    monkeypatch.setattr(A, "det_bareiss", lambda m: (10 ** 9, 0))                                  # Betrag über der Permanente
    assert not any(r["bound_all"] for r in ev.sweep_det(sizes=(3,), dens_list=(50,), count=5, seed=1))
    monkeypatch.setattr(A, "det_bareiss", lambda m: (real(m)[0] + 1, 0))                           # Parität verletzt, Betrag unter per nicht garantiert
    rows = ev.sweep_det(sizes=(3,), dens_list=(50,), count=5, seed=1)
    assert not rows[0]["parity_all"]
    calls = iter([1, 0, 0, 0, 0] * 3)                                                              # nur die erste Matrix verletzt: das Merkmal bleibt falsch
    monkeypatch.setattr(A, "det_bareiss", lambda m: (real(m)[0] + next(calls), 0))
    assert not ev.sweep_det(sizes=(3,), dens_list=(50,), count=5, seed=1)[0]["parity_all"]


def test_sweep_det_bound_flag_is_false_if_only_one_matrix_violates(monkeypatch):
    real = A.det_bareiss
    seen = []

    def fake(m):
        seen.append(1)
        return (10 ** 9 if len(seen) == 1 else real(m)[0]), 0

    monkeypatch.setattr(A, "det_bareiss", fake)
    assert not ev.sweep_det(sizes=(3,), dens_list=(50,), count=5, seed=1)[0]["bound_all"]


def test_numpy_check_tolerance_is_relative_to_the_size_of_the_determinant(monkeypatch):
    a = _base(n=20)
    assert a.det == -5120
    monkeypatch.setattr(np.linalg, "det", lambda m: a.det * (1 + 1e-7))
    assert not _has(a, "numpy")                                                                   # Abweichung 5 · 10^-4 liegt unter der relativen Toleranz 1e-6 · 5120
    monkeypatch.setattr(np.linalg, "det", lambda m: a.det * (1 + 1e-5))
    assert _has(a, "numpy")
