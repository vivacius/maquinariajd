import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================================
# 1. MAESTRO FIJO DE EQUIPOS
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
    ["938555-SI", "7230J", "Tractor", "1BM7230JCPH009888", "Siembra"],

    ["T937293-CV", "6170J", "Tractor", "1BM6170JHND600108", "Vinaza"],
    ["T939134-CV", "6170J", "Tractor", "1BM6170JAPD650491", "Vinaza"]
]

MAESTRO = pd.DataFrame(MAESTRO_DATA, columns=[
    "Máquina", "Modelo", "Tipo", "Número de serie de la máquina", "Grupo_trabajo"
])

# ============================================================
# 2. METAS POR GRUPO
# ============================================================

METAS = {
    "Fertilización": {"func": 77, "ralenti": 13, "escala": 12},
    "Preparación":   {"func": 82, "ralenti": 12, "escala": 4.5},
    "Siembra":       {"func": 72, "ralenti": 15, "escala": 17},
    "Vinaza":        {"func": 73, "ralenti": 20, "escala": 10},
}

# ============================================================
# 3. FUNCIONES DE PROCESAMIENTO DIARIO
# ============================================================

def preparar_datos_diarios(df, escala):
    df_pct = df[[
        "Máquina",
        "Utilización En funcionamiento (%)",
        "Utilización Transporte (%)",
        "Utilización Ralentí (%)",
        "Grupo_trabajo"
    ]].copy()

    df_pct = df_pct.rename(columns={
        "Utilización En funcionamiento (%)": "Funcionamiento",
        "Utilización Transporte (%)": "Transporte",
        "Utilización Ralentí (%)": "Ralenti"
    })

    df_pct = df_pct.melt(
        id_vars=["Máquina", "Grupo_trabajo"],
        value_vars=["Funcionamiento", "Transporte", "Ralenti"],
        var_name="Tipo",
        value_name="Porcentaje"
    )

    df_pct["Porcentaje"] = df_pct["Porcentaje"] * 100

    df_horas = df[[
        "Máquina",
        "Utilización En funcionamiento (h)",
        "Utilización Transporte (h)",
        "Utilización Ralentí (h)",
        "Horas de trabajo del motor Período (h)",
        "Grupo_trabajo"
    ]].copy()

    df_horas = df_horas.rename(columns={
        "Utilización En funcionamiento (h)": "Funcionamiento",
        "Utilización Transporte (h)": "Transporte",
        "Utilización Ralentí (h)": "Ralenti",
        "Horas de trabajo del motor Período (h)": "Horas_Motor"
    })

    df_horas = df_horas.melt(
        id_vars=["Máquina", "Grupo_trabajo"],
        value_vars=["Funcionamiento", "Transporte", "Ralenti", "Horas_Motor"],
        var_name="TipoHora",
        value_name="Horas"
    )

    df_horas["HorasEscaladas"] = df_horas["Horas"] * escala

    return df_pct, df_horas


def grafico_diario(df_pct, df_horas, grupo, meta_func, meta_ralenti, escala):
    dfp = df_pct[df_pct["Grupo_trabajo"] == grupo]
    dfh = df_horas[df_horas["Grupo_trabajo"] == grupo]

    fig = go.Figure()

    colores = {
        "Funcionamiento": "#32CD32",
        "Transporte": "#888888",
        "Ralenti": "#FF6F00"
    }

    for tipo in colores.keys():
        datos = dfp[dfp["Tipo"] == tipo]
        fig.add_trace(go.Bar(
            x=datos["Máquina"],
            y=datos["Porcentaje"],
            name=tipo,
            marker_color=colores[tipo],
            text=datos["Porcentaje"].round(0),
            textposition="outside"
        ))

    for tipo in ["Funcionamiento", "Transporte", "Ralenti"]:
        d = dfh[dfh["TipoHora"] == tipo]
        fig.add_trace(go.Scatter(
            x=d["Máquina"], y=d["HorasEscaladas"],
            mode="markers+text",
            text=d["Horas"].round(1),
            textposition="top center",
            name=f"{tipo} (h)"
        ))

    hm = dfh[dfh["TipoHora"] == "Horas_Motor"]
    fig.add_trace(go.Scatter(
        x=hm["Máquina"], y=hm["HorasEscaladas"],
        mode="markers+text",
        marker_color="red",
        marker_size=12,
        text=hm["Horas"].round(1),
        textposition="bottom center",
        name="Horas Motor"
    ))

    fig.add_hline(y=meta_func, line_dash="dash", line_color="green")
    fig.add_hline(y=meta_ralenti, line_dash="dash", line_color="orange")

    fig.update_layout(
        title=f"Tiempos de operación — {grupo}",
        barmode="group",
        height=600,
        template="simple_white"
    )

    return fig


