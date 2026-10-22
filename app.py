"""Zählen: Permanente gegen Determinante - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Neuntes (optionales) Stück der Komplexitätsklassen-Reihe: Entscheiden ist leicht, Zählen vermutlich schwer, und die Determinante ist die Permanente mit Vorzeichen. Aufwand in Multiplikationen, nie in Sekunden.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import prn_constants as C
from prn_evaluation import (
    Settings,
    analyse,
    cost_rows,
    fmt_big,
    fmt_fraction,
    fmt_int,
    fmt_ratio,
    kasteleyn_rows,
    polya_rows,
    sweep_det,
    sweep_estimator,
    validation_errors,
    verdict_costs,
    verdict_det_sweep,
    verdict_estimator,
    verdict_kasteleyn,
    verdict_main,
    verdict_polya,
)
from prn_layout import dunkles_design, kopf_css
from prn_pdf_export import build_pdf
from prn_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from prn_visualization import build_costs, build_det_ratio, build_estimator, build_matrix, build_polya

st.set_page_config(page_title="Zählen: Permanente gegen Determinante – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _costs():
    return cost_rows()


@st.cache_data(show_spinner=False)
def _det_sweep():
    return sweep_det()


@st.cache_data(show_spinner=False)
def _polya():
    return polya_rows()


@st.cache_data(show_spinner=False)
def _kasteleyn():
    return kasteleyn_rows()


@st.cache_data(show_spinner=False)
def _estimator():
    return sweep_estimator()


@st.cache_data(show_spinner=False)
def _pdf(settings):
    return build_pdf(analyse(settings))


def _md_table(header, rows):
    lines = ["| " + " | ".join(str(c) for c in header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in prn_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔢 Zählen: Permanente gegen Determinante")

st.markdown(
    """
„Gibt es eine perfekte Paarung?“ ist leicht zu beantworten, „**Wie viele** gibt es?“ vermutlich nicht. Die Zahl der perfekten Paarungen eines bipartiten Graphen (Aufgaben gegen Ressourcen, 1 = erlaubt) ist die **Permanente** der
0/1-Matrix: dieselbe Summe über alle Zuordnungen wie bei der **Determinante**, nur ohne die Vorzeichen. Die Vorzeichen löschen sich aus und machen die Determinante in n³ Schritten berechenbar, aber als Zählung **falsch**.
Die Demo stellt die gezählten Kosten gegenüber (Brute Force, Ryser, Glynn gegen Gauß), misst, was der Determinante fehlt, fragt, ob sich die Vorzeichen reparieren lassen, und probiert einen **Zufallsschätzer**.
Aufwand wird in **Multiplikationen** gezählt, nicht in Sekunden. Neuntes (optionales) Stück der Komplexitätsklassen-Reihe; die Fall-Demos behandeln einzelne Anwendungen, hier steht eine Frage der Komplexitätstheorie im Mittelpunkt.

Weiter unten: die Experimente **🔬 Wie teuer ist Zählen?**, **🔬 Was fehlt der Determinante?**, **🔬 Lassen sich die Vorzeichen reparieren?** und **🔬 Zählen durch Würfeln?**, dann **🚧 Wo die Annahmen enden** und der Expander
**📐 Mathematische Formulierung**.
"""
)

with st.expander("Zählen statt Entscheiden", expanded=True):
    st.markdown(
        """
1. **Entscheiden.** „Gibt es eine perfekte Paarung?“ beantworten augmentierende Wege in wenigen Schritten (Klasse **P**); die Demo benutzt dieses Verfahren für die Anzeige „Paarung vorhanden“.
2. **Zählen.** Die Zahl der perfekten Paarungen ist die **Permanente**. Nach Valiant (1979) ist ihre Berechnung **#P-vollständig**: so schwer wie das Zählen der Lösungen jedes NP-Problems (Literatur, nicht gemessen).
   Ein polynomielles Verfahren gäbe es nur, wenn P = NP gälte. Die besten hier gebauten exakten Verfahren (**Ryser**, **Glynn**) brauchen etwa 2^n · n Multiplikationen.
