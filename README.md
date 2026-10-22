# Zählen: Permanente gegen Determinante – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-permanente-demo.streamlit.app/)** -->

Neuntes (optionales) Stück der **Komplexitätsklassen-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Stück 8 ([zufallsverfahren-demo](https://github.com/sebastian-hanisch/zufallsverfahren-demo)) zeigt, was der Zufall bei einem Entscheidungsproblem kauft; dieses Stück zeigt die Gegenseite: **Zählen** statt Entscheiden. Anders als die Fall-Demos zeigt es **eine Frage der Komplexitätstheorie** an einem kleinen Beispiel. Die planare Ausnahme, in der das Zählen perfekter Paarungen leicht wird, steht im [kasteleyn-demo](https://github.com/sebastian-hanisch/kasteleyn-demo) (Verfahren von Fisher, Kasteleyn und Temperley); hier wird sie nur gegengeprüft, nicht nachgebaut. Die Existenz einer Paarung entscheidet sich mit augmentierenden Wegen (vgl. [hopcroft-karp-demo](https://github.com/sebastian-hanisch/hopcroft-karp-demo)).

## Warum dieses Problem

„Gibt es eine perfekte Paarung?“ ist leicht, „**Wie viele** gibt es?“ vermutlich nicht. Die Zahl der perfekten Paarungen eines bipartiten Graphen (Zeilen gegen Spalten, 1 = erlaubt) ist die **Permanente** der 0/1-Matrix, per(A) = Σ über alle Permutationen π von Π a_{i,π(i)}. Die **Determinante** hat dieselbe Summe mit dem Vorzeichen von π: die Vorzeichen löschen sich aus und machen sie in n³ Schritten berechenbar (Gauß, hier Bareiss mit ganzen Zahlen), aber als Zählung **falsch**. Nach Valiant (1979) ist die Permanente **#P-vollständig** (Literatur, nicht gemessen); die Demo **misst** nur, was die hier gebauten exakten Verfahren kosten, was der Determinante fehlt, ob sich ihre Vorzeichen richten lassen und was ein einfacher Zufallsschätzer leistet. Aufwand wird in **Multiplikationen** gezählt (ein Produkt aus n Faktoren kostet n − 1), nie in Sekunden.

## Modell

- **Matrizen.** n × n mit Einträgen 0 und 1 (n = 2 bis 20), fünf Arten: zufällig mit Dichte 20 bis 80 % (eigener SplitMix64-Generator, deshalb auf jeder Plattform dieselben Matrizen; jeder Eintrag ist 1, wenn `below(100) < Dichte`), alle Einsen (J), J − I, Blockdiagonale aus n / 2 Blöcken J₂ (bei ungeradem n am Ende ein Block (1)) und die Biadjazenzmatrix eines **Gitters** (schwarze gegen weiße Zellen; n wählt die Form, zum Beispiel n = 8: 4 × 4, n = 18: 6 × 6, n = 20: 5 × 8). **Jede Zahl gilt für diese Familien**, nicht für alle 0/1-Matrizen.
- **Permanente, vier Wege.** Brute Force (alle n! Permutationen, nur bis n = 8 als Gegenprobe), **Ryser** (Summe über alle 2ⁿ − 1 nichtleeren Spaltenteilmengen), **Glynn** (2ⁿ⁻¹ Vorzeichenvektoren im Gray-Code, das Verfahren der Anzeige) und eine **Bitmasken-DP** (numpy, int64; zweite Rechnung der Prüfung vor der Anzeige). Multiplikationen: n!·(n − 1), (2ⁿ − 1)·(n − 1), 2ⁿ⁻¹·(n − 1).
- **Determinante.** Bareiss in ganzen Zahlen; Multiplikationen (n − 1)·n·(2n − 1) / 3, bei Singularität früher beendet (dann gezählt weniger).
- **Existenz.** Größte Paarung nach Kuhn (augmentierende Wege), ohne zu zählen.
- **Vorzeichen (Pólya).** Alle 2^e Vorzeichenmuster einer Matrix mit e ≤ 16 Einsen; gefragt wird, wie oft |det| gleich der Permanente ist. **Gitter:** Vorzeichen −1 an den senkrechten Kanten in ungeraden Spalten (Spalten ab 0).
- **Schätzer (Godsil–Gutman).** X = det(A ∘ S)² mit unabhängigen zufälligen Vorzeichen S; E[X] = per(A). Die Vorzeichen kommen aus dem Strom des Generators (64 je Wort, niedrigstes Bit zuerst), die Determinanten werden auf ganze Zahlen gerundet (bis n = 14 exakt, im Regler bis n = 12). **Illustration, kein Beleg.**
- Mathematik (Ryser, Glynn, Godsil–Gutman, Blockvarianz) und Annahmentabelle: Expander **📐 Mathematische Formulierung** in der App.

## Methodik

| Baustein | Datei | Anmerkung |
|---|---|---|
| Permanente (Brute Force, Ryser, Glynn, DP), Determinante (Bareiss), Existenz, Vorzeichenmuster, Gitter und Kasteleyn-Vorzeichen, Schätzer | `prn_algorithm.py` | eine Regel = eine Funktion; Kosten als geschlossene Formeln, im Test gegen die Zählung |
| 0/1-Matrizen der fünf Arten | `prn_scenario.py` | deterministisch aus Art, n, Dichte und Zufalls-Seed |
| SplitMix64 | `prn_rng.py` | **wörtliche Kopie** von reduktionskette-demo/red_scenario.py (Commit ba24648); Regressionstest `tests/test_copies.py` |
| Kennzahlen, Messreihen, Prüfung vor der Anzeige, Verdikte | `prn_evaluation.py` | Anteile als `Fraction`; alle Verdikte reine Funktionen |

Experimente in der App: **Wie teuer ist Zählen?** (sofort), **Was fehlt der Determinante?** (Knopf, unter einer Sekunde), **Lassen sich die Vorzeichen reparieren?** (sofort), **Zählen durch Würfeln?** (Knopf, rund 2 Sekunden), **Einordnung** (#P, Näherung; nur Text).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Die Messreihen laufen über feste Instanzen aus dem eigenen Generator, die Presets sind Einzelinstanzen und als solche ausgewiesen. Schätzer-Streuungen sind Messwerte (auf drei Stellen), alles andere exakt.

| Frage | Befund |
|---|---|
| **Was kostet Zählen gegen Determinante?** (H1, H2) | Multiplikationen für n = 4 / 8 / 12 / 16 / 20: Brute Force 72 / 282.240 / 5.269.017.600 / 3,1 · 10¹⁴ / 4,6 · 10¹⁹; Ryser 45 / 1.785 / 45.045 / 983.025 / 19.922.925; **Glynn 24 / 896 / 22.528 / 491.520 / 9.961.472**; Determinante (Formel) 28 / 280 / 1.012 / 2.480 / **4.940** (gezählt an einer festen Zufallsmatrix: 26 / 280 / 1.012 / 2.480 / 4.940). **Ryser ist ab n = 4 billiger als Brute Force**; Glynn kostet etwa die Hälfte von Ryser (bei n = 20: 2 · 9.961.472 − 19 = 19.922.925); **Glynn kostet ab n = 5 mehr als die Determinante** (64 gegen 60), bei n = 20 **rund 2.016-mal so viel**. Glynn bei n = 20 in reinem Python in etwa einer Sekunde (Entwicklungsrechner, keine Test-Aussage) (`test_claim_cost_table`, `test_claim_cost_crossovers`). |
| **Was fehlt der Determinante?** (H3, H4) | 5 Größen (n = 4, 6, 8, 10, 12) · 3 Dichten (30, 50, 70 %) · 200 feste Zufallsmatrizen = **3.000 Matrizen: in allen |det| ≤ per und dieselbe Parität** (beides Sätze: Vorzeichen sind ±1, modulo 2 gleich 1). Bei Dichte 50 % fällt das **mittlere |det| / per** von **0,453 (n = 4)** über 0,160 (6), 0,023 (8), 0,0021 (10) auf **0,0002 (n = 12)**; bei jeder Dichte fällt es mit n. **Auslöschung vollständig:** bei Dichte 50 % haben 45 von 108 (n = 4), 74 von 158 (6), 73 von 184 (8), 59 von 196 (10) und 30 von 200 (12) Matrizen mit Paarung die Determinante 0; der größte Anteil überhaupt ist **141 von 196 = 71,9 %** (n = 6, Dichte 70 %) (`test_claim_det_table`, `test_claim_theorems_hold_in_all_3000_matrices`). |
| **Lassen sich die Vorzeichen reparieren?** (H5, H6) | **J₃** (alle Einsen, Permanente 6): von allen **512** Vorzeichenmustern ergibt keines |det| = 6 (die Beträge sind 0 in 320 und 4 in 192 Mustern). **J₄** (Permanente 24): von allen **65.536** keines (0 in 43.264, 8 in 21.504, 16 in 768 Mustern). **Gitter 2 × 3** (Permanente 3): 32 von 128 Mustern; **Gitter 2 × 4** (5): 128 von 1.024. Mit dem Kasteleyn-Vorzeichen (−1 an senkrechten Kanten in ungeraden Spalten) zählt |det| die Domino-Pflasterungen in **allen 10** geprüften Gittern: 2 × 2: 2, 2 × 3: 3, 2 × 4: 5, 3 × 4: 11, **4 × 4: 36**, 4 × 5: 95, 4 × 6: 281, 5 × 6: 1.183, **6 × 6: 6.728**, 5 × 8 (n = 20): 14.824; ohne Vorzeichen ist |det| nur 0 oder 1 (`test_claim_polya_table`, `test_claim_kasteleyn_table`). |
| **Zählen durch Würfeln?** (H7, H8, H9) | Der Schätzer ist erwartungstreu: für J₃ und J₄ aufgezählt E[X] = 6 und 24; Varianz / Permanente² dort 5/3 und 8/3. **Zufallsmatrizen** (Dichte 50 %, 10 je Größe, 20 Wiederholungen, 1.000 Vorzeichenmatrizen je Schätzer): relative Streuung **5,5 % (n = 6), 7,0 % (8), 9,2 % (10), 10,5 % (12)**; 1 von 10 Matrizen ohne Paarung bei n = 6 und n = 10. **Blöcke aus J₂** (n = 2k, Permanente 2ᵏ): Varianz / Permanente² = **2ᵏ − 1 exakt** (aufgezählt für k = 1 bis 4); gemessene Streuung bei N = 1.000: **6,2 % / 8,5 % / 11,3 % / 21,4 % / 22,2 %** für k = 2 bis 6 gegen √((2ᵏ − 1) / 1.000) = 5,5 / 8,4 / 12,2 / 17,6 / 25,1 %; die gemessenen Werte stammen aus nur 20 Wiederholungen und schwanken, die Rechnung ist der verlässlichere Wert; für eine Standardabweichung von 10 % braucht man etwa 100·(2ᵏ − 1) Vorzeichenmatrizen: 300 / 700 / 1.500 / 3.100 / 6.300, **etwa das Doppelte mit jedem Block** (`test_claim_estimator_on_random_matrices`, `test_claim_estimator_on_blocks`, `test_claim_estimator_is_unbiased_and_the_variance_of_j3_and_j4_is_small`). |
| **Presets (Einzelinstanzen)** | Permanente / Determinante / Multiplikationen Glynn gegen Determinante: **Standardfall** (n = 8, Dichte 50 %, Zufalls-Seed 35): 104 / −2 / 896 gegen 280. **Lehrbeispiel** (J₃): 6 / 0 / 8 gegen 8. **Derangements** (J − I, n = 7): 1.854 / 6 / 384 gegen 182. **Blöcke** (n = 12): 64 / 0 / 22.528 gegen 242; der Schätzer liefert bei 12 von 1.000 Vorzeichenmatrizen einen Wert über 0 und im Mittel 49,2 statt 64. **Gitter 4 × 4**: 36 / 0 / 896 gegen 278. **Dichte Matrix** (n = 10, 80 %): 330.936 / 0 / 4.608 gegen 560. **Dünne Matrix** (n = 10, 20 %): keine perfekte Paarung, Permanente 0 (`test_claim_presets_are_single_instances_with_these_values`). |
| **Größte Matrix** | n = 20, alle Einsen: **20! = 2.432.902.008.176.640.000** Paarungen, passt in int64 (20! < 2⁶³); Determinante 0 (`test_claim_the_largest_matrix_has_twenty_factorial_pairings`). |
| **Handwerte** | J₃: 6 Produkte der Größe 1, drei mit + und drei mit −, also per 6 und det 0; J − I: Derangements 2, 9, 44, 1.854 (n = 3, 4, 5, 7) mit Determinante 2, −3, 4, 6; 2 × 2-Gitter: Matrix ((1, 1), (1, 1)), mit Kasteleyn-Vorzeichen ((1, 1), (−1, 1)), Determinante 2 (`test_claim_hand_values_of_the_small_cases`). |

### Hypothesen des Plans

| | Hypothese | Ergebnis |
|---|---|---|
| H1 | Ryser = Glynn = Brute Force | **Ja**, auf allen 512 3 × 3-Matrizen und 830 Zufallsmatrizen (n = 4 bis 8) gleich, dazu die DP und eine rekursive Fassung (Orakel-Test) |
| H2 | Die Determinante ist billig, Ryser und Glynn sind exponentiell | **Ja**, gezählt: bei n = 20 4.940 gegen 9.961.472 (Glynn); Glynn ist erst ab n = 5 teurer als die Determinante |
| H3 | `det ≡ per (mod 2)` und `|det| ≤ per` | **Ja**, in allen 3.000 Matrizen und an **allen 65.536** 4 × 4-Matrizen (Orakel-Test); beides Sätze |
| H4 | Die Determinante unterschätzt die Permanente mit wachsendem n stärker | **Ja**: 0,453 → 0,0002 (n = 4 → 12, Dichte 50 %); „det = 0 trotz Paarung“ bis 71,9 % |
| H5 | Kein Vorzeichenmuster macht aus J₃ oder J₄ eine Determinante | **Ja**, alle 512 bzw. 65.536 aufgezählt (der allgemeine Satz von Pólya und Szegő wird nicht nachgeschlagen und nicht bewiesen) |
| H6 | Auf Gitter-Biadjazenzmatrizen gibt es ein Vorzeichenmuster mit |det| = per | **Ja**, in 10 von 10 Gittern bis n = 20; die Zahlen decken sich mit denen von `kasteleyn-demo` |
| H7 | Der Godsil–Gutman-Schätzer ist erwartungstreu | **Ja**, exakt aufgezählt für sechs Matrizen bis 4 × 4 (Orakel-Test) |
| H8 | Seine Streuung ist auf Zufallsmatrizen klein, im schlimmsten Fall exponentiell | **Ja**: 5,5 bis 10,5 % gegen 2ᵏ − 1 bei Blöcken (exakt) |
| H9 | Zufall löst das Zählproblem effizient | **Nein, nicht in dieser Gestalt**: der einfache Schätzer braucht bei Blöcken exponentiell viele Stichproben; das polynomielle Näherungsverfahren von Jerrum, Sinclair und Vigoda (2004) ist ein anderes Verfahren und wird nur genannt |

## Ehrliche Grenzen

- **#P-Vollständigkeit ist Literatur, nicht Messung.** Die Demo misst die Kosten der hier gebauten Verfahren bis n = 20 und die Wirkung der Vorzeichen; ob es ein wesentlich schnelleres exaktes Verfahren gibt, ist offen; ein polynomielles würde P = NP (sogar FP = #P) nach sich ziehen, nach einem Satz der Literatur, den die Demo nicht nachprüft.
- **Ryser und Glynn sind keine Rekordhalter der Praxis**, sondern die lehrbaren exakten Verfahren; Verbesserungen im Detail (schnellere Gray-Code-Schritte, Zerlegung nach Struktur) kennt die Demo nicht.
- **Multiplikationen sind ein Maß, kein Zeitmaß.** Additionen, Vergleiche und Speicherzugriffe fehlen; Bareiss braucht zusätzlich ganzzahlige Divisionen. Die Aussage trägt das Verhältnis (2.016 : 1), nicht die Einzelzahl.
- **Zufallsmatrizen stehen nicht für alle Matrizen.** Die Auslöschung der Determinante hängt von der Struktur ab: Gitter, Blöcke und Zufallsmatrizen verhalten sich verschieden (Gitter-Determinante 0 oder 1, Zufallsmatrizen mit Dichte 70 % fast immer 0).
- **Der Schätzer ist die einfache Fassung** und nur bis n = 12 im Regler (bis 14 in der Rechnung) gebaut; er ist hier Illustration. Seine Streuung wächst bei strukturierten Matrizen exponentiell; Matrizen ohne Paarung liefern immer 0.
- **Pólyas Frage ist nur an J₃, J₄ und zwei kleinen Gittern aufgezählt** (höchstens 16 Einsen). Dass es für n ≥ 3 allgemein keine Vorzeichenregel gibt, folgt aus der Literatur, nicht aus der Demo.
- **Die Kasteleyn-Regel für Gitter wurde an 10 Gittern geprüft**, nicht bewiesen und nicht auf beliebige planare Graphen ausgedehnt (das ist das Verfahren von `kasteleyn-demo`).
- **Gewichte:** die Permanente zählt hier Paarungen einer 0/1-Matrix; für gewichtete Matrizen gelten dieselben Formeln, die Demo zeigt sie nicht.

## Befunde und Korrekturen gegenüber dem Plan

- **Kosten mit n − 1 Multiplikationen je Produkt gezählt** (Plan: n je Produkt): Glynn bei n = 20 kostet 9.961.472 (Plan: 10.485.760), Ryser 19.922.925 (Plan: 20.971.500); die Gestalt ist dieselbe.
- **Vormessung und Bau liegen auf anderen Matrizen:** das mittlere |det| / per bei n = 4 ist 0,453 (Vormessung 0,44), bei n = 10 0,0021 (Vormessung 0,003); der Schätzer streut bei Zufallsmatrizen mit 5,5 bis 10,5 % (Vormessung 5 bis 13 % für n = 6 bis 14, das Regler-Maximum ist hier 12).
- **Auslöschungen genauer als geplant:** Der Plan nannte „det = 0 trotz Paarung bei 24 bis 39 %“ für Dichte 50 %; die Messreihe über drei Dichten zeigt bis 71,9 % (n = 6, Dichte 70 %).
- **Gitter ohne Kasteleyn-Vorzeichen:** der Plan vermutete „0 oder −1“, die Determinante der Gitter-Matrix ist 0 oder 1 (Betrag); sie zählt nicht.
- **Permanente in den Messreihen per Bitmasken-DP:** gleiche Zahl wie Glynn (Orakel-Test), aber schnell genug für 3.000 Matrizen; die Anzeige rechnet mit Glynn.
- **Brute Force bis n = 8** als Gegenprobe (Plan: Anzeige bis n ≤ 9).
- **Preset „Dünne Matrix“ zeigt eine Matrix ohne Paarung:** gewollt, weil es den Unterschied Entscheiden gegen Zählen zeigt (Existenz sofort „nein“).
- **Schätzer im Regler bis n = 12**, in der Rechnung bis 14 (Plan: n ≤ 12).

## Verifikation

- **Kern:** jede Einheit gegen Handrechnung an Mini-Matrizen (`tests/conftest.py`, `tests/test_algorithm.py`): J₂, T₂, J₃, obere Dreiecksmatrix, Kreise C₃ und C₄ (per 2, det 2 und 0), Derangements, Blöcke, Kostenformeln (n = 3: 12, 14, 8, 10), Bareiss mit Zeilentausch und vorzeitigem Ende, Existenz mit augmentierendem Weg, Vorzeichenmuster in fester Reihenfolge, Gitter 2 × 2 und 2 × 3 von Hand, Kasteleyn-Vorzeichen, Bits des Vorzeichenstroms, Blockvarianz.
- **Orakel** (`tests/test_oracle_permanente.py`): alle vier Verfahren und eine **fünfte, rekursive Fassung** stimmen auf allen 512 3 × 3-Matrizen und 830 Zufallsmatrizen (n = 4 bis 8, Dichten 10 bis 90 %) überein, Glynn, DP und Rekursion bis n = 12; die Sätze `|det| ≤ per`, `det ≡ per (mod 2)` und „Existenz ⇔ per > 0“ an **allen 65.536** 4 × 4-Matrizen; Derangements gegen die Rekursion D_n = (n − 1)(D_{n−1} + D_{n−2}) bis n = 12; **Gitter** gegen ein unabhängiges Zählverfahren (Randprofil) für alle 19 Formen, Kasteleyn-Vorzeichen bis n = 20; alle Vorzeichenmuster von J₃ und J₄ mit einer zweiten Determinante (Bareiss statt numpy); der Schätzer **exakt unverfälscht** durch Aufzählung für sechs Matrizen und die Blockvarianz 2ᵏ − 1 durch Aufzählung für k = 1 bis 4; die Auswertung über ein Raster aus Art, Größe und Dichte ohne Prüffehler.
- **Kopie** (`tests/test_copies.py`): wortgleich mit dem Original, solange es im Portfolio-Ordner liegt, dazu die bekannten ersten Werte der SplitMix64-Konvention.
- **Prüfung vor der Anzeige:** `validation_errors` prüft die Matrix (quadratisch, 0/1), die Permanente gegen die DP und (bis n = 8) die Definition, ihre Schranke (höchstens das Produkt der Zeilen- bzw. Spaltensummen), |det| ≤ per, die Parität, die Existenz, die Determinante gegen numpy, die Kosten gegen die Formeln und den Schätzer (nie negativ, bei Permanente 0 genau 0, bei höchstens 16 Einsen aufgezählt); jede Meldung wird einzeln ausgelöst, auch an den Grenzen (`tests/test_evaluation.py`).
- **Messreihen** gegen unabhängige Nachrechnungen (Definition, Gauß mit Brüchen, Vorzeichenaufzählung, exakte Determinanten je Vorzeichenmatrix); **Verdikte** als reine Funktionen, jede Zahl im Text und jede Schwelle an handgesetzten Werten (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Presets:** vollständig, gültige Werte, Hilfetexte erst nach der Messung geschrieben, erstes Preset gleich Standard, jedes Preset ohne Prüffehler (`tests/test_presets.py`); Randfälle (`tests/test_edge_cases.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen, auch n = 20), beide Messreihen-Knöpfe einzeln (`tests/test_app_sweeps.py`), Permalink mit Begrenzung, Layout, Footer, Abbildungen und PDF (`tests/test_visualization.py`).
- **Browser:** Standardansicht, beide Messreihen per Klick, Preset-Wechsel; keine Konsolenmeldung nach dem Erstrendern.

## Mutationsprüfung und großer Lauf

- **Großer Lauf im Scratch-Ordner (nicht im Repo):** 184.141 Prüfungen, **0 Abweichungen**: auf **allen 65.536** 4 × 4-Matrizen die fünf Permanenten-Verfahren (Brute Force, Ryser, Glynn, DP, Rekursion) gleich, Bareiss gegen den Gauß mit Brüchen, `|det| ≤ per`, gleiche Parität und „Existenz ⇔ per > 0“; auf 25.680 Zufallsmatrizen (n = 5 bis 8, alle Dichten 10 bis 90 %) dasselbe; Glynn gegen DP und die Sätze auf 341 Matrizen mit n = 9 bis 16; alle 41 Gitter mit höchstens 40 Zellen (Zeilen und Spalten bis 8) gegen das unabhängige Randprofil-Zählverfahren und mit Kasteleyn-Vorzeichen; der Erwartungswert des Schätzers **exakt** aufgezählt für alle 512 3 × 3-Matrizen und 300 zufällige 4 × 4-Matrizen; die Auswertung samt Prüfung vor der Anzeige für jede Art und jedes n von 2 bis 20.
- **Mutationsprüfung** (`tools/mutate_demo.py`, über `prn_algorithm.py` und `prn_evaluation.py`; Darstellung, PDF, Presets, Szenario und Oberfläche mutiert das Werkzeug nicht, sie sind durch Rauch-, Verdikt-, Claims- und Orakel-Tests abgesichert; die wörtliche Kopie `prn_rng.py` ist ausgenommen, ihre Tests liegen in Stück 3): **328 Stellen**, davon **292 gefangen**, **6 als äquivalent festgehalten** (`tests/mutation_state.json`) und 30 durch wortgleiche Zeilen in Nachbar-Demos gesichert (die Zahlenformate). Der erste Lauf ließ 14 Stellen überleben; geschlossen wurden die Lücken mit Grenztests: die Zahl der Wörter des Vorzeichenstroms, wenn die Bitzahl um 1 über einem Vielfachen von 64 liegt (n = 1, 65, 129 Vorzeichen), der Standardfehler ab genau zwei Stichproben, die Kennzeichen „|det| ≤ per“ und „Parität“ der Messreihe (mit künstlich verletzten Determinanten, auch wenn nur die erste Matrix verletzt) und die relative Toleranz des numpy-Vergleichs bei großer Determinante (5120 mit Abweichung 5 · 10⁻⁴ gegen 5 · 10⁻²). Aus dem Befund folgte eine Vereinfachung: das Feld „Parität gleich“ der Analyse war überflüssig (der Satz gilt immer, die Prüfung vor der Anzeige rechnet ihn selbst nach) und wurde entfernt. Äquivalent sind: die Suche nach dem Tauschpartner in der Determinante ab der Pivotzeile statt der Zeile darunter (die Pivotzeile hat dort den Wert 0 und kann nicht gewählt werden), die Rundungsgrenze `>` gegen `>=` der Schätzer-Determinante (Gleichheit auf der Grenze tritt nicht auf), der Index des Gray-Code-Schritts bei Glynn um ±1 verschoben (die feste Spalte δ = +1 darf eine beliebige sein, die Summe bleibt dieselbe) und `per − det` gegen `per + det` in der Paritätsprüfung (beide haben dieselbe Parität; zwei Stellen).

## Einordnung und Quellen (anhand der Quellen geprüft)

**Bibliografisch geprüft** (Verlags- bzw. Bibliothekseinträge, Inhalte nicht im Original gelesen): Valiant, *The complexity of computing the permanent*, Theoretical Computer Science 8 (2), 1979, S. 189 bis 201 (Permanente auch für 0/1-Matrizen #P-vollständig); Jerrum, Sinclair und Vigoda, *A polynomial-time approximation algorithm for the permanent of a matrix with nonnegative entries*, Journal of the ACM 51 (4), 2004, S. 671 bis 697; Glynn, *The permanent of a square matrix*, European Journal of Combinatorics 31 (7), 2010, S. 1887 bis 1891 (Formel mit Vorzeichenvektoren, gleiche Größenordnung 2ⁿ·n wie Ryser). **Nicht nachgeschlagen:** Ryser 1963 (Formel), Godsil und Gutman 1981 (Schätzer; die Erwartungstreue prüft die Demo selbst durch Aufzählung), Pólya 1913 und Szegő 1913 (Vorzeichenproblem), Bareiss 1968, Kuhn bzw. Hopcroft und Karp (augmentierende Wege), Fisher, Kasteleyn und Temperley (nur über `kasteleyn-demo`). Aussagen wie „ein polynomielles exaktes Verfahren gäbe es nur bei P = NP“ sind Lehrbuchwissen, nicht nachgeschlagen.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Matrix mit Permanente, Determinante, Existenz und Kosten, Schätzer, vier Experimente, Einordnung, Annahmentabelle, Formeln |
| `prn_algorithm.py` | Kern: Permanente (vier Wege), Determinante, Existenz, Vorzeichenmuster, Gitter, Schätzer |
| `prn_constants.py` | Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben, Presets mit Hilfetexten |
| `prn_evaluation.py` | Analyse, Messreihen, Prüfung vor der Anzeige, Verdikte, Zahlenformate |
| `prn_layout.py` | Fester Kopf (Stylesheet) |
| `prn_pdf_export.py` | PDF-Bericht (fpdf2) |
| `prn_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `prn_rng.py` | wörtliche Kopie: SplitMix64 aus Stück 3 |
| `prn_scenario.py` | 0/1-Matrizen der fünf Arten |
| `prn_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Matrizen, Orakel, Kopie, Auswertung, Verdikte, Claims, Presets, Randfälle, Layout, AppTest-Smoke-Test und Messreihen-Knöpfe, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Das FKT-Verfahren (Pfaffsche Orientierung planarer Graphen):** steht im `kasteleyn-demo`; hier nur die Gitter-Zahlen gegengeprüft.
- **Das polynomielle Näherungsverfahren (Jerrum, Sinclair, Vigoda):** nur genannt; es braucht Markov-Ketten und ist ein eigenes Stück.
- **Zählprobleme außerhalb der Permanente:** #SAT, lineare Erweiterungen (`zulaessige-reihenfolgen-demo` zählt sie exakt), Zuverlässigkeit von Netzen (`random-spanning-tree-demo` nennt die #P-Schwere).
- **Gewichtete Permanenten und komplexe Matrizen:** die Formeln gelten, die Demo zeigt 0/1-Matrizen.
- **Größere Matrizen:** n > 20 wäre mit Ryser und Glynn nicht mehr im Browser rechenbar, die Permanente nicht mehr in int64.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
