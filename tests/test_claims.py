"""Jede Zahl der README steht hier und wird über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Alle Matrizen kommen aus dem eigenen SplitMix64-Generator (plattform- und versionsunabhängig); Anzahlen sind exakte ganze Zahlen, Anteile exakte Brüche. Die Schätzer-Streuungen sind Messwerte
aus festen Strömen (auf drei Stellen gerundet verglichen), der Schätzer selbst steht in der Auswertung nur als Illustration."""

from fractions import Fraction as F

import pytest

import prn_algorithm as A
import prn_constants as C
import prn_evaluation as ev

# --- Befund 1: Kosten --------------------------------------------------------------------------------------------------------------------------

COSTS = {   # n: (Brute Force, Ryser, Glynn, Determinante nach Formel, Determinante gezählt)
    2: (2, 3, 2, 2, 2), 4: (72, 45, 24, 28, 26), 5: (480, 124, 64, 60, 50), 6: (3600, 315, 160, 110, 50), 8: (282240, 1785, 896, 280, 280), 10: (32659200, 9207, 4608, 570, 570),
    12: (5269017600, 45045, 22528, 1012, 1012), 16: (313841848320000, 983025, 491520, 2480, 2480), 20: (46225138155356160000, 19922925, 9961472, 4940, 4940),
}


@pytest.fixture(scope="module")
def costs():
    return ev.cost_rows()


def test_claim_cost_table(costs):
    """README, Befund 1: Multiplikationen je n (Produkt aus n Faktoren = n − 1 Multiplikationen)."""
    by = {r["n"]: r for r in costs}
    assert {n: (by[n]["brute"], by[n]["ryser"], by[n]["glynn"], by[n]["det"], by[n]["det_counted"]) for n in COSTS} == COSTS


def test_claim_cost_crossovers(costs):
    """README: Ryser ist ab n = 4 billiger als Brute Force; Glynn halbiert Ryser ungefähr (2 gegen 3 bei n = 2, 9.961.472 gegen 19.922.925 bei n = 20); Glynn kostet ab n = 5 mehr als die Determinante,
    bei n = 20 rund 2.016-mal so viel (9.961.472 gegen 4.940); Brute Force bei n = 20 rund 4,6 · 10^19."""
    assert next(r["n"] for r in costs if r["ryser"] < r["brute"]) == 4
    assert next(r["n"] for r in costs if r["glynn"] > r["det"]) == 5 and all(r["glynn"] <= r["det"] for r in costs if r["n"] < 5)
    last = costs[-1]
    assert round(last["glynn"] / last["det"]) == 2016 and ev.fmt_big(last["brute"]) == "4,6 · 10^19"
    assert last["ryser"] == 19 * (2 ** 20 - 1) == 19_922_925 == 2 * last["glynn"] - 19 and last["glynn"] == 19 * 2 ** 19 == 9_961_472
    text = ev.verdict_costs(costs)[1]
    assert "Das Verhältnis Glynn : Determinante wächst von 1,0 : 1 bei n = 2 auf rund 2.016 : 1 bei n = 20. Ryser ist ab n = 4 billiger als Brute Force." in text


# --- Befund 2: Determinante gegen Permanente ---------------------------------------------------------------------------------------------------

# (n, Dichte): (Matrizen mit perfekter Paarung von 200, davon det = 0, mittleres |det| / per, Median)
DET = {
    (4, 30): (21, 3, "0,825", "1,000"), (4, 50): (108, 45, "0,453", "0,333"), (4, 70): (190, 117, "0,170", "0,0000"),
    (6, 30): (29, 11, "0,504", "0,333"), (6, 50): (158, 74, "0,160", "0,037"), (6, 70): (196, 141, "0,015", "0,0000"),
    (8, 30): (79, 27, "0,326", "0,176"), (8, 50): (184, 73, "0,023", "0,0047"), (8, 70): (200, 121, "0,0016", "0,0000"),
    (10, 30): (106, 35, "0,168", "0,053"), (10, 50): (196, 59, "0,0021", "0,0007"), (10, 70): (200, 98, "3,6 · 10^(−5)", "5,3 · 10^(−6)"),
    (12, 30): (131, 38, "0,044", "0,012"), (12, 50): (200, 30, "0,0002", "9,4 · 10^(−5)"), (12, 70): (200, 64, "1,7 · 10^(−6)", "4,0 · 10^(−7)"),
}