3. **Determinante.** Dieselbe Summe mit dem Vorzeichen der Permutation. Sie ist in n³ Schritten berechenbar (**Bareiss**, ganzzahlig) und stimmt mit der Permanente höchstens im Betrag überein, wenn sich die Vorzeichen zufällig oder
   durch die Struktur der Matrix ausgleichen.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    n = st.slider("Größe n der Matrix", *bounds("n_slider"), key="n_slider", help=f"n × n; Glynn rechnet 2^(n − 1) Vorzeichenvektoren (bei n = {C.N_MAX} rund 10 Millionen Multiplikationen). Brute Force nur bis n = {C.BRUTE_N_MAX} als Gegenprobe.")
    kind = st.selectbox("Matrixart", list(C.KINDS), format_func=C.KINDS.get, key="kind_select", help="Beim Gitter wählt n die Form (zum Beispiel n = 8: 4 × 4, n = 18: 6 × 6); „zufällig“ benutzt Dichte und Zufalls-Seed.")
    dens = st.select_slider("Dichte der Einsen in %", options=list(C.DENS_OPTIONS), key="dens_select", help="Nur für die Art „zufällig“.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt auf die zufällige Matrix und auf die Vorzeichenmatrizen des Schätzers.")
    st.button("🎲 Neue Matrix generieren", width="stretch", on_click=randomize_seed)
    samples = st.select_slider("Vorzeichenmatrizen des Schätzers", options=list(C.SAMPLES_OPTIONS), format_func=fmt_int, key="samples_select",
                               help=f"Nur Illustration (bis n = {C.EST_N_MAX}): wie viele zufällige Vorzeichenmatrizen der Schätzer mittelt.")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "kind_select": kind, "dens_select": int(dens), "samples_select": int(samples)})

settings = Settings(n=int(n), seed=int(seed), kind=kind, dens=int(dens), samples=int(samples))
with st.spinner("Rechne die Permanente …"):
    a = _analysis(settings)
for message in validation_errors(a):
    st.error(message)

# --- Hauptansicht --------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Wie viele perfekte Paarungen hat die Matrix?")
st.markdown(f"Matrix {len(a.matrix)} × {len(a.matrix)}, Art: {C.KINDS[settings.kind]}, {fmt_int(a.ones)} Einsen. Zeile = Aufgabe, Spalte = Ressource, dunkel = erlaubt.")
g1, g2 = st.columns([2, 3])
with g1:
    st.plotly_chart(build_matrix(a.matrix), width="stretch", key="matrix_chart")
with g2:
    m1, m2, m3 = st.columns(3)
    m1.metric("Permanente = Paarungen", fmt_int(a.per), help="Zahl der perfekten Paarungen (Glynn, gegengerechnet mit der Bitmasken-DP).")
    m2.metric("Determinante", fmt_int(a.det), help="Dieselbe Summe mit Vorzeichen (Bareiss, ganzzahlig).")
    m3.metric("Paarung vorhanden?", "ja" if a.exists else "nein", help="Entscheidung mit augmentierenden Wegen, ohne zu zählen.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Glynn", fmt_big(a.per_mults), help="Multiplikationen: 2^(n − 1) Vorzeichenvektoren, je ein Produkt aus n Zeilensummen.")
    k2.metric("Ryser", fmt_big(a.ryser_mults), help="Multiplikationen: 2^n − 1 Spaltenteilmengen.")
    k3.metric("Brute Force", fmt_big(a.brute_mults), help="Multiplikationen: n! Permutationen. Als Gegenprobe nur bis n = 8 gerechnet.")
    k4.metric("Determinante", fmt_int(a.det_mults), help="Gezählte Multiplikationen von Bareiss (endet früher, wenn die Matrix singulär ist).")
    vkind, vtext = verdict_main(a)
    getattr(st, vkind)(vtext)

st.markdown("### Zählen durch Würfeln?")
if a.estimate is None:
    st.info(f"Der Schätzer (Godsil und Gutman) läuft bis n = {C.EST_N_MAX}; hier ist n = {settings.n}.")
