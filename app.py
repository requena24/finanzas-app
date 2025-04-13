# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px

# Título principal
st.title("💰 Finanzas Personales")

# Conexión a Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)
sheet = client.open("finanzas-personales").worksheet("Hoja1")

# ============================
# FORMULARIO PARA NUEVO GASTO
# ============================
st.subheader("➕ Añadir nuevo movimiento")
fecha = st.date_input("Fecha:", datetime.today())
mes = fecha.strftime("%B")
tipo = st.selectbox("Tipo:", ["Ingreso", "Gasto"])
categoria = st.text_input("Categoría:")
concepto = st.text_input("Concepto:")
monto = st.number_input("Monto:", min_value=0.0, step=1.0)
forma_pago = st.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
nota = st.text_area("Nota (opcional):")

if st.button("Guardar movimiento 💾"):
    nueva_fila = [str(fecha), mes, tipo, categoria, concepto, monto, forma_pago, nota]
    sheet.append_row(nueva_fila)
    st.success("✅ Movimiento guardado correctamente. Recarga la app para ver los cambios.")

# Cargar datos
datos = sheet.get_all_records()
df = pd.DataFrame(datos)
df.columns = [str(col).lower() for col in df.columns]

# Mostrar datos actuales
st.subheader("📋 Movimientos actuales")
st.dataframe(df)

# =============================
# SECCIÓN: ELIMINAR MOVIMIENTOS
# =============================
st.subheader("🗑 Eliminar movimientos")

if not df.empty:
    df['Seleccionar'] = False

    col_boton, _ = st.columns([1, 5])
    with col_boton:
        eliminar_click = st.button("Eliminar seleccionados 🗑️")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Eliminar",
                default=False
            )
        },
        hide_index=True,
        key="editor"
    )

    if eliminar_click:
        rows_to_delete = edited_df[edited_df["Seleccionar"] == True]
        if not rows_to_delete.empty:
            for i in rows_to_delete.index:
                sheet.delete_rows(i + 2)
            st.success("✅ Movimientos eliminados correctamente. Recarga la app para ver los cambios.")
        else:
            st.warning("⚠️ No se seleccionó ningún movimiento para eliminar.")
else:
    st.info("No hay movimientos para eliminar.")

# ==================================
# GRÁFICO DE BARRAS: INGRESOS/GASTOS
# ==================================
if 'monto' in df.columns and 'mes' in df.columns and 'tipo' in df.columns:
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0)
    resumen_mensual = df.groupby(['mes', 'tipo'])['monto'].sum().reset_index()
    st.subheader("📊 Ingresos vs Gastos por mes")
    fig_bar = px.bar(
        resumen_mensual,
        x='mes',
        y='monto',
        color='tipo',
        barmode='group',
        text_auto='.2s',
        labels={'monto': 'Total', 'mes': 'Mes'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("⚠️ No se encontraron columnas necesarias para mostrar el gráfico de barras.")

# ===============================
# GRÁFICO CIRCULAR DE CATEGORÍAS
# ===============================
if 'tipo' in df.columns and 'categoria' in df.columns and 'monto' in df.columns:
    df_gastos = df[df['tipo'] == 'Gasto']
    if not df_gastos.empty and not df_gastos['categoria'].isna().all():
        gastos_categoria = df_gastos.groupby('categoria')['monto'].sum().reset_index()
        if not gastos_categoria.empty:
            st.subheader("🍕 Distribución de gastos por categoría")
            fig_pie = px.pie(
                gastos_categoria,
                values='monto',
                names='categoria',
                title='Distribución porcentual por categoría',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("⚠️ No hay montos válidos para las categorías.")
    else:
        st.info("⚠️ No hay datos válidos de gastos para mostrar el gráfico.")
else:
    st.info("⚠️ No se encontraron columnas necesarias para mostrar el gráfico circular.")
