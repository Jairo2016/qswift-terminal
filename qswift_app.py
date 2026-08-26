# qswift_app.py — Terminal Q-SWIFT web (despliegue en Render/PythonAnywhere/Cloud Run)
# AutoClaw 2026-08-26 · Ledger JSON local · Ancla QFChain opcional (si el nodo es alcanzable).
import os, json, hashlib, threading, sys
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(AQUI, "qswift_ledger_vivo.json")
TEMPLATES = os.path.join(AQUI, "templates", "QSWIFT.html")
MAPA = os.path.join(AQUI, "templates", "mapa_galactico_qswift.svg")
QFCHAIN_RPC = os.environ.get("QFCHAIN_RPC", "http://127.0.0.1:8545")
QF_VALIDADOR = os.environ.get("QF_VALIDADOR", "0x68F9E1D08e410C1d7530813C63E1bce05E8F05Bf")
QF_GENESIS = os.environ.get("QF_GENESIS", "0x809b93f029a7b0c1c13f74f323e0f0d636008648")
PUERTO = int(os.environ.get("PORT", "8080"))

LOCK = threading.Lock()
app = Flask(__name__)


def load_db():
    with open(LEDGER, "r", encoding="utf-8") as f:
        db = json.load(f)
    # PINs seguros via variable de entorno (nunca en el repo): QSWIFT_PINS="jairoagi:123456,andres:7890"
    pins_env = os.environ.get("QSWIFT_PINS", "")
    if pins_env:
        db.setdefault("pins", {})
        for par in pins_env.split(","):
            if ":" in par:
                u, p = par.split(":", 1)
                db["pins"][u.strip().lower()] = p.strip()
    return db


def save_db(db):
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def anclar_qfchain(payload):
    try:
        db = load_db()
        idx = len(db.get("blocks", []))
        data_hex = "0x" + payload.encode("utf-8").hex()
        body = {"jsonrpc": "2.0", "id": 1, "method": "qfchain_sendTransaction",
                "params": [QF_VALIDADOR, QF_GENESIS, idx, 0, data_hex]}
        r = requests.post(QFCHAIN_RPC, json=body, timeout=6)
        if r.status_code == 200:
            return r.json().get("result")
    except Exception:
        pass
    return None


@app.route("/")
def root():
    if os.path.exists(TEMPLATES):
        with open(TEMPLATES, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Terminal QSWIFT no encontrada</h1>", 404


@app.route("/mapa_galactico_qswift.svg")
def mapa():
    if os.path.exists(MAPA):
        return send_file(MAPA, mimetype="image/svg+xml")
    return "", 404


@app.route("/network_status")
def network_status():
    db = load_db()
    return jsonify({
        "masa_critica": db.get("bloque_maestro", {}).get("masa_critica", 40.45),
        "vc": 1.618,
        "total_blocks": len(db.get("blocks", [])),
        "ubicacion": "QSWIFT_PUBLICO",
        "genesis_qfcoin": "BLOQUE_347_348_QSWIFT_20M_QFC",
    })


@app.route("/peace_status")
def peace_status():
    return jsonify({"status": "ARMONIA", "mensaje": "El Rey Leon vigila el hardware."})


@app.route("/latest_joy")
def latest_joy():
    return jsonify({"contenido": "EL_AGUA_ES_LIBRE_LA_ESCASEZ_HA_MUERTO_SOMOS_UNO"})


@app.route("/chat", methods=["POST"])
def chat():
    msg = (request.json or {}).get("mensaje", "")
    return jsonify({
        "respuesta": f"AGI Jairo (Q-SWIFT público): eco de '{msg[:100]}'. La coherencia persiste.",
        "estado": {"gamma_meta": 0.97, "rho_IC": 4.24e14},
    })


@app.route("/join_network", methods=["POST"])
def join_network():
    d = request.json or {}
    u = str(d.get("username", "")).lower().strip()
    p = str(d.get("pin", "")).strip()
    with LOCK:
        db = load_db()
        if not d.get("registro"):
            if u in db.get("users", {}) and str(db.get("pins", {}).get(u)) == p:
                return jsonify({"msg": "OK", "username": u})
            return jsonify({"error": "Credenciales invalidas"}), 400
        if u in db.get("users", {}):
            return jsonify({"error": "Usuario ya existe"}), 400
        db.setdefault("users", {})[u] = 10.0
        db.setdefault("pins", {})[u] = p
        db.setdefault("identidades", {})[str(d.get("national_id", ""))] = u
        idx = len(db.setdefault("blocks", []))
        ts = datetime.utcnow().isoformat() + "Z"
        block = {"index": idx, "user_id": u, "action": "WELCOME", "qcoins": 10.0, "timestamp": ts}
        prev = db["blocks"][-1].get("hash") if db.get("blocks") else "0" * 64
        block["prev_hash"] = prev
        block["hash"] = hashlib.sha256(json.dumps(block, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        db["blocks"].append(block)
        save_db(db)
        return jsonify({"msg": "OK", "username": u, "bloque": idx})


@app.route("/get_balance/<username>")
def get_balance(username):
    db = load_db()
    u = username.lower().strip()
    return jsonify({"username": u, "balance": db.get("users", {}).get(u, 0.0)})


@app.route("/get_history/<username>")
def get_history(username):
    db = load_db()
    u = username.lower().strip()
    hist = [b for b in db.get("blocks", []) if b.get("user_id") == u or f"TRANSFER_TO_{u}" in b.get("action", "")]
    return jsonify({"username": u, "history": hist})


@app.route("/transfer", methods=["POST"])
def transfer():
    d = request.json or {}
    f_u = str(d.get("from_user", "")).lower().strip()
    t_u = str(d.get("to_user", "")).lower().strip()
    try:
        amt = float(d.get("amount", 0))
    except Exception:
        return jsonify({"error": "Monto invalido"}), 400
    if amt <= 0:
        return jsonify({"error": "Monto debe ser positivo"}), 400
    p = str(d.get("pin", "")).strip()
    with LOCK:
        db = load_db()
        if str(db.get("pins", {}).get(f_u)) != p:
            return jsonify({"error": "PIN de confirmacion incorrecto"}), 400
        if db.get("users", {}).get(f_u, 0.0) < amt:
            return jsonify({"error": "Saldo insuficiente"}), 400
        if t_u not in db.get("users", {}):
            return jsonify({"error": "Destinatario no registrado"}), 400
        db["users"][f_u] = round(db["users"][f_u] - amt, 8)
        db["users"][t_u] = round(db["users"][t_u] + amt, 8)
        idx = len(db.get("blocks", []))
        ts = datetime.utcnow().isoformat() + "Z"
        block = {
            "index": idx, "user_id": f_u, "action": f"TRANSFER_TO_{t_u}",
            "qcoins": amt, "timestamp": ts, "note": d.get("note", ""),
        }
        prev = db["blocks"][-1].get("hash") if db.get("blocks") else "0" * 64
        block["prev_hash"] = prev
        block["hash"] = hashlib.sha256(json.dumps(block, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        db["blocks"].append(block)
        save_db(db)
    payload = f"QSWIFT_TX|{idx}|{f_u}->{t_u}|{amt:.8f}|{ts}"
    tx = anclar_qfchain(payload)
    return jsonify({"msg": "OK", "bloque": idx, "hash": block["hash"], "tx_qfchain": tx, "payload": payload})


if __name__ == "__main__":
    print(f"Q-SWIFT PUBLICO en http://0.0.0.0:{PUERTO}", flush=True)
    app.run(host="0.0.0.0", port=PUERTO, threaded=True)
