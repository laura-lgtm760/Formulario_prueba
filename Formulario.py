import streamlit as st
import pandas as pd
import io  # <-- Esto sirve para fabricar el archivo en la memoria RAM
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.title("Formulario de Registro de Parcelas")

# =========================================================
# FUNCION PARA ENVIAR EL EMAIL LEYENDO DE LA MEMORIA RAM
# =========================================================
def enviar_excel_por_correo(nombre_usuario, df_datos):
    try:
        # LEEMOS LOS DATOS SEGUROS DESDE LA CAJA FUERTE (SECRETS)
        correo_emisor = st.secrets["CORREO_EMISOR"]
        contraseña_emisor = st.secrets["CONTRASEÑA_EMISOR"]
        correo_receptor = st.secrets["CORREO_RECEPTOR"]

        msg = MIMEMultipart()
        msg['From'] = correo_emisor
        msg['To'] = correo_receptor
        msg['Subject'] = f"Nuevo formulario de parcelas: {nombre_usuario}"
        
        cuerpo = f"Hola,\n\nSe han recibido nuevas parcelas del usuario {nombre_usuario}.\nAdjunto encontrarás su archivo Excel."
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        # TRUCO DE GOOGLE: Convertimos el DataFrame a Excel dentro de la memoria RAM (un "buffer" de bytes)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_datos.to_excel(writer, index=False)
        buffer_excel.seek(0)
        
        # Adjuntamos el archivo virtual directamente al correo
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(buffer_excel.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={nombre_usuario}.xlsx")
        msg.attach(part)
        
        # Envío a través del servidor de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(correo_emisor, contraseña_emisor)
        server.sendmail(correo_emisor, correo_receptor, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")
        return False

# =========================================================
# MEMORIA DE LA SESIÓN (Para acumular parcelas temporalmente)
# =========================================================
if "nombre_guardado" not in st.session_state:
    st.session_state.nombre_guardado = ""
if "telefono_guardado" not in st.session_state:
    st.session_state.telefono_guardado = ""
if "mostrar_boton_otra" not in st.session_state:
    st.session_state.mostrar_boton_otra = False
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False
if "contador_form" not in st.session_state:
    st.session_state.contador_form = 0
# Aquí acumulamos las parcelas en la memoria RAM de la sesión del usuario actual
if "lista_parcelas" not in st.session_state:
    st.session_state.lista_parcelas = []

# Pantalla de finalización
if st.session_state.finalizado:
    st.success("🎉 ¡Formulario completado! Muchas gracias.")
    st.info("Los datos han sido procesados y enviados por correo correctamente.")
    if st.button("Registrar un nuevo usuario"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# =========================================================
# FORMULARIO DE ENTRADA
# =========================================================
with st.form(key=f"formulario_parcela_{st.session_state.contador_form}", enter_to_submit= False):
    st.subheader("Datos Personales")
    nombre = st.text_input("Nombre completo:", value=st.session_state.nombre_guardado)
    telefono = st.text_input("Teléfono:", value=st.session_state.telefono_guardado)
    
    st.subheader("Datos de la Parcela")
    municipio = st.text_input("Municipio:")
    cod_mun = st.number_input("Código municipio:", step=1, value=0)
    poligono = st.number_input("Polígono:", step=1, value=0)
    parcela = st.number_input("Parcela:", step=1, value=0)
    recinto = st.number_input("Recinto:", step=1, value=0)
    super_ha = st.number_input("Superficie (Ha):", min_value=0.0, step=0.01)
    cultivo_anterior = st.text_input("Cultivo anterior:")
    cultivo_posterior = st.text_input("Cultivo posterior:")
    observaciones = st.text_input("Notas / Observaciones:")
    
    enviado = st.form_submit_button("Guardar esta Parcela")

if enviado:
    if not nombre or not municipio:
        st.error("Rellene nombre y municipio")
    else:
        st.session_state.nombre_guardado = nombre
        st.session_state.telefono_guardado = telefono
        
        nueva_fila = {
            "Nombre": nombre, "Teléfono": telefono, "Municipio": municipio,
            "Código Municipio": cod_mun, "Polígono": poligono, "Parcela": parcela,
            "Recinto": recinto, "Superficie Ha": super_ha,
            "Cultivo Anterior": cultivo_anterior, "Cultivo Posterior": cultivo_posterior,
            "Observaciones": observaciones
        }
        
        # Guardamos la parcela en la lista de la memoria RAM del navegador del usuario
        st.session_state.lista_parcelas.append(nueva_fila)
        
        st.toast(f"¡Parcela de {municipio} guardada temporalmente!")
        st.session_state.mostrar_boton_otra = True
        st.rerun()

# Botones de acción tras guardar
if st.session_state.mostrar_boton_otra:
    st.info(f"Has guardado {len(st.session_state.lista_parcelas)} parcela(s). ¿Qué deseas hacer?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Añadir otra Parcela"):
            st.session_state.contador_form += 1
            st.session_state.mostrar_boton_otra = False
            st.rerun()
    with col2:
        if st.button("Terminar y Enviar"):
            # Convertimos la lista de parcelas que tenemos en la RAM a un DataFrame
            df_final = pd.DataFrame(st.session_state.lista_parcelas)
            
            with st.spinner("Enviando datos por correo..."):
                exito = enviar_excel_por_correo(st.session_state.nombre_guardado, df_final)
            if exito:
                st.session_state.finalizado = True
                st.rerun()