
import streamlit as st
import random
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

st.set_page_config(page_title="Generador de Rifa", page_icon="🎟️")

st.title("🎟️ Generador de Números de Rifa")
st.markdown("#### ganaconuliseslaguaira.com")

nombre = st.text_input("🧑 Nombre del participante")
cantidad = st.number_input("🔢 Cantidad de números (1 a 10000)", min_value=1, max_value=10000, step=1)

if st.button("🎰 Generar números de rifa"):
    if not nombre.strip():
        st.error("⚠️ Debes ingresar el nombre del participante.")
    else:
        numeros = random.sample(range(10000), cantidad)
        numeros_formateados = [f"{n:04d}" for n in numeros]

        # --- Guardar en Excel ---
        archivo_excel = "rifa.xlsx"
        nueva_fila = pd.DataFrame([{
            "Nombre": nombre,
            "Cantidad": cantidad,
            "Números": ", ".join(numeros_formateados),
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        }])

        if os.path.exists(archivo_excel):
            df_existente = pd.read_excel(archivo_excel)
            df_total = pd.concat([df_existente, nueva_fila], ignore_index=True)
        else:
            df_total = nueva_fila

        df_total.to_excel(archivo_excel, index=False)

        # --- Generar PDF ---
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

        nombre_pdf = f"Rifa_{nombre.replace(' ', '_')}.pdf"
        pdf.output(nombre_pdf)

        st.success(f"✅ ¡Números generados con éxito!")
        st.write(f"📄 Se generó el PDF: `{nombre_pdf}`")
        st.write(f"📊 Registro actualizado en `{archivo_excel}`")

        with open(nombre_pdf, "rb") as f:
            st.download_button("⬇️ Descargar PDF", f, file_name=nombre_pdf)
