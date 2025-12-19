# ============================================================
#     STREAMLIT — ANALÍTICA MAQUINARIA / PROVIDENCIA IPSA
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64
import os


st.set_page_config(
    page_title="Panel de Maquinaria — Providencia",
    layout="wide",
    page_icon="🚜"
)

# ============================================================
# 1. ESTILOS Y COLORES CORPORATIVOS
# ============================================================

PRIMARY = "#1A7335"      # Verde caña
SECONDARY = "#F2C14E"    # Amarillo caña
ACCENT = "#3E92CC"       # Azul corporativo
GRAY = "#555555"
BG = "#FAFAFA"

st.markdown("""
<style>
/* Fondo general */
body {
    background-color: #F6F8F7;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1A7335;
}

/* Texto general del sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white !important;
}

/* === INPUTS DEL SIDEBAR (file uploader, selectbox, etc) === */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}

/* File uploader específico */
section[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 0.5rem;
}

/* Texto interno del file uploader */
section[data-testid="stSidebar"] div[data-testid="stFileUploader"] * {
    color: #000000 !important;
}

/* Cards */
.card {
    background-color: white;
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background-color: #E0E0E0;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. MAESTRO — FIJO EN EL SCRIPT
# ============================================================

MAESTRO_DATA = [
    ["939434-N", "6170J", "Tractor", "1BM6170JLRD650768", "Fertilización"],
    ["939435-N", "6170J", "Tractor", "1BM6170JPRD650762", "Fertilización"],
    ["939436-S", "6170J", "Tractor", "1BM6170JJRD650764", "Fertilización"],
    ["939437-S", "6170J", "Tractor", "1BM6170JCRD650765", "Fertilización"],
    ["939438-CN", "6170J", "Tractor", "1BM6170JARD650767", "Fertilización"],
    ["939439-O", "6170J", "Tractor", "1BM6170JHRD650769", "Fertilización"],

    ["939692-P", "7M 230", "Tractor", "1BM7230CHRH000277", "Preparación"],
    ["938556-P", "8320R", "Tractor", "1BM8320RHPS100735", "Preparación"],
    ["938557-P", "8320R", "Tractor", "1BM8320REPS100736", "Preparación"],
    ["939471-P", "8320R", "Tractor", "1BM8320RJRS100858", "Preparación"],
    ["939472-P", "8320R", "Tractor", "1BM8320RKRS100857", "Preparación"],
    ["939473-P", "8320R", "Tractor", "1BM8320RCRS100859", "Preparación"],

    ["T939131-SI", "6170J", "Tractor", "1BM6170JHPD650493", "Siembra"],
    ["T939132-SI", "6170J", "Tractor", "1BM6170JVPD650490", "Siembra"],
    ["938555-SI",  "7230J", "Tractor", "1BM7230JCPH009888", "Siembra"],

    ["T937293-CV", "6170J", "Tractor", "1BM6170JHND600108", "Vinaza"],
    ["T939134-CV", "6170J", "Tractor", "1BM6170JAPD650491", "Vinaza"]
]

MAESTRO = pd.DataFrame(MAESTRO_DATA, columns=[
    "Máquina", "Modelo", "Tipo", "Número de serie de la máquina", "Grupo_trabajo"
])

# ============================================================
# 3. METAS POR GRUPO
# ============================================================

METAS = {
    "Fertilización": {"func": 77, "ralenti": 13, "escala": 12},
    "Preparación":   {"func": 82, "ralenti": 12, "escala": 4.5},
    "Siembra":       {"func": 72, "ralenti": 15, "escala": 17},
    "Vinaza":        {"func": 73, "ralenti": 20, "escala": 10},
}

# ============================================================
# 4. CACHE DE ARCHIVOS
# ============================================================

@st.cache_data
def cargar_excel(file):
    return pd.read_excel(file)

@st.cache_data
def unir_maestro(df):
    return df.merge(MAESTRO, on="Máquina", how="left")

# ============================================================
# 5. PROCESAMIENTO DIARIO
# ============================================================

def preparar_diario(df, escala):
    df_pct = df[[
        "Máquina", "Grupo_trabajo",
        "Utilización En funcionamiento (%)",
        "Utilización Transporte (%)",
        "Utilización Ralentí (%)"
    ]].copy()

    df_pct.columns = ["Máquina", "Grupo_trabajo", "Funcionamiento", "Transporte", "Ralenti"]
    df_pct = df_pct.melt(id_vars=["Máquina", "Grupo_trabajo"], var_name="Tipo", value_name="Porcentaje")
    df_pct["Porcentaje"] *= 100

    df_h = df[[
        "Máquina", "Grupo_trabajo",
        "Utilización En funcionamiento (h)",
        "Utilización Transporte (h)",
        "Utilización Ralentí (h)",
        "Horas de trabajo del motor Período (h)"
    ]].copy()

    df_h.columns = ["Máquina", "Grupo_trabajo", "Funcionamiento", "Transporte", "Ralenti", "Horas_Motor"]
    df_horas = df_h.melt(id_vars=["Máquina", "Grupo_trabajo"], var_name="TipoHora", value_name="Horas")
    df_horas["HorasEscaladas"] = df_horas["Horas"] * escala

    return df_pct, df_horas

def preparar_promedio_semanal(df_long, grupo):
    """
    Promedio semanal por Máquina y Tipo
    """
    df_g = df_long[df_long["Grupo_trabajo"] == grupo]

    prom = (
        df_g
        .groupby(["Máquina", "Tipo"])
        .agg(prom_semana=("Porcentaje", "mean"))
        .reset_index()
    )

    return prom


import plotly.graph_objects as go

def grafico_diario(df_pct, df_horas, df_long_semanal, grupo, meta_func, meta_ralenti):

    # ===== COLORES =====
    COLOR_FUNC = "#32CD32"
    COLOR_TRANS = "#A6A6A6"
    COLOR_RALENTI = "#FF8C00"
    COLOR_META_F = "#006400"
    COLOR_META_R = "#CC5500"

    COLOR_PFUNC = "#037403"
    COLOR_PRAL = "#613703"
    COLOR_PTRAS = "#777777"

    COLOR_FUNC_WEEK = "rgba(50,205,50,0.35)"
    COLOR_RAL_WEEK  = "rgba(255,140,0,0.35)"
    COLOR_TRANS_WEEK= "rgba(166,166,166,0.35)"

    # ===== FILTRAR GRUPO =====
    dfp = df_pct[df_pct["Grupo_trabajo"] == grupo].copy()
    dfh = df_horas[df_horas["Grupo_trabajo"] == grupo].copy()

    # ===== EJE X NUMÉRICO =====
    maquinas = list(dfp["Máquina"].unique())
    x_index = {m: i for i, m in enumerate(maquinas)}

    OFFSET = {
        "Funcionamiento": -0.25,
        "Ralenti": 0.0,
        "Transporte": 0.25
    }

    COLORS_BAR = {
        "Funcionamiento": COLOR_FUNC,
        "Ralenti": COLOR_RALENTI,
        "Transporte": COLOR_TRANS
    }

    COLORS_PT = {
        "Funcionamiento": COLOR_PFUNC,
        "Ralenti": COLOR_PRAL,
        "Transporte": COLOR_PTRAS
    }

    fig = go.Figure()

    # ======================================================
    # 0. BARRAS PROMEDIO SEMANAL (FONDO)
    # ======================================================
    df_week = preparar_promedio_semanal(df_long_semanal, grupo)

    for tipo in ["Funcionamiento", "Ralenti", "Transporte"]:
        d = df_week[df_week["Tipo"] == tipo].copy()
        d["x_num"] = d["Máquina"].map(x_index) + OFFSET[tipo]

        fig.add_trace(go.Bar(
            x=d["x_num"],
            y=d["prom_semana"],
            marker_color=COLORS_BAR[tipo],
            opacity=0.50,
            width=0.38,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=d["x_num"] + 0.06,
            y=d["prom_semana"],
            mode="text",
            text=d["prom_semana"].round(0),
            textfont=dict(color="#444444", size=8),
            showlegend=False,
            hoverinfo="skip"
        ))

    # ======================================================
    # 1. BARRAS DIARIAS (%)
    # ======================================================
    for tipo in ["Funcionamiento", "Ralenti", "Transporte"]:
        d = dfp[dfp["Tipo"] == tipo].copy()
        d["x_num"] = d["Máquina"].map(x_index) + OFFSET[tipo]

        fig.add_trace(go.Bar(
            x=d["x_num"],
            y=d["Porcentaje"],
            marker_color=COLORS_BAR[tipo],
            text=d["Porcentaje"].round(0),
            textposition="outside",
            textfont=dict(color="black"),
            width=0.22,
            name=tipo
        ))

    # ======================================================
    # 2. PUNTOS DE HORAS (EJE SECUNDARIO)
    # ======================================================
    for tipo in ["Funcionamiento", "Ralenti", "Transporte"]:
        dh = dfh[dfh["TipoHora"] == tipo].copy()
        dh["x_num"] = dh["Máquina"].map(x_index) + OFFSET[tipo]

        fig.add_trace(go.Scatter(
            x=dh["x_num"],
            y=dh["Horas"],
            yaxis="y2",
            mode="markers+text",
            text=dh["Horas"].round(1),
            textposition="bottom center",
            textfont=dict(color="black"),   
            marker=dict(
                size=6,
                color=COLORS_PT[tipo],
                line=dict(color="black", width=0.5)
            ),
            showlegend=False
        ))

    # ======================================================
    # 3. HORAS MOTOR (EJE SECUNDARIO)
    # ======================================================
    hm = dfh[dfh["TipoHora"] == "Horas_Motor"].copy()
    hm["x_num"] = hm["Máquina"].map(x_index)

    fig.add_trace(go.Scatter(
        x=hm["x_num"],
        y=hm["Horas"],
        yaxis="y2",
        mode="markers+text",
        text=hm["Horas"].round(1),
        textposition="top center",
        marker=dict(color="red", size=13),
        textfont=dict(color="red"),
        name="Horas motor"
    ))

    # ======================================================
    # 4. LÍNEAS DE META (%)
    # ======================================================
    xmin = min(x_index.values()) - 0.6
    xmax = max(x_index.values()) + 0.6

    fig.add_trace(go.Scatter(
        x=[xmin, xmax],
        y=[meta_func, meta_func],
        mode="lines+text",
        line=dict(color=COLOR_META_F, dash="dash", width=2),
        text=[None, f"{meta_func}%"],
        textposition="middle right",
        name="Meta funcionamiento"
    ))

    fig.add_trace(go.Scatter(
        x=[xmin, xmax],
        y=[meta_ralenti, meta_ralenti],
        mode="lines+text",
        line=dict(color=COLOR_META_R, dash="dash", width=2),
        text=[None, f"{meta_ralenti}%"],
        textposition="middle right",
        name="Meta ralentí"
    ))

    # ======================================================
    # 5. LAYOUT (EJE SECUNDARIO)
    # ======================================================
    fig.update_layout(
        height=650,
        template="simple_white",
        barmode="overlay",
        title=f"Tiempos de operación diario — {grupo}",

        yaxis=dict(
            title="% Tiempo",
            range=[0, 100]
        ),

        yaxis2=dict(
            title="Horas",
            linecolor="red", 
            tickcolor="red",    
            overlaying="y",
            side="right",
            range=[0, dfh["Horas"].max() * 1.15],  # ← empieza en 0
            showgrid=False
        ),


        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=50, r=60, t=80, b=120)
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=list(x_index.values()),
        ticktext=maquinas,
        title_text="Máquina"
    )

    # ======================================================
    # LEYENDA PROMEDIO SEMANAL
    # ======================================================
    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color=COLOR_FUNC_WEEK,
        name="Funcionamiento · Promedio semanal"
    ))

    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color=COLOR_RAL_WEEK,
        name="Ralentí · Promedio semanal"
    ))

    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color=COLOR_TRANS_WEEK,
        name="Transporte · Promedio semanal"
    ))

    return fig


def insights_diarios(df_pct, grupo, meta_f, meta_r):
    insights = []

    df_g = df_pct[df_pct["Grupo_trabajo"] == grupo].copy()

    # ======================================================
    # 1. RESUMEN EJECUTIVO DEL GRUPO (BREVE)
    # ======================================================
    resumen_grp = (
        df_g
        .groupby("Tipo")["Porcentaje"]
        .mean()
        .to_dict()
    )

    pf = resumen_grp.get("Funcionamiento", 0)
    pr = resumen_grp.get("Ralenti", 0)

    if pf < meta_f - 8 or pr > meta_r + 6:
        estado = "🔴 Riesgo operativo alto"
    elif pf < meta_f or pr > meta_r:
        estado = "🟡 Riesgo operativo moderado"
    else:
        estado = "🟢 Operación bajo control"

    insights.append(
        f"{estado} — Promedio grupo: Funcionamiento {pf:.1f}% | Ralentí {pr:.1f}%."
    )

    # ======================================================
    # 2. DIAGNÓSTICO POR MÁQUINA
    # ======================================================
    df_maquina = (
        df_g
        .groupby(["Máquina", "Tipo"])["Porcentaje"]
        .mean()
        .unstack()
        .reset_index()
    )

    # Asegurar columnas
    for col in ["Funcionamiento", "Ralenti", "Transporte"]:
        if col not in df_maquina.columns:
            df_maquina[col] = 0

    # ======================================================
    # 3. SEMÁFORO Y DESVIACIÓN POR MÁQUINA
    # ======================================================
    diagnosticos = []

    for _, row in df_maquina.iterrows():
        maq = row["Máquina"]
        f = row["Funcionamiento"]
        r = row["Ralenti"]

        # Semáforo por máquina
        if f < meta_f - 8 or r > meta_r + 6:
            sem = "🔴"
            nivel = "Crítica"
        elif f < meta_f or r > meta_r:
            sem = "🟡"
            nivel = "En observación"
        else:
            sem = "🟢"
            nivel = "Estable"

        impacto = (meta_f - f) + max(0, r - meta_r)

        diagnosticos.append({
            "Máquina": maq,
            "Funcionamiento": f,
            "Ralenti": r,
            "Semáforo": sem,
            "Nivel": nivel,
            "Impacto": impacto
        })

    df_diag = pd.DataFrame(diagnosticos)

    # ======================================================
    # 4. RANKING DE MÁQUINAS (TOP CRÍTICAS)
    # ======================================================
    df_crit = (
        df_diag
        .sort_values("Impacto", ascending=False)
        .head(4)
    )

    if not df_crit.empty:
        insights.append("🚜 Diagnóstico por máquina (prioridad):")

        for _, r in df_crit.iterrows():
            insights.append(
                f"{r['Semáforo']} {r['Máquina']} — "
                f"Func {r['Funcionamiento']:.1f}% | "
                f"Ral {r['Ralenti']:.1f}% "
                f"→ {r['Nivel']}"
            )
    else:
        insights.append("🚜 Todas las máquinas operan dentro de parámetros esperados.")

    # ======================================================
    # 5. ACCIÓN OPERATIVA CONCRETA
    # ======================================================
    if estado.startswith("🔴"):
        cierre = (
            "🎯 Acción inmediata: intervenir máquinas críticas con bajo funcionamiento "
            "y alto ralentí. Revisar causas de tiempos muertos y coordinación operativa."
        )
    elif estado.startswith("🟡"):
        cierre = (
            "🎯 Acción recomendada: seguimiento diario por máquina en observación "
            "para evitar escalamiento del riesgo."
        )
    else:
        cierre = (
            "🎯 Acción recomendada: mantener condiciones operativas actuales y control rutinario."
        )

    insights.append(cierre)

    return insights


def exportar_reporte_png(fig, insights, grupo, nombre="reporte_maquinaria.png"):
    """
    Genera un PNG ejecutivo con:
    - gráfico (Plotly) a la izquierda
    - panel insights a la derecha
    Usando base64 para evitar que el gráfico salga roto.
    """

    # 1) Render del gráfico Plotly a PNG (tamaño fijo para evitar cortes)
    tmp_png = f"grafico_{grupo}.png".replace(" ", "_").replace("/", "_")
    fig.write_image(tmp_png, width=1200, height=700, scale=2)  # clave: size fijo

    # 2) Convertir imagen a base64 (evita rutas rotas en html2image)
    with open(tmp_png, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    # 3) HTML del reporte (con imagen embebida)
    texto_html = "<br>".join(insights)

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{
        font-family: Arial, sans-serif;
        background: white;
        margin: 0;
        padding: 24px;
      }}
      .container {{
        display: flex;
        gap: 24px;
        align-items: flex-start;
      }}
      .left {{
        width: 70%;
      }}
      .right {{
        width: 30%;
        background-color: #F8F9F7;
        border: 3px solid #1A7335;
        border-radius: 16px;
        padding: 18px;
        box-sizing: border-box;
      }}
      .title {{
        color: #1A7335;
        margin: 0 0 6px 0;
        font-size: 18px;
        font-weight: 700;
      }}
      .subtitle {{
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 700;
        color: #000;
      }}
      .ins {{
        font-size: 13px;
        line-height: 1.6;
        color: #000;
      }}
      img {{
        width: 100%;
        height: auto;
        display: block;
      }}
    </style>
    </head>
    <body>
      <div class="container">
        <div class="left">
          <img src="data:image/png;base64,{img_b64}" />
        </div>
        <div class="right">
          <div class="title">🧭 Diagnóstico Operativo</div>
          <div class="subtitle">{grupo}</div>
          <div class="ins">{texto_html}</div>
        </div>
      </div>
    </body>
    </html>
    """

    # 4) HTML -> PNG
    hti = Html2Image(output_path=".")
    hti.screenshot(
        html_str=html,
        save_as=nombre,
        size=(1800, 950)   # canvas del reporte
    )

    # 5) Limpieza del temporal
    try:
        os.remove(tmp_png)
    except Exception:
        pass

    return nombre

# ============================================================
# 6. SEMANAL
# ============================================================

def preparar_semanal(df):
    df["Fecha"] = pd.to_datetime(df["Fecha de inicio"], errors="coerce")
    df["Semana"] = df["Fecha"].dt.isocalendar().week

    df_pct = df[[
        "Máquina", "Semana", "Grupo_trabajo",
        "Utilización En funcionamiento (%)",
        "Utilización Transporte (%)",
        "Utilización Ralentí (%)"
    ]].copy()

    df_pct.columns = ["Máquina", "Semana", "Grupo_trabajo", "Funcionamiento", "Transporte", "Ralenti"]
    df_long = df_pct.melt(id_vars=["Máquina", "Semana", "Grupo_trabajo"], var_name="Tipo", value_name="Porcentaje")
    df_long["Porcentaje"] *= 100

    return df_long

def boxplot_semanal(df_long, grupo):
    df_g = df_long[df_long["Grupo_trabajo"] == grupo]

    fig = px.box(
        df_g,
        x="Tipo",
        y="Porcentaje",
        color="Semana",
        title=f"📦 Comportamiento semanal — {grupo}",
        color_discrete_sequence=px.colors.qualitative.Set2,
        points="all"
    )

    fig.update_layout(height=550, template="simple_white")

    return fig


def insights_semanales(df_long, grupo):
    df_g = df_long[df_long["Grupo_trabajo"] == grupo]
    semanas = sorted(df_g["Semana"].unique())

    if len(semanas) < 2:
        return ["⚠ Solo hay datos de una semana."]

    w1, w2 = semanas[-2], semanas[-1]
    txt = [f"📅 Comparación Semana {w1} → Semana {w2}"]

    for tipo in ["Funcionamiento", "Ralenti", "Transporte"]:
        prev = df_g[(df_g["Semana"]==w1)&(df_g["Tipo"]==tipo)]["Porcentaje"].mean()
        curr = df_g[(df_g["Semana"]==w2)&(df_g["Tipo"]==tipo)]["Porcentaje"].mean()

        if curr > prev:
            txt.append(f"📈 {tipo}: aumentó {curr-prev:.1f}%")
        else:
            txt.append(f"📉 {tipo}: disminuyó {prev-curr:.1f}%")

    return txt



# ============================================================
# 7. UI — STREAMLIT
# ============================================================

st.sidebar.title("🚜 Panel de Maquinaria")
menu = "Reporte Completo"


st.title("📊 Seguimiento diario de la maquinaria — Ingenio Providencia")

#st.markdown("<hr>", unsafe_allow_html=True)

# ------------------------------------------------------------
# REPORTE DIARIO
# ------------------------------------------------------------

#st.subheader("Seguimiento diario de la maquinaria")

st.sidebar.header("📂 Cargue de Información")

archivo_diario = st.sidebar.file_uploader(
    "📅 Archivo diario (Operation Center)",
    type=["xlsx"],
    key="diario"
)

archivo_semanal = st.sidebar.file_uploader(
    "📆 Archivo semanal (Operation Center)",
    type=["xlsx"],
    key="semanal"
)

if archivo_diario and archivo_semanal:

    # === CARGA Y PREPARACIÓN ===
    df_d = cargar_excel(archivo_diario)
    df_d = unir_maestro(df_d)

    df_s = cargar_excel(archivo_semanal)
    df_s = unir_maestro(df_s)
    df_long = preparar_semanal(df_s)

    grupos = sorted(df_d["Grupo_trabajo"].dropna().unique())

    st.markdown("---")

    for grupo in grupos:
        #st.markdown(f"## 🔷 {grupo}")

        metas = METAS[grupo]

        # === DIARIO ===
        df_pct, df_h = preparar_diario(df_d, metas["escala"])
        fig_diario = grafico_diario(
            df_pct,
            df_h,
            df_long,          # ← data semanal
            grupo,
            metas["func"],
            metas["ralenti"]
        )


        #st.markdown("<div class='card'>", unsafe_allow_html=True)

        
        #st.plotly_chart(fig_diario, use_container_width=True)
        # ✅ AQUÍ SE DEFINE insights (antes de usarlo en el HTML)
        insights = insights_diarios(df_pct, grupo, metas["func"], metas["ralenti"])
        # === LAYOUT TIPO LÁMINA ===
        col_graf, col_txt = st.columns([0.7, 0.3], gap="large")

        with col_graf:
            #st.markdown("### 📊 Desempeño Diario")
            st.plotly_chart(fig_diario, use_container_width=True)

        import streamlit.components.v1 as components

        with col_txt:

            resumen = insights[0]
            diagnostico = insights[1:-1]
            accion = insights[-1]

            html = f"""
            <div style="
                background-color:#F8F9F7;
                border:3px solid #1A7335;
                border-radius:16px;
                padding:22px;
                font-family: Arial, sans-serif;
                box-sizing: border-box;
            ">

                <!-- TÍTULO -->
                <div style="
                    color:#1A7335;
                    font-size:18px;
                    font-weight:700;
                    margin-bottom:4px;
                ">
                    🧭 Diagnóstico Operativo
                </div>

                <!-- GRUPO (MÁS GRANDE) -->
                <div style="
                    font-size:22px;
                    font-weight:800;
                    margin-bottom:14px;
                    color:#000;
                ">
                    {grupo}
                </div>

                <!-- RESUMEN -->
                <div style="
                    font-size:13px;
                    line-height:1.6;
                    margin-bottom:14px;
                ">
                    {resumen}
                </div>

                <hr style="border:none; border-top:1px solid #C7D8CC; margin:14px 0;">

                <!-- DIAGNÓSTICO POR MÁQUINA -->
                <div style="
                    font-size:13px;
                    line-height:1.6;
                    margin-bottom:14px;
                ">
                    {"<br>".join(diagnostico)}
                </div>

                <hr style="border:none; border-top:1px solid #C7D8CC; margin:14px 0;">

                <!-- ACCIÓN -->
                <div style="
                    font-size:13px;
                    line-height:1.6;
                    font-weight:600;
                ">
                    {accion}
                </div>

            </div>
            """

            components.html(html, height=600)



        st.markdown("</div>", unsafe_allow_html=True)



        # === INSIGHTS ===
        #st.markdown("### 📌 Insights del Día")
        #for ins in insights_diarios(df_pct, grupo, metas["func"], metas["ralenti"]):
        #    st.write(ins)
                
     
        st.markdown("---")


#C:\Users\sacorreac\Downloads\.venv\Scripts\streamlit.exe run C:\Users\sacorreac\Downloads\archivo_maquina\maquinaria.py