@pytest.fixture(scope="module")
def det_rows():
    return ev.sweep_det()


def test_claim_det_table(det_rows):
    """README, Befund 2: 5 Größen · 3 Dichten · 200 feste Zufallsmatrizen = 3.000; Matrizen mit Paarung, davon det = 0, mittleres und Median-Verhältnis |det| / per."""
    assert {(r["n"], r["dens"]): (r["with_pm"], r["det_zero"], ev.fmt_ratio(r["mean"]), ev.fmt_ratio(r["median"])) for r in det_rows} == DET
    assert sum(r["count"] for r in det_rows) == 3000 and all(r["count"] == 200 for r in det_rows)


def test_claim_theorems_hold_in_all_3000_matrices(det_rows):
    """README: in allen 3.000 Matrizen |det| ≤ per und gleiche Parität (beides Sätze); der größte Anteil „Paarung vorhanden, aber det = 0“ ist 141 von 196 = 71,9 % (n = 6, Dichte 70 %)."""
    assert all(r["bound_all"] and r["parity_all"] for r in det_rows)
    worst = max(det_rows, key=lambda r: F(r["det_zero"], r["with_pm"]))
    assert (worst["n"], worst["dens"], worst["det_zero"], worst["with_pm"]) == (6, 70, 141, 196) and ev.fmt_percent(F(141, 196)) == "71,9 %"
    text = ev.verdict_det_sweep(det_rows)[1]
    assert "Bei Dichte 50 % fällt das mittlere |det| / per von 0,453 (n = 4) auf 0,0002 (n = 12)." in text and "am größten bei n = 6, Dichte 70 %: 71,9 %." in text


def test_claim_the_ratio_falls_with_n_at_each_density(det_rows):
    for dens in C.DET_DENS:
        means = [r["mean"] for r in sorted((r for r in det_rows if r["dens"] == dens), key=lambda r: r["n"])]
        assert means == sorted(means, reverse=True)


# --- Befund 3: Vorzeichen -----------------------------------------------------------------------------------------------------------------------

POLYA = {
    "J2": (16, 2, {0: 8, 2: 8}, 8), "J3": (512, 6, {0: 320, 4: 192}, 0), "J4": (65536, 24, {0: 43264, 8: 21504, 16: 768}, 0),
    "Gitter 2 × 3": (128, 3, {1: 96, 3: 32}, 32), "Gitter 2 × 4": (1024, 5, {1: 768, 3: 128, 5: 128}, 128),
}
KASTELEYN = {(2, 2): (2, 2, 0), (2, 3): (3, 3, 1), (2, 4): (5, 5, 1), (3, 4): (11, 11, 1), (4, 4): (36, 36, 0), (4, 5): (95, 95, 1), (4, 6): (281, 281, 1), (5, 6): (1183, 1183, 1),
             (6, 6): (6728, 6728, 0), (5, 8): (14824, 14824, 0)}   # (Pflasterungen, |det| mit Kasteleyn-Vorzeichen, |det| ohne Vorzeichen)


def test_claim_polya_table():
    """README, Befund 3: alle Vorzeichenmuster; J3 (512 Muster) und J4 (65.536) erreichen die Permanente nie; Gitter 2 × 3: 32 von 128, 2 × 4: 128 von 1.024."""
    rows = {r["name"]: r for r in ev.polya_rows()}
    assert {k: (v["patterns"], v["per"], v["counts"], v["hits"]) for k, v in rows.items()} == POLYA
    text = ev.verdict_polya(list(rows.values()))[1]
    assert "Bei J3 erreicht keines der 512 Vorzeichenmuster |det| = 6 (die Beträge sind nur 0, 4); bei J4 keines der 65.536 (Beträge 0, 8, 16, die Permanente ist 24)." in text
    assert "Beim Gitter 2 × 3 erreichen 32 von 128 Mustern die Permanente 3, beim Gitter 2 × 4 128 von 1.024 (Permanente 5)" in text


