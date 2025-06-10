
import streamlit as st
import random
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import zipfile
import io

st.set_page_config(page_title="Generador de Rifa", page_icon="🎟️")

st.title("🎟️ Generador de Números de Rifa")
st.markdown("#### ganaconuliseslaguaira.com")

nombre = st.text_input("🧑 Nombre del participante")
cantidad = st.number_input("🔢 Cantidad de números (1 a 10000)", min_value=1, max_value=10000, step=1)

if st.button("🎰 Generar números de rifa"):
    if not nombre.strip():
        st.error("⚠️ Debes ingresar el nombre del participante.")
    else:
        cantidad = int(cantidad)
        archivo_excel = "rifa.xlsx"

        # Leer números ya asignados
        usados = set()
        if os.path.exists(archivo_excel):
            df_existente = pd.read_excel(archivo_excel)
            if "Números" in df_existente.columns:
                for lista in df_existente["Números"]:
                    for num in str(lista).split(","):
                        usados.add(num.strip())
        else:
            df_existente = pd.DataFrame()

        # Crear lista de disponibles (0000 a 9999 menos los usados)
        disponibles = [f"{n:04d}" for n in range(10000) if f"{n:04d}" not in usados]

        # Verifica que haya suficientes disponibles
        if len(disponibles) < cantidad:
            st.error(f"😢 Solo quedan {len(disponibles)} números disponibles.")
            st.stop()

        # Elegir números únicos
        numeros_formateados = random.sample(disponibles, cantidad)

        # --- Guardar en Excel ---
        nueva_fila = pd.DataFrame([{
            "Nombre": nombre,
            "Cantidad": cantidad,
            "Números": ", ".join(numeros_formateados),
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        }])

        df_total = pd.concat([df_existente, nueva_fila], ignore_index=True)
        df_total.to_excel(archivo_excel, index=False)

        # --- Generar PDF en memoria ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "¡Gracias por participar!", 0, 1, "C")
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Participante: {nombre}", 0, 1)
        pdf.cell(0, 10, f"Números asignados: {', '.join(numeros_formateados)}", 0, 1)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
        pdf.ln(10)
        pdf.set_font("Arial", "I", 12)
        pdf.multi_cell(0, 10, "¡Gracias por confiar en nosotros! Tus números han sido registrados oficialmente para el sorteo.", 0, "C")
        pdf.ln(15)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "ganaconuliseslaguaira.com", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Contacto: ulinel815@gmail.com | Tel: +58 414-3298246", 0, 1, "C")

        # --- Guardar PDF en memoria ---
        pdf_buffer = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)

        # --- Guardar Excel en memoria ---
        excel_buffer = io.BytesIO()
        df_total.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # --- Guardar en session_state ---
        st.session_state["pdf_data"] = pdf_buffer
        st.session_state["pdf_filename"] = f"Rifa_{nombre.replace(' ', '_')}.pdf"
        st.session_state["excel_data"] = excel_buffer
        st.session_state["excel_filename"] = "rifa.xlsx"

        nombre_pdf = f"Rifa_{nombre.replace(' ', '_')}.pdf"
        pdf.output(nombre_pdf)

        # Mostrar botones de descarga si ya están los archivos generados
        if "pdf_data" in st.session_state and "excel_data" in st.session_state:
            st.success("✅ ¡Números generados con éxito!")
        
            col1, col2 = st.columns(2)
        
            with col1:
                st.download_button(
                    label="📄 Descargar PDF",
                    data=st.session_state["pdf_data"],
                    file_name=st.session_state["pdf_filename"],
                    mime="application/pdf"
                )
        
            with col2:
                st.download_button(
                    label="📊 Descargar Excel",
                    data=st.session_state["excel_data"],
                    file_name=st.session_state["excel_filename"],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
