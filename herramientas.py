def mostrar_menu(st, pd, datetime, DB_FILE, USERS_FILE, LOGO_FILE, TIPOS_SPLITTER, df_usuarios, df_inventario, cargar_datos, cargar_usuarios, generar_kml):
    import os
    
    # DISEÑO DE LA BARRA LATERAL CORPORATIVA
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=140)
        st.markdown("<h2 style='color: #E74C3C; margin-top: 0;'>LEVELPLUS</h2>", unsafe_allow_embedded_html=True)
        st.markdown(f"👤 *{st.session_state.usuario_actual}*\n\n🔹 Rol: {st.session_state.rol_actual}")
        st.markdown("---")
        opc = ["🏠 Panel de Control", "➕ Registrar Caja FAT", "📊 Inventario Completo", "⚙️ Técnicos"] if st.session_state.rol_actual == "Máster" else ["➕ Registrar Caja FAT", "📊 Mis Actividades"]
        sel = st.radio("Módulos del Sistema:", opc)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    df_act = cargar_datos()

    # MÓDULO 1: PANEL DE CONTROL VISUAL CON METRICAS Y MAPA
    if sel == "🏠 Panel de Control":
        st.markdown("<h1 style='color: #2C3E50;'>📊 Panel de Control General</h1>", unsafe_allow_embedded_html=True)
        st.write("Estado de la infraestructura óptica en tiempo real.")
        
        # DISEÑO DE TARJETAS DE COLORES (KPIs)
        total_cajas = len(df_act)
        operativas = len(df_act[df_act["Estado"] == "Operativo"])
        fallas = len(df_act[df_act["Estado"] == "Falla"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label="📦 Cajas FAT Totales", value=total_cajas)
        c2.metric(label="🟢 Cajas Operativas", value=operativas)
        c3.metric(label="🔴 Alertas / Fallas", value=fallas)
        
        st.markdown("---")
        
        # EL MAPA INTERACTIVO
        st.subheader("📍 Georreferenciación de Nodos y Cajas")
        if df_act.empty:
            st.info("No hay datos geográficos registrados aún para mostrar en el mapa.")
        else:
            try:
                map_df = df_act.dropna(subset=["Latitud", "Longitud"])
                map_df["latitude"] = pd.to_numeric(map_df["Latitud"])
                map_df["longitude"] = pd.to_numeric(map_df["Longitud"])
                st.map(map_df, size=22, use_container_width=True)
            except:
                st.warning("Revisa el formato de coordenadas en tu base de datos.")

    # MÓDULO 2: REGISTRO TÉCNICO
    elif sel == "➕ Registrar Caja FAT":
        st.markdown("<h1 style='color: #E74C3C;'>➕ Registro de Nueva Infraestructura</h1>", unsafe_allow_embedded_html=True)
        with st.form("f_fibra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                elem = st.selectbox("Tipo de Elemento", ["Caja FAT / CTO", "Mufa de Empalme", "Poste", "OLT Node"])
                cod = st.text_input("Código Identificador (FAT ID)")
                spl = st.selectbox("Splitter Asignado", TIPOS_SPLITTER)
                cap = st.number_input("Total Puertos", min_value=1, value=16)
                ocu = st.number_input("Puertos Asignados (Ocupados)", min_value=0, value=0)
            with col2:
                coords_juntas = st.text_input("Pegar Coordenadas Completas (GPS)", placeholder="Ej: 10.4806, -66.9036")
                est = st.select_slider("Estado Inicial del Nodo", options=["Operativo", "Mantenimiento", "Falla"])
                not_t = st.text_area("Notas Técnicas / Observaciones")
            
            if st.form_submit_button("💾 DEPOSITAR EN BASE DE DATOS", use_container_width=True):
                if not cod or not coords_juntas: st.error("⚠️ El código y las coordenadas son campos obligatorios.")
                else:
                    try:
                        parts = coords_juntas.split(",")
                        lat_val, lon_val = float(parts[0].strip()), float(parts[1].strip())
                        n_f = {"Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Registrado Por": st.session_state.usuario_
