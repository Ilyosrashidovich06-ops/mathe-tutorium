import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from scipy import stats
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import date

st.set_page_config(
    page_title="Tutorium – Wirtschaftsmathematik",
    page_icon="📈",
    layout="wide",
)

# ── Dark-mode-safe global CSS ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .card-blue  { background:#1a3a5c !important; border-left:5px solid #42a5f5;
                  padding:16px; border-radius:8px; height:100%; }
    .card-green { background:#1a3d2b !important; border-left:5px solid #66bb6a;
                  padding:16px; border-radius:8px; height:100%; }
    .card-red    { background:#3d1a1a !important; border-left:5px solid #ef5350;
                  padding:16px; border-radius:8px; height:100%; }
    .card-orange { background:#3d2200 !important; border-left:5px solid #ffa726;
                  padding:16px; border-radius:8px; height:100%; }
    .card-blue   h4 { color:#90caf9;  margin-top:0; }
    .card-green  h4 { color:#a5d6a7;  margin-top:0; }
    .card-red    h4 { color:#ef9a9a;  margin-top:0; }
    .card-orange h4 { color:#ffcc80;  margin-top:0; }
    .card-blue  p, .card-green p, .card-red p,
    .card-orange p  { color:#e0e0e0; font-size:13px; }
    .card-blue  .anw, .card-green .anw, .card-red .anw,
    .card-orange .anw { color:#bdbdbd; font-size:12px; }
    .formula {
        font-family: monospace;
        background: rgba(255,255,255,0.08);
        color: #f0f0f0;
        padding: 8px 10px;
        border-radius: 5px;
        font-size: 14px;
        margin: 6px 0 10px;
        display: block;
    }
    .fra-logo-box {
        background: linear-gradient(135deg,#003366,#0055a5);
        color: white;
        border-radius: 8px;
        padding: 14px 10px;
        text-align: center;
        margin-bottom: 12px;
    }
    .fra-logo-box .abbr  { font-size:32px; font-weight:800; letter-spacing:3px; }
    .fra-logo-box .full  { font-size:10px; opacity:0.75; letter-spacing:0.5px; margin-top:4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:linear-gradient(90deg,#003366 0%,#0055a5 100%);
                padding:28px 36px;border-radius:10px;margin-bottom:8px;">
        <p style="color:#cce0ff;font-size:13px;margin:0;letter-spacing:1.5px;">
            FRANKFURT UNIVERSITY OF APPLIED SCIENCES
        </p>
        <h1 style="color:#ffffff;font-size:26px;margin:6px 0 4px;">
            Tutorium: Wirtschaftsmathematik
        </h1>
        <p style="color:#cce0ff;font-size:15px;margin:0;">
            International Business Administration &nbsp;·&nbsp; Ilyos Umurzakov
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Woche 1 – Zinsmodelle")
st.markdown(
    "Vergleich der drei klassischen Verzinsungsmodelle. "
    "Passen Sie die Parameter links an, um die Graphen live zu aktualisieren."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # University logo block (works without an image file)
    st.markdown(
        """
        <div class="fra-logo-box">
            <div class="abbr">FRA·UAS</div>
            <div class="full">FRANKFURT UNIVERSITY OF APPLIED SCIENCES</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Parameter")
    K0 = st.number_input("Anfangskapital K₀ (€)", min_value=100, max_value=100_000,
                          value=750, step=50)
    p  = st.slider("Zinssatz p (% p.a.)", min_value=0.5, max_value=15.0,
                   value=2.5, step=0.25)
    T  = st.slider("Zeitraum t (Jahre)", min_value=1, max_value=50, value=10)
    st.markdown("---")
    st.caption("Tutorium · Wirtschaftsmathematik · Fra UAS")

with st.sidebar:
    st.markdown("---")
    st.markdown("### Woche 2 – Renditen")
    K0_r = st.number_input("Anfangswert K(0) (€)", 1.0, 1_000_000.0,
                            6_000.0, step=100.0, key="rend_K0")
    KT_r = st.number_input("Endwert K(T) (€)",     1.0, 1_000_000.0,
                            8_000.0, step=100.0, key="rend_KT")
    T_r  = st.number_input("Haltedauer T (Jahre)",  0.25, 50.0,
                            3.0,   step=0.25,  key="rend_T")
    st.markdown("---")
    st.markdown("#### Effektivzins (unterjährig)")
    p_nom_r = st.slider("Nominalzins p_nom (%)", 0.5, 15.0, 4.5,
                        step=0.25, key="rend_pnom")
    _m_labels = {1:"jährlich (m=1)", 2:"halbjährlich (m=2)",
                 4:"vierteljährlich (m=4)", 12:"monatlich (m=12)",
                 52:"wöchentlich (m=52)", 365:"täglich (m=365)"}
    m_r = st.selectbox("Verzinsungsperiode", list(_m_labels.keys()),
                       index=2, format_func=lambda x: _m_labels[x],
                       key="rend_m")
    K0_eff_r = st.number_input("Anfangskapital K(0) (€)", 100.0,
                                1_000_000.0, 12_000.0, step=500.0,
                                key="rend_K0eff")
    T_eff_r  = st.slider("Laufzeit (Jahre)", 1, 30, 3, key="rend_Teff")

# ── Compute ───────────────────────────────────────────────────────────────────
t = np.linspace(0, T, 500)

K_simple     = K0 * (1 + t * p / 100)
K_compound   = K0 * (1 + p / 100) ** t
K_continuous = K0 * np.exp(t * p / 100)

# ── Main comparison plot ──────────────────────────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=t, y=K_simple, mode="lines", name="Einfache Verzinsung",
    line=dict(color="#42a5f5", width=2.5, dash="dot"),
    hovertemplate="t = %{x:.1f} J<br>K = %{y:,.2f} €<extra>Einfach</extra>",
))
fig.add_trace(go.Scatter(
    x=t, y=K_compound, mode="lines", name="Jährliche Zinsverrechnung (Zinseszins)",
    line=dict(color="#66bb6a", width=2.5),
    hovertemplate="t = %{x:.1f} J<br>K = %{y:,.2f} €<extra>Zinseszins</extra>",
))
fig.add_trace(go.Scatter(
    x=t, y=K_continuous, mode="lines", name="Kontinuierliche Verzinsung",
    line=dict(color="#ef5350", width=2.5, dash="dash"),
    hovertemplate="t = %{x:.1f} J<br>K = %{y:,.2f} €<extra>Kontinuierlich</extra>",
))

fig.add_hline(y=K0, line_dash="longdash", line_color="#888",
              line_width=1, annotation_text=f"K₀ = {K0:,.0f} €",
              annotation_position="right")

fig.update_layout(
    title=dict(
        text=f"Kapitalwachstum: K₀ = {K0:,.0f} €, p = {p} %, t = 0 – {T} Jahre",
        font=dict(size=16),
    ),
    xaxis=dict(title="Zeit t (Jahre)", gridcolor="rgba(128,128,128,0.2)"),
    yaxis=dict(title="Kapital K(t) in €", tickformat=",.0f",
               gridcolor="rgba(128,128,128,0.2)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=480,
    margin=dict(t=80, b=60, l=60, r=40),
    font=dict(color="#e0e0e0"),
)

st.plotly_chart(fig, use_container_width=True)

# ── Final-value summary cards ─────────────────────────────────────────────────
K_s_final = K_simple[-1]
K_c_final = K_compound[-1]
K_e_final = K_continuous[-1]

col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"Einfache Verzinsung nach {T} J",
    value=f"{K_s_final:,.2f} €",
    delta=f"+ {K_s_final - K0:,.2f} € Zinsen",
)
col2.metric(
    label=f"Zinseszins nach {T} J",
    value=f"{K_c_final:,.2f} €",
    delta=f"+ {K_c_final - K0:,.2f} € Zinsen",
)
col3.metric(
    label=f"Kontinuierlich nach {T} J",
    value=f"{K_e_final:,.2f} €",
    delta=f"+ {K_e_final - K0:,.2f} € Zinsen",
)

st.markdown("---")

# ── Model explanation cards ───────────────────────────────────────────────────
st.markdown("### Die drei Zinsmodelle im Überblick")

exp1, exp2, exp3 = st.columns(3)

with exp1:
    st.markdown(
        """
        <div class="card-blue">
          <h4>🔵 Einfache Verzinsung</h4>
          <span class="formula">K(t) = K₀ · (1 + t · p%)</span>
          <p>Zinsen werden <b>nur auf das Anfangskapital</b> berechnet –
          die aufgelaufenen Zinsen tragen keine weiteren Zinsen.
          <b>Lineares</b> Wachstum.</p>
          <p class="anw"><b>Anwendung:</b> Kurzfristige Anlagen,
          Geldmarktpapiere, Kontokorrentkredite (lt. PAngV).</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with exp2:
    st.markdown(
        """
        <div class="card-green">
          <h4>🟢 Jährliche Zinsverrechnung</h4>
          <span class="formula">K(t) = K₀ · (1 + p%)ᵗ</span>
          <p>Zinsen werden jährlich dem Kapital zugeschlagen und
          <b>im Folgejahr mitverzinst</b> (Zinseszinseffekt).
          <b>Exponentielles</b> Wachstum (diskret).</p>
          <p class="anw"><b>Anwendung:</b> Sparkonten, Festgeld, Anleihen –
          gesetzlicher Standard gemäß PAngV.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with exp3:
    st.markdown(
        """
        <div class="card-red">
          <h4>🔴 Kontinuierliche Verzinsung</h4>
          <span class="formula">K(t) = K₀ · e^(t · p%)</span>
          <p>Zinsen werden <b>unendlich oft</b> innerhalb des Jahres
          gutgeschrieben (Grenzwert der unterjährigen Verzinsung).
          <b>Stärkste</b> Wachstumsform.</p>
          <p class="anw"><b>Anwendung:</b> Optionspreistheorie (Black-Scholes),
          quantitative Finance, Finanzmathematik.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Formula comparison table ──────────────────────────────────────────────────
with st.expander("Formelübersicht & Vergleichstabelle", expanded=False):
    years_show = sorted({1, 2, 5, 10, 20, T})
    rows = []
    for yr in years_show:
        ks = K0 * (1 + yr * p / 100)
        kc = K0 * (1 + p / 100) ** yr
        ke = K0 * np.exp(yr * p / 100)
        rows.append({
            "Jahr": yr,
            "Einfach (€)":        f"{ks:,.2f}",
            "Zinseszins (€)":     f"{kc:,.2f}",
            "Kontinuierlich (€)": f"{ke:,.2f}",
        })
    st.dataframe(pd.DataFrame(rows).set_index("Jahr"), use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Woche 2 – Renditenrechnung
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Woche 2 – Renditenrechnung")
st.markdown(
    "Von der einfachen Rendite über den Effektivzins bis zur stetigen Log-Rendite. "
    "Passen Sie **K(0)**, **K(T)** und **T** in der Seitenleiste an."
)

# ── Calculations from sidebar ─────────────────────────────────────────────────
r_gesamt = (KT_r - K0_r) / K0_r
r_jaerl  = r_gesamt / T_r
p_eff_r  = (KT_r / K0_r) ** (1 / T_r) - 1
r_log    = np.log(KT_r / K0_r)
r_log_j  = r_log / T_r

p_eff_uj = (1 + p_nom_r / 100 / m_r) ** m_r - 1
KT_eff   = K0_eff_r * (1 + p_nom_r / 100 / m_r) ** (m_r * T_eff_r)

# ── Formula cards ─────────────────────────────────────────────────────────────
st.markdown("### Die Renditekennzahlen im Überblick")
fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    st.markdown("""
    <div class="card-blue">
      <h4>🔵 Einfache Rendite</h4>
      <span class="formula">r = (K(T) − K(0)) / K(0)</span>
      <p>Gesamtgewinn/-verlust relativ zum eingesetzten Kapital.
      <b>Nicht</b> zeitadjustiert.</p>
      <span class="formula">r̄ = r / T</span>
      <p class="anw">Jahresrendite: lineare Aufteilung auf T Jahre –
      kein Zinseszins unterstellt.</p>
    </div>""", unsafe_allow_html=True)

with fc2:
    st.markdown("""
    <div class="card-green">
      <h4>🟢 Effektivzins (PAngV)</h4>
      <span class="formula">p_EFF = (K(T)/K(0))^(1/T) − 1</span>
      <p>Geometrisch gemittelte Jahresrendite. Berücksichtigt den
      Zinseszinseffekt. <b>Gesetzlicher Standard</b> für Vergleiche.</p>
      <p class="anw">Anwendung: Kreditvergleich, Sparpläne,
      Investitionsvergleich gemäß PAngV.</p>
    </div>""", unsafe_allow_html=True)

with fc3:
    st.markdown("""
    <div class="card-red">
      <h4>🔴 Log-Rendite (stetig)</h4>
      <span class="formula">r_log = ln(K(T) / K(0))</span>
      <p>Stetige Rendite – über die Zeit <b>additiv</b>. Für kleine
      Renditen ≈ einfacher Rendite.</p>
      <span class="formula">r̄_log = r_log / T</span>
      <p class="anw">Anwendung: Optionspreismodelle (Black-Scholes),
      VaR, Risikomodelle.</p>
    </div>""", unsafe_allow_html=True)

with fc4:
    st.markdown("""
    <div class="card-orange">
      <h4>🟠 Effektivzins (unterjährig)</h4>
      <span class="formula">p_EFF = (1 + p_nom/m)^m − 1</span>
      <p>Nominalzins p_nom wird m-mal pro Jahr verrechnet.
      Mehr Perioden → höherer Effektivzins.</p>
      <span class="formula">K(T) = K(0)·(1+p_nom/m)^(m·T)</span>
      <p class="anw">Anwendung: Sparbücher, Ratenkredite,
      Hypotheken mit unterjähriger Zinsgutschrift.</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Interactive Rechner ───────────────────────────────────────────────────────
st.markdown("### Interaktiver Rendite-Rechner")
gain_loss = KT_r - K0_r
st.markdown(
    f"K(0) = **{K0_r:,.2f} €** &nbsp;→&nbsp; K(T) = **{KT_r:,.2f} €** "
    f"&nbsp;|&nbsp; T = **{T_r} Jahre** &nbsp;|&nbsp; "
    f"Gewinn/Verlust: **{gain_loss:+,.2f} €**"
)

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
dc = "normal" if gain_loss >= 0 else "inverse"
mc1.metric("Gesamtrendite r",    f"{r_gesamt*100:.2f}%",
           f"{gain_loss:+,.2f} €", delta_color=dc)
mc2.metric("Jahresrendite r̄",    f"{r_jaerl*100:.2f}%",
           "einfach / T",         delta_color="off")
mc3.metric("Effektivzins p_EFF", f"{p_eff_r*100:.4f}%",
           "geometr. Mittel",     delta_color="off")
mc4.metric("Log-Rendite r_log",  f"{r_log*100:.4f}%",
           "stetig gesamt",       delta_color="off")
mc5.metric("Log-Rendite p.a.",   f"{r_log_j*100:.4f}%",
           "stetig / T",          delta_color="off")

# Charts
ch1, ch2 = st.columns(2)

with ch1:
    fig_bar_r = go.Figure(go.Bar(
        x=["Jahresrendite r̄", "Effektivzins p_EFF", "Log-Rendite r̄_log"],
        y=[r_jaerl*100, p_eff_r*100, r_log_j*100],
        marker_color=["#42a5f5", "#66bb6a", "#ef5350"],
        text=[f"{v:.4f}%" for v in [r_jaerl*100, p_eff_r*100, r_log_j*100]],
        textposition="outside",
    ))
    fig_bar_r.update_layout(
        title="Jährliche Renditekennzahlen im Vergleich",
        yaxis=dict(title="Rendite (%)", gridcolor="rgba(128,128,128,0.2)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"), height=340,
        margin=dict(t=50, b=40, l=55, r=20), showlegend=False,
    )
    st.plotly_chart(fig_bar_r, use_container_width=True)

with ch2:
    t_line = np.linspace(0, T_r, 300)
    K_line = K0_r * (1 + p_eff_r) ** t_line
    fig_grow = go.Figure()
    fig_grow.add_trace(go.Scatter(
        x=t_line, y=K_line, mode="lines",
        line=dict(color="#66bb6a", width=2.5),
        hovertemplate="t=%{x:.2f} J<br>K=%{y:,.2f} €<extra></extra>",
    ))
    fig_grow.add_scatter(x=[0, T_r], y=[K0_r, KT_r], mode="markers",
                         marker=dict(color=["#42a5f5", "#ef5350"], size=10),
                         showlegend=False)
    fig_grow.add_annotation(x=0,   y=K0_r, text=f"K(0)={K0_r:,.0f}€",
                            showarrow=False, yshift=14, font=dict(color="#42a5f5"))
    fig_grow.add_annotation(x=T_r, y=KT_r, text=f"K(T)={KT_r:,.0f}€",
                            showarrow=False, yshift=14, font=dict(color="#ef5350"))
    fig_grow.update_layout(
        title="Wachstum zum Effektivzins p_EFF",
        xaxis=dict(title="Zeit (Jahre)", gridcolor="rgba(128,128,128,0.2)"),
        yaxis=dict(title="Kapital (€)", tickformat=",.0f",
                   gridcolor="rgba(128,128,128,0.2)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"), height=340,
        margin=dict(t=50, b=40, l=65, r=20), showlegend=False,
    )
    st.plotly_chart(fig_grow, use_container_width=True)

st.info(
    "**Reihenfolge bei positiver Rendite:** "
    "Jahresrendite r̄ ≥ Effektivzins p_EFF ≥ Log-Rendite r̄_log  \n"
    "Der Effektivzins ist der gesetzliche Standard für Vergleiche (PAngV)."
)

st.markdown("---")

# ── Effektivzins bei unterjähriger Verzinsung ─────────────────────────────────
st.markdown("### Effektivzins bei unterjähriger Verzinsung")

eff_c1, eff_c2 = st.columns([1.6, 1])

with eff_c1:
    m_arr    = np.array([1, 2, 3, 4, 6, 12, 26, 52, 365])
    peff_arr = (1 + p_nom_r / 100 / m_arr) ** m_arr - 1
    peff_cont = np.exp(p_nom_r / 100) - 1

    fig_eff = go.Figure()
    fig_eff.add_trace(go.Scatter(
        x=m_arr, y=peff_arr * 100, mode="lines+markers",
        line=dict(color="#ffa726", width=2.5), marker=dict(size=7),
        hovertemplate="m=%{x}<br>p_EFF=%{y:.4f}%<extra></extra>",
    ))
    fig_eff.add_hline(
        y=peff_cont * 100, line_dash="dash", line_color="#ef5350",
        annotation_text=f"Stetig (m→∞): {peff_cont*100:.4f}%",
        annotation_font_color="#ef5350", annotation_position="bottom right",
    )
    fig_eff.update_layout(
        title=f"p_EFF vs. m bei p_nom = {p_nom_r}% p.a.",
        xaxis=dict(title="Zinsperioden pro Jahr m", type="log",
                   tickvals=[1,2,4,12,52,365],
                   ticktext=["1","2","4","12","52","365"],
                   gridcolor="rgba(128,128,128,0.2)"),
        yaxis=dict(title="p_EFF (%)", gridcolor="rgba(128,128,128,0.2)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"), height=340,
        margin=dict(t=50, b=50, l=60, r=20), showlegend=False,
    )
    st.plotly_chart(fig_eff, use_container_width=True)

with eff_c2:
    st.markdown(f"#### Ihre Berechnung (p_nom = {p_nom_r}%)")
    st.metric("Effektivzins p_EFF", f"{p_eff_uj*100:.4f}%",
              _m_labels[m_r])
    st.metric(f"K(T) nach {T_eff_r} Jahren",
              f"{KT_eff:,.2f} €", f"K(0) = {K0_eff_r:,.0f} €")
    with st.expander("Vergleichstabelle aller m"):
        tbl_rows = []
        for mv in [1, 2, 4, 12, 52, 365]:
            pe = (1 + p_nom_r/100/mv)**mv - 1
            kt = K0_eff_r * (1 + p_nom_r/100/mv)**(mv*T_eff_r)
            tbl_rows.append({"m": _m_labels[mv].split("(")[0].strip(),
                             "p_EFF (%)": f"{pe*100:.4f}",
                             f"K(T) €": f"{kt:,.2f}"})
        pe_c = np.exp(p_nom_r/100) - 1
        kt_c = K0_eff_r * np.exp(p_nom_r/100 * T_eff_r)
        tbl_rows.append({"m": "∞ (stetig)",
                         "p_EFF (%)": f"{pe_c*100:.4f}",
                         f"K(T) €": f"{kt_c:,.2f}"})
        st.dataframe(pd.DataFrame(tbl_rows).set_index("m"),
                     use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Übungsaufgaben
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Übungsaufgaben")
st.markdown(
    "Versuchen Sie jede Aufgabe zunächst selbst zu lösen. "
    "Klappen Sie dann den Tipp oder die vollständige Lösung auf."
)

# ── Aufgabe 1 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 1 ⭐ – Alle Renditekennzahlen")
st.markdown(
    "Herr Xapp investiert zu Beginn des Jahres 2020 **€ 5.000,–** in einen Fonds. "
    "Ende 2023 (nach genau **4 Jahren**) ist sein Anteil **€ 7.200,–** wert.  \n"
    "Berechnen Sie: **(a)** Gesamtrendite &nbsp;·&nbsp; **(b)** Jahresrendite "
    "&nbsp;·&nbsp; **(c)** Effektivzins &nbsp;·&nbsp; **(d)** Log-Rendite "
    "&nbsp;·&nbsp; **(e)** jährliche Log-Rendite."
)
a1c1, a1c2 = st.columns(2)
with a1c1:
    with st.expander("💡 Tipp"):
        st.markdown(
            "Fünf Formeln, dieselben Eingaben: K(0) = 5.000, K(T) = 7.200, T = 4  \n\n"
            "- r = (K(T)−K(0)) / K(0)  \n"
            "- r̄ = r / T  \n"
            "- p_EFF = (K(T)/K(0))^(1/T) − 1  \n"
            "- r_log = ln(K(T)/K(0))  \n"
            "- r̄_log = r_log / T"
        )
with a1c2:
    with st.expander("✅ Schritt-für-Schritt Lösung"):
        r1   = (7200-5000)/5000
        pe1  = (7200/5000)**(1/4) - 1
        rl1  = np.log(7200/5000)
        st.latex(r"r = \frac{7200-5000}{5000} = 44{,}00\%")
        st.latex(r"\bar{r} = \frac{44\%}{4} = 11{,}00\%\ \text{p.a.}")
        st.latex(r"p_{EFF} = 1{,}44^{0{,}25}-1")
        st.latex(r"r_{log} = \ln(1{,}44) = 36{,}46\%\ \text{gesamt}")
        df1 = pd.DataFrame({
            "Kennzahl": ["r gesamt","r̄ p.a.","p_EFF p.a.","r_log gesamt","r̄_log p.a."],
            "Wert":     [f"{r1*100:.2f}%", f"{r1/4*100:.2f}%",
                         f"{pe1*100:.2f}%", f"{rl1*100:.2f}%", f"{rl1/4*100:.2f}%"],
        })
        st.dataframe(df1.set_index("Kennzahl"), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 2 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 2 ⭐ – Aktienrendite")
st.markdown(
    "Frau K. kauft **200 Volkswagen-Aktien** zu je **€ 90,–**. "
    "Nach **2,5 Jahren** notiert die Aktie bei **€ 114,30**.  \n"
    "Berechnen Sie: Gesamtrendite, jährliche Durchschnittsrendite, Effektivzins."
)
a2c1, a2c2 = st.columns(2)
with a2c1:
    with st.expander("💡 Tipp"):
        st.markdown(
            "Berechnen Sie zunächst K(0) und K(T) aus Stückzahl × Kurs.  \n"
            "Dann gelten die gleichen Formeln wie in Aufgabe 1."
        )
with a2c2:
    with st.expander("✅ Schritt-für-Schritt Lösung"):
        K0_2, KT_2, T_2 = 200*90, 200*114.30, 2.5
        r2  = (KT_2-K0_2)/K0_2
        pe2 = (KT_2/K0_2)**(1/T_2) - 1
        st.markdown(f"K(0) = 200 × 90 = **{K0_2:,.0f} €** &nbsp;|&nbsp; "
                    f"K(T) = 200 × 114,30 = **{KT_2:,.0f} €**")
        st.latex(r"r = \frac{22860-18000}{18000} = 27{,}00\%")
        st.latex(r"\bar{r} = \frac{27\%}{2{,}5} = 10{,}80\%\ \text{p.a.}")
        st.latex(r"p_{EFF} = 1{,}27^{0{,}4}-1")
        st.markdown(f"**p_EFF = {pe2*100:.2f}% p.a.**")

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 3 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 3 ⭐⭐ – Investitionsvergleich (Vorsicht: Falle!)")
st.markdown(
    "Zwei Investments haben **jeweils 20% Gesamtrendite** erzielt:  \n"
    "- **Investment A:** K(0) = € 8.000,– → K(T) = € 9.600,– in **2 Jahren**  \n"
    "- **Investment B:** K(0) = € 3.000,– → K(T) = € 3.600,– in **1 Jahr**  \n\n"
    "Welches war auf **jährlicher Basis** besser? Begründen Sie."
)
a3c1, a3c2 = st.columns(2)
with a3c1:
    with st.expander("💡 Tipp"):
        st.markdown(
            "Gleiche Gesamtrendite ≠ gleiche Jahresrendite!  \n"
            "Berechnen Sie den **Effektivzins** für beide und vergleichen."
        )
with a3c2:
    with st.expander("✅ Schritt-für-Schritt Lösung"):
        peA = (9600/8000)**0.5 - 1
        peB = (3600/3000)**1.0 - 1
        st.markdown("**Investment A:**")
        st.latex(r"p_{EFF,A} = 1{,}2^{0{,}5}-1 \approx 9{,}54\%\ \text{p.a.}")
        st.markdown("**Investment B:**")
        st.latex(r"p_{EFF,B} = 1{,}2^{1}-1 = 20{,}00\%\ \text{p.a.}")
        st.success(
            f"**B ist deutlich besser** ({peB*100:.2f}% > {peA*100:.2f}% p.a.)  \n"
            "Gleiche Gesamtrendite – aber B hat sie in der Hälfte der Zeit erreicht!"
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 4 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 4 ⭐⭐ – Effektivzins bei unterjähriger Verzinsung")
st.markdown(
    "**€ 12.000,–** werden zu **4,5 % Nominalzins p.a.** bei "
    "**monatlicher Zinsverrechnung** für **3 Jahre** angelegt.  \n"
    "**(A)** Wie hoch ist der Effektivzins?  \n"
    "**(B)** Wie hoch ist das Endkapital K(3)?"
)
a4c1, a4c2 = st.columns(2)
with a4c1:
    with st.expander("💡 Tipp"):
        st.markdown(
            "Monatlich → m = 12  \n"
            "- p_EFF = (1 + p_nom/m)^m − 1  \n"
            "- K(T) = K(0) · (1 + p_nom/m)^(m·T)"
        )
with a4c2:
    with st.expander("✅ Schritt-für-Schritt Lösung"):
        pe4 = (1 + 0.045/12)**12 - 1
        KT4 = 12000 * (1 + 0.045/12)**(36)
        st.markdown("**(A) Effektivzins:**")
        st.latex(r"p_{EFF}=\!\left(1+\frac{0{,}045}{12}\right)^{12}\!-1=(1{,}00375)^{12}-1")
        st.markdown(f"**p_EFF = {pe4*100:.4f}% p.a.**")
        st.markdown("**(B) Endkapital:**")
        st.latex(r"K(3)=12000\cdot(1{,}00375)^{36}")
        st.markdown(f"**K(3) = {KT4:,.2f} €**")

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 5 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 5 ⭐⭐⭐ – Log-Rendite & Kennzahlenvergleich")
st.markdown(
    "Eine Aktie wird zu **€ 44,–** gekauft. Nach **18 Monaten** liegt "
    "der Kurs bei **€ 52,80**.  \n"
    "**(A)** Stetige Log-Rendite gesamt und p.a.  \n"
    "**(B)** Effektivzins p.a.  \n"
    "**(C)** Übersichtstabelle aller fünf Kennzahlen – erklären Sie die Unterschiede."
)
a5c1, a5c2 = st.columns(2)
with a5c1:
    with st.expander("💡 Tipp"):
        st.markdown(
            "18 Monate = T = **1,5 Jahre**.  \n"
            "r_log = ln(K(T)/K(0)) – natürlicher Logarithmus.  \n"
            "Für die Tabelle: alle fünf Formeln der Woche anwenden."
        )
with a5c2:
    with st.expander("✅ Schritt-für-Schritt Lösung"):
        K0_5, KT_5, T_5 = 44.0, 52.80, 1.5
        r5   = (KT_5-K0_5)/K0_5
        pe5  = (KT_5/K0_5)**(1/T_5) - 1
        rl5  = np.log(KT_5/K0_5)
        st.markdown("**(A)** r_log = ln(52,80/44) = ln(1,2)")
        st.markdown(f"**r_log = {rl5*100:.2f}% gesamt &nbsp;|&nbsp; r̄_log = {rl5/T_5*100:.2f}% p.a.**")
        st.markdown("**(B)** p_EFF = 1,2^(1/1,5) − 1 = 1,2^(2/3) − 1")
        st.markdown(f"**p_EFF = {pe5*100:.2f}% p.a.**")
        st.markdown("**(C) Übersicht:**")
        df5 = pd.DataFrame({
            "Kennzahl": ["r gesamt", "r̄ p.a.", "p_EFF p.a.",
                         "r_log gesamt", "r̄_log p.a."],
            "Wert": [f"{r5*100:.2f}%", f"{r5/T_5*100:.2f}%",
                     f"{pe5*100:.2f}%", f"{rl5*100:.2f}%", f"{rl5/T_5*100:.2f}%"],
        })
        st.dataframe(df5.set_index("Kennzahl"), use_container_width=True)
        st.info(
            f"r̄ ({r5/T_5*100:.2f}%) > p_EFF ({pe5*100:.2f}%) > r̄_log ({rl5/T_5*100:.2f}%)  \n"
            "Log-Rendite liegt leicht darunter – sie unterstellt stetige Verzinsung. "
            "Bei kleinen Renditen sind alle drei nahezu gleich."
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Live-Marktdaten Aufgaben
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Live-Marktdaten Aufgaben 📡")
st.markdown(
    "Die aktuellen Kurse werden **live von der Börse** abgerufen – "
    "die Aufgaben sind daher jedes Mal aktuell."
)

@st.cache_data(ttl=300)
def fetch_price(ticker: str):
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        series = hist["Close"].dropna()
        if not series.empty:
            return round(float(series.iloc[-1]), 2)
    except Exception:
        pass
    return None

sap_now = fetch_price("SAP.DE")
dbk_now = fetch_price("DBK.DE")
alv_now = fetch_price("ALV.DE")

# Live price status bar
lc1, lc2, lc3, lc4 = st.columns(4)
lc1.markdown("**Letzte Kurse (XETRA)**")
lc2.metric("SAP SE (SAP.DE)",         f"€ {sap_now:,.2f}" if sap_now else "–")
lc3.metric("Deutsche Bank (DBK.DE)",  f"€ {dbk_now:,.2f}" if dbk_now else "–")
lc4.metric("Allianz (ALV.DE)",        f"€ {alv_now:,.2f}" if alv_now else "–")
st.caption("Kurse werden alle 5 Minuten aktualisiert · Quelle: Yahoo Finance")

# Shared purchase dates
_buy_2023 = date(2023, 1, 2)
_buy_2024 = date(2024, 1, 2)
_today    = date.today()
T_23 = (_today - _buy_2023).days / 365.25
T_24 = (_today - _buy_2024).days / 365.25

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 6 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 6 ⭐ – SAP SE: Rendite eines Technologietitels")
if sap_now:
    st.markdown(
        f"Herr M. kauft am **02.01.2023** genau **50 SAP-Aktien** zu je **€ 112,50**.  \n"
        f"Heute (**{_today.strftime('%d.%m.%Y')}**) notiert die Aktie bei "
        f"**€ {sap_now:,.2f}** *(aktueller Börsenkurs)*.  \n\n"
        "Berechnen Sie: **(a)** Gesamtrendite &nbsp;·&nbsp; **(b)** Jahresrendite "
        "&nbsp;·&nbsp; **(c)** Effektivzins &nbsp;·&nbsp; **(d)** Log-Rendite p.a."
    )
else:
    st.warning("SAP-Kurs konnte nicht abgerufen werden – bitte manuell recherchieren.")

if sap_now:
    a6c1, a6c2 = st.columns(2)
    with a6c1:
        with st.expander("💡 Tipp"):
            st.markdown(
                f"K(0) = 50 × 112,50 = **€ 5.625,–**  \n"
                f"K(T) = 50 × {sap_now:.2f} = **€ {50*sap_now:,.2f}**  \n"
                f"T = {T_23:.2f} Jahre  \n\n"
                "Dann die vier Formeln aus Woche 2 anwenden."
            )
    with a6c2:
        with st.expander("✅ Schritt-für-Schritt Lösung"):
            K0_6 = 50 * 112.50
            KT_6 = 50 * sap_now
            r6   = (KT_6 - K0_6) / K0_6
            pe6  = (KT_6 / K0_6) ** (1 / T_23) - 1
            rl6  = np.log(KT_6 / K0_6)
            st.markdown(f"K(0) = 50 × 112,50 = **{K0_6:,.2f} €**  \n"
                        f"K(T) = 50 × {sap_now:.2f} = **{KT_6:,.2f} €**  \n"
                        f"T = {T_23:.2f} Jahre")
            df6 = pd.DataFrame({
                "Kennzahl": ["r gesamt", "r̄ p.a.", "p_EFF p.a.", "r̄_log p.a."],
                "Formel":   ["(KT−K0)/K0", "r/T",
                             "(KT/K0)^(1/T)−1", "ln(KT/K0)/T"],
                "Wert":     [f"{r6*100:.2f}%", f"{r6/T_23*100:.2f}%",
                             f"{pe6*100:.2f}%", f"{rl6/T_23*100:.2f}%"],
            })
            st.dataframe(df6.set_index("Kennzahl"), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 7 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 7 ⭐⭐ – Deutsche Bank vs. Allianz: Wer hat besser abgeschnitten?")
if dbk_now and alv_now:
    st.markdown(
        f"Frau K. investiert am **02.01.2024** jeweils rund **€ 1.200,–** in zwei Aktien:  \n"
        f"- **100 Deutsche Bank-Aktien** zu je **€ 12,50** → K₀ = € 1.250,–  \n"
        f"- **5 Allianz-Aktien** zu je **€ 238,00** → K₀ = € 1.190,–  \n\n"
        f"Aktuelle Kurse heute (**{_today.strftime('%d.%m.%Y')}**):  \n"
        f"DBK = **€ {dbk_now:,.2f}** &nbsp;·&nbsp; ALV = **€ {alv_now:,.2f}**  \n\n"
        "Welche Aktie hatte den höheren **Effektivzins**? Berechnen Sie für beide."
    )
else:
    st.warning("Kurse konnten nicht abgerufen werden.")

if dbk_now and alv_now:
    a7c1, a7c2 = st.columns(2)
    with a7c1:
        with st.expander("💡 Tipp"):
            st.markdown(
                "Gleiche Formel für beide: p_EFF = (K(T)/K(0))^(1/T) − 1  \n"
                f"T ist für beide gleich: **{T_24:.2f} Jahre**  \n"
                "Vergleichen Sie danach die beiden Effektivzinsen."
            )
    with a7c2:
        with st.expander("✅ Schritt-für-Schritt Lösung"):
            K0_db, KT_db = 100*12.50, 100*dbk_now
            K0_al, KT_al = 5*238.00,  5*alv_now
            pe_db = (KT_db/K0_db)**(1/T_24) - 1
            pe_al = (KT_al/K0_al)**(1/T_24) - 1
            winner = "Deutsche Bank" if pe_db > pe_al else "Allianz"
            st.markdown("**Deutsche Bank:**")
            st.markdown(f"K(0)={K0_db:,.2f} € → K(T)={KT_db:,.2f} €  \n"
                        f"**p_EFF = {pe_db*100:.2f}% p.a.**")
            st.markdown("**Allianz:**")
            st.markdown(f"K(0)={K0_al:,.2f} € → K(T)={KT_al:,.2f} €  \n"
                        f"**p_EFF = {pe_al*100:.2f}% p.a.**")
            if pe_db > pe_al:
                st.success(f"**Deutsche Bank** hatte den höheren Effektivzins "
                           f"({pe_db*100:.2f}% > {pe_al*100:.2f}% p.a.)")
            else:
                st.success(f"**Allianz** hatte den höheren Effektivzins "
                           f"({pe_al*100:.2f}% > {pe_db*100:.2f}% p.a.)")

st.markdown("<br>", unsafe_allow_html=True)

# ── Aufgabe 8 ─────────────────────────────────────────────────────────────────
st.markdown("#### Aufgabe 8 ⭐⭐⭐ – Mini-Portfolio: Gesamtrendite berechnen")
if sap_now and dbk_now and alv_now:
    st.markdown(
        f"Herr X baut am **02.01.2023** ein Portfolio aus drei deutschen Aktien auf:  \n\n"
        "| Aktie | Stück | Kaufkurs | Kaufwert |  \n"
        "|---|---|---|---|  \n"
        "| SAP SE | 20 | € 112,50 | € 2.250,– |  \n"
        "| Deutsche Bank | 150 | € 10,80 | € 1.620,– |  \n"
        "| Allianz | 10 | € 198,00 | € 1.980,– |  \n"
        "| **Gesamt** | | | **€ 5.850,–** |  \n\n"
        f"Aktuelle Kurse: SAP = **€ {sap_now:,.2f}** · DBK = **€ {dbk_now:,.2f}** "
        f"· ALV = **€ {alv_now:,.2f}**  \n\n"
        "**(A)** Wie viel ist das Portfolio heute wert?  \n"
        "**(B)** Wie hoch sind Gesamtrendite und Effektivzins des Portfolios?"
    )
else:
    st.warning("Kurse konnten nicht abgerufen werden.")

if sap_now and dbk_now and alv_now:
    a8c1, a8c2 = st.columns(2)
    with a8c1:
        with st.expander("💡 Tipp"):
            st.markdown(
                "Schritt 1: Berechnen Sie den heutigen Wert jeder Position  \n"
                "(Stückzahl × aktueller Kurs)  \n\n"
                "Schritt 2: Addieren Sie alle drei → K(T)  \n\n"
                "Schritt 3: K(0) = 5.850 €, dann Renditeformeln anwenden.  \n"
                f"T = {T_23:.2f} Jahre"
            )
    with a8c2:
        with st.expander("✅ Schritt-für-Schritt Lösung"):
            K0_8  = 20*112.50 + 150*10.80 + 10*198.00
            KT_sap = 20 * sap_now
            KT_dbk = 150 * dbk_now
            KT_alv = 10  * alv_now
            KT_8   = KT_sap + KT_dbk + KT_alv
            r8  = (KT_8 - K0_8) / K0_8
            pe8 = (KT_8 / K0_8) ** (1 / T_23) - 1
            rl8 = np.log(KT_8 / K0_8)

            st.markdown("**(A) Heutiger Portfoliowert:**")
            df8 = pd.DataFrame({
                "Aktie":   ["SAP (20×)", "Deutsche Bank (150×)", "Allianz (10×)", "**Portfolio**"],
                "Kaufwert €": ["2.250,00", "1.620,00", "1.980,00", f"**{K0_8:,.2f}**"],
                "Heute €":    [f"{KT_sap:,.2f}", f"{KT_dbk:,.2f}",
                               f"{KT_alv:,.2f}", f"**{KT_8:,.2f}**"],
                "Gewinn €":   [f"{KT_sap-2250:+,.2f}", f"{KT_dbk-1620:+,.2f}",
                               f"{KT_alv-1980:+,.2f}", f"**{KT_8-K0_8:+,.2f}**"],
            })
            st.dataframe(df8.set_index("Aktie"), use_container_width=True)

            st.markdown("**(B) Portfolio-Rendite:**")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Gesamtrendite r",  f"{r8*100:.2f}%")
            col_b.metric("Effektivzins p_EFF", f"{pe8*100:.2f}% p.a.")
            col_c.metric("Log-Rendite p.a.", f"{rl8/T_23*100:.2f}%")

            # Mini bar chart of individual contributions
            fig8 = go.Figure(go.Bar(
                x=["SAP", "Deutsche Bank", "Allianz"],
                y=[KT_sap-2250, KT_dbk-1620, KT_alv-1980],
                marker_color=["#42a5f5", "#ff9800", "#66bb6a"],
                text=[f"{v:+,.0f} €" for v in [KT_sap-2250, KT_dbk-1620, KT_alv-1980]],
                textposition="outside",
            ))
            fig8.update_layout(
                title="Gewinn/Verlust je Position",
                yaxis=dict(title="€", gridcolor="rgba(128,128,128,0.2)"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0"), height=300,
                margin=dict(t=40, b=30, l=60, r=20), showlegend=False,
            )
            st.plotly_chart(fig8, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Formula reference ─────────────────────────────────────────────────────────
with st.expander("📐 Formelreferenz – alle Renditekennzahlen", expanded=False):
    st.markdown("""
| Kennzahl | Formel | Einheit |
|---|---|---|
| Gesamtrendite | r = (K(T) − K(0)) / K(0) | % |
| Jahresrendite (arithm.) | r̄ = r / T | % p.a. |
| Effektivzins (PAngV) | p_EFF = (K(T)/K(0))^(1/T) − 1 | % p.a. |
| Log-Rendite (stetig) | r_log = ln(K(T)/K(0)) | % |
| Log-Rendite p.a. | r̄_log = r_log / T | % p.a. |
| Effektivzins (unterjährig) | p_EFF = (1 + p_nom/m)^m − 1 | % p.a. |
| Endkapital (unterjährig) | K(T) = K(0) · (1 + p_nom/m)^(m·T) | € |
| Endkapital (stetig) | K(T) = K(0) · e^(p·T) | € |
    """)
    st.latex(
        r"\text{Reihenfolge (pos. Rendite): }"
        r"\bar{r}\ \geq\ p_{EFF}\ \geq\ \bar{r}_{log}"
    )

st.markdown(
    "<p style='text-align:center;color:#888;font-size:12px;margin-top:32px;'>"
    "Frankfurt University of Applied Sciences · Tutorium Wirtschaftsmathematik · "
    "Ilyos Umurzakov · 2025/26</p>",
    unsafe_allow_html=True,
)
