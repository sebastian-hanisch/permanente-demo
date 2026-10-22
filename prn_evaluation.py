"""Kennzahlen, Messreihen und Verdikte (alle Verdikte sind reine Funktionen (Art, Text), DEMO-PLAYBOOK §12).

Anteile sind **Brüche** (`Fraction`): Schranken werden exakt verglichen, nie mit Gleitkomma. Anzahlen sind ganze Zahlen (exakt, Python)."""

import math
from dataclasses import dataclass
from fractions import Fraction
from statistics import median

import numpy as np

import prn_algorithm as A
import prn_constants as C
from prn_rng import SplitMix64
from prn_scenario import make_matrix, random01


@dataclass(frozen=True, kw_only=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    kind: str = C.DEFAULT_KIND
    dens: int = C.DEFAULT_DENS
    samples: int = C.DEFAULT_SAMPLES


@dataclass(frozen=True)
class Estimate:
    samples: int
    mean: Fraction                   # Mittel der Werte X = det(A ∘ S)^2 (exakt: Summe ganzer Zahlen durch N)
    std_error: float                 # Standardfehler des Mittels aus der Stichprobe
    nonzero: int                     # Stichproben mit X > 0
    maximum: int


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    matrix: tuple
    ones: int
    per: int                         # Permanente = Zahl der perfekten Paarungen (Glynn)
    per_mults: int                   # Multiplikationen von Glynn
    ryser_mults: int
    brute_mults: int
    det: int
    det_mults: int                   # gezählte Multiplikationen der Determinante (bei vorzeitigem Ende weniger als die Formel)
    exists: bool                     # perfekte Paarung vorhanden (augmentierende Wege)
    ratio: Fraction | None           # |det| / per (None bei per = 0)
    estimate: Estimate | None        # None bei n > EST_N_MAX


# --- Zahlen im deutschen Format ------------------------------------------------------------------------------------------------------------


def fmt_int(n: int) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner (1.720.350)."""
    return f"{n:,}".replace(",", ".").replace("-", "−")


def fmt_num(x: float, digits: int = 1) -> str:
    """Dezimalzahl mit Komma (22,7)."""
    return f"{x:.{digits}f}".replace(".", ",")


def fmt_big(n: int) -> str:
    """Ganze Zahl: bis 10^9 mit Tausenderpunkten, darüber in Zehnerpotenz („3,3 · 10^14“)."""
    if abs(n) < 10 ** 9:
        return fmt_int(n)
    mantissa, exponent = f"{n:.1e}".split("e")
    return f"{mantissa.replace('.', ',').replace('-', '−')} · 10^{int(exponent)}"


def fmt_fraction(f: Fraction, digits: int = 4) -> str:
    """Bruch mit Dezimalwert: „1/2 (0,5)“, sehr kleine Werte (unter 0,0001) in Zehnerpotenz; ganze Zahlen ohne Bruch."""
    if f.denominator == 1:
        return str(f.numerator)
    x = float(f)
    if 0 < x < 10 ** (-digits):
        mantissa, exponent = f"{x:.1e}".split("e")
        dec = f"{mantissa.replace('.', ',')} · 10^(−{abs(int(exponent))})"
    else:
        dec = f"{x:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{f.numerator}/{f.denominator} ({dec})"


def fmt_percent(f, digits: int = 1) -> str:
    """Anteil als Prozentzahl mit Komma, ohne überflüssige Nachkommastelle (57,1 %, 25 %)."""
    x = round(float(f) * 100, digits)
    return (fmt_int(int(x)) if x == int(x) else fmt_num(x, digits)) + " %"


def fmt_ratio(f: Fraction) -> str:
    """Verhältnis als Dezimalzahl mit Komma (drei Stellen, ab 0,01 abwärts vier); unter 0,0001 in Zehnerpotenz („2,3 · 10^(−9)“)."""
    x = float(f)
    if 0 < x < 1e-4:
        mantissa, exponent = f"{x:.1e}".split("e")
        return f"{mantissa.replace('.', ',')} · 10^(−{abs(int(exponent))})"
    return fmt_num(x, 3 if x >= 0.01 else 4)


# --- Schätzer ------------------------------------------------------------------------------------------------------------------------------


def estimate(a, samples: int, seed: int) -> Estimate:
    """Godsil–Gutman: `samples` zufällige Vorzeichenmatrizen (Strom des Generators mit dem Zufalls-Seed `seed`), X = det(A ∘ S)^2; E[X] = per(A)."""
    n = len(a)
    values = A.gg_values(a, A.random_signs(SplitMix64(seed), samples, n))
    total = int(values.sum())
    mean = Fraction(total, samples)
    if samples > 1:
        var = float(np.var(values.astype(np.float64), ddof=1))
        std_error = math.sqrt(var / samples)
    else:
        std_error = 0.0
    return Estimate(samples, mean, std_error, int((values > 0).sum()), int(values.max()))


# --- Einzelanalyse -------------------------------------------------------------------------------------------------------------------------


def analyse(settings: Settings) -> Analysis:
    a = make_matrix(settings.kind, settings.n, settings.dens, settings.seed)
    n = len(a)
    per, per_mults = A.per_glynn(a)
    det, det_mults = A.det_bareiss(a)
    est = estimate(a, settings.samples, settings.seed ^ 0x9E3779B1) if n <= C.EST_N_MAX else None
    return Analysis(settings, a, sum(map(sum, a)), per, per_mults, A.mults_ryser(n), A.mults_brute(n), det, det_mults, A.has_perfect_matching(a),
                    Fraction(abs(det), per) if per else None, est)


def validation_errors(a: Analysis) -> list:
    """Ergebnis vor der Anzeige prüfen (DEMO-PLAYBOOK §1d): Permanente gegen eine zweite und (bis n = 8) dritte Rechnung, Schranken und Parität der Determinante, Existenz gegen die Anzahl, Kosten gegen die
    Formeln, Determinante gegen numpy, Schätzer (nie negativ, bei per = 0 genau 0, bei höchstens 16 Einsen alle Werte aus der Aufzählung)."""
    errors = []
    m, n = a.matrix, len(a.matrix)
    if any(len(row) != n or any(x not in (0, 1) for x in row) for row in m):
        return ["Die Matrix ist nicht quadratisch oder nicht 0/1."]
    if a.per != A.per_dp(m):
        errors.append("Die Permanente widerspricht der zweiten Rechnung (Bitmasken-DP).")
    if n <= C.BRUTE_N_MAX and a.per != A.per_brute(m)[0]:
        errors.append("Die Permanente widerspricht der Definition (Brute Force).")
    rows = math.prod(sum(row) for row in m)
    cols = math.prod(sum(m[i][j] for i in range(n)) for j in range(n))
    if a.per < 0 or a.per > min(rows, cols):
        errors.append("Die Permanente liegt außerhalb von 0 bis zum Produkt der Zeilen- bzw. Spaltensummen.")
    if abs(a.det) > a.per:
        errors.append("Der Betrag der Determinante ist größer als die Permanente.")
    if (a.per - a.det) % 2:
        errors.append("Determinante und Permanente haben verschiedene Parität.")
    if a.exists != (a.per > 0):
        errors.append("Die Existenz einer perfekten Paarung widerspricht der Permanente.")
    if abs(float(np.linalg.det(np.array(m, dtype=float))) - a.det) > 1e-6 * max(1, abs(a.det)):
        errors.append("Die Determinante widerspricht numpy.")
    if a.per_mults != A.mults_glynn(n) or a.ryser_mults != A.mults_ryser(n) or a.brute_mults != A.mults_brute(n) or not 0 <= a.det_mults <= A.mults_det(n):
        errors.append("Die gezählten Multiplikationen widersprechen den Formeln.")
    if a.estimate is not None:
        e = a.estimate
        if e.mean < 0 or (a.per == 0 and e.mean != 0):
            errors.append("Der Schätzer ist negativ oder von null verschieden bei Permanente 0.")
        if a.ones <= A.SIGN_ONES_MAX:
            dets = A.all_sign_dets(m)
            if Fraction(int((dets.astype(np.int64) ** 2).sum()), len(dets)) != a.per:
                errors.append("Der Erwartungswert des Schätzers (aufgezählt) ist nicht die Permanente.")
            if e.maximum not in {int(d) ** 2 for d in dets}:
                errors.append("Ein Stichprobenwert kommt unter den aufgezählten Werten nicht vor.")
    return errors


# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------


def cost_rows(ns=range(C.N_MIN, C.N_MAX + 1)) -> list:
    """Multiplikationen je n: Brute Force, Ryser, Glynn (geschlossene Formeln) und die Determinante (Formel und gezählt an einer festen Zufallsmatrix mit Dichte 50 %)."""
    rows = []
    for n in ns:
        counted = A.det_bareiss(random01(n, 50, SplitMix64(C.COST_SEED + n)))[1]
        rows.append({"n": n, "brute": A.mults_brute(n), "ryser": A.mults_ryser(n), "glynn": A.mults_glynn(n), "det": A.mults_det(n), "det_counted": counted})
    return rows


def sweep_det(sizes=C.DET_SIZES, dens_list=C.DET_DENS, count: int = C.DET_COUNT, seed: int = C.DET_SEED) -> list:
    """Determinante gegen Permanente an festen Zufallsmatrizen je Größe und Dichte (Permanente per Bitmasken-DP, im Orakel-Test gleich Glynn): Matrizen mit perfekter Paarung, davon det = 0, mittleres und
    mittleres Median-Verhältnis |det| / per (exakte Brüche), Parität und Schranke |det| ≤ per bei allen."""
    rows = []
    for n in sizes:
        for dens in dens_list:
            rng = SplitMix64(seed + 1000 * dens + n)
            ratios, det_zero, parity, bound = [], 0, True, True
            for _ in range(count):
                m = random01(n, dens, rng)
                per = A.per_dp(m)
                det = A.det_bareiss(m)[0]
                parity = parity and (per - det) % 2 == 0
                bound = bound and abs(det) <= per
                if per:
                    ratios.append(Fraction(abs(det), per))
                    det_zero += det == 0
            rows.append({"n": n, "dens": dens, "count": count, "with_pm": len(ratios), "det_zero": det_zero, "mean": sum(ratios) / len(ratios) if ratios else None,
                         "median": median(ratios) if ratios else None, "parity_all": parity, "bound_all": bound})
    return rows


def polya_rows() -> list:
    """Alle Vorzeichenmuster kleiner Matrizen: wie oft ist |det| gleich der Permanente? Matrizen: J2, J3, J4, Gitter 2 × 3 und 2 × 4."""
    cases = {"J2": ((1, 1), (1, 1)), "J3": ((1,) * 3,) * 3, "J4": ((1,) * 4,) * 4, "Gitter 2 × 3": A.grid_biadjacency(2, 3)[0], "Gitter 2 × 4": A.grid_biadjacency(2, 4)[0]}
    rows = []
    for name in C.POLYA_CASES:
        m = cases[name]
        per = A.per_dp(m)
        counts = A.sign_pattern_counts(m)
        rows.append({"name": name, "n": len(m), "ones": sum(map(sum, m)), "patterns": 2 ** sum(map(sum, m)), "per": per, "counts": dict(sorted(counts.items())), "hits": counts.get(per, 0)})
    return rows


KASTELEYN_SHAPES = ((2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (4, 5), (4, 6), (5, 6), (6, 6), (5, 8))


def kasteleyn_rows(shapes=KASTELEYN_SHAPES) -> list:
    """Gitter: Zahl der Pflasterungen (Permanente, Bitmasken-DP) und |det| der Matrix mit Kasteleyn-Vorzeichen (senkrechte Kanten in ungeraden Spalten −1)."""
    rows = []
    for r, c in shapes:
        m = A.grid_biadjacency(r, c)[0]
        per = A.per_dp(m)
        rows.append({"rows": r, "cols": c, "n": len(m), "per": per, "det_signed": abs(A.det_bareiss(A.kasteleyn_signed(r, c))[0]), "det_plain": abs(A.det_bareiss(m)[0])})
    return rows


def _rel_std(estimates: list, per: int) -> float:
    """Stichproben-Standardabweichung der Schätzer-Mittel (exakte Brüche, Wurzel erst am Ende) geteilt durch die Permanente."""
    reps = len(estimates)
    mean = sum(estimates) / reps
    var = sum((e - mean) ** 2 for e in estimates) / (reps - 1)
    return math.sqrt(float(var)) / per


def sweep_estimator(sizes=C.EST_SIZES, matrices: int = C.EST_MATRICES, reps: int = C.EST_REPS, samples: int = C.EST_N, blocks=C.EST_BLOCKS, seed: int = C.EST_SEED) -> dict:
    """Streuung des Schätzers: je Größe `matrices` Zufallsmatrizen (Dichte 50 %), je Matrix `reps` Schätzer aus `samples` Vorzeichenmatrizen; gemessen wird die relative Standardabweichung der Schätzer.
    Dazu Blockdiagonalen aus k Blöcken J2 (n = 2k): gemessen gegen die exakte Vorhersage sqrt((2^k − 1) / samples)."""
    random_rows = []
    for n in sizes:
        rels, skipped = [], 0
        for i in range(matrices):
            m = random01(n, 50, SplitMix64(seed + 100 * n + i))
            per = A.per_dp(m)
            if per == 0:
                skipped += 1
                continue
            rng = SplitMix64(seed + 7 * n + i)
            ests = [Fraction(int(A.gg_values(m, A.random_signs(rng, samples, n)).sum()), samples) for _ in range(reps)]
            rels.append(_rel_std(ests, per))
        random_rows.append({"n": n, "matrices": len(rels), "skipped": skipped, "mean_rel": sum(rels) / len(rels), "max_rel": max(rels)})
    block_rows = []
    for k in blocks:
        m = tuple(tuple(int(i // 2 == j // 2) for j in range(2 * k)) for i in range(2 * k))
        rng = SplitMix64(seed + 5000 + k)
        ests = [Fraction(int(A.gg_values(m, A.random_signs(rng, samples, 2 * k)).sum()), samples) for _ in range(reps)]
        var = A.block_variance(k)
        block_rows.append({"k": k, "n": 2 * k, "per": 2 ** k, "rel": _rel_std(ests, 2 ** k), "predicted": math.sqrt(var / samples), "variance": var, "needed": 100 * var})
    return {"samples": samples, "reps": reps, "random": random_rows, "blocks": block_rows}


# --- Verdikte (reine Funktionen: (Art, Text)) ------------------------------------------------------------------------------------------------------


def verdict_main(a: Analysis) -> tuple:
    n = len(a.matrix)
    cost = (f"Aufwand: Glynn {fmt_big(a.per_mults)} Multiplikationen, Ryser {fmt_big(a.ryser_mults)}, Brute Force {fmt_big(a.brute_mults)}; die Determinante {fmt_int(a.det_mults)}.")
    if not a.exists:
        return "info", (f"Es gibt keine perfekte Paarung (Permanente 0, Determinante {fmt_int(a.det)}): einzelne Zeilen oder Spalten sind nicht zu besetzen. Die Existenz hat der Test mit augmentierenden Wegen "
                        f"in wenigen Schritten gezeigt, ohne zu zählen. {cost}")
    head = (f"Die {n} × {n}-Matrix hat {fmt_int(a.per)} perfekte Paarungen (Permanente). Die Determinante ist {fmt_int(a.det)}")
    if a.det == 0:
        return "warning", (f"{head}, obwohl Paarungen existieren: die Vorzeichen löschen sich vollständig aus. Beide haben dieselbe Parität. {cost}")
    if abs(a.det) == a.per:
        return "success", (f"{head}: hier gleich der Permanente im Betrag (kein Zufall der Vorzeichen, sondern Struktur der Matrix). Beide haben dieselbe Parität. {cost}")
    return "warning", (f"{head}, im Betrag {fmt_ratio(a.ratio)} der Permanente: die Vorzeichen löschen einen Teil aus, die Parität bleibt gleich. {cost}")


def verdict_costs(rows: list) -> tuple:
    first, last = rows[0], rows[-1]
    first_ryser = next(r["n"] for r in rows if r["ryser"] < r["brute"])
    return "info", (
        f"Bei n = {last['n']} kostet Brute Force {fmt_big(last['brute'])} Multiplikationen, Ryser {fmt_big(last['ryser'])}, Glynn {fmt_big(last['glynn'])}, die Determinante {fmt_int(last['det'])} "
        f"(gezählt an einer festen Zufallsmatrix: {fmt_int(last['det_counted'])}). Das Verhältnis Glynn : Determinante wächst von {fmt_num(first['glynn'] / first['det'], 1)} : 1 bei n = {first['n']} "
        f"auf rund {fmt_int(round(last['glynn'] / last['det']))} : 1 bei n = {last['n']}. Ryser ist ab n = {first_ryser} billiger als Brute Force."
    )


def verdict_det_sweep(rows: list) -> tuple:
    total = sum(r["count"] for r in rows)
    if not all(r["bound_all"] for r in rows):
        return "error", "Der Betrag der Determinante überschritt die Permanente: das darf nicht sein."
    if not all(r["parity_all"] for r in rows):
        return "error", "Determinante und Permanente hatten verschiedene Parität: das darf nicht sein."
    mid = [r for r in rows if r["dens"] == 50]
    lo, hi = mid[0], mid[-1]
    zero = max(rows, key=lambda r: Fraction(r["det_zero"], r["with_pm"]))
    return "info", (
        f"In allen {fmt_int(total)} Matrizen war |det| ≤ per und die Parität gleich (Sätze, hier geprüft). Bei Dichte 50 % fällt das mittlere |det| / per von {fmt_ratio(lo['mean'])} (n = {lo['n']}) auf "
        f"{fmt_ratio(hi['mean'])} (n = {hi['n']}). Der Anteil der Matrizen mit perfekter Paarung, aber det = 0, ist am größten bei n = {zero['n']}, Dichte {zero['dens']} %: "
        f"{fmt_percent(Fraction(zero['det_zero'], zero['with_pm']))}."
    )


def verdict_polya(rows: list) -> tuple:
    by = {r["name"]: r for r in rows}
    j3, j4 = by["J3"], by["J4"]
    if j3["hits"] or j4["hits"]:
        return "error", "Für J3 oder J4 gibt es ein Vorzeichenmuster mit |det| = per: das widerspricht der Aufzählung."
    g23, g24 = by["Gitter 2 × 3"], by["Gitter 2 × 4"]
    return "info", (
        f"Bei J3 erreicht keines der {fmt_int(j3['patterns'])} Vorzeichenmuster |det| = {j3['per']} (die Beträge sind nur {', '.join(str(k) for k in j3['counts'])}); bei J4 keines der {fmt_int(j4['patterns'])} "
        f"(Beträge {', '.join(str(k) for k in j4['counts'])}, die Permanente ist {j4['per']}). Beim Gitter 2 × 3 erreichen {fmt_int(g23['hits'])} von {fmt_int(g23['patterns'])} Mustern die Permanente {g23['per']}, "
        f"beim Gitter 2 × 4 {fmt_int(g24['hits'])} von {fmt_int(g24['patterns'])} (Permanente {g24['per']}): Auf planaren Gittern lassen sich die Vorzeichen richten, allgemein nicht."
    )


def verdict_kasteleyn(rows: list) -> tuple:
    if any(r["det_signed"] != r["per"] for r in rows):
        return "error", "Mit den Kasteleyn-Vorzeichen war |det| nicht die Zahl der Pflasterungen: das darf nicht sein."
    big = rows[-1]
    plain = sum(1 for r in rows if r["det_plain"] != r["per"])
    return "success", (
        f"Mit dem Vorzeichen −1 an den senkrechten Kanten in ungeraden Spalten zählt die Determinante in allen {len(rows)} Gittern die Pflasterungen (größtes: {big['rows']} × {big['cols']} mit {fmt_int(big['per'])}); "
        f"ohne die Vorzeichen ist |det| in {plain} von {len(rows)} Gittern falsch."
    )


def verdict_estimator(res: dict) -> tuple:
    rnd, blocks = res["random"], res["blocks"]
    last = blocks[-1]
    return "warning", (
        f"Auf Zufallsmatrizen (Dichte 50 %) liegt die relative Streuung des Schätzers aus {fmt_int(res['samples'])} Vorzeichenmatrizen bei {fmt_percent(rnd[0]['mean_rel'])} (n = {rnd[0]['n']}) bis "
        f"{fmt_percent(rnd[-1]['mean_rel'])} (n = {rnd[-1]['n']}): brauchbar. Bei Blöcken aus J2 beträgt sie nach der Rechnung exakt √((2^k − 1) / N): für k = {last['k']} (n = {last['n']}) vorhergesagt {fmt_percent(last['predicted'])}, "
        f"gemessen {fmt_percent(last['rel'])}; für eine Standardabweichung von 10 % braucht man etwa {fmt_int(last['needed'])} Vorzeichenmatrizen, und die Zahl wird mit jedem Block etwa verdoppelt."
    )