def test_claim_kasteleyn_table():
    """README: auf 10 Gittern bis 5 × 8 (n = 20) zählt |det| mit dem Vorzeichen −1 an den senkrechten Kanten in ungeraden Spalten die Pflasterungen (u. a. 36, 6.728, 14.824); ohne Vorzeichen ist |det| nur 0 oder 1."""
    rows = ev.kasteleyn_rows()
    assert {(r["rows"], r["cols"]): (r["per"], r["det_signed"], r["det_plain"]) for r in rows} == KASTELEYN
    assert "in allen 10 Gittern" in ev.verdict_kasteleyn(rows)[1] and "ohne die Vorzeichen ist |det| in 10 von 10 Gittern falsch" in ev.verdict_kasteleyn(rows)[1]


def test_claim_hand_values_of_the_small_cases():
    """README (Handwerte): J3: per 6, det 0, drei Produkte mit + und drei mit −; J − I: Derangements 2, 9, 44, 1.854 (n = 3, 4, 5, 7), Determinante 2, −3, 4, 6; 2 × 2-Gitter: Matrix ((1, 1), (1, 1)),
    mit Kasteleyn-Vorzeichen ((1, 1), (−1, 1)) und Determinante 2."""
    j3 = ((1,) * 3,) * 3
    assert A.per_glynn(j3)[0] == 6 and A.det_bareiss(j3)[0] == 0
    assert [A.per_dp(tuple(tuple(int(i != j) for j in range(n)) for i in range(n))) for n in (3, 4, 5, 7)] == [2, 9, 44, 1854]
    assert [A.det_bareiss(tuple(tuple(int(i != j) for j in range(n)) for i in range(n)))[0] for n in (3, 4, 5, 7)] == [2, -3, 4, 6]
    assert A.grid_biadjacency(2, 2)[0] == ((1, 1), (1, 1)) and A.kasteleyn_signed(2, 2) == ((1, 1), (-1, 1))


# --- Befund 4: Schätzer ---------------------------------------------------------------------------------------------------------------------------

EST_RANDOM = {6: (9, 1, 0.055), 8: (10, 0, 0.070), 10: (9, 1, 0.092), 12: (10, 0, 0.105)}     # n: (Matrizen mit Paarung, übersprungen, mittlere relative Streuung)
EST_BLOCKS = {2: (4, 0.062, 0.055, 300), 3: (8, 0.085, 0.084, 700), 4: (16, 0.113, 0.122, 1500), 5: (32, 0.214, 0.176, 3100), 6: (64, 0.222, 0.251, 6300)}   # k: (per, gemessen, Rechnung, Matrizen für 10 %)


@pytest.fixture(scope="module")
def est():
    return ev.sweep_estimator()


def test_claim_estimator_on_random_matrices(est):
    """README, Befund 4: relative Streuung eines Schätzers aus 1.000 Vorzeichenmatrizen, 10 Zufallsmatrizen (Dichte 50 %) je Größe, 20 Wiederholungen."""
    assert {r["n"]: (r["matrices"], r["skipped"], pytest.approx(r["mean_rel"], abs=5e-4)) for r in est["random"]} == {n: (m, s, pytest.approx(v, abs=5e-4)) for n, (m, s, v) in EST_RANDOM.items()}
    assert est["samples"] == 1000 and est["reps"] == 20 and C.EST_MATRICES == 10


def test_claim_estimator_on_blocks(est):
    """README: Blöcke aus J2: Varianz / Permanente² = 2^k − 1 (exakt, Aufzählung für k bis 4 im Orakel-Test), Streuung bei N = 1.000 gemessen gegen √((2^k − 1) / 1.000); für 10 % Fehler 100 · (2^k − 1) Matrizen."""
    got = {r["k"]: (r["per"], r["rel"], r["predicted"], r["needed"]) for r in est["blocks"]}
    assert set(got) == set(EST_BLOCKS)
    for k, (per, rel, pred, needed) in EST_BLOCKS.items():
        assert got[k][0] == per and got[k][1] == pytest.approx(rel, abs=5e-4) and got[k][2] == pytest.approx(pred, abs=5e-4) and got[k][3] == needed == 100 * (2 ** k - 1)


