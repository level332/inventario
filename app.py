import streamlit as st
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# CONFIGURACIÓN DE ARCHIVOS
DB_FILE = "inventario_fibra_empresarial.xlsx"
USERS_FILE = "usuarios_sistema.xlsx"
LOGO_FILE = "logo.png"

TIPOS_SPLITTER = [
    "Asimétrico 99/1", "Asimétrico 98/2", "Asimétrico 97/3", "Asimétrico 95/5", "Asimétrico 90/10",
    "Asimétrico 85/15", "Asimétrico 80/20", "Asimétrico 75/25", "Asimétrico 70/30", "Asimétrico 65/35",
    "Asimétrico 60/40", "Asimétrico 55/45", "Simétrico 50/50 (1x2)", "Simétrico 1x4", "Simétrico 1x8",
    "Simétrico 1x16", "Simétrico 1x32", "Simétrico 1x64"
]

def generar_kml(dataframe):
    kml = ET.Element("kml", xmlns="http://opengis.net")
    document = ET.SubElement(kml, "Document")
    ET.SubElement(document, "name").text = "Inventario de Fibra Óptica - Red LEVELPLUS"
    for _, fila in dataframe.iterrows():
        try:
            lat, lon = str(fila["Latitud"]).strip(), str(fila["Longitud"]).strip()
            if lat and lon and lat != "nan" and lon != "nan":
                placemark = ET.SubElement(document, "Placemark")
                ET.SubElement(placemark, "name").text = f"{fila['Código/Nombre']} ({fila['Elemento/Caja FAT']})"
                desc = ET.SubElement(placemark, "description")
                desc.text = f"Splitter: {fila['Tipo de Splitter']}\nCapacidad: {fila['Puertos Ocupados']}/{fila['Capacidad Total']}\nTécnico: {fila['Registrado Por']}"
                ET.SubElement(ET.SubElement(placemark, "Point"), "coordinates").text = f"{lon},{lat},0"
        except: continue
    return ET.tostring(kml, encoding="utf-8")

def cargar_usuarios():
    if os.path.exists(USERS_FILE): return pd.read_excel(USERS_FILE)
    df = pd.DataFrame([{"Usuario": "admin_master", "Clave": "master2026", "Rol": "Máster"}])
    df.to_excel(USERS_FILE, index=False)
    return df

def cargar_datos():
    if os.path.exists(DB_FILE): return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=["Fecha/Hora", "Registrado Por", "Rol Usuario", "Elemento/Caja FAT", "Código/Nombre", "Tipo de Splitter", "Capacidad Total", "Puertos Ocupados", "Latitud", "Longitud", "Estado", "Notas"])

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = ""
if "rol_actual" not in st.session_state: st.session_state.rol_actual = ""

df_usuarios = cargar_usuarios()
df_inventario = cargar_datos()

st.set_page_config(page_title="LEVELPLUS Fibra", layout="wide")

# PANTALLA DE INICIO DE SESIÓN
if not st.session_state.autenticado:
    st.title("🦁 LEVELPLUS")
    st.subheader("Dedicados a Conectarte - Gestión de Redes FO")
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=140)
    st.markdown("---")
    with st.form("login_form"):
        st.write("🔒 Acceso Seguro a la Intranet")
        u_in = st.text_input("Usuario / Técnico")
        c_in = st.text_input("Contraseña", type="password")
        if st.form_submit_button("🚀 ACCEDER AL SISTEMA", use_container_width=True):
            user_row = df_usuarios[df_usuarios["Usuario"] == u_in]
            
            # Validación corregida para evitar fallos de lectura en DataFrames
            if not user_row.empty and str(user_row["Clave"].values[0]) == str(c_in):
                st.session_state.autenticado = True
                st.session_state.usuario_actual = u_in
                st.session_state.rol_actual = user_row["Rol"].values[0]
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")