else:
    e = a.estimate
    s1, s2, s3 = st.columns(3)
    s1.metric("Schätzer (Mittel)", fmt_fraction(e.mean, 2), help=f"Mittel von det(A ∘ S)² über {fmt_int(e.samples)} Matrizen S mit zufälligen Vorzeichen; Erwartungswert = Permanente.")
    s2.metric("Permanente", fmt_int(a.per))
    s3.metric("Stichproben mit Wert > 0", f"{fmt_int(e.nonzero)} von {fmt_int(e.samples)}", help="Bei Matrizen mit viel Struktur ist fast jeder Wert 0.")
    st.caption("Illustration: der Beleg ist die Aufzählung im Experiment 4. Der Schätzer ist erwartungstreu, aber nicht immer brauchbar.")

if st.button("📄 PDF erstellen"):
    st.session_state["pdf_for"] = settings
if st.session_state.get("pdf_for") == settings:
    st.download_button("⬇️ PDF herunterladen", data=_pdf(settings), file_name="zaehlen-permanente-determinante.pdf", mime="application/pdf")

st.markdown("## ❓ Kernfrage: Warum ist Zählen schwer, wenn die Determinante so billig ist?")
st.markdown(
    "Weil die Vorzeichen, die die Determinante billig machen, genau das Zählen zerstören: Positives und Negatives löschen sich aus, und niemand weiß im Voraus, wie viel. Die Experimente messen den Kostenabstand, "
    "die Auslöschung, die Frage, ob sich die Vorzeichen richten lassen, und was ein Zufallsschätzer leistet."
)

st.markdown("---")

# --- Experimente --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie teuer ist Zählen?")
st.caption("Multiplikationen über n, aus den Formeln der Verfahren (die Zählung in den Funktionen ist gegen sie getestet). Die Determinante ist zusätzlich an einer festen Zufallsmatrix je n gezählt.")
costs = _costs()
st.plotly_chart(build_costs(costs), width="stretch", key="costs_chart")
st.markdown(_md_table(
    ["n", "Brute Force n!", "Ryser", "Glynn", "Determinante (Formel)", "Determinante (gezählt)"],
    [[r["n"], fmt_big(r["brute"]), fmt_big(r["ryser"]), fmt_big(r["glynn"]), fmt_int(r["det"]), fmt_int(r["det_counted"])] for r in costs if r["n"] in (2, 4, 6, 8, 10, 12, 14, 16, 18, 20)],
))
vkind, vtext = verdict_costs(costs)
getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Was fehlt der Determinante?")
st.caption(f"Je Größe n = {', '.join(str(x) for x in C.DET_SIZES)} und Dichte {', '.join(str(x) for x in C.DET_DENS)} % je {C.DET_COUNT} feste Zufallsmatrizen; Permanente per Bitmasken-DP (dieselbe Zahl wie Glynn). Unter einer Sekunde.")
if st.button("▶️ Messreihe Determinante rechnen"):
    st.session_state["det_on"] = True
if st.session_state.get("det_on"):
    with st.spinner("Rechne Permanente und Determinante für 3.000 Matrizen …"):
        det_rows = _det_sweep()
    st.plotly_chart(build_det_ratio(det_rows), width="stretch", key="det_chart")
    st.markdown(_md_table(
        ["n", "Dichte", "Matrizen mit Paarung", "davon det = 0", "mittleres |det| / per", "Median |det| / per"],
        [[r["n"], f"{r['dens']} %", f"{r['with_pm']} von {r['count']}", r["det_zero"], fmt_ratio(r["mean"]), fmt_ratio(r["median"])] for r in det_rows if r["with_pm"]],
    ))
    vkind, vtext = verdict_det_sweep(det_rows)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Lassen sich die Vorzeichen reparieren?")
st.caption("Alle Vorzeichenmuster kleiner Matrizen: jede Eins wird +1 oder −1. Wie oft ist dann |det| gleich der Permanente? (Pólyas Frage: lässt sich die Permanente durch Vorzeichenwechsel in eine Determinante verwandeln?)")
polya = _polya()
st.plotly_chart(build_polya(polya), width="stretch", key="polya_chart")
st.markdown(_md_table(
    ["Matrix", "Einsen", "Muster", "Permanente", "Beträge |det| (Häufigkeit)", "Muster mit |det| = per"],
    [[r["name"], r["ones"], fmt_int(r["patterns"]), fmt_int(r["per"]), ", ".join(f"{k}: {fmt_int(v)}" for k, v in r["counts"].items()), fmt_int(r["hits"])] for r in polya],
))
vkind, vtext = verdict_polya(polya)
getattr(st, vkind)(vtext)
st.markdown("**Auf Gittern gibt es eine Regel.** Wer Dominosteine zählt, bekommt die Zahl der Pflasterungen als Betrag der Determinante, wenn die senkrechten Kanten in ungeraden Spalten das Vorzeichen −1 tragen "
            "(Kasteleyn; das planare Verfahren steht im `kasteleyn-demo`):")