def insights_diarios(df_pct, grupo, meta_func, meta_ralenti):
    insights = []
    df_g = df_pct[df_pct["Grupo_trabajo"] == grupo]

    prom_func = df_g[df_g["Tipo"]=="Funcionamiento"]["Porcentaje"].mean()
    prom_ral = df_g[df_g["Tipo"]=="Ralenti"]["Porcentaje"].mean()

    if prom_func < meta_func - 10:
        insights.append(f"⚠️ Funcionamiento muy bajo: {prom_func:.1f}% (meta {meta_func}%).")
    elif prom_func < meta_func:
        insights.append(f"🔍 Funcionamiento ligeramente bajo: {prom_func:.1f}% < {meta_func}.")
    else:
        insights.append(f"✅ Funcionamiento superior: {prom_func:.1f}%.")

    if prom_ral > meta_ralenti + 5:
        insights.append(f"🚨 Ralentí crítico: {prom_ral:.1f}% (meta {meta_ralenti}%).")
    elif prom_ral > meta_ralenti:
        insights.append(f"⚠️ Ralentí alto: {prom_ral:.1f}%")
    else:
        insights.append(f"👍 Ralentí dentro del objetivo ({prom_ral:.1f}%).")

    return insights

# ============================================================
# 4. FUNCIONES DE PROCESAMIENTO SEMANAL
# ============================================================


def preparar_datos_semanales(df):
    df["Fecha"] = pd.to_datetime(df["Fecha de inicio"], errors="coerce")
    df["Semana"] = df["Fecha"].dt.isocalendar().week

    df_pct = df[[
        "Máquina",
        "Semana",
        "Utilización En funcionamiento (%)",
        "Utilización Transporte (%)",
        "Utilización Ralentí (%)",
        "Grupo_trabajo"
    ]].copy()

    df_pct = df_pct.rename(columns={
        "Utilización En funcionamiento (%)": "Funcionamiento",
        "Utilización Transporte (%)": "Transporte",
        "Utilización Ralentí (%)": "Ralenti",
    })

    df_long = df_pct.melt(
        id_vars=["Máquina", "Semana", "Grupo_trabajo"],
        value_vars=["Funcionamiento", "Transporte", "Ralenti"],
        var_name="Tipo",
        value_name="Porcentaje"
    )

    df_long["Porcentaje"] *= 100
    return df_long


def boxplot_semanal(df_long, grupo):
    df_g = df_long[df_long["Grupo_trabajo"] == grupo]

    fig = px.box(
        df_g,
        x="Tipo",
        y="Porcentaje",
        color="Semana",
        title=f"Comparación semanal — {grupo}",
        color_discrete_sequence=px.colors.qualitative.Set2,
        points="all"
    )

    fig.update_layout(height=600, template="simple_white")
    return fig


