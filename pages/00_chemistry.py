import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="반응차수별 농도-시간 시각화",
    page_icon="⚗️",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans KR', sans-serif; }
h1, h2, h3, h4 { font-family: 'IBM Plex Mono', monospace !important; }
section[data-testid="stSidebar"] { background: #13161f; border-right: 1px solid #2a2d3a; }
</style>
""", unsafe_allow_html=True)

COLORS = {"0차": "#4f8ef7", "1차": "#34d399", "2차": "#f97316"}

# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚗️ 파라미터 설정")
    st.divider()

    st.markdown("**초기 조건**")
    C0    = st.slider("초기 농도 C₀ (mol/L)", 0.5, 10.0, 2.0, 0.1)
    t_max = st.slider("최대 시간 t (s)",       10,  300,  80,  5)

    st.divider()
    st.markdown("**반응속도 상수 k**")
    k0 = st.slider("k₀ — 0차 (mol/L·s)",  0.01, 0.50, 0.05, 0.01, format="%.3f")
    k1 = st.slider("k₁ — 1차 (1/s)",      0.01, 0.30, 0.05, 0.005, format="%.3f")
    k2 = st.slider("k₂ — 2차 (L/mol·s)", 0.01, 0.50, 0.05, 0.01, format="%.3f")

    st.divider()
    st.markdown("**표시할 반응차수**")
    show_0 = st.checkbox("0차 반응", value=True)
    show_1 = st.checkbox("1차 반응", value=True)
    show_2 = st.checkbox("2차 반응", value=True)

    st.divider()
    st.markdown("**추가 옵션**")
    show_linear = st.checkbox("선형화 그래프 표시", value=True)
    show_half   = st.checkbox("반감기 수직선 표시", value=True)

# ── 계산 ──────────────────────────────────────────────────
t   = np.linspace(0, t_max, 500)
C_0 = np.maximum(C0 - k0 * t, 0)
C_1 = C0 * np.exp(-k1 * t)
C_2 = C0 / (1 + k2 * C0 * t)

t_half_0 = C0 / (2 * k0)
t_half_1 = np.log(2) / k1
t_half_2 = 1 / (k2 * C0)

def fmt_half(th):
    return f"{th:.1f} s" if th <= t_max else f"> {t_max} s"

# ── 헤더 ──────────────────────────────────────────────────
st.title("반응차수별 농도-시간 곡선")
st.caption("슬라이더로 파라미터를 조절하며 0차 / 1차 / 2차 반응의 농도 변화를 실시간으로 비교합니다.")
st.divider()

# ── 반감기 메트릭 ──────────────────────────────────────────
st.markdown("#### 반감기 t½")
col1, col2, col3 = st.columns(3)
col1.metric("0차  (C₀ / 2k₀)",  fmt_half(t_half_0))
col2.metric("1차  (ln2 / k₁)",  fmt_half(t_half_1))
col3.metric("2차  (1 / k₂C₀)", fmt_half(t_half_2))

st.divider()

# ── 플롯 ──────────────────────────────────────────────────
PLOT_BG  = "#13161f"
PAPER_BG = "#0d0f14"
GRID_CLR = "#1f2232"
TICK_CLR = "#6b7280"
ANNO_CLR = "#9ca3af"

axis_style = dict(
    gridcolor=GRID_CLR, gridwidth=1,
    linecolor="#2a2d3a", linewidth=1,
    tickfont=dict(color=TICK_CLR, size=11, family="IBM Plex Mono"),
    title_font=dict(color=ANNO_CLR, size=12, family="IBM Plex Mono"),
    zeroline=False,
)

if show_linear:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("농도-시간 곡선  C vs t", "선형화 그래프"),
        horizontal_spacing=0.10,
    )
else:
    fig = make_subplots(rows=1, cols=1)

orders = [
    ("0차", show_0, C_0, C_0,         t_half_0),
    ("1차", show_1, C_1, np.log(C_1), t_half_1),
    ("2차", show_2, C_2, 1.0 / C_2,  t_half_2),
]

for order, visible, C_arr, lin_arr, th in orders:
    if not visible:
        continue
    color = COLORS[order]

    fig.add_trace(
        go.Scatter(
            x=t, y=C_arr,
            mode="lines",
            name=f"{order} 반응",
            line=dict(color=color, width=2.5),
            hovertemplate="t = %{x:.1f} s<br>C = %{y:.4f} mol/L<extra>" + f"{order}</extra>",
        ),
        row=1, col=1,
    )

    if show_half and th <= t_max:
        fig.add_vline(
            x=th, line_dash="dot", line_color=color,
            line_width=1.2, opacity=0.55,
            annotation_text=f"t½={th:.1f}s",
            annotation_font_color=color,
            annotation_font_size=11,
            row=1, col=1,
        )

    if show_linear:
        lin_labels = {"0차": "C", "1차": "ln(C)", "2차": "1/C"}
        fig.add_trace(
            go.Scatter(
                x=t, y=lin_arr,
                mode="lines",
                name=f"{order} 선형",
                line=dict(color=color, width=2),
                showlegend=False,
                hovertemplate="t = %{x:.1f} s<br>" + lin_labels[order] + " = %{y:.4f}<extra>" + f"{order}</extra>",
            ),
            row=1, col=2,
        )

fig.update_layout(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family="IBM Plex Sans KR", color="#e8eaf0"),
    legend=dict(
        bgcolor="#1a1d28", bordercolor="#2a2d3a", borderwidth=1,
        font=dict(size=12, family="IBM Plex Mono", color="#e8eaf0"),
        x=0.01, y=0.99,
    ),
    margin=dict(t=50, b=40, l=10, r=10),
    height=440,
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1a1d28", bordercolor="#2a2d3a",
        font_color="#e8eaf0", font_family="IBM Plex Mono",
    ),
)

fig.update_xaxes(title_text="시간 t (s)", **axis_style)
fig.update_yaxes(title_text="농도 C (mol/L)", **axis_style, row=1, col=1)
if show_linear:
    fig.update_yaxes(title_text="선형화 값", **axis_style, row=1, col=2)
    for ann in fig.layout.annotations:
        ann.font.color  = ANNO_CLR
        ann.font.family = "IBM Plex Mono"
        ann.font.size   = 13

st.plotly_chart(fig, use_container_width=True)

# ── 적분 속도식 ───────────────────────────────────────────
st.divider()
st.markdown("#### 적분 속도식 (Integrated Rate Laws)")

fc1, fc2, fc3 = st.columns(3)
fc1.code("0차:  C = C₀ − k₀·t\n선형: C vs t  (기울기 = −k₀)", language=None)
fc2.code("1차:  C = C₀·exp(−k₁t)\n선형: ln(C) vs t  (기울기 = −k₁)", language=None)
fc3.code("2차:  1/C = 1/C₀ + k₂·t\n선형: 1/C vs t  (기울기 = k₂)", language=None)
