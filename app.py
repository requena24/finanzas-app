# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
sheet_wallet = client.open("finanzas-personales").worksheet("Wallet")

# Cargar datos
datos = sheet.get_all_records()
df = pd.DataFrame(datos)
df.columns = [str(col).lower() for col in df.columns]

if not df.empty:
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0)
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

# Tabs para organizar secciones
secciones = st.tabs(["📋 Movimientos", "➕ Agregar movimiento", "📑 Formas de pago", "💳 Wallet", "📊 Gráficos", "🗑 Eliminar"])

# ============================
# TAB 1: MOVIMIENTOS
# ============================
with secciones[0]:
    st.subheader("📋 Movimientos actuales")
    if not df.empty:
        df_display = df.copy()
        df_display['fecha'] = df_display['fecha'].dt.strftime('%d/%m/%Y')
        df_display['monto'] = df_display['monto'].apply(lambda x: f"$ {x:,.2f}")
        st.dataframe(df_display, hide_index=True)
    else:
        st.info("No hay movimientos registrados.")

# ============================
# TAB 2: AGREGAR MOVIMIENTO
# ============================
with secciones[1]:
    st.subheader("➕ Añadir nuevo movimiento")
    with st.form("formulario_movimiento"):
        fecha = st.date_input("Fecha:", datetime.today())
        mes = fecha.strftime("%B")
        tipo = st.selectbox("Tipo:", ["Ingreso", "Gasto"])
        categoria = st.text_input("Categoría:")
        concepto = st.text_input("Concepto:")
        monto = st.number_input("Monto ($):", min_value=0.0, step=1.0, format="%.2f")
        forma_pago = st.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])

        tarjetas = [""] + sheet_wallet.col_values(1)[1:] if sheet_wallet.row_count > 1 else [""]
        if not tarjetas:
            st.warning("⚠️ No tienes tarjetas registradas. Ve a la sección Wallet para agregarlas.")
        tarjeta_usada = st.selectbox("Selecciona la tarjeta usada (solo si aplica):", tarjetas) if tarjetas else st.text_input("Tarjeta usada (solo si aplica):")

        nota = st.text_area("Nota (opcional):")
        submit = st.form_submit_button("Guardar movimiento 💾")

        if submit:
            forma_completa = tarjeta_usada if forma_pago == "Tarjeta" and tarjeta_usada else forma_pago
            nueva_fila = [str(fecha), mes, tipo, categoria, concepto, monto, forma_completa, nota]
            sheet.append_row(nueva_fila)
            st.success("✅ Movimiento guardado correctamente. Recarga la app para ver los cambios.")

# ============================
# TAB 3: FORMAS DE PAGO Y TARJETAS
# ============================
with secciones[2]:
    st.subheader("📑 Análisis por forma de pago y tarjetas")

    st.markdown("### 💳 Gastos por forma de pago")
    if not df.empty and 'monto' in df.columns and 'forma de pago' in df.columns:
        resumen_pago = df[df['tipo'] == 'Gasto'].groupby('forma de pago')['monto'].sum().reset_index()
        resumen_pago.columns = ['Forma de pago', 'Total gastado']
        resumen_pago['Total gastado'] = resumen_pago['Total gastado'].apply(lambda x: f"$ {x:,.2f}")
        st.dataframe(resumen_pago, use_container_width=True, hide_index=True)

    st.markdown("### 🧾 Gastos por tarjeta (con rango de fechas)")
    if 'fecha' in df.columns and 'monto' in df.columns and 'forma de pago' in df.columns:
        tarjetas_unicas = df[df['forma de pago'].isin(sheet_wallet.col_values(1)[1:])]['forma de pago'].unique().tolist()

        fecha_inicio = st.date_input("Fecha de corte desde:", value=datetime.today().replace(day=1), key="inicio")
        fecha_fin = st.date_input("Fecha de pago hasta:", value=datetime.today(), key="fin")

        df_tarjetas = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) &
                         (df['fecha'] <= pd.to_datetime(fecha_fin)) &
                         (df['forma de pago'].isin(tarjetas_unicas)) &
                         (df['tipo'] == 'Gasto')]

        if not df_tarjetas.empty:
            resumen_tarjetas = df_tarjetas.groupby('forma de pago')['monto'].sum().reset_index()
            resumen_tarjetas.columns = ['Tarjeta', 'Total gastado en rango']
            resumen_tarjetas['Total gastado en rango'] = resumen_tarjetas['Total gastado en rango'].apply(lambda x: f"$ {x:,.2f}")
            st.dataframe(resumen_tarjetas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay gastos con tarjetas en el rango de fechas seleccionado.")

# ============================
# TAB 4: WALLET
# ============================
with secciones[3]:
    st.subheader("💳 Tus métodos de pago")
    tarjetas_actuales = sheet_wallet.col_values(1)[1:] if sheet_wallet.row_count > 1 else []
    if tarjetas_actuales:
        st.write("Tarjetas registradas:")
        st.dataframe(pd.DataFrame(tarjetas_actuales, columns=["Tarjeta"]), hide_index=True)
    else:
        st.info("No tienes tarjetas registradas.")

    with st.form("form_wallet"):
        nueva_tarjeta = st.text_input("Nombre de nueva tarjeta (ej. BBVA Azul, Citibanamex Oro):")
        guardar_tarjeta = st.form_submit_button("Agregar tarjeta 💳")
        if guardar_tarjeta and nueva_tarjeta:
            sheet_wallet.append_row([nueva_tarjeta])
            st.success("✅ Tarjeta agregada correctamente. Recarga la app para verla en la lista.")

# ============================
# TAB 5: GRÁFICOS
# ============================
with secciones[4]:
    if 'monto' in df.columns and 'mes' in df.columns and 'tipo' in df.columns:
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
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            margin=dict(t=40, l=10, r=10, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("⚠️ No se encontraron columnas necesarias para mostrar el gráfico de barras.")

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
                fig_pie.update_traces(textinfo='percent+label', pull=[0.02]*len(gastos_categoria))
                fig_pie.update_layout(
                    showlegend=True,
                    margin=dict(t=40, l=10, r=10, b=40),
                    font=dict(size=14),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("⚠️ No hay montos válidos para las categorías.")
        else:
            st.info("⚠️ No hay datos válidos de gastos para mostrar el gráfico.")

# ============================
# TAB 6: ELIMINAR MOVIMIENTOS
# ============================
with secciones[5]:
    st.subheader("🗑 Eliminar movimientos")

    if not df.empty:
        df.insert(0, 'Seleccionar', False)

        eliminar_click = st.button("Eliminar seleccionados 🗑️")

        df_edit_display = df.copy()
        df_edit_display['fecha'] = df_edit_display['fecha'].dt.strftime('%d/%m/%Y')
        df_edit_display['monto'] = df_edit_display['monto'].apply(lambda x: f"$ {x:,.2f}")
        edited_df = st.data_editor(
            df_edit_display,
            use_container_width=True,
            column_order=list(df_edit_display.columns),
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
