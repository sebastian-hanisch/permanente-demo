"""Abbildungen: Reihen, Farben, gesperrte Achsen; der PDF-Bau mit Umlauten."""

from fractions import Fraction

import numpy as np

import prn_constants as C
import prn_evaluation as ev
import prn_visualization as V
from prn_pdf_export import build_pdf


def _locked(fig):
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_matrix_grid_has_one_cell_per_entry():
    m = ((1, 0, 1), (0, 1, 1), (1, 1, 0))
    fig = V.build_matrix(m)
    assert np.array_equal(np.array(fig.data[0].z), np.array(m)) and fig.data[0].colorscale[1][1] == C.COLOR_DET and fig.layout.yaxis.autorange == "reversed"
    _locked(fig)


def test_cost_chart_has_four_series_on_a_log_axis():
    rows = ev.cost_rows(range(2, 9))
    fig = V.build_costs(rows)
    assert [t.name for t in fig.data] == ["Brute Force n!", "Ryser 2^n", "Glynn 2^(n−1)", "Determinante (Bareiss)"] and fig.layout.yaxis.type == "log"
    assert list(fig.data[0].x) == list(range(2, 9)) and list(fig.data[3].y) == [r["det"] for r in rows] and fig.data[0].line.color == C.COLOR_BRUTE
    _locked(fig)


def test_det_ratio_chart_has_one_line_per_density_and_skips_empty_cells():
    rows = [{"n": 4, "dens": 30, "mean": Fraction(1, 2)}, {"n": 6, "dens": 30, "mean": Fraction(1, 4)}, {"n": 4, "dens": 50, "mean": Fraction(2, 5)}, {"n": 6, "dens": 50, "mean": None}]
    fig = V.build_det_ratio(rows)
    assert [t.name for t in fig.data] == ["Dichte 30 %", "Dichte 50 %"] and list(fig.data[0].y) == [0.5, 0.25] and list(fig.data[1].x) == [4] and fig.layout.yaxis.type == "log"
    _locked(fig)


def test_polya_chart_shows_the_share_of_hits():
    rows = ev.polya_rows()
    fig = V.build_polya(rows)
    assert list(fig.data[0].x) == list(C.POLYA_CASES) and list(fig.data[0].y)[1] == 0 and abs(fig.data[0].y[3] - 25.0) < 1e-12 and fig.data[0].text[1] == "0 von 512"
    _locked(fig)


def test_estimator_chart_has_measured_and_predicted_block_series():
    res = ev.sweep_estimator(sizes=(4,), matrices=2, reps=3, samples=20, blocks=(2, 3), seed=1)
    fig = V.build_estimator(res)
    assert [t.name for t in fig.data] == ["Zufallsmatrizen (gemessen)", "Blöcke J2 (gemessen)", "Blöcke J2: √((2^k − 1) / N)"] and list(fig.data[1].x) == [4, 6]
    assert abs(fig.data[2].y[0] - (3 / 20) ** 0.5) < 1e-12 and fig.layout.yaxis.type == "log"
    _locked(fig)


def test_pdf_builds_with_umlauts_for_every_kind():
    for kind in C.KINDS:
        pdf = build_pdf(ev.analyse(ev.Settings(n=6, kind=kind, samples=100)))
        assert pdf[:5] == b"%PDF-" and len(pdf) > 1500
    assert build_pdf(ev.analyse(ev.Settings(n=14, kind="full")))[:5] == b"%PDF-"                      # ohne Schätzer
