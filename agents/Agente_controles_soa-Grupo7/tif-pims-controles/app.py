import os
from flask import Flask, jsonify, request, send_file
from agents.controles import AgenteControles
from exportar_soa_docx import generar_documento_soa

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
knowledge_dir = os.path.join(BASE_DIR, "knowledge")

app = Flask(__name__, static_folder=static_dir, static_url_path="")
controles = AgenteControles(carpeta=knowledge_dir)

# Soporte CORS sin dependencias externas
@app.after_request
def habilitar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.get("/")
def inicio():
    return app.send_static_file("index.html")

@app.route("/api/controles/catalogo", methods=["GET", "OPTIONS"])
def catalogo():
    if request.method == "OPTIONS":
        return "", 204
    return jsonify(controles.catalogo)

@app.route("/api/controles/ejecutar", methods=["POST", "OPTIONS"])
def ejecutar():
    if request.method == "OPTIONS":
        return "", 204
    entrada = request.get_json(silent=True) or {}
    return jsonify(controles.ejecutar(entrada))

@app.route("/api/controles/exportar-docx", methods=["POST", "OPTIONS"])
def exportar_docx():
    if request.method == "OPTIONS":
        return "", 204
    entrada = request.get_json(silent=True) or {}
    if "datos" in entrada and "soa" in entrada["datos"]:
        datos_soa = entrada["datos"]
    elif "soa" in entrada:
        datos_soa = entrada
    else:
        res = controles.ejecutar(entrada)
        datos_soa = res.get("datos", {})

    ruta_archivo = os.path.join(BASE_DIR, "Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx")
    generar_documento_soa(datos_soa, ruta_salida=ruta_archivo)
    return send_file(
        ruta_archivo,
        as_attachment=True,
        download_name="Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if __name__ == "__main__":
    import os
    puerto = int(os.environ.get("PORT", 5000))
    print(f"Servidor Agente de Controles iniciado en http://127.0.0.1:{puerto}")
    app.run(host="0.0.0.0", port=puerto, debug=True)