kast = _kasteleyn()
st.markdown(_md_table(
    ["Gitter", "n", "Pflasterungen (Permanente)", "|det| mit Vorzeichen", "|det| ohne Vorzeichen"],
    [[f"{r['rows']} × {r['cols']}", r["n"], fmt_int(r["per"]), fmt_int(r["det_signed"]), fmt_int(r["det_plain"])] for r in kast],
))
vkind, vtext = verdict_kasteleyn(kast)
getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Zählen durch Würfeln?")
st.caption(f"Der Schätzer von Godsil und Gutman: X = det(A ∘ S)² mit zufälligen Vorzeichen S hat den Erwartungswert per(A). Gemessen wird die relative Streuung eines Schätzers aus {fmt_int(C.EST_N)} Vorzeichenmatrizen "
           f"(je {C.EST_MATRICES} Zufallsmatrizen mit {C.EST_REPS} Wiederholungen; dazu Blöcke aus 2 × 2). Rund 2 Sekunden.")
if st.button("▶️ Messreihe Schätzer rechnen"):
    st.session_state["est_on"] = True
if st.session_state.get("est_on"):
    with st.spinner("Würfle Vorzeichenmatrizen …"):
        est = _estimator()
    st.plotly_chart(build_estimator(est), width="stretch", key="estimator_chart")
    st.markdown(_md_table(
        ["Blöcke k", "n", "Permanente 2^k", "gemessene Streuung", "Rechnung √((2^k − 1) / N)", "Vorzeichenmatrizen für 10 %"],
        [[r["k"], r["n"], fmt_int(r["per"]), f"{100 * r['rel']:.1f} %".replace(".", ","), f"{100 * r['predicted']:.1f} %".replace(".", ","), fmt_int(r["needed"])] for r in est["blocks"]],
    ))
    st.markdown(_md_table(
        ["n", "Zufallsmatrizen mit Paarung", "mittlere Streuung", "größte Streuung"],
        [[r["n"], f"{r['matrices']} von {r['matrices'] + r['skipped']}", f"{100 * r['mean_rel']:.1f} %".replace(".", ","), f"{100 * r['max_rel']:.1f} %".replace(".", ",")] for r in est["random"]],
    ))
    vkind, vtext = verdict_estimator(est)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Einordnung: #P, Näherung und Zufall")
