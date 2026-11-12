from flask import Flask, jsonify

# Cria a aplicação. __name__ diz ao Flask onde está o módulo atual.
app = Flask(__name__)


@app.route("/health")
def health():
    # Endpoint de saúde: o Kubernetes vai usá-lo mais tarde para saber
    # se o container está vivo. Retorna JSON e código HTTP 200.
    return jsonify(status="ok")
