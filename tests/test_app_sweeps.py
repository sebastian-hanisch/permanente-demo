"""Die beiden Messreihen-Knöpfe (▶️) lässt der allgemeine Rauchtest aus (er überspringt Auto-Play-Marken): hier wird jeder Knopf einzeln gedrückt und die Seite ohne Ausnahme gerendert."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "600"))


@pytest.mark.parametrize("label", ["Messreihe Determinante", "Messreihe Schätzer"])
def test_each_sweep_button_renders(label):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    before = len(at.get("plotly_chart"))
    next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("plotly_chart")) == before + 1
    assert not at.error, [e.value for e in at.error]                                                                  # kein Verdikt der Art „error“


def test_both_sweeps_together_and_a_preset_afterwards():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    for label in ("Messreihe Determinante", "Messreihe Schätzer"):
        next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert len(at.get("plotly_chart")) == 1 + 1 + 1 + 2     # Matrix, kosten, polya + 2 Messreihen
    next(b for b in at.button if "Lehrbeispiel" in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["n_slider"] == 3 and at.session_state["kind_select"] == "full"