def insights_semanales(df_long, grupo):
    df_g = df_long[df_long["Grupo_trabajo"] == grupo]

    semanas = sorted(df_g["Semana"].dropna().unique())
    if len(semanas) < 2:
        return ["⚠️ Solo hay datos de una semana. No se puede comparar."]

    w1, w2 = semanas[-2], semanas[-1]

    insights = [f"📅 Comparando semana {w1} vs {w2}"]

    for tipo in ["Funcionamiento", "Ralenti", "Transporte"]:
        prev = df_g[(df_g["Semana"] == w1) & (df_g["Tipo"] == tipo)]["Porcentaje"].mean()
        curr = df_g[(df_g["Semana"] == w2) & (df_g["Tipo"] == tipo)]["Porcentaje"].mean()

        if pd.isna(prev) or pd.isna(curr):
            continue
        
        diff = curr - prev

        if tipo == "Funcionamiento":
            if diff > 0:
                insights.append(f"📈 Funcionamiento mejoró **{diff:.1f}%**.")
            else:
                insights.append(f"📉 Funcionamiento cayó **{abs(diff):.1f}%**.")

        if tipo == "Ralenti":
            if diff > 0:
                insights.append(f"🚨 Ralentí aumentó **{diff:.1f}%** (peor).")
            else:
                insights.append(f"👍 Ralentí mejoró **{abs(diff):.1f}%**.")

    # Outliers
    q1 = df_g["Porcentaje"].quantile(0.25)
    q3 = df_g["Porcentaje"].quantile(0.75)
    iqr = q3 - q1
    limite = q3 + 1.5 * iqr

    outliers = df_g[df_g["Porcentaje"] > limite]["Máquina"].unique()

    if len(outliers) > 0:
        insights.append(f"🔎 Outliers detectados: {', '.join(outliers)}")
    else:
        insights.append("✔ Sin outliers significativos.")

    return insights
# ============================================================
# 5. INTERFAZ STREAMLIT COMPLETA
# ============================================================

st.sidebar.title("📊 Panel de Maquinaria")
menu = st.sidebar.radio("Selecciona un reporte", ["Reporte Diario", "Reporte Semanal"])

st.title("🚜 Análisis de Maquinaria — Ingenio Providencia")


# ------------------------------------------------------------
# 📌 REPORTE DIARIO
# ------------------------------------------------------------
if menu == "Reporte Diario":

    st.subheader("📅 Reporte Diario — Archivo del día")
    archivo = st.file_uploader("Cargar archivo XLSX del día", type=["xlsx"])

    if archivo:
        df_oc = pd.read_excel(archivo)

        df = df_oc.merge(MAESTRO, on="Máquina", how="left")
        grupos = df["Grupo_trabajo"].dropna().unique()

        st.success(f"Grupos detectados: {', '.join(grupos)}")

        for grupo in grupos:
            metas = METAS[grupo]

            st.markdown(f"## 🔷 {grupo}")

            df_pct, df_horas = preparar_datos_diarios(df, metas["escala"])

            fig = grafico_diario(df_pct, df_horas, grupo, metas["func"], metas["ralenti"], metas["escala"])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📌 Insights del día")
            insights = insights_diarios(df_pct, grupo, metas["func"], metas["ralenti"])
            for i in insights:
                st.write(i)



# ------------------------------------------------------------
# 📌 REPORTE SEMANAL
# ------------------------------------------------------------
if menu == "Reporte Semanal":

    st.subheader("📅 Reporte Semanal — Múltiples días")
    archivo = st.file_uploader("Cargar archivo semanal (XLSX)", type=["xlsx"])

    if archivo:
        df_oc = pd.read_excel(archivo)
        df = df_oc.merge(MAESTRO, on="Máquina", how="left")

        df_long = preparar_datos_semanales(df)
        grupos = df_long["Grupo_trabajo"].dropna().unique()

        for grupo in grupos:
            st.markdown(f"## 🔷 {grupo}")

            fig = boxplot_semanal(df_long, grupo)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📌 Insights semanales")
            insights = insights_semanales(df_long, grupo)
            for i in insights:
                st.write(i)