# ENTORNO PRINCIPAL CON MENÚ LATERAL Y DISEÑO PREMIUM
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=130)
        # Se corrigió el parámetro a unsafe_allow_html=True
        st.markdown("<h2 style='color: #E74C3C; margin-top: 0;'>LEVELPLUS</h2>", unsafe_allow_html=True)
        st.markdown(f"👤 *{st.session_state.usuario_actual}* ({st.session_state.rol_actual})")
        st.markdown("---")
        opc = ["🏠 Panel / Mapa", "➕ Registrar Caja FAT", "📊 Inventario", "⚙️ Técnicos"] if st.session_state.rol_actual == "Máster" else ["➕ Registrar Caja FAT", "📊 Mis Actividades"]
        sel = st.radio("Módulos del Sistema:", opc)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    df_act = cargar_datos()

    if sel == "🏠 Panel / Mapa":
        st.markdown("<h1 style='color: #2C3E50;'>📊 Resumen General de la Red</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Cajas FAT Totales", len(df_act))
        c2.metric("🟢 Operativas", len(df_act[df_act["Estado"] == "Operativo"]))
        c3.metric("🔴 En Falla", len(df_act[df_act["Estado"] == "Falla"]))
        st.markdown("---")
        st.subheader("📍 Mapa de Infraestructura en Tiempo Real")
        if df_act.empty:
            st.info("No hay ubicaciones registradas.")
        else:
            try:
                map_df = df_act.dropna(subset=["Latitud", "Longitud"])
                map_df["latitude"] = pd.to_numeric(map_df["Latitud"])
                map_df["longitude"] = pd.to_numeric(map_df["Longitud"])
                st.map(map_df, size=22, use_container_width=True)
            except: st.warning("Revisa el formato de los datos geográficos.")

    elif sel == "➕ Registrar Caja FAT":
        st.markdown("<h1 style='color: #E74C3C;'>➕ Registro Técnico</h1>", unsafe_allow_html=True)
        with st.form("f_fibra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                elem = st.selectbox("Elemento", ["Caja FAT / CTO", "Mufa de Empalme", "Poste", "OLT"])
                cod = st.text_input("Código FAT ID")
                spl = st.selectbox("Splitter", TIPOS_SPLITTER)
                cap = st.number_input("Total Puertos", min_value=1, value=16)
                ocu = st.number_input("Ocupados", min_value=0, value=0)
            with col2:
                coords_juntas = st.text_input("Pegar Coordenadas Completas (GPS)", placeholder="Ej: 10.4806, -66.9036")
                est = st.select_slider("Estado del Nodo", options=["Operativo", "Mantenimiento", "Falla"])
                not_t = st.text_area("Observaciones")
            if st.form_submit_button("💾 GUARDAR REGISTRO", use_container_width=True):
                if not cod or not coords_juntas: st.error("⚠️ Ingrese Código y Coordenadas.")
                else:
                    try:
                        parts = coords_juntas.split(",")
                        lat_val, lon_val = float(parts[0].strip()), float(parts[1].strip())
                        n_f = {"Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Registrado Por": st.session_state.usuario_actual, "Rol Usuario": st.session_state.rol_actual, "Elemento/Caja FAT": elem, "Código/Nombre": cod, "Tipo de Splitter": spl, "Capacidad Total": cap, "Puertos Ocupados": ocu, "Latitud": lat_val, "Longitud": lon_val, "Estado": est, "Notas": not_t}
                        pd.concat([df_act, pd.DataFrame([n_f])], ignore_index=True).to_excel(DB_FILE, index=False)
                        st.success("✅ Sincronizado con éxito."); st.rerun()
                    except: st.error("❌ Formato incorrecto. Coloque una coma en medio (Ej: 10.48, -66.90)")

    elif sel in ["📊 Inventario", "📊 Mis Actividades"]:
        st.markdown("<h1 style='color: #2C3E50;'>📋 Base de Datos de Inventario</h1>", unsafe_allow_html=True)
        df_m = df_act if st.session_state.rol_actual == "Máster" else df_act[df_act["Registrado Por"] == st.session_state.usuario_actual]
        if df_m.empty: st.info("Sin registros.")
        else:
            st.dataframe(df_m, use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                with open(DB_FILE, "rb") as f: st.download_button("📥 EXPORTAR A EXCEL", f, "Inventario_LEVELPLUS.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c2: st.download_button("🌍 EXPORTAR KML (GOOGLE EARTH)", generar_kml(df_m), "Red_LEVELPLUS.kml", "application/vnd.google-earth.kml+xml", use_container_width=True)

    elif sel == "⚙️ Técnicos":
        st.markdown("<h1 style='color: #2C3E50;'>⚙️ Gestión de Cuentas Técnicas</h1>", unsafe_allow_html=True)
        df_u = cargar_usuarios()
        st.dataframe(df_u[["Usuario", "Rol"]], use_container_width=True)
        with st.form("a_tec", clear_on_submit=True):
            n_u = st.text_input("Usuario").strip()
            n_c = st.text_input("Contraseña", type="password")
            if st.form_submit_button("➕ REGISTRAR TÉCNICO", use_container_width=True) and n_u and n_c:
                if n_u in df_u["Usuario"].values: st.error("⚠️ Ya existe.")
                else:
                    pd.concat([df_u, pd.DataFrame([{"Usuario": n_u, "Clave": n_c, "Rol": "Técnico"}])], ignore_index=True).to_excel(USERS_FILE, index=False)
                    st.success("🎉 Creado con éxito."); st.rerun()
