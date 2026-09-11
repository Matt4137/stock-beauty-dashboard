from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "datos" / "productos_limpios.csv"

st.set_page_config(
    page_title="Stock&Beauty",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #0d1117; color: #f8fafc; }
    [data-testid="stSidebar"] { background: #111827; }
    [data-testid="stSidebar"] * { color: #f8fafc; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    .hero {
        padding: 1.35rem 1.55rem;
        margin-bottom: 1rem;
        border-radius: 0 0 18px 18px;
        background: linear-gradient(110deg, #121c2e, #374151);
        border-left: 5px solid #38bdf8;
    }
    .hero h1 { margin: 0 0 .4rem 0; color: #ffffff; }
    .hero p { margin: 0; color: #dbeafe; }

    /* Tarjetas KPI: colores explícitos para modo claro y oscuro. */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #162033, #1f2d45);
        border: 1px solid #334155;
        border-left: 5px solid #38bdf8;
        border-radius: 15px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 22px rgba(0, 0, 0, .20);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        color: #cbd5e1 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 750 !important;
    }
    [data-testid="stMetricDelta"] { color: #7dd3fc !important; }

    div[data-testid="stAlert"] { border-radius: 12px; }
    .small-note { color: #94a3b8; font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    datos = pd.read_csv(DATA_FILE)
    datos["precio"] = pd.to_numeric(datos["precio"], errors="coerce")
    datos["stock"] = pd.to_numeric(datos["stock"], errors="coerce").fillna(0).astype(int)
    datos["valor_inventario"] = datos["precio"] * datos["stock"]
    datos["estado_stock"] = pd.cut(
        datos["stock"],
        bins=[-1, 10, 40, float("inf")],
        labels=["Crítico", "Medio", "Saludable"],
    )
    return datos


df = cargar_datos()

with st.sidebar:
    st.markdown("## StockVision")
    st.caption("Sistema de análisis de productos e inventario")
    st.divider()
    pagina = st.radio(
        "Navegación",
        ["Resumen", "Dashboard", "Productos", "Inventario", "Estadísticas", "Datos"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Proyecto de Lenguaje de Ciencia de Datos II")
    st.markdown("### Filtros")
    categorias = st.multiselect("Categoría", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique()))
    marcas_disponibles = sorted(df.loc[df["categoria"].isin(categorias), "marca"].unique())
    marcas = st.multiselect("Marca", marcas_disponibles, default=marcas_disponibles)
    minimo, maximo = float(df["precio"].min()), float(df["precio"].max())
    precio = st.slider("Rango de precio (S/)", minimo, maximo, (minimo, maximo))

filtrado = df[
    df["categoria"].isin(categorias)
    & df["marca"].isin(marcas)
    & df["precio"].between(precio[0], precio[1])
].copy()

st.markdown(
    """
    <div class="hero">
      <h1>Stock&Beauty</h1>
      <p>Panel para supervisar productos, precios, marcas e inventario del sector de belleza.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtrado.empty:
    st.warning("No hay productos que coincidan con los filtros seleccionados.")
    st.stop()


def kpis(datos: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Productos", f"{len(datos):,}")
    c2.metric("Stock total", f"{int(datos['stock'].sum()):,}")
    c3.metric("Precio promedio", f"S/ {datos['precio'].mean():,.2f}")
    c4.metric("Valor del inventario", f"S/ {datos['valor_inventario'].sum():,.2f}")


def aplicar_tema(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f8fafc",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


if pagina == "Resumen":
    kpis(filtrado)
    st.markdown("## Estado general")
    izquierda, derecha = st.columns([1.7, 1])
    por_categoria = filtrado.groupby("categoria", as_index=False)["valor_inventario"].sum().sort_values("valor_inventario", ascending=False)
    with izquierda:
        fig = px.bar(
            por_categoria,
            x="categoria",
            y="valor_inventario",
            text_auto=".2s",
            title="Valor de inventario por categoría",
            color_discrete_sequence=["#7dd3fc"],
            labels={"categoria": "Categoría", "valor_inventario": "Valor de inventario (S/)"},
        )
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)
    with derecha:
        estados = filtrado.groupby("estado_stock", observed=True, as_index=False).size()
        fig = px.pie(
            estados,
            names="estado_stock",
            values="size",
            hole=.45,
            title="Estado del stock",
            color="estado_stock",
            color_discrete_map={"Saludable": "#7dd3fc", "Medio": "#0f73c9", "Crítico": "#fb9298"},
        )
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    st.markdown("## Hallazgos rápidos")
    mayor_valor = filtrado.loc[filtrado["valor_inventario"].idxmax()]
    mas_caro = filtrado.loc[filtrado["precio"].idxmax()]
    criticos = int((filtrado["estado_stock"] == "Crítico").sum())
    c1, c2, c3 = st.columns(3)
    c1.info(f" Mayor valor almacenado: {mayor_valor['producto']} (S/ {mayor_valor['valor_inventario']:,.2f})")
    c2.info(f" Producto más caro: {mas_caro['producto']} (S/ {mas_caro['precio']:,.2f})")
    c3.warning(f" Productos con stock crítico: {criticos}")

elif pagina == "Dashboard":
    st.markdown("## Dashboard interactivo")
    kpis(filtrado)
    c1, c2 = st.columns(2)
    with c1:
        top_stock = filtrado.nlargest(10, "stock").sort_values("stock")
        fig = px.bar(top_stock, x="stock", y="producto", orientation="h", title="Productos con mayor stock", color="stock", color_continuous_scale="Blues")
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)
    with c2:
        por_marca = filtrado.groupby("marca", as_index=False)["valor_inventario"].sum().sort_values("valor_inventario", ascending=False)
        fig = px.bar(por_marca, x="marca", y="valor_inventario", title="Valor del inventario por marca", color="valor_inventario", color_continuous_scale="Teal")
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)
    fig = px.scatter(
        filtrado,
        x="precio",
        y="stock",
        size="valor_inventario",
        color="categoria",
        hover_name="producto",
        title="Relación entre precio y stock",
        labels={"precio": "Precio (S/)", "stock": "Stock"},
    )
    st.plotly_chart(aplicar_tema(fig), use_container_width=True)

elif pagina == "Productos":
    st.markdown("## Explorador de productos")
    busqueda = st.text_input("Buscar producto", placeholder="Escribe parte del nombre...")
    productos = filtrado[filtrado["producto"].str.contains(busqueda, case=False, na=False)] if busqueda else filtrado
    st.caption(f"{len(productos)} producto(s) encontrado(s)")
    st.dataframe(
        productos[["producto", "categoria", "marca", "precio", "stock", "estado_stock", "valor_inventario"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "precio": st.column_config.NumberColumn("Precio", format="S/ %.2f"),
            "valor_inventario": st.column_config.NumberColumn("Valor inventario", format="S/ %.2f"),
            "stock": st.column_config.ProgressColumn("Stock", min_value=0, max_value=max(100, int(df["stock"].max()))),
        },
    )

elif pagina == "Inventario":
    st.markdown("## Control de inventario")
    umbral = st.number_input("Umbral para reposición", min_value=1, max_value=100, value=20)
    bajo = filtrado[filtrado["stock"] <= umbral].copy()
    bajo["cantidad_sugerida"] = (umbral * 2 - bajo["stock"]).clip(lower=0)
    c1, c2, c3 = st.columns(3)
    c1.metric("Productos por reponer", len(bajo))
    c2.metric("Unidades actuales", int(bajo["stock"].sum()))
    c3.metric("Reposición sugerida", int(bajo["cantidad_sugerida"].sum()))
    if bajo.empty:
        st.success("No hay productos por debajo del umbral seleccionado.")
    else:
        st.warning(f"Se detectaron {len(bajo)} productos con stock igual o menor a {umbral}.")
        fig = px.bar(bajo.sort_values("stock"), x="stock", y="producto", orientation="h", color="stock", title="Productos con bajo stock", color_continuous_scale="Reds_r")
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)
        st.dataframe(bajo[["producto", "marca", "stock", "cantidad_sugerida"]], use_container_width=True, hide_index=True)

elif pagina == "Estadísticas":
    st.markdown("## Estadísticas descriptivas")
    resumen = filtrado[["precio", "stock", "valor_inventario"]].describe().T
    resumen = resumen.rename(columns={"count": "Cantidad", "mean": "Promedio", "std": "Desv. estándar", "min": "Mínimo", "25%": "Q1", "50%": "Mediana", "75%": "Q3", "max": "Máximo"})
    st.dataframe(resumen.style.format("{:,.2f}"), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(filtrado, x="categoria", y="precio", color="categoria", title="Distribución de precios por categoría")
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)
    with c2:
        conteo = filtrado.groupby("marca", as_index=False).size().sort_values("size", ascending=False)
        fig = px.bar(conteo, x="marca", y="size", title="Cantidad de productos por marca", color_discrete_sequence=["#38bdf8"])
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

else:
    st.markdown("## Datos del proyecto")
    st.write("Consulta los datos procesados o descarga los registros que coinciden con los filtros.")
    st.dataframe(filtrado, use_container_width=True, hide_index=True)
    csv = filtrado.drop(columns=["estado_stock"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇Descargar CSV filtrado", csv, "productos_filtrados.csv", "text/csv", use_container_width=False)
    st.markdown('<p class="small-note">Los indicadores se recalculan automáticamente al modificar los filtros.</p>', unsafe_allow_html=True)