def test_claim_estimator_is_unbiased_and_the_variance_of_j3_and_j4_is_small():
    """README: E[X] = per (exakt aufgezählt für J3 und J4: 6 und 24); Varianz / Permanente² bei J3 5/3, bei J4 8/3."""
    for m, per, var in ((((1,) * 3,) * 3, 6, F(5, 3)), (((1,) * 4,) * 4, 24, F(8, 3))):
        xs = [int(d) ** 2 for d in A.all_sign_dets(m)]
        mean = F(sum(xs), len(xs))
        assert mean == per and (F(sum(x * x for x in xs), len(xs)) - mean ** 2) / mean ** 2 == var


# --- Presets (Einzelinstanzen) -----------------------------------------------------------------------------------------------------------------

# Preset: (Permanente, Determinante, Paarung vorhanden, Glynn, Ryser, Brute Force, Determinante gezählt, Schätzer-Mittel, Stichproben mit Wert > 0)
PRESETS = {
    "Standardfall (Voreinstellung)": (104, -2, True, 896, 1785, 282240, 280, F(1031, 10), 843),
    "Lehrbeispiel (3 × 3, alle Einsen)": (6, 0, True, 8, 14, 12, 8, F(802, 125), 401),
    "Derangements (J − I)": (1854, 6, True, 384, 762, 30240, 182, F(38584, 25), 935),
    "Blöcke (Schätzer streut)": (64, 0, True, 22528, 45045, 5269017600, 242, F(6144, 125), 12),
    "Gitter 4 × 4 (36 Pflasterungen)": (36, 0, True, 896, 1785, 282240, 278, F(4432, 125), 559),
    "Dichte Matrix": (330936, 0, True, 4608, 9207, 32659200, 560, F(36511592, 125), 980),
    "Dünne Matrix": (0, 0, False, 4608, 9207, 32659200, 460, F(0), 0),
}


@pytest.mark.parametrize("name", list(PRESETS))
def test_claim_presets_are_single_instances_with_these_values(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    assert (a.per, a.det, a.exists, a.per_mults, a.ryser_mults, a.brute_mults, a.det_mults, a.estimate.mean, a.estimate.nonzero) == PRESETS[name]
    assert ev.validation_errors(a) == []


def test_claim_preset_help_texts_quote_these_numbers():
    h = C.PRESET_HELP
    assert "104 perfekte Paarungen" in h["Standardfall (Voreinstellung)"] and "−2" in h["Standardfall (Voreinstellung)"] and "896" in h["Standardfall (Voreinstellung)"] and "280" in h["Standardfall (Voreinstellung)"]
    assert "6 Paarungen (3!)" in h["Lehrbeispiel (3 × 3, alle Einsen)"] and "1.854" in h["Derangements (J − I)"] and "ist 6" in h["Derangements (J − I)"]
    assert "64 Paarungen" in h["Blöcke (Schätzer streut)"] and "12 von 1.000" in h["Blöcke (Schätzer streut)"] and "49,2 statt 64" in h["Blöcke (Schätzer streut)"]
    assert "36 Domino-Pflasterungen" in h["Gitter 4 × 4 (36 Pflasterungen)"] and "330.936" in h["Dichte Matrix"] and "keine perfekte Paarung" in h["Dünne Matrix"]
    assert float(PRESETS["Blöcke (Schätzer streut)"][7]) == pytest.approx(49.152)


def test_claim_the_largest_matrix_has_twenty_factorial_pairings():
    """README: n = 20, alle Einsen: 20! = 2.432.902.008.176.640.000 Paarungen; die Determinante ist 0, der Betrag passt in int64."""
    a = ev.analyse(ev.Settings(n=20, kind="full"))
    assert a.per == 2_432_902_008_176_640_000 and a.det == 0 and a.det_mults == 722 and ev.fmt_int(a.per) == "2.432.902.008.176.640.000"
