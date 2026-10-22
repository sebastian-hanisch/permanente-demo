"""Konstanten: Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben und Presets.

Rechengrenze am Regler-Maximum (DEMO-PLAYBOOK §1c): n = 20: Glynn 2^19 Vektoren mit je 19 Multiplikationen (rund 10 Millionen, reines Python, ganze Zahlen), die Bitmasken-DP (numpy, int64) als zweite Rechnung
über 2^20 Zustände, die Determinante exakt in 4.940 Multiplikationen; Brute Force nur bis n = 8 (8! = 40.320 Permutationen). Der Schätzer läuft für n ≤ 12."""

N_MIN, N_MAX, DEFAULT_N = 2, 20, 8                    # Größe der Matrix
SEED_MAX, DEFAULT_SEED = 999999, 35
KINDS = {
    "random": "zufällig (Dichte einstellbar)",
    "full": "alle Einsen (J)",
    "derange": "J − I (alles erlaubt außer der Diagonale)",
    "blocks": "Blöcke aus 2 × 2 (alle Einsen)",
    "grid": "Gitter (Domino-Pflasterungen)",
}
DEFAULT_KIND = "random"
DENS_OPTIONS = (20, 30, 40, 50, 60, 70, 80)           # Dichte der Einsen in Prozent (nur für „zufällig“)
DEFAULT_DENS = 50
SAMPLES_OPTIONS = (100, 1_000, 10_000)                # Vorzeichenmatrizen des Schätzers (Illustration, nicht Beleg)
DEFAULT_SAMPLES = 1_000
BRUTE_N_MAX = 8                                       # Brute Force (Gegenprobe) nur bis hierhin
EST_N_MAX = 12                                        # Schätzer bis hierhin (die Determinante bleibt auf ganze Zahlen genau)
GRID_SHAPES = {                                       # n -> (Zeilen, Spalten) des Gitters mit n schwarzen und n weißen Zellen
    2: (2, 2), 3: (2, 3), 4: (2, 4), 5: (2, 5), 6: (3, 4), 7: (2, 7), 8: (4, 4), 9: (3, 6), 10: (4, 5), 11: (2, 11), 12: (4, 6), 13: (2, 13), 14: (4, 7),
    15: (5, 6), 16: (4, 8), 17: (2, 17), 18: (6, 6), 19: (2, 19), 20: (5, 8),
}

# Messreihen (alle Instanzen aus dem eigenen Generator: auf jeder Plattform dieselben)
DET_SIZES = (4, 6, 8, 10, 12)
DET_DENS = (30, 50, 70)
DET_COUNT = 200                                       # Matrizen je Größe und Dichte
DET_SEED = 2000
COST_SEED = 17                                        # Matrix für die gezählten Kosten der Determinante je n
EST_SIZES = (6, 8, 10, 12)
EST_MATRICES = 10                                     # Zufallsmatrizen (Dichte 50 %) je Größe
EST_REPS = 20                                         # Wiederholungen des Schätzers je Matrix
EST_N = 1_000                                         # Vorzeichenmatrizen je Schätzer
EST_SEED = 3000
EST_BLOCKS = (2, 3, 4, 5, 6)                          # Blöcke J2 (n = 4 bis 12)
POLYA_CASES = ("J2", "J3", "J4", "Gitter 2 × 3", "Gitter 2 × 4")     # Matrizen, deren Vorzeichenmuster alle aufgezählt werden

COLOR_BRUTE = "#C0392B"
COLOR_RYSER = "#B8860B"
COLOR_GLYNN = "#7a5195"
COLOR_DET = "#2F6B65"
COLOR_EXACT = "#4c78a8"
COLOR_SERIES = ("#2F6B65", "#4c78a8", "#B8860B", "#C0392B", "#7a5195")

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "random", "dens": DEFAULT_DENS, "samples": DEFAULT_SAMPLES},
    "Lehrbeispiel (3 × 3, alle Einsen)": {"n": 3, "seed": DEFAULT_SEED, "kind": "full", "dens": DEFAULT_DENS, "samples": DEFAULT_SAMPLES},
    "Derangements (J − I)": {"n": 7, "seed": DEFAULT_SEED, "kind": "derange", "dens": DEFAULT_DENS, "samples": DEFAULT_SAMPLES},
    "Blöcke (Schätzer streut)": {"n": 12, "seed": DEFAULT_SEED, "kind": "blocks", "dens": DEFAULT_DENS, "samples": DEFAULT_SAMPLES},
    "Gitter 4 × 4 (36 Pflasterungen)": {"n": 8, "seed": DEFAULT_SEED, "kind": "grid", "dens": DEFAULT_DENS, "samples": DEFAULT_SAMPLES},
    "Dichte Matrix": {"n": 10, "seed": DEFAULT_SEED, "kind": "random", "dens": 80, "samples": DEFAULT_SAMPLES},
    "Dünne Matrix": {"n": 10, "seed": DEFAULT_SEED, "kind": "random", "dens": 20, "samples": DEFAULT_SAMPLES},
}
PRESET_HELP = {   # nach der Messung geschrieben (DEMO-PLAYBOOK: Hilfetexte nie vor der Messung); jede Zahl steht in tests/test_claims.py
    "Standardfall (Voreinstellung)": "8 × 8, zufällig mit Dichte 50 % (Zufalls-Seed 35): 104 perfekte Paarungen, die Determinante ist −2; Glynn braucht 896 Multiplikationen, die Determinante 280.",
    "Lehrbeispiel (3 × 3, alle Einsen)": "3 × 3 mit lauter Einsen: 6 Paarungen (3!), aber die Determinante ist 0: drei Produkte tragen ein Plus, drei ein Minus und löschen sich aus.",
    "Derangements (J − I)": "J − I mit n = 7: 1.854 Paarungen (Permutationen ohne Fixpunkt), die Determinante ist 6.",
    "Blöcke (Schätzer streut)": "Sechs Blöcke aus 2 × 2 (n = 12): 64 Paarungen, Determinante 0. Der Schätzer streut stark: bei nur 12 von 1.000 Vorzeichenmatrizen ist der Wert größer als 0, das Mittel ist 49,2 statt 64.",
    "Gitter 4 × 4 (36 Pflasterungen)": "Das 4 × 4-Gitter als Matrix: 36 Domino-Pflasterungen, die einfache Determinante ist 0; mit dem Kasteleyn-Vorzeichen (Experiment 3) zählt sie die 36.",
    "Dichte Matrix": "10 × 10 mit Dichte 80 %: 330.936 Paarungen, die Determinante ist 0.",
    "Dünne Matrix": "10 × 10 mit Dichte 20 %: keine perfekte Paarung (Permanente 0). Die Existenz stellt das Verfahren mit augmentierenden Wegen fest, ohne zu zählen.",
}
