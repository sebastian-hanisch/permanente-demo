"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import prn_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_matrix(matrix):
    """Die 0/1-Matrix als Raster: dunkel = 1 (erlaubt), hell = 0; Zeile = Aufgabe, Spalte = Ressource."""
    z = np.array(matrix, dtype=int)
    fig = go.Figure(go.Heatmap(z=z, colorscale=[[0, "rgba(150,150,150,0.2)"], [1, C.COLOR_DET]], showscale=False, xgap=1, ygap=1, hovertemplate="Zeile %{y}, Spalte %{x}: %{z}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", title="Zeile (Aufgabe)")
    fig.update_xaxes(title="Spalte (Ressource)")
    return _base(fig, 320)


def build_costs(rows):
    """Multiplikationen über n (logarithmisch): Brute Force, Ryser, Glynn, Determinante."""
    ns = [r["n"] for r in rows]
    fig = go.Figure()
    for key, name, color in (("brute", "Brute Force n!", C.COLOR_BRUTE), ("ryser", "Ryser 2^n", C.COLOR_RYSER), ("glynn", "Glynn 2^(n−1)", C.COLOR_GLYNN), ("det", "Determinante (Bareiss)", C.COLOR_DET)):
        fig.add_trace(go.Scatter(x=ns, y=[r[key] for r in rows], mode="lines+markers", name=name, line=dict(color=color)))
    fig.update_xaxes(title="Größe n", dtick=2)
    fig.update_yaxes(type="log", title="Multiplikationen")
    return _base(fig, 380)


def build_det_ratio(rows):
    """Mittleres |det| / per über n, eine Linie je Dichte (logarithmisch)."""
    fig = go.Figure()
    for color, dens in zip(C.COLOR_SERIES, sorted({r["dens"] for r in rows})):
        sel = [r for r in rows if r["dens"] == dens and r["mean"] is not None]
        fig.add_trace(go.Scatter(x=[r["n"] for r in sel], y=[float(r["mean"]) for r in sel], mode="lines+markers", name=f"Dichte {dens} %", line=dict(color=color)))
    fig.add_hline(y=1, line=dict(color=C.COLOR_BRUTE, dash="dash"), annotation_text="|det| = per", annotation_position="top right")
    fig.update_xaxes(title="Größe n", dtick=2)
    fig.update_yaxes(type="log", title="mittleres |det| / per")
    return _base(fig, 360)


def build_polya(rows):
    """Anteil der Vorzeichenmuster, die |det| gleich der Permanente machen, je Matrix."""
    fig = go.Figure(go.Bar(x=[r["name"] for r in rows], y=[100 * r["hits"] / r["patterns"] for r in rows], marker_color=C.COLOR_DET,
                           text=[f"{r['hits']} von {r['patterns']}" for r in rows], textposition="outside"))
    fig.update_yaxes(title="Muster mit |det| = per in %", range=[0, 110])
    fig.update_xaxes(type="category")
    return _base(fig, 340)


def build_estimator(res):
    """Relative Streuung des Schätzers über n (logarithmisch): Zufallsmatrizen (gemessen), Blöcke aus J2 (gemessen und nach der Rechnung)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["random"]], y=[r["mean_rel"] for r in res["random"]], mode="lines+markers", name="Zufallsmatrizen (gemessen)", line=dict(color=C.COLOR_DET)))
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["blocks"]], y=[r["rel"] for r in res["blocks"]], mode="lines+markers", name="Blöcke J2 (gemessen)", line=dict(color=C.COLOR_BRUTE)))
    fig.add_trace(go.Scatter(x=[r["n"] for r in res["blocks"]], y=[r["predicted"] for r in res["blocks"]], mode="lines+markers", name="Blöcke J2: √((2^k − 1) / N)", line=dict(color=C.COLOR_BRUTE, dash="dash")))
    fig.update_xaxes(title="Größe n", dtick=2)
    fig.update_yaxes(type="log", title="relative Streuung des Schätzers")
    return _base(fig, 360)
