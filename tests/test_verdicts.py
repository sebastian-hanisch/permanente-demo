"""Verdikte und Zahlenformate an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Zufalls-Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

from fractions import Fraction

import prn_evaluation as ev


def _analysis(n=4, per=24, det=0, exists=True, det_mults=28):
    m = tuple((1,) * n for _ in range(n))
    ratio = Fraction(abs(det), per) if per else None
    return ev.Analysis(ev.Settings(n=n), m, n * n, per, 24, 45, 72, det, det_mults, exists, ratio, None)


# --- Formate ------------------------------------------------------------------------------------------------------------------------------


def test_number_formats():
    assert ev.fmt_int(131071) == "131.071" and ev.fmt_int(12) == "12" and ev.fmt_int(-5120) == "−5.120" and ev.fmt_int(0) == "0"
    assert ev.fmt_num(22.7) == "22,7" and ev.fmt_num(3, 2) == "3,00"


def test_fmt_big_switches_to_a_power_of_ten_at_one_billion():
    assert ev.fmt_big(999_999_999) == "999.999.999" and ev.fmt_big(1_000_000_000) == "1,0 · 10^9" and ev.fmt_big(4_864_000_000_000_000_000) == "4,9 · 10^18"
    assert ev.fmt_big(-999_999_999) == "−999.999.999" and ev.fmt_big(-2_000_000_000) == "−2,0 · 10^9"


def test_fmt_fraction():
    assert ev.fmt_fraction(Fraction(1, 2)) == "1/2 (0,5)" and ev.fmt_fraction(Fraction(1, 3)) == "1/3 (0,3333)" and ev.fmt_fraction(Fraction(3)) == "3" and ev.fmt_fraction(Fraction(0)) == "0"
    assert ev.fmt_fraction(Fraction(1, 10000)) == "1/10000 (0,0001)"                                  # genau an der Grenze: noch Dezimalschreibweise
    assert ev.fmt_fraction(Fraction(1, 10001)) == "1/10001 (1,0 · 10^(−4))"
    assert ev.fmt_fraction(Fraction(1, 3), digits=2) == "1/3 (0,33)" and ev.fmt_fraction(Fraction(1031, 10), 2) == "1031/10 (103,1)"


def test_fmt_percent():
    assert ev.fmt_percent(Fraction(1, 4)) == "25 %" and ev.fmt_percent(Fraction(4, 7)) == "57,1 %" and ev.fmt_percent(0.105) == "10,5 %" and ev.fmt_percent(0.05) == "5 %"
    assert ev.fmt_percent(Fraction(13, 10000), 2) == "0,13 %" and ev.fmt_percent(Fraction(1)) == "100 %"


def test_fmt_ratio_uses_more_digits_below_one_hundredth_and_a_power_below_one_ten_thousandth():
    assert ev.fmt_ratio(Fraction(1, 2)) == "0,500" and ev.fmt_ratio(Fraction(1, 100)) == "0,010" and ev.fmt_ratio(Fraction(1, 101)) == "0,0099"
    assert ev.fmt_ratio(Fraction(1, 10000)) == "0,0001" and ev.fmt_ratio(Fraction(1, 10001)) == "1,0 · 10^(−4)" and ev.fmt_ratio(Fraction(23, 10 ** 10)) == "2,3 · 10^(−9)"
    assert ev.fmt_ratio(Fraction(0)) == "0,0000" and ev.fmt_ratio(Fraction(1)) == "1,000"


# --- verdict_main -------------------------------------------------------------------------------------------------------------------------


def test_verdict_main_without_a_perfect_matching():
    kind, text = ev.verdict_main(_analysis(per=0, det=0, exists=False))
    assert kind == "info" and text.startswith("Es gibt keine perfekte Paarung (Permanente 0, Determinante 0)")
    assert "Aufwand: Glynn 24 Multiplikationen, Ryser 45, Brute Force 72; die Determinante 28." in text


def test_verdict_main_when_the_determinant_vanishes():
    kind, text = ev.verdict_main(_analysis())
    assert kind == "warning"
    assert "Die 4 × 4-Matrix hat 24 perfekte Paarungen (Permanente). Die Determinante ist 0, obwohl Paarungen existieren: die Vorzeichen löschen sich vollständig aus." in text


def test_verdict_main_when_the_determinant_equals_the_permanent():
    kind, text = ev.verdict_main(_analysis(n=3, per=36, det=-36))
    assert kind == "success" and "Die Determinante ist −36: hier gleich der Permanente im Betrag" in text
    kind, text = ev.verdict_main(_analysis(n=3, per=36, det=36))
    assert kind == "success"


def test_verdict_main_for_a_partial_cancellation_names_the_ratio():
    kind, text = ev.verdict_main(_analysis(n=8, per=104, det=-2))
    assert kind == "warning" and "Die Determinante ist −2, im Betrag 0,019 der Permanente" in text
    kind, text = ev.verdict_main(_analysis(n=8, per=104, det=102))
    assert kind == "warning" and "im Betrag 0,981 der Permanente" in text
    assert "Die 8 × 8-Matrix hat 104 perfekte Paarungen (Permanente)." in text


def test_verdict_main_cost_line_uses_powers_for_huge_counts():
    a = ev.Analysis(ev.Settings(n=20), ((1,),) * 1, 1, 5, 9_961_472, 19_922_925, 4_864_000_000_000_000_000, 3, 4940, True, Fraction(3, 5), None)
    assert "Aufwand: Glynn 9.961.472 Multiplikationen, Ryser 19.922.925, Brute Force 4,9 · 10^18; die Determinante 4.940." in ev.verdict_main(a)[1]


# --- verdict_costs ------------------------------------------------------------------------------------------------------------------------


def _cost_rows():
    return [{"n": 2, "brute": 2, "ryser": 3, "glynn": 2, "det": 2, "det_counted": 2}, {"n": 3, "brute": 12, "ryser": 14, "glynn": 8, "det": 10, "det_counted": 8},
            {"n": 4, "brute": 72, "ryser": 45, "glynn": 24, "det": 12, "det_counted": 12}]


def test_verdict_costs_names_last_row_ratio_and_the_first_ryser_win():
    kind, text = ev.verdict_costs(_cost_rows())
    assert kind == "info"
    assert "Bei n = 4 kostet Brute Force 72 Multiplikationen, Ryser 45, Glynn 24, die Determinante 12 (gezählt an einer festen Zufallsmatrix: 12)." in text
    assert "Das Verhältnis Glynn : Determinante wächst von 1,0 : 1 bei n = 2 auf rund 2 : 1 bei n = 4. Ryser ist ab n = 4 billiger als Brute Force." in text


def test_verdict_costs_ryser_boundary_is_strict():
    rows = _cost_rows()
    rows[1]["ryser"] = 12                                                                        # gleich Brute Force: noch nicht billiger
    assert "ab n = 4 billiger" in ev.verdict_costs(rows)[1]
    rows[1]["ryser"] = 11
    assert "ab n = 3 billiger" in ev.verdict_costs(rows)[1]


# --- verdict_det_sweep --------------------------------------------------------------------------------------------------------------------


def _det_rows(bound=True, parity=True):
    def row(n, dens, with_pm, det_zero, mean):
        return {"n": n, "dens": dens, "count": 200, "with_pm": with_pm, "det_zero": det_zero, "mean": Fraction(mean), "median": Fraction(mean) / 2, "parity_all": parity, "bound_all": bound}
    return [row(4, 30, 50, 10, "1/2"), row(4, 50, 100, 20, "9/20"), row(12, 50, 190, 38, "1/5000"), row(12, 70, 200, 180, "1/10000")]


def test_verdict_det_sweep_names_totals_ratios_and_the_worst_cell():
    kind, text = ev.verdict_det_sweep(_det_rows())
    assert kind == "info"
    assert "In allen 800 Matrizen war |det| ≤ per und die Parität gleich" in text
    assert "Bei Dichte 50 % fällt das mittlere |det| / per von 0,450 (n = 4) auf 0,0002 (n = 12)." in text
    assert "am größten bei n = 12, Dichte 70 %: 90 %." in text


def test_verdict_det_sweep_reports_violations_of_the_theorems():
    assert ev.verdict_det_sweep(_det_rows(bound=False))[0] == "error"
    assert ev.verdict_det_sweep(_det_rows(parity=False))[0] == "error"
    assert "Parität" in ev.verdict_det_sweep(_det_rows(parity=False))[1] and "überschritt" in ev.verdict_det_sweep(_det_rows(bound=False))[1]


# --- verdict_polya / kasteleyn ---------------------------------------------------------------------------------------------------------


def _polya_rows(j3_hits=0, j4_hits=0):
    return [
        {"name": "J2", "n": 2, "ones": 4, "patterns": 16, "per": 2, "counts": {0: 8, 2: 8}, "hits": 8},
        {"name": "J3", "n": 3, "ones": 9, "patterns": 512, "per": 6, "counts": {0: 320, 4: 192}, "hits": j3_hits},
        {"name": "J4", "n": 4, "ones": 16, "patterns": 65536, "per": 24, "counts": {0: 43264, 8: 21504, 16: 768}, "hits": j4_hits},
        {"name": "Gitter 2 × 3", "n": 3, "ones": 7, "patterns": 128, "per": 3, "counts": {0: 64, 1: 32, 3: 32}, "hits": 32},
        {"name": "Gitter 2 × 4", "n": 4, "ones": 10, "patterns": 1024, "per": 5, "counts": {0: 512, 5: 128}, "hits": 128},
    ]


def test_verdict_polya_names_the_counts():
    kind, text = ev.verdict_polya(_polya_rows())
    assert kind == "info"
    assert "Bei J3 erreicht keines der 512 Vorzeichenmuster |det| = 6 (die Beträge sind nur 0, 4)" in text
    assert "bei J4 keines der 65.536 (Beträge 0, 8, 16, die Permanente ist 24)" in text
    assert "Beim Gitter 2 × 3 erreichen 32 von 128 Mustern die Permanente 3, beim Gitter 2 × 4 128 von 1.024 (Permanente 5)" in text


def test_verdict_polya_flags_a_hit_for_j3_or_j4_as_an_error():
    assert ev.verdict_polya(_polya_rows(j3_hits=1))[0] == "error" and ev.verdict_polya(_polya_rows(j4_hits=1))[0] == "error"


def _kasteleyn_rows(broken=False):
    rows = [{"rows": 2, "cols": 2, "n": 2, "per": 2, "det_signed": 2, "det_plain": 0}, {"rows": 4, "cols": 4, "n": 8, "per": 36, "det_signed": 36, "det_plain": 0},
            {"rows": 6, "cols": 6, "n": 18, "per": 6728, "det_signed": 6728, "det_plain": 6728}]
    if broken:
        rows[1]["det_signed"] = 35
    return rows


def test_verdict_kasteleyn_names_the_largest_grid_and_counts_the_failures_without_signs():
    kind, text = ev.verdict_kasteleyn(_kasteleyn_rows())
    assert kind == "success" and "in allen 3 Gittern" in text and "größtes: 6 × 6 mit 6.728" in text and "ohne die Vorzeichen ist |det| in 2 von 3 Gittern falsch" in text
    assert ev.verdict_kasteleyn(_kasteleyn_rows(broken=True))[0] == "error"


# --- verdict_estimator -------------------------------------------------------------------------------------------------------------------------


def test_verdict_estimator_quotes_random_and_block_streuung():
    res = {"samples": 1000, "reps": 20,
           "random": [{"n": 6, "matrices": 8, "skipped": 2, "mean_rel": 0.05, "max_rel": 0.07}, {"n": 12, "matrices": 10, "skipped": 0, "mean_rel": 0.105, "max_rel": 0.12}],
           "blocks": [{"k": 5, "n": 10, "per": 32, "rel": 0.2, "predicted": 0.176, "variance": 31, "needed": 3100}, {"k": 6, "n": 12, "per": 64, "rel": 0.222, "predicted": 0.251, "variance": 63, "needed": 6300}]}
    kind, text = ev.verdict_estimator(res)
    assert kind == "warning"
    assert "aus 1.000 Vorzeichenmatrizen bei 5 % (n = 6) bis 10,5 % (n = 12): brauchbar." in text
    assert "für k = 6 (n = 12) vorhergesagt 25,1 %, gemessen 22,2 %; für eine Standardabweichung von 10 % braucht man etwa 6.300 Vorzeichenmatrizen" in text
