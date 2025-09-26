import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.api import VAR
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import streamlit.components.v1 as components
import plotly.express as px
from bumplot import bumplot
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap


st.set_page_config( page_title="Análisis Inflación 2017-2025",layout="wide")


# Ocultar el sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Texto en color mostaza */
    html, body, [class*="css"], .stText, .stMarkdown, .stSelectbox, .stRadio, .stCheckbox, .stButton,
    .stMetricValue, .stMetricLabel, .stExpander, .stPlotlyChart, .stDataFrame, .stTable, .stTextInput {
        color: #d4a017 !important;
    }

    /* Fondos en gris oscuro */
    .stApp, .block-container, .stExpander, .stDataFrame, .stTable, .stMetric, .stPlotlyChart, .stButton > button {
        background-color: #1e1e1e !important;
    }

    /* Ajuste especial para inputs, selects, radios */
    .stSelectbox div, .stRadio div, .stTextInput input {
        background-color: #2b2b2b !important;
        color: #d4a017 !important;
    }

    /* Borde sutil para diferenciar */
    .stDataFrame, .stTable {
        border: 1px solid #444 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title(":material/currency_exchange: Dashboard Argentina Variación IPC mensual (2017-2025)")

with st.expander("Inflación Análisis y Modelos Predictivos",  expanded=False, icon=":material/monitoring:", width="stretch"):
    # --- ESTILOS ---
    chartCategoricalColors = st.get_option("theme.chartCategoricalColors")
    secondaryBackgroundColor = st.get_option("theme.secondaryBackgroundColor")
    textColor = st.get_option("theme.textColor")

    st.write('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)
    st.markdown("""
    <style>
        .stMetric, .stMetric svg {
            background-color: #FCF9F3!important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- FUNCIONES ---
    @st.cache_data
    def cargarDatos():
        df = pd.read_excel("data/ipc-09-25.xlsx")
        df = df.rename(columns=lambda x: x.strip())
        df['meses'] = pd.to_datetime(df['meses'], format='%b-%y')

        nivel_general = [
            "Alimentos y bebidas no alcohólicas", "Bebidas alcohólicas y tabaco",
            "Prendas de vestir y calzado", "Vivienda, agua, electricidad, gas y otros combustibles",
            "Equipamiento y mantenimiento del hogar", "Salud", "Transporte", "Comunicación",
            "Recreación y cultura", "Educación", "Restaurantes y hoteles", "Bienes y servicios varios"
        ]
        
        categorias = ["Estacional", "Núcleo", "Regulados"]
        bienes_servicios = ["Bienes", "Servicios"]

        id_vars = ['meses', 'regiones']

        dfNivel = df.melt(id_vars=id_vars, value_vars=nivel_general, var_name='Subrubro', value_name='Valor')
        dfNivel['Rubro'] = 'Nivel general'

        dfCat = df.melt(id_vars=id_vars, value_vars=categorias, var_name='Subrubro', value_name='Valor')
        dfCat['Rubro'] = 'Categorías'

        dfBienServ = df.melt(id_vars=id_vars, value_vars=bienes_servicios, var_name='Subrubro', value_name='Valor')
        dfBienServ['Rubro'] = 'Bienes y servicios'

        dfFinal = pd.concat([dfNivel, dfCat, dfBienServ], axis=0)
        dfFinal['Mes'] = dfFinal['meses'].dt.month
        dfFinal['Año'] = dfFinal['meses'].dt.year
        dfFinal['NombreMes'] = dfFinal['meses'].dt.month_name(locale='es_ES')
        dfFinal['MesNum'] = dfFinal['meses'].dt.strftime('%Y-%m')

        return dfFinal

    def aplicarBackgroundChart(fig, color):
        return fig.update_layout({
            "plot_bgcolor": color,
            "paper_bgcolor": color,
        })

    def generarMetrica(df, titulo):
        ultimo = df.iloc[-1]["Valor"]
        anterior = df.iloc[-2]["Valor"]
        variacion = (ultimo - anterior) / anterior
        st.metric(label=titulo, value=f"{ultimo:.1f}%", delta=f"{variacion:.2%}")

    # --- CARGA DE DATOS ---
    dfDatos = cargarDatos()

    # --- FILTRO DE REGIÓN ---
    regiones = [
        "Total nacional", "Región GBA", "Región Pampeana",
        "Región Noroeste", "Región Noreste", "Región Cuyo", "Región Patagonia"
    ]
    region_elegida = st.selectbox("Selecciona una región", options=regiones)
    dfDatos = dfDatos[dfDatos["regiones"] == region_elegida]

    # --- FILTRO POR CATEGORÍA ---
    categorias = dfDatos["Rubro"].unique().tolist()
    parCategoria = st.selectbox("Selecciona una categoría", options=categorias)
    dfCategoria = dfDatos[dfDatos["Rubro"] == parCategoria]

    # --- AGRUPACIONES PARA BARRAS ---
    dfSubrubroMes = dfCategoria.groupby(["Año", "Mes", "Subrubro"]).agg({"Valor": "mean"}).reset_index()
    dfMesTotal = dfCategoria.groupby(["Año", "Mes"]).agg({"Valor": "mean"}).reset_index()

    cols = st.columns([2,2])
    with cols[0]:
        with st.container(horizontal=True, horizontal_alignment="center", border=True):
            # --- GRÁFICO DE BARRAS ---
            figBar = px.bar(
                dfSubrubroMes,
                x="Mes",
                y="Valor",
                color="Subrubro",
                barmode="group",
                title=f"Variación mensual por subrubro - {parCategoria}",
                color_discrete_sequence=chartCategoricalColors
            )
            st.plotly_chart(aplicarBackgroundChart(figBar, secondaryBackgroundColor), use_container_width=True, theme=None)


    with cols[1]:
            with st.container(horizontal=True, horizontal_alignment="center", border=True):
                # --- GRAFICO SUNBURST ---
                # Agrupamos toda la jerarquía: Región -> Rubro -> Subrubro
                df_sunburst = dfDatos.groupby(['regiones', 'Rubro', 'Subrubro']).agg({'Valor': 'sum'}).reset_index()

                figSunburst = px.sunburst(
                    df_sunburst,
                    path=['regiones', 'Rubro', 'Subrubro'],
                    values='Valor',
                    title=f"Distribución jerárquica del IPC - {region_elegida}",
                    color='Rubro',
                    color_discrete_sequence=chartCategoricalColors
                )
                figSunburst.update_layout(paper_bgcolor=secondaryBackgroundColor, plot_bgcolor=secondaryBackgroundColor)
                st.plotly_chart(figSunburst, use_container_width=True, theme=None)


    cols = st.columns([2,2])
    with cols[0]:
        with st.container( border=True):
                    # --- 1. TÍTULO SOBRE EL GRÁFICO CON REGIÓN ---
            st.markdown(
                f"<h5 style='text-align: center; color: #ffffff;'>Variación mensual por subrubro Región: <b>{region_elegida}</b></h5>",
                unsafe_allow_html=True
            )

            # --- 2. HEATMAP / TABLA PIVOTE ---
            dfPivot = dfSubrubroMes.pivot_table(
                index="Subrubro", 
                columns="Mes", 
                values="Valor", 
                aggfunc="mean"
            ).fillna(0)

            # Calcular ancho según el subrubro más largo
            max_len = dfPivot.index.astype(str).map(len).max()
            col_width = f"{max_len + 2}ch"  # +2 para margen visual

            cmap = LinearSegmentedColormap.from_list(
                "custom", ["#8B0000", "#DAA520", "#228B22"], N=256
            )
            styled_df = (
                dfPivot.style
                .background_gradient(cmap=cmap)
                .format("{:.1f}")
                .set_table_styles(
                    [
                        {
                            "selector": "th.row_heading.level0",
                            "props": [("min-width", col_width), ("max-width", col_width)]
                        },
                        {
                            "selector": "td.row_heading.level0",
                            "props": [("min-width", col_width), ("max-width", col_width)]
                        }
                    ],
                    overwrite=False
                )
            )

            st.dataframe(styled_df, hide_index=False, use_container_width=True)

            # --- BUMP CHART DESDE ENERO 2025 ---
            dfBump = dfCategoria.copy()
            dfBump = dfBump[dfBump['meses'] >= pd.Timestamp('2025-01-01')]

            dfBumpAgg = (
                dfBump.groupby(["Mes", "Subrubro"])
                .agg({"Valor": "mean"})
                .reset_index()
            )
            dfBumpAgg["Rank"] = dfBumpAgg.groupby("Mes")["Valor"].rank(
                ascending=False, method="min"
            )

            dfBumpWide = dfBumpAgg.pivot(
                index="Mes", columns="Subrubro", values="Rank"
            ).reset_index()
            dfBumpWide = dfBumpWide.sort_values(by="Mes")
            
    with cols[1]:
            with st.container(horizontal=True, horizontal_alignment="center", border=True):
                # --- GRAFICAR BUMP ---
                camposCategorias = [x for x in dfBumpWide.columns if x != "Mes"]

                # Obtener colores del tema de Streamlit o usar valores por defecto
                chartCategoricalColors = st.get_option("theme.chartCategoricalColors")
                if chartCategoricalColors is None:
                    chartCategoricalColors = [
                        "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b",  # marrón
                        "#e377c2","#7f7f7f","#bcbd22", #"#17becf", #"#aec7e8", 
                        "#ffbb78","#00FF00","#FF00FF" 
                    ]

                # Lo mismo para fondo y color de texto
                secondaryBackgroundColor = st.get_option("theme.secondaryBackgroundColor")
                if secondaryBackgroundColor is None:
                    secondaryBackgroundColor = "#FFFFFF"  # blanco por defecto

                textColor = st.get_option("theme.textColor")
                if textColor is None:
                    textColor = "#000000"  # negro por defecto

                # Expandir colores si hay más subrubros que colores disponibles
                num_subrubros = len(camposCategorias)
                if len(chartCategoricalColors) < num_subrubros:
                    chartCategoricalColors = (
                        chartCategoricalColors * ((num_subrubros // len(chartCategoricalColors)) + 1)
                    )[:num_subrubros]

                # Crear gráfico
                fig, ax = plt.subplots(figsize=(6, 4))
                bumplot(
                    x="Mes",
                    y_columns=camposCategorias,
                    data=dfBumpWide,
                    curve_force=0.5,
                    plot_kwargs={"lw": 3},
                    scatter_kwargs={"s": 100, "ec": "black", "lw": 1},
                    colors=chartCategoricalColors,
                )

                ax.set_title(f"Ranking de subrubros por mes desde 2025 ({parCategoria})", fontsize=14)
                ax.set_facecolor(secondaryBackgroundColor)
                fig.patch.set_facecolor(secondaryBackgroundColor)

                mes_max = dfBumpWide["Mes"].max()

                for i, cat in enumerate(camposCategorias):
                    serie = dfBumpWide[cat]    
                    # No mostrar etiquetas de subrubros que tengan solo ceros
                    if (serie == 0).all():
                        continue

                    try:
                        last_valid_index = serie[serie != 0].last_valid_index()
                        rank = serie[last_valid_index]
                    except Exception:
                        continue

                    ax.text(
                        x=mes_max + 0.3,
                        y=rank,
                        s=cat,
                        va="center",
                        ha="left",
                        fontsize=5,
                        color=textColor
                    )

                ax.set_xlabel("Mes (1.ene / 2.feb / 3.mar / 4.abr / 5.may / 6.jun / 7.jul / 8.ago)")
                ax.invert_yaxis()
                ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
                ax.grid(alpha=0.3)

                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_color(textColor)
                ax.title.set_color(textColor)
                ax.xaxis.label.set_color(textColor)

                st.pyplot(fig)

with st.expander("Inflación Análisis y Modelos Predictivos",  expanded=False, icon=":material/finance_mode:", width="stretch"):
    st.markdown(
    """
    <style>
    /* Cambiar el color de todo el texto visible */
    .css-1d391kg, /* texto normal */
    .css-1v0mbdj, /* encabezados */
    .stMetricValue, /* valores métricas */
    .stMetricLabel, /* labels métricas */
    .css-ffhzg2, /* subheaders */
    .css-1v3fvcr { /* otros textos */
        color: #d4a017 !important; /* color mostaza */
    }

    /* También para el texto dentro de los expanders, markdown, y etiquetas */
    .element-container p, 
    .element-container span, 
    .element-container div {
        color: #d4a017 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st.header("Análisis y Predicción de % Inflación (2017-2025)")

    # Ocultar el sidebar
    hide_sidebar = """
        <style>
            [data-testid="stSidebar"] {display: none;}
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

    # --- Leer archivo y hoja ---
    archivo_excel = "data/ipc_09_25.xlsx"
    hoja = "Var. mensual IPC"

    try:
        xls = pd.ExcelFile(archivo_excel)
        df = pd.read_excel(xls, sheet_name=hoja)
    except Exception as e:
        st.error(f"Error leyendo el archivo o la hoja: {e}")
        st.stop()

    with st.expander("Composición de las variables a estudiar"):

        regiones = [
            "Total nacional", "Región GBA", "Región Pampeana",
            "Región Noroeste", "Región Noreste", "Región Cuyo", "Región Patagonia"
        ]

        rubros = [
            "Nivel general", "Categorías", "Bienes y servicios"
        ]

        nivel_general_detalle = [
            "Alimentos y bebidas no alcohólicas", "Bebidas alcohólicas y tabaco", "Prendas de vestir y calzado",
            "Vivienda, agua, electricidad, gas y otros combustibles", "Equipamiento y mantenimiento del hogar",
            "Salud", "Transporte", "Comunicación", "Recreación y cultura", "Educación",
            "Restaurantes y hoteles", "Bienes y servicios varios"
        ]

        categorias_detalle = [
            "Estacional", "Núcleo", "Regulados"
        ]

        bienes_servicios_detalle = [
            "Bienes", "Servicios"
        ]

        # Mostrar regiones
        st.markdown(":red[**Regiones**]")
        for region in regiones:
            st.write(f"- {region}")

        # Mostrar rubros y detalles
        st.markdown(":blue[**Rubros**]")
        for rubro in rubros:
            st.markdown(f"<u>:green[{rubro}]</u>", unsafe_allow_html=True)
            #st.write(f"- **{rubro}**")
            if rubro == "Nivel general":
                for item in nivel_general_detalle:
                    st.write(f"    - {item}")
            elif rubro == "Categorías":
                for item in categorias_detalle:
                    st.write(f"    - {item}")
            elif rubro == "Bienes y servicios":
                for item in bienes_servicios_detalle:
                    st.write(f"    - {item}")

    # Limpiar nombres columnas
    df.columns = df.columns.str.strip().str.lower()

    # Comprobar columnas clave
    columnas_clave = ["meses", "regiones", "nivel general", "categorías", "bienes y servicios"]
    faltantes = [c for c in columnas_clave if c not in df.columns]
    if faltantes:
        st.error(f"Faltan columnas clave: {faltantes}")
        st.stop()

    # Conversión de tipos
    df['meses'] = pd.to_datetime(df['meses'], errors='coerce')
    df = df.dropna(subset=['meses', 'regiones'])

    # --- Interfaz de usuario ---
    regiones = [
        "Total nacional", "Región GBA", "Región Pampeana",
        "Región Noroeste", "Región Noreste", "Región Cuyo", "Región Patagonia"
    ]
    with st.container(border=True):
    
        col1, col2 = st.columns([2, 2])
        with col1: 
            region_seleccionada = st.selectbox("Selecciona la región para analizar", regiones)
            # --- Filtro por región ---
            df_region = df[df['regiones'] == region_seleccionada].copy()
            df_region = df_region.set_index('meses').sort_index()

            # --- Comparación inicial de variables clave ---
            st.subheader("Comparación inicial: Nivel General vs Categorías vs Bienes y Servicios")

            variables_comparar = ["nivel general", "categorías", "bienes y servicios"]

            # Asegurarse de que los valores sean numéricos
            for var in variables_comparar:
                df_region[var] = pd.to_numeric(df_region[var], errors='coerce')

            df_comp = df_region[variables_comparar].dropna()

            # Tipo de gráfico
            tipo_grafico = st.radio("Tipo de gráfico comparativo", ["Línea", "Barras mensuales"], horizontal=True)

            if tipo_grafico == "Línea":
                st.line_chart(df_comp)
            else:
                # Gráfico de barras mensuales
                st.markdown("**Comparación mensual (últimos 36 meses)**")
                df_barras = df_comp.tail(36).copy()
                df_barras['mes'] = df_barras.index.strftime('%Y-%m')

                # Transponer para que las variables sean columnas
                df_barras_reset = df_barras.reset_index()[['mes'] + variables_comparar]
                df_barras_melted = pd.melt(df_barras_reset, id_vars='mes', value_vars=variables_comparar,
                                        var_name='Variable', value_name='Valor')

                import altair as alt
                chart = alt.Chart(df_barras_melted).mark_bar().encode(
                    x=alt.X('mes:N', title='Mes'),
                    y=alt.Y('Valor:Q', title='Valor'),
                    color='Variable:N',
                    column=alt.Column('Variable:N', title=None)
                ).properties(
                    width=150,
                    height=300
                )
                st.altair_chart(chart)


        with col2:
            variable_objetivo = st.selectbox(
                "Selecciona la variable objetivo para el análisis",
                ["nivel general", "categorías", "bienes y servicios"]
            )
            # --- Filtro por región ---
            #df_region = df[df['regiones'] == region_seleccionada].copy()
            #df_region = df_region.set_index('meses').sort_index()
            df_region[variable_objetivo] = pd.to_numeric(df_region[variable_objetivo], errors='coerce')
            df_region = df_region.dropna(subset=[variable_objetivo])

            if df_region.empty:
                st.error(f"No hay datos disponibles para la región seleccionada: {region_seleccionada}")
                st.stop()

            # --- Visualización inicial ---
            st.subheader(f"Datos de {variable_objetivo.title()} para {region_seleccionada}")
            st.write("###")
            st.line_chart(df_region[variable_objetivo])

    with st.container(border=True):
        
        # --- Test ADF ---
        st.subheader("Test de Estacionariedad (ADF)")   
        col1, col2 = st.columns([1, 3])
        with col1: 
            adf_result = adfuller(df_region[variable_objetivo])
            st.write(f"**ADF Statistic:** {adf_result[0]:.4f}")
            st.write(f"**p-value:** {adf_result[1]:.4f}")
            for k, v in adf_result[4].items():
                st.write(f"  {k}: {v:.4f}")
        with col2:
            if adf_result[1] > 0.05:
                st.warning("La serie **no es estacionaria**. Aplicando primera diferencia...")
                df_region_diff = df_region[variable_objetivo].diff().dropna()
                st.line_chart(df_region_diff)
            else:
                st.success("La serie es estacionaria.")

    with st.container(border=True):
        # --- Modelo SARIMA ---
        st.subheader(f"Modelo SARIMA para {variable_objetivo.title()}")
        try:
            model = SARIMAX(df_region[variable_objetivo], order=(1, 1, 1), seasonal_order=(1, 0, 1, 12))
            results = model.fit(disp=False)
            df_region["predicciones"] = results.fittedvalues

            rmse = np.sqrt(mean_squared_error(df_region[variable_objetivo].iloc[1:], df_region["predicciones"].iloc[1:]))
            mae = mean_absolute_error(df_region[variable_objetivo].iloc[1:], df_region["predicciones"].iloc[1:])
            aic = results.aic
            bic = results.bic
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("RMSE(Root Mean Squared Error)", f"{rmse:.4f}")
                st.metric("MAE(Mean Absolute Error) ", f"{mae:.4f}")
                st.write(f"AIC (Akaike Information Criterion): {aic:.2f} | BIC (Bayesian Information Criterion): {bic:.2f}")
                st.write("criterios se basan en la función de verosimilitud,")
                st.write("que cuantifica qué tan bien el modelo se ajusta a los datos,")
                st.write("y penaliza al modelo por tener más parámetros,")
                st.write("lo que aumenta el riesgo de sobreajuste. ")  
                st.write("Cuanto más bajo sea el AIC o BIC, mejor será el modelo.")  

            with col2:
                fig, ax = plt.subplots(figsize=(12, 5))
                plt.style.use("dark_background")
                ax.plot(df_region.index, df_region[variable_objetivo], label="Real", color="cyan")
                ax.plot(df_region.index, df_region["predicciones"], label="SARIMA", color="orange", linestyle="--")
                ax.set_title(f"{variable_objetivo.title()} Real vs Predicho (SARIMA)")
                ax.set_xlabel("Meses")
                ax.set_ylabel("%")
                ax.legend()
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error en SARIMA: {e}")
            

    with st.container(border=True):
        # --- Modelo VAR ---
        #st.subheader(f"Modelo VAR para {variable_objetivo.title()}")
        st.subheader("Modelo VAR para Inflación VariablesMultiples (nivel general-categorías-bienes y servicios) ")

        try:
            
            variables_var = ["nivel general", "categorías", "bienes y servicios"]
            df_var = df_region[variables_var].copy()
            df_var = df_var.dropna()
            df_var_diff = df_var.diff().dropna()

            # División en train y test
            train = df_var_diff[:-12]
            test = df_var_diff[-12:]

            # Entrenamiento del modelo VAR
            model_var = VAR(train)
            results_var = model_var.fit(maxlags=12, ic='aic')

            # Pronóstico
            forecast = results_var.forecast(train.values[-results_var.k_ar:], steps=12)
            forecast_df = pd.DataFrame(forecast, index=test.index, columns=variables_var)

            # Reconstrucción de niveles desde la última observación real
            last_values = df_var.iloc[-13]
            forecast_values = forecast_df.cumsum() + last_values
            
                # Visualización y métricas para cada variable
            for variable in variables_var:
                col1, col2 = st.columns([3, 1])
                with col1:
                    fig, ax = plt.subplots(figsize=(12, 5))
                    plt.style.use("dark_background")
                    ax.plot(df_var.index, df_var[variable], label="Real", color="cyan")
                    ax.plot(forecast_values.index, forecast_values[variable], label="VAR", color="lime", linestyle="--")
                    ax.set_title(f"Predicción con VAR - {variable.title()}")
                    ax.set_xlabel("Meses")
                    ax.set_ylabel("%")
                    ax.legend()
                    st.pyplot(fig)                
                with col2:
                    # Métricas
                    rmse_var = np.sqrt(mean_squared_error(df_var.loc[forecast_values.index][variable], forecast_values[variable]))
                    mae_var = mean_absolute_error(df_var.loc[forecast_values.index][variable], forecast_values[variable])
                    st.metric(f"RMSE (VAR) - {variable.title()}", f"{rmse_var:.4f}")
                    st.metric(f"MAE (VAR) - {variable.title()}", f"{mae_var:.4f}")

        except Exception as e:
            st.error(f"Error en modelo VAR: {e}")
            
    with st.container(border=True):    
        # --- Modelo XGBoost ---
        st.subheader(f"Modelo XGBoost - {variable_objetivo.title()}")

        def create_lags(df_in, lags=3):
            df_lags = df_in.copy()
            for lag in range(1, lags + 1):
                df_lags[f"{df_in.columns[0]}_lag_{lag}"] = df_in[df_in.columns[0]].shift(lag)
            df_lags.dropna(inplace=True)
            return df_lags

        try:
            df_xgb = df_region[[variable_objetivo]].copy()
            df_xgb = df_xgb.dropna()

            max_lags = st.slider("Número de lags para XGBoost:", 1, 12, 3)
            df_features = create_lags(df_xgb, lags=max_lags)

            X = df_features.drop(columns=[variable_objetivo])
            y = df_features[variable_objetivo]

            split_idx = int(len(df_features) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

            model_xgb = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
            model_xgb.fit(X_train, y_train)

            y_pred_test = model_xgb.predict(X_test)

            rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_test))
            mae_xgb = mean_absolute_error(y_test, y_pred_test)
            #---------------------------------------------------------------------------
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.metric("RMSE (XGBoost)", f"{rmse_xgb:.4f}")
                st.metric("MAE (XGBoost)", f"{mae_xgb:.4f}")
            with col2:
                fig4, ax4 = plt.subplots(figsize=(12, 5))
                plt.style.use("dark_background")
                ax4.plot(y_test.index, y_test, label="Real", color="cyan")
                ax4.plot(y_test.index, y_pred_test, label="XGBoost", color="magenta", linestyle="--")
                ax4.set_title(f"Predicción XGBoost - {variable_objetivo.title()}")
                ax4.set_xlabel("Meses")
                ax4.set_ylabel("%")
                ax4.legend()
                st.pyplot(fig4)

        except Exception as e:
            st.error(f"Error en modelo XGBoost: {e}")


    # --- CSS estilo Matrix para el botón ---
    disconnect_button_css = """
    <style>
    .disconnect-button-container {
        display: flex;
        justify-content: center;
        margin-top: 50px;
    }

    .disconnect-button {
        background-color: black;
        border: 2px solid #00FF00;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        font-size: 20px;
        padding: 12px 30px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease-in-out;
    }

    .disconnect-button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: rgba(0,255,0,0.2);
        transform: skewX(-20deg);
    }

    .disconnect-button:hover::before {
        animation: shine 0.75s forwards;
    }

    @keyframes shine {
        0% {
            left: -100%;
        }
        100% {
            left: 100%;
        }
    }

    .disconnect-button:hover {
        color: black;
        background-color: #00FF00;
    }
    </style>
    """

    # --- Mostrar el botón con estilo personalizado ---
    st.markdown(disconnect_button_css, unsafe_allow_html=True)

    # Usamos una columna para centrar el botón
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Disconnet", key="disconnet_button"):
            st.switch_page("pages/endsession.py")  #

