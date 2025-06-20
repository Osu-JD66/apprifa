import streamlit as st
import random
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import io

# Configuración inicial
st.set_page_config(page_title="Generador de Rifa", page_icon="🎟️")
st.title("🎟️ Generador de Números de Rifa")
st.markdown("#### ganaconuliseslaguaira.com")

# Archivos
archivo_excel = "rifa.xlsx"
PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

# Entrada de datos
nombre = st.text_input("🧑 Nombre del participante")
cantidad = st.number_input("🔢 Cantidad de números (1 a 10000)", min_value=1, max_value=10000, step=1)

# Botón generar rifa
if st.button("🎰 Generar números de rifa"):
    if not nombre.strip():
        st.error("⚠️ Debes ingresar el nombre del participante.")
    else:
        cantidad = int(cantidad)

        # Leer números usados
        usados = set()
        if os.path.exists(archivo_excel):
            df_existente = pd.read_excel(archivo_excel)
            if "Números" in df_existente.columns:
                for lista in df_existente["Números"]:
                    for num in str(lista).split(","):
                        usados.add(num.strip())
        else:
            df_existente = pd.DataFrame()

        disponibles = [f"{n:04d}" for n in range(10000) if f"{n:04d}" not in usados]

        if len(disponibles) < cantidad:
            st.error(f"😢 Solo quedan {len(disponibles)} números disponibles.")
            st.stop()

        numeros_formateados = random.sample(disponibles, cantidad)

        # Crear PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "¡Gracias por participar!", ln=1, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Participante: {nombre}", ln=1)

        # Organizar los números en líneas de máximo 10 números por línea
        numeros_por_linea = 12
        lineas_numeros = [
            ", ".join(numeros_formateados[i:i+numeros_por_linea])
            for i in range(0, len(numeros_formateados), numeros_por_linea)
        ]
        texto_numeros = "\n".join(lineas_numeros)
                                  
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Números asignados:\n{texto_numeros}")

        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1)
        pdf.ln(10)

        pdf.set_font("Arial", "I", 12)
        pdf.multi_cell(0, 10, "¡Gracias por confiar en nosotros! Tus números han sido registrados oficialmente para el sorteo.", align="C")
        pdf.ln(15)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "ganaconuliseslaguaira.com", ln=1, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Contacto: salcedocross54@gmail.com | Tel: +58 424-1650376", ln=1, align="C")

        # Guardar PDF
        nombre_pdf = f"Rifa_{nombre.replace(' ', '_')}.pdf"
        ruta_pdf = os.path.join(PDF_FOLDER, nombre_pdf)
        pdf.output(ruta_pdf)

        # Guardar en Excel
        nueva_fila = pd.DataFrame([{
            "Nombre": nombre,
            "Cantidad": cantidad,
            "Números": ", ".join(numeros_formateados),
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Archivo PDF": nombre_pdf
        }])
        df_total = pd.concat([df_existente, nueva_fila], ignore_index=True)
        df_total.to_excel(archivo_excel, index=False)

        # Descargar PDF
        pdf_buffer = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)

        st.success("✅ ¡Números generados con éxito!")

        st.download_button(
            label="📄 Descargar PDF",
            data=pdf_buffer,
            file_name=nombre_pdf,
            mime="application/pdf"
        )

# Borrar registro completo
#if st.button("🗑️ Borrar registro completo y empezar de nuevo"):
   # if os.path.exists(archivo_excel):
       # os.remove(archivo_excel)
        #st.success("✅ Registro borrado correctamente.")
    #else:
       # st.info("ℹ️ No existe ningún registro para borrar.")

# Mostrar historial de participantes
st.markdown("---")
st.markdown("### 📋 Registro de todos los participantes")

if os.path.exists(archivo_excel):
    df_registro = pd.read_excel(archivo_excel)

    # Filtro por nombre
    filtro = st.text_input("🔍 Buscar participante por nombre")
    if filtro:
        df_filtrado = df_registro[df_registro["Nombre"].str.contains(filtro, case=False)]
    else:
        df_filtrado = df_registro

    # Mostrar tabla
    columnas = ["Nombre", "Cantidad", "Números", "Fecha"]
    st.dataframe(df_filtrado[columnas])

    # Total de números asignados
    total_numeros = df_filtrado["Cantidad"].sum()
    st.markdown(f"**🔢 Total de números asignados:** {total_numeros}")

    numero_buscar = st.text_input("🔍 Buscar participante por número de rifa (ejemplo: 0123)")

 if numero_buscar:
    if os.path.exists(archivo_excel):
        df_registro = pd.read_excel(archivo_excel)
        
        # Filtrar filas donde el número esté en la lista de números asignados
        # La columna "Números" contiene cadenas tipo "0001, 0023, 0456"
        df_encontrado = df_registro[df_registro["Números"].apply(
            lambda x: numero_buscar.zfill(4) in [n.strip() for n in str(x).split(",")]
        )]

        if not df_encontrado.empty:
            st.success(f"El número {numero_buscar.zfill(4)} fue asignado a:")
            for _, row in df_encontrado.iterrows():
                st.write(f"- **{row['Nombre']}**, asignado el {row['Fecha']}")
        else:
            st.warning(f"El número {numero_buscar.zfill(4)} no está asignado a ningún participante.")
    else:
        st.info("No hay registros todavía.")


    # Botón para descargar Excel
    excel_output = io.BytesIO()
    df_filtrado.to_excel(excel_output, index=False)
    excel_output.seek(0)

    st.download_button(
        label="📥 Descargar registro completo (Excel)",
        data=excel_output,
        file_name="registro_completo_rifa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Aún no hay registros para mostrar.")

    # Enlaces a los PDF
    # 📂 Mostrar todos los PDF generados en la carpeta /pdfs
    st.markdown("### 📄 Historial de PDFs generados")

    pdfs_disponibles = [
        f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")
    ]

    if pdfs_disponibles:
        for pdf_name in sorted(pdfs_disponibles, reverse=True):
            ruta = os.path.join(PDF_FOLDER, pdf_name)
            with open(ruta, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(
                    label=f"📥 Descargar {pdf_name}",
                    data=pdf_bytes,
                    file_name=pdf_name,
                    mime="application/pdf"
                )
    else:
        st.info("No hay PDFs generados aún.")
