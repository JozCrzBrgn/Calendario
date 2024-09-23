
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from config.configuration import config, read_json_from_supabase

#* USER AUTHENTICATION
credenciales = read_json_from_supabase(config.BUCKET_GENERAL, config.CREDENCIALES_FILE)
authenticator = stauth.Authenticate(
    credenciales,
    st.secrets["COOKIE_NAME"],
    st.secrets["COOKIE_KEY"],
    int(st.secrets["COOKIE_EXPIRY_DAYS"]),
)
name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username ands password')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenida {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Reporte de Ventas")

    sucursal = st.radio("Selecciona un sucursal", ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán"])
    fecha = st.date_input("Selecciona una fecha")

    tabla_inv_db = {
        "Agrícola Oriental":"db04_inventario_agri", 
        "Nezahualcóyotl":"db04_inventario_neza", 
        "Zapotitlán":"db04_inventario_zapo", 
        "Oaxtepec":"db04_inventario_oaxt", 
        "Pantitlán":"db04_inventario_panti"
        }
    tabla_tks_db = {
        "Agrícola Oriental":"db05_tickets_agri", 
        "Nezahualcóyotl":"db05_tickets_neza", 
        "Zapotitlán":"db05_tickets_zapo", 
        "Oaxtepec":"db05_tickets_oaxt", 
        "Pantitlán":"db05_tickets_panti"
        }
    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    cols_inv = "clave,producto,fecha_estatus,hora_estatus,no_ticket"
    data_inv = config.supabase.table(tabla_inv_db[sucursal]).select(cols_inv).eq("fecha_estatus", fecha).execute().data
    cols_tks = "no_ticket,nombre_cajero"
    data_tks = config.supabase.table(tabla_tks_db[sucursal]).select(cols_tks).eq("fecha", fecha).execute().data
    # Creamos los Dataframe
    df_inv = pd.DataFrame(data_inv)
    df_tks = pd.DataFrame(data_tks)
    # Renombrar la columna 'tipo_combo' a 'promocion'
    df_inv.rename(columns={'fecha_estatus': 'fecha_venta', 'hora_estatus': 'hora_venta'}, inplace=True)
    if df_inv.empty!=False:
        st.warning(f"La sucursal de {sucursal} no tiene ventas para la fecha {fecha}.")
    else:
        # Realizar el merge entre df_inv y df_ventas en base a la columna 'no_ticket'
        df_new = pd.merge(df_inv, df_tks, on='no_ticket')
        # Seleccionar las columnas del nuevo DataFrame
        df_new = df_new[['clave', 'nombre_cajero', 'producto', 'fecha_venta', 'hora_venta']]
        # Asegurarse de que la columna esté en formato de tiempo
        df_new['hora_venta'] = pd.to_datetime(df_new['hora_venta'], format='%H:%M:%S').dt.time
        # Ordenamos por hora de venta
        df_sorted = df_new.sort_values(by=['hora_venta'])
        st.table(df_sorted)