"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzung."""

import pytest

import prn_constants as C
import prn_evaluation as ev
import prn_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert C.N_MIN <= p["n"] <= C.N_MAX and 0 <= p["seed"] <= C.SEED_MAX and p["kind"] in C.KINDS, name
        assert p["dens"] in C.DENS_OPTIONS and p["samples"] in C.SAMPLES_OPTIONS, name


def test_every_grid_preset_uses_a_size_with_a_grid_shape():
    for p in C.PRESETS.values():
        if p["kind"] == "grid":
            assert p["n"] in C.GRID_SHAPES


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_analyses_without_validation_errors():
    for name, p in C.PRESETS.items():
        assert ev.validation_errors(ev.analyse(ev.Settings(**p))) == [], name


@pytest.mark.parametrize("raw, expected", [("7", 7), ("0", 2), ("99", 20), (["5"], 5), ("abc", None), (None, None)])
def test_permalink_values_are_clamped_to_the_slider(raw, expected):
    assert P._coerce(P.SETTING_SPECS["n_slider"], raw) == expected


def test_permalink_choice_values_must_be_listed():
    spec = P.SETTING_SPECS["kind_select"]
    assert P._coerce(spec, "grid") == "grid" and P._coerce(spec, "bogus") is None
    assert P._coerce(P.SETTING_SPECS["samples_select"], "10000") == 10_000 and P._coerce(P.SETTING_SPECS["samples_select"], "7") is None
    assert P._coerce(P.SETTING_SPECS["dens_select"], "50") == 50 and P._coerce(P.SETTING_SPECS["dens_select"], "55") is None
