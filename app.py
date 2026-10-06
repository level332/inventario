import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración del archivo de base de datos
DB_FILE = "inventario_fibra.xlsx"

# Función para cargar o crear la base de datos en Excel
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "Fecha/Hora", "Elemento", "Código/Nombre", 
            "Capacidad (Hilos)", "Hilos Ocupados", 
            "Latitud", "Longitud", "Estado", "Notas"
        ])

# Inicializar datos
df = cargar_datos()

# Interfaz del programa
st.set_page_config(page_title="Gestión de Fibra Óptica", layout="wide")
st.title("🛰️ Sistema de Registro de Fibra Óptica")
st.subheader("Agrega y consulta la información de la red en tiempo real")

# Crear pestañas para organizar el programa
tab1, tab2 = st.tabs(["➕ Agregar Información", "📊 Consultar Inventario"])

with tab1:
    st.header("Registrar Nuevo Elemento de Red")
    
    # Formulario de entrada de datos
    with st.form("formulario_fibra", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            elemento = st.selectbox("Tipo de Elemento", ["Caja CTO", "Mufa/Cierre de Empalme", "Poste", "Central/OLT", "Cliente"])
            codigo = st.text_input("Código o Nombre identificador", placeholder="Ej: CTO-04-BarrioCentro")
            capacidad = st.number_input("Capacidad Total (Hilos/Fibras)", min_value=1, value=16)
            ocupados = st.number_input("Hilos Ocupados actualmente", min_value=0, value=0)
            
        with col2:
            latitud = st.text_input("Latitud GPS", placeholder="Ej: 10.4806")
            longitud = st.text_input("Longitud GPS", placeholder="Ej: -66.9036")
            estado = st.select_slider("Estado del Elemento", options=["Disponible", "Mantenimiento", "Crítico/Dañado"])
            notas = st.text_area("Notas / Observaciones adicionales")
            
        # Botón para guardar
        guardar = st.form_submit_button("💾 Guardar en la Base de Datos")
        
        if guardar:
            if not codigo:
                st.error("⚠️ El campo 'Código/Nombre' es obligatorio.")
            else:
                # Crear nueva fila con la información
                nueva_fila = {
                    "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Elemento": elemento,
                    "Código/Nombre": codigo,
                    "Capacidad (Hilos)": capacidad,
                    "Hilos Ocupados": ocupados,
                    "Latitud": latitud,
                    "Longitud": longitud,
                    "Estado": estado,
                    "Notas": notas
                }
                
                # Guardar en el Excel
                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                df.to_excel(DB_FILE, index=False)
                st.success(f"✅ ¡{elemento} '{codigo}' registrado con éxito!")

with tab2:
    st.header("Datos Registrados")
    
    # Recargar datos actualizados
    df_actualizado = cargar_datos()
    
    if df_actualizado.empty:
        st.info("Aún no hay datos registrados. Utiliza la pestaña anterior para agregar información.")
    else:
        # Mostrar tabla interactiva
        st.dataframe(df_actualizado, use_container_width=True)
        
        # Botón para descargar el Excel directamente desde la web
        with open(DB_FILE, "rb") as file:
            st.download_button(
                label="📥 Descargar Base de Datos Completa (Excel)",
                data=file,
                file_name=DB_FILE,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
         