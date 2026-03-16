import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B3 Short Prospector",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #0a0e17; color: #e0e6f0; }

section[data-testid="stSidebar"] {
    background: #0d1220;
    border-right: 1px solid #1e2d45;
}

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.metric-card {
    background: linear-gradient(135deg, #0d1a2e 0%, #0f2040 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 6px 0;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #2e6aad; }

.metric-label {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5a7fa8;
    font-weight: 600;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    margin: 4px 0 2px 0;
}
.metric-sub { font-size: 12px; color: #7a9cc0; }

.signal-short {
    background: linear-gradient(135deg, #2d0a0a, #3d1010);
    border: 1px solid #8b2020;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px 0;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
}
.signal-neutro {
    background: linear-gradient(135deg, #0d1a0d, #152015);
    border: 1px solid #1a4020;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px 0;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
}
.tag-red {
    background: #8b0000; color: #ffaaaa;
    padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 700;
    letter-spacing: 1px;
}
.tag-green {
    background: #005a00; color: #aaffaa;
    padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 700;
    letter-spacing: 1px;
}
.tag-yellow {
    background: #5a4a00; color: #ffe066;
    padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 700;
    letter-spacing: 1px;
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #e0f0ff;
    letter-spacing: -1px;
}
.header-sub {
    color: #3a6a9a;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 600;
}
.ranking-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0d1a2e;
    border: 1px solid #1a2e45;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 4px 0;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    transition: background 0.2s;
}
.divider { border: none; border-top: 1px solid #1a2e45; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ─── ATIVOS ────────────────────────────────────────────────────────────────────
ATIVOS_B3 = {
    "PETR4": "Petrobras PN", "VALE3": "Vale ON", "ITUB4": "Itaú PN",
    "BBDC4": "Bradesco PN", "ABEV3": "Ambev ON", "MGLU3": "Magazine Luiza",
    "LREN3": "Lojas Renner", "COGN3": "Cogna ON", "CIEL3": "Cielo ON",
    "AMER3": "Americanas ON", "PETZ3": "Petz ON", "YDUQ3": "Yduqs ON",
    "SOMA3": "Grupo Soma ON", "WEGE3": "WEG ON", "RENT3": "Localiza ON",
    "RADL3": "Raia Drogasil", "MRVE3": "MRV ON", "CYRE3": "Cyrela ON",
    "BEEF3": "Minerva ON", "BBAS3": "Banco do Brasil",
    "BPAC11": "BTG Pactual", "SANB11": "Santander BR",
    "TOTS3": "Totvs ON", "EZTC3": "EZTEC ON", "DIRR3": "Direcional ON"
}

PERIODOS = {"1 Mês": "1mo", "3 Meses": "3mo", "6 Meses": "6mo", "1 Ano": "1y"}

# ─── FUNÇÕES ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)  # cache 15 minutos
def baixar_dados(ticker_sa: str, period: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker_sa, period=period, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except:
        return pd.DataFrame()

def calcular_rsi(series: pd.Series, periodo: int = 14) -> pd.Series:
    delta = series.diff()
    ganho = delta.clip(lower=0).ewm(com=periodo-1, min_periods=periodo).mean()
    perda = (-delta.clip(upper=0)).ewm(com=periodo-1, min_periods=periodo).mean()
    rs = ganho / perda.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)

def calcular_bollinger(close: pd.Series, periodo: int = 20):
    mm = close.rolling(periodo).mean()
    std = close.rolling(periodo).std()
    return mm + 2*std, mm, mm - 2*std

def afastamento_mm(close: pd.Series, periodo: int = 200) -> float:
    p = min(periodo, len(close))
    mm = close.rolling(p).mean().iloc[-1]
    return round(((close.iloc[-1] - mm) / mm) * 100, 2) if mm > 0 else 0.0

def score_short(rsi: float, afas: float, vol_ratio: float) -> float:
    s = 0.0
    if rsi > 70: s += (rsi - 70) * 2.0
    elif rsi > 60: s += (rsi - 60) * 0.8
    if afas > 15: s += (afas - 15) * 3.0
    elif afas > 8: s += (afas - 8) * 1.5
    elif afas > 3: s += (afas - 3) * 0.5
    if vol_ratio > 2: s += (vol_ratio - 2) * 8
    elif vol_ratio > 1.3: s += (vol_ratio - 1.3) * 4
    return round(s, 1)

def sinal_texto(rsi: float, afas: float) -> tuple:
    if rsi > 75 and afas > 15:
        return "🔴 SHORT FORTE", "tag-red"
    elif rsi > 70 or afas > 10:
        return "🟠 SHORT MODERADO", "tag-yellow"
    elif rsi < 40:
        return "🟢 NEUTRO / COMPRA", "tag-green"
    else:
        return "⚪ AGUARDAR", "tag-yellow"

@st.cache_data(ttl=900)
def calcular_ranking() -> pd.DataFrame:
    resultados = []
    for ticker, nome in ATIVOS_B3.items():
        try:
            df = baixar_dados(f"{ticker}.SA", "3mo")
            if df.empty or len(df) < 20:
                continue
            close = df["Close"]
            volume = df["Volume"]
            rsi_val = float(calcular_rsi(close).iloc[-1])
            afas = afastamento_mm(close, 200)
            vol_med = volume.rolling(20).mean().iloc[-1]
            vol_ratio = float(volume.iloc[-1] / vol_med) if vol_med > 0 else 1.0
            sc = score_short(rsi_val, afas, vol_ratio)
            preco = float(close.iloc[-1])
            var_dia = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100) if len(close) > 1 else 0
            sinal, _ = sinal_texto(rsi_val, afas)
            resultados.append({
                "Ticker": ticker, "Nome": nome, "Preço": preco,
                "Var%": round(var_dia, 2), "RSI": round(rsi_val, 1),
                "Afas.MM200%": afas, "Vol.Ratio": round(vol_ratio, 2),
                "Score Short": sc, "Sinal": sinal
            })
        except:
            continue
    df_rank = pd.DataFrame(resultados)
    if not df_rank.empty:
        df_rank = df_rank.sort_values("Score Short", ascending=False).reset_index(drop=True)
        df_rank.index += 1
    return df_rank

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="header-title">📉 B3 Short</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">Prospector v1.0</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("**🔍 Análise Individual**")
    ticker_input = st.text_input("Ticker", value="PETR4", help="Digite o código sem .SA").upper().strip()
    periodo_label = st.selectbox("Período", list(PERIODOS.keys()), index=1)
    periodo = PERIODOS[periodo_label]

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**⚙️ Indicadores**")
    show_bb = st.checkbox("Bollinger Bands", value=True)
    show_mm20 = st.checkbox("Média Móvel 20", value=True)
    show_mm50 = st.checkbox("Média Móvel 50", value=False)
    show_mm200 = st.checkbox("Média Móvel 200", value=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**🏆 Ranking**")
    if st.button("🔄 Atualizar Ranking", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.caption(f"Dados: Yahoo Finance (15min delay)\nAtualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ─── MAIN ──────────────────────────────────────────────────────────────────────
aba1, aba2 = st.tabs(["📊 Análise do Ativo", "🏆 Ranking de Shorts"])

# ══════════════════════════════════════════════════════════════════════
# ABA 1 — ANÁLISE INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════
with aba1:
    ticker_sa = f"{ticker_input}.SA"
    with st.spinner(f"Buscando dados de {ticker_input}..."):
        df = baixar_dados(ticker_sa, periodo)

    if df.empty:
        st.error(f"❌ Não foi possível obter dados para **{ticker_input}**. Verifique o ticker.")
        st.stop()

    close = df["Close"]
    volume = df["Volume"]
    nome_ativo = ATIVOS_B3.get(ticker_input, ticker_input)

    # Calcular indicadores
    rsi = calcular_rsi(close)
    bb_sup, bb_med, bb_inf = calcular_bollinger(close)
    mm20 = close.rolling(20).mean()
    mm50 = close.rolling(50).mean()
    mm200 = close.rolling(200).mean()
    afas = afastamento_mm(close, 200)
    vol_med = volume.rolling(20).mean()
    vol_ratio = float(volume.iloc[-1] / vol_med.iloc[-1]) if vol_med.iloc[-1] > 0 else 1.0
    rsi_atual = float(rsi.iloc[-1])
    preco_atual = float(close.iloc[-1])
    var_dia = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100) if len(close) > 1 else 0
    sc = score_short(rsi_atual, afas, vol_ratio)
    sinal, tag_class = sinal_texto(rsi_atual, afas)

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"## {ticker_input} — {nome_ativo}")
    with col_h2:
        st.markdown(f'<div style="text-align:right;padding-top:12px"><span class="{tag_class}">{sinal}</span></div>', unsafe_allow_html=True)

    # Métricas
    c1, c2, c3, c4, c5 = st.columns(5)
    cor_var = "#ff4444" if var_dia < 0 else "#44ff88"
    cor_rsi = "#ff4444" if rsi_atual > 70 else ("#44ff88" if rsi_atual < 40 else "#ffcc00")
    cor_afas = "#ff4444" if afas > 10 else ("#44ff88" if afas < -5 else "#ffcc00")
    cor_vol = "#ff4444" if vol_ratio > 1.5 else "#aabbcc"

    with c1:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">Preço Atual</div>
            <div class="metric-value" style="color:#e0f0ff">R$ {preco_atual:.2f}</div>
            <div class="metric-sub" style="color:{cor_var}">{var_dia:+.2f}% hoje</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">RSI (14)</div>
            <div class="metric-value" style="color:{cor_rsi}">{rsi_atual:.1f}</div>
            <div class="metric-sub">{"⚠️ Sobrecomprado" if rsi_atual>70 else ("💚 Sobrevendido" if rsi_atual<30 else "Neutro")}</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">Afas. MM200</div>
            <div class="metric-value" style="color:{cor_afas}">{afas:+.1f}%</div>
            <div class="metric-sub">{"⚠️ Muito esticado" if afas>10 else ("Normal" if abs(afas)<5 else "Atenção")}</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">Volume Ratio</div>
            <div class="metric-value" style="color:{cor_vol}">{vol_ratio:.2f}x</div>
            <div class="metric-sub">vs. média 20 dias</div>
        </div>''', unsafe_allow_html=True)
    with c5:
        cor_score = "#ff4444" if sc > 30 else ("#ffcc00" if sc > 10 else "#44ff88")
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">Score Short</div>
            <div class="metric-value" style="color:{cor_score}">{sc}</div>
            <div class="metric-sub">{"🔥 Alto" if sc>30 else ("⚠️ Moderado" if sc>10 else "Baixo")}</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # GRÁFICO PRINCIPAL
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("", "", "RSI (14)")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="Preço",
        increasing_line_color="#26a69a", increasing_fillcolor="#26a69a",
        decreasing_line_color="#ef5350", decreasing_fillcolor="#ef5350",
    ), row=1, col=1)

    # Bollinger
    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=bb_sup, name="BB Superior",
            line=dict(color="#4a90d9", width=1, dash="dot"), opacity=0.7), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=bb_inf, name="BB Inferior",
            line=dict(color="#4a90d9", width=1, dash="dot"), opacity=0.7,
            fill="tonexty", fillcolor="rgba(74,144,217,0.05)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=bb_med, name="BB Médio",
            line=dict(color="#4a90d9", width=1), opacity=0.5), row=1, col=1)

    if show_mm20:
        fig.add_trace(go.Scatter(x=df.index, y=mm20, name="MM20",
            line=dict(color="#ffcc00", width=1.5), opacity=0.9), row=1, col=1)
    if show_mm50:
        fig.add_trace(go.Scatter(x=df.index, y=mm50, name="MM50",
            line=dict(color="#ff9900", width=1.5), opacity=0.9), row=1, col=1)
    if show_mm200:
        fig.add_trace(go.Scatter(x=df.index, y=mm200, name="MM200",
            line=dict(color="#ff4488", width=2), opacity=0.9), row=1, col=1)

    # Volume
    cores_vol = ["#ef5350" if df["Close"].iloc[i] < df["Open"].iloc[i] else "#26a69a"
                 for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=volume, name="Volume",
        marker_color=cores_vol, opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=vol_med, name="Vol.Médio",
        line=dict(color="#ffffff", width=1, dash="dot"), opacity=0.5), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI",
        line=dict(color="#a78bfa", width=2)), row=3, col=1)
    fig.add_hline(y=70, line_color="#ef5350", line_width=1, line_dash="dash", row=3, col=1)
    fig.add_hline(y=30, line_color="#26a69a", line_width=1, line_dash="dash", row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef5350", opacity=0.07, row=3, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#26a69a", opacity=0.07, row=3, col=1)

    fig.update_layout(
        height=650,
        paper_bgcolor="#0a0e17",
        plot_bgcolor="#0d1220",
        font=dict(color="#aabbcc", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    for i in range(1, 4):
        fig.update_yaxes(gridcolor="#1a2535", showgrid=True, row=i, col=1)
        fig.update_xaxes(gridcolor="#1a2535", showgrid=False, row=i, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # Sinais de alerta
    st.markdown("### 🚨 Análise de Sinais")
    alertas = []
    if rsi_atual > 75:
        alertas.append(("🔴 RSI CRÍTICO", f"RSI em {rsi_atual:.1f} — ativo extremamente sobrecomprado. Risco elevado de correção.", "short"))
    elif rsi_atual > 70:
        alertas.append(("🟠 RSI ALTO", f"RSI em {rsi_atual:.1f} — ativo sobrecomprado. Atenção para sinal de short.", "short"))
    if afas > 15:
        alertas.append(("🔴 MUITO ESTICADO", f"Preço {afas:.1f}% acima da MM200 — reversão à média provável.", "short"))
    elif afas > 8:
        alertas.append(("🟠 AFASTADO DA MÉDIA", f"Preço {afas:.1f}% acima da MM200 — monitorar.", "short"))
    if vol_ratio > 2:
        alertas.append(("🔴 VOLUME ANORMAL", f"Volume {vol_ratio:.1f}x acima da média — possível exaustão de compra.", "short"))
    if var_dia < -3:
        alertas.append(("🟢 QUEDA FORTE HOJE", f"Variação de {var_dia:.2f}% — movimento de baixa confirmado.", "neutro"))
    if not alertas:
        alertas.append(("⚪ SEM SINAIS", "Nenhuma condição de short identificada no momento.", "neutro"))

    for titulo, descricao, tipo in alertas:
        css = "signal-short" if tipo == "short" else "signal-neutro"
        st.markdown(f'<div class="{css}"><strong>{titulo}</strong> — {descricao}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# ABA 2 — RANKING
# ══════════════════════════════════════════════════════════════════════
with aba2:
    st.markdown("## 🏆 Ranking — Melhores Oportunidades de Short")
    st.caption("Calculado com base em RSI, afastamento da MM200 e volume anormal. Atualizado a cada 15 min.")

    with st.spinner("Analisando 25 ativos da B3... (pode levar ~30 segundos)"):
        df_rank = calcular_ranking()

    if df_rank.empty:
        st.warning("Não foi possível calcular o ranking. Tente novamente.")
    else:
        # Top 3 destaque
        top3 = df_rank.head(3)
        c1, c2, c3 = st.columns(3)
        for col, (_, row) in zip([c1, c2, c3], top3.iterrows()):
            cor = "#ff4444" if row["Score Short"] > 30 else "#ffaa00"
            with col:
                st.markdown(f'''<div class="metric-card">
                    <div class="metric-label">#{row.name} MELHOR SHORT</div>
                    <div class="metric-value" style="color:{cor};font-size:22px">{row["Ticker"]}</div>
                    <div class="metric-sub">{row["Nome"]}</div>
                    <div style="margin-top:8px;font-family:'Space Mono',monospace;font-size:12px;color:#aabbcc">
                        Score: <strong style="color:{cor}">{row["Score Short"]}</strong> &nbsp;|&nbsp;
                        RSI: <strong>{row["RSI"]}</strong> &nbsp;|&nbsp;
                        MM200: <strong>{row["Afas.MM200%"]:+.1f}%</strong>
                    </div>
                </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabela completa
        st.markdown("### 📋 Tabela Completa")
        df_display = df_rank.copy()
        df_display["Preço"] = df_display["Preço"].apply(lambda x: f"R$ {x:.2f}")
        df_display["Var%"] = df_display["Var%"].apply(lambda x: f"{x:+.2f}%")
        df_display["Afas.MM200%"] = df_display["Afas.MM200%"].apply(lambda x: f"{x:+.1f}%")

        st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            column_config={
                "Score Short": st.column_config.ProgressColumn(
                    "Score Short", min_value=0, max_value=100, format="%f"
                ),
                "RSI": st.column_config.NumberColumn("RSI", format="%.1f"),
            }
        )

        st.markdown("---")
        st.markdown("""
        **📖 Como ler o Ranking:**
        - **Score Short**: Pontuação de 0–100. Quanto maior, mais indicado para short.
        - **RSI > 70**: Ativo sobrecomprado — potencial de queda.
        - **Afas.MM200%**: Quanto o preço está acima da Média Móvel de 200 períodos. Valores altos indicam esticamento.
        - **Vol.Ratio**: Volume atual ÷ média de 20 dias. Acima de 1.5x é sinal de atenção.
        """)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚠️ Este dashboard é apenas para fins informativos e educacionais. Não constitui recomendação de investimento. Dados com delay de ~15 minutos via Yahoo Finance.")