st.markdown(
    "Zählen ist eine eigene Schwierigkeit neben dem Entscheiden: **#P** fragt nach der *Zahl* der Lösungen. Die Permanente ist #P-vollständig (Valiant 1979, Literatur). Auf **planaren** Graphen geht das Zählen perfekter Paarungen "
    "trotzdem in Polynomialzeit (Kasteleyn, Experiment 3; Verfahren im `kasteleyn-demo`). Für Matrizen mit nichtnegativen Einträgen gibt es ein polynomielles **Näherungsverfahren** (Jerrum, Sinclair und Vigoda 2004; Literatur, "
    "hier nicht nachgebaut): ganz anders als der einfache Schätzer oben, dessen Streuung im schlimmsten Fall exponentiell wächst. Im Gegensatz zu Stück 8 (dort kostet der Zufall wenig, und der Fehler ist beschränkt) hilft er hier "
    "nur mit einem aufwendigeren Verfahren."
)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Zählen ist #P-vollständig** | Das ist ein Satz der Literatur (Valiant 1979), die Demo misst ihn nicht. Sie misst nur die Kosten der hier gebauten Verfahren bis n = 20. | – |
| **Ryser und Glynn sind die besten exakten Verfahren** | Die Demo kennt nur diese; ob es wesentlich schnellere exakte Verfahren gibt, ist offen (ein polynomielles gäbe es nur bei P = NP). | – |
| **Kosten = Multiplikationen** | Gezählt werden Multiplikationen einer Python-Umsetzung mit ganzen Zahlen; Additionen und der Zugriff auf Einträge fehlen. Das Verhältnis, nicht die Einzelzahl, trägt die Aussage. | – |
| **Matrizen sind klein und zufällig** | Alle Messreihen gelten für Zufallsmatrizen bis n = 12 (Dichte 30 bis 70 %) und die genannten Sonderfälle; die Auslöschung hängt von der Struktur ab (Gitter und Blöcke verhalten sich anders). | – |
| **Der Schätzer ist brauchbar** | Er ist erwartungstreu, aber seine Streuung wächst bei Blöcken exponentiell (Experiment 4); nur Matrizen bis n = 12 und die einfache Fassung sind gebaut. | – |
| **Vorzeichen lassen sich richten** | Nur auf planaren Gittern (Kasteleyn); bei J3 und J4 gelingt es mit keinem der Muster. Allgemeine Aussagen (Pólya, Szegő) werden hier nicht bewiesen. | – |
| **Eine Paarung zu finden heißt sie zu zählen** | Existenz ist leicht (augmentierende Wege); die Zahl der Paarungen wächst bis n! (bei n = 20 über 2 · 10^18). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(r"**Permanente und Determinante.** Für eine $n \times n$-Matrix $A$ mit Einträgen $a_{ij} \in \{0, 1\}$ ist die Zahl der perfekten Paarungen")
    st.latex(r"\operatorname{per}(A) = \sum_{\pi \in S_n} \prod_{i=1}^{n} a_{i,\pi(i)}, \qquad \det(A) = \sum_{\pi \in S_n} \operatorname{sgn}(\pi) \prod_{i=1}^{n} a_{i,\pi(i)}")
    st.markdown(r"Weil $\operatorname{sgn}(\pi) = \pm 1$, gilt $|\det A| \le \operatorname{per} A$ und $\det A \equiv \operatorname{per} A \pmod 2$ (Vorzeichen sind modulo 2 gleich 1).")
    st.markdown(r"**Ryser.** Summe über die Teilmengen $S$ der Spalten:")
    st.latex(r"\operatorname{per}(A) = (-1)^n \sum_{S \subseteq \{1, \dots, n\}} (-1)^{|S|} \prod_{i=1}^{n} \sum_{j \in S} a_{ij}")
    st.markdown(r"**Glynn.** Summe über $\delta \in \{\pm 1\}^n$ mit $\delta_n = 1$, im Gray-Code durchlaufen:")
    st.latex(r"\operatorname{per}(A) = \frac{1}{2^{n-1}} \sum_{\delta} \Big(\prod_{k} \delta_k\Big) \prod_{i=1}^{n} \sum_{j=1}^{n} \delta_j a_{ij}")
    st.markdown(r"**Godsil–Gutman.** Sei $S$ eine Matrix unabhängiger zufälliger Vorzeichen $\pm 1$ und $\circ$ das Eintragsprodukt. Dann ist $X = \det(A \circ S)^2$ erwartungstreu:")
    st.latex(r"\mathbb{E}[X] = \operatorname{per}(A)")
    st.markdown(r"Für die Blockdiagonale aus $k$ Blöcken $J_2$ ist $X$ das Produkt von $k$ unabhängigen Faktoren aus $\{0, 4\}$ (gleich wahrscheinlich, Mittel 2, zweites Moment 8); daher:")
    st.latex(r"\operatorname{per} = 2^k, \qquad \frac{\operatorname{Var}(X)}{\operatorname{per}^2} = 2^k - 1")
    st.markdown(
        r"""
| Annahme | Bedeutung | Wer setzt an |
|---|---|---|
| 0/1-Matrix | die Permanente zählt Paarungen; bei anderen Einträgen zählt sie gewichtete Paarungen | – |
| Quadratisch | perfekte Paarung braucht gleich viele Zeilen und Spalten | – |
| Ganze Zahlen | alle Anzahlen und Determinanten sind exakt (Bareiss ohne Brüche, Glynn und Ryser in ganzen Zahlen) | – |
| Zufällige Vorzeichen | unabhängig und gleichverteilt (hier ein Generator mit festem Zufalls-Seed) | – |
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
