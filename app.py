from flask import Flask, render_template, request, send_file
import os
import xml.etree.ElementTree as ET
import pandas as pd

app = Flask(__name__)

# 📌 Carpeta para subir archivos XML
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 📌 Página principal
@app.route("/")
def index():
    return render_template("index.html")

# 📌 Ruta para procesar archivos XML
@app.route("/procesar", methods=["POST"])
def procesar():
    archivos = request.files.getlist("xml_files")
    datos = []

    for archivo in archivos:
        if archivo.filename.endswith(".xml"):
            ruta_xml = os.path.join(app.config["UPLOAD_FOLDER"], archivo.filename)
            archivo.save(ruta_xml)

            try:
                tree = ET.parse(ruta_xml)
                root = tree.getroot()

                folio = root.find(".//cfdi:Comprobante", {"cfdi": "http://www.sat.gob.mx/cfd/4"}).attrib.get("Folio", "No encontrado")
                rfc = root.find(".//cfdi:Emisor", {"cfdi": "http://www.sat.gob.mx/cfd/4"}).attrib.get("Rfc", "No encontrado")
                monto = root.find(".//cfdi:Comprobante", {"cfdi": "http://www.sat.gob.mx/cfd/4"}).attrib.get("Total", "No encontrado")

                datos.append({"Archivo": archivo.filename, "Folio": folio, "RFC": rfc, "Monto": monto})

            except Exception as e:
                return f"❌ Error procesando {archivo.filename}: {e}"

    # 📌 Guardar en Excel
    df = pd.DataFrame(datos)
    archivo_excel = "datos_extraidos.xlsx"
    df.to_excel(archivo_excel, index=False)

    return send_file(archivo_excel, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
