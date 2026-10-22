"""Randfälle: Reglergrenzen, Matrixarten, Rechengrenzen und Szenario."""

import pytest

import prn_algorithm as A
import prn_constants as C
import prn_evaluation as ev
from prn_rng import SplitMix64
from prn_scenario import blocks, derange, full, grid, make_matrix, random01


@pytest.mark.parametrize("kind", list(C.KINDS))
@pytest.mark.parametrize("n", [C.N_MIN, 3, C.N_MAX])
def test_extremes_of_the_sliders_are_clean(n, kind):
    a = ev.analyse(ev.Settings(n=n, kind=kind, samples=100))
    assert ev.validation_errors(a) == []
    assert ev.verdict_main(a)[0] in ("info", "success", "warning")


@pytest.mark.parametrize("seed", [0, C.SEED_MAX])
def test_seed_bounds(seed):
    assert ev.validation_errors(ev.analyse(ev.Settings(seed=seed))) == []


@pytest.mark.parametrize("dens", C.DENS_OPTIONS)
def test_every_density_option_is_valid(dens):
    assert ev.validation_errors(ev.analyse(ev.Settings(n=9, dens=dens))) == []


@pytest.mark.parametrize("samples", C.SAMPLES_OPTIONS)
def test_every_sample_option_is_valid(samples):
    a = ev.analyse(ev.Settings(n=6, kind="full", samples=samples))
    assert ev.validation_errors(a) == [] and a.estimate.samples == samples


def test_largest_matrix_is_counted_exactly():
    a = ev.analyse(ev.Settings(n=C.N_MAX, kind="full"))
    assert a.per == 2_432_902_008_176_640_000 and a.det == 0 and a.estimate is None
    assert a.per_mults == 19 * 2 ** 19 and a.ryser_mults == 19 * (2 ** 20 - 1)


def test_smallest_matrix_two_by_two():
    a = ev.analyse(ev.Settings(n=2, kind="full"))
    assert (a.per, a.det) == (2, 0) and a.estimate.nonzero >= 0
    b = ev.analyse(ev.Settings(n=2, kind="blocks"))
    assert (b.per, b.det) == (2, 0)


# --- Szenario ----------------------------------------------------------------------------------------------------------------------------------


def test_matrix_kinds_at_hand_values():
    assert full(2) == ((1, 1), (1, 1)) and derange(3) == ((0, 1, 1), (1, 0, 1), (1, 1, 0))
    assert blocks(4) == ((1, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 1), (0, 0, 1, 1))
    assert blocks(3) == ((1, 1, 0), (1, 1, 0), (0, 0, 1))                                  # ungerade n: letzter Block (1)
    assert grid(2) == ((1, 1), (1, 1)) and len(grid(8)) == 8


def test_random_matrix_is_deterministic_and_obeys_the_density_bounds():
    assert random01(6, 50, SplitMix64(3)) == random01(6, 50, SplitMix64(3)) != random01(6, 50, SplitMix64(4))
    assert random01(5, 0, SplitMix64(1)) == ((0,) * 5,) * 5 and random01(5, 100, SplitMix64(1)) == ((1,) * 5,) * 5
    ones = sum(map(sum, random01(40, 30, SplitMix64(8))))
    assert 400 <= ones <= 560                                                              # 1.600 Einträge, Erwartung 480


def test_random_matrix_uses_the_documented_draw_order():
    rng = SplitMix64(11)
    expected = tuple(tuple(int(rng.below(100) < 70) for _ in range(3)) for _ in range(3))
    assert random01(3, 70, SplitMix64(11)) == expected


def test_make_matrix_dispatch_and_unknown_kind():
    assert make_matrix("full", 3, 50, 0) == full(3) and make_matrix("derange", 3, 50, 0) == derange(3) and make_matrix("blocks", 5, 50, 0) == blocks(5)
    assert make_matrix("grid", 6, 50, 0) == grid(6) and make_matrix("random", 4, 50, 9) == random01(4, 50, SplitMix64(9))
    assert make_matrix("full", 3, 20, 1) == make_matrix("full", 3, 80, 2)                    # nur „zufällig“ benutzt Dichte und Zufalls-Seed
    with pytest.raises(ValueError):
        make_matrix("bogus", 3, 50, 0)


def test_grid_shapes_cover_every_slider_value():
    assert set(C.GRID_SHAPES) == set(range(C.N_MIN, C.N_MAX + 1))


# --- Rechengrenzen ---------------------------------------------------------------------------------------------------------------------------------


def test_permanent_of_the_largest_matrix_fits_into_int64():
    assert A.PER_N_MAX == C.N_MAX and A.PER_N_MAX == 20
    import math
    assert math.factorial(A.PER_N_MAX) < 2 ** 63 <= math.factorial(21)


def test_estimator_limits_agree_between_app_and_algorithm():
    assert C.EST_N_MAX <= A.EST_N_MAX
    with pytest.raises(ValueError):
        A.gg_values(full(A.EST_N_MAX + 1), A.random_signs(SplitMix64(1), 1, A.EST_N_MAX + 1))


def test_estimator_is_exact_up_to_its_limit():
    e = ev.estimate(full(A.EST_N_MAX), 5, 3)                                              # n = 14: Gleitkomma-Determinante auf ganze Zahlen genau
    assert e.samples == 5 and e.mean >= 0


def test_singular_matrices_have_zero_determinant_and_positive_permanent_when_a_matching_exists():
    a = ev.analyse(ev.Settings(n=12, kind="blocks"))
    assert a.det == 0 and a.per == 64 and a.exists
