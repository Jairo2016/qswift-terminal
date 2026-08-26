# Q-SWIFT Terminal — web público

Terminal soberana Q-SWIFT V8.2 desplegable en la nube: consulta de saldos y **transacciones reales** (QFC)
con registro en ledger JSON (hash-encadenado) y ancla opcional en QFChain.

## Desplegar en Render (gratis, ~5 min)

1. Sube esta carpeta a un repo de GitHub (p. ej. `qswift-terminal`).
2. https://render.com → **New** → **Web Service** → conecta el repo.
3. Config: Runtime `Python 3` · Build `pip install -r requirements.txt` ·
   Start `gunicorn qswift_app:app --bind 0.0.0.0:$PORT`.
4. **Deploy**. Render te da una URL pública permanente: `https://<nombre>.onrender.com`.

## Desplegar en PythonAnywhere (gratis)

- Upload `qswift_app.py`, `qswift_ledger_vivo.json` y `templates/` a tu cuenta →
  WSGI apuntando a `qswift_app:app` → URL `https://<usuario>.pythonanywhere.com`.

## Endpoints

| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Terminal Q-SWIFT |
| `/get_balance/<user>` | GET | Saldo de un ciudadano |
| `/join_network` | POST | Login / registro (usuario, PIN, ID) |
| `/transfer` | POST | Transferencia real (from_user, to_user, amount, pin, note) |
| `/get_history/<user>` | GET | Historial de movimientos |
| `/network_status` · `/peace_status` · `/latest_joy` · `/chat` | GET/POST | Estado del sistema |

## Variables de entorno (opcionales)

- `QFCHAIN_RPC` — RPC del nodo QFChain para anclar (por defecto `http://127.0.0.1:8545`).
- `QF_VALIDADOR` / `QF_GENESIS` — billeteras del ancla.

## Ledger

`qswift_ledger_vivo.json` — usuarios, PINs, identidades y bloques (hash encadenado).
Génesis QFCoin: bloques 347-348 Q-SWIFT · 20M QFC · PDF `25fd6066…`.
