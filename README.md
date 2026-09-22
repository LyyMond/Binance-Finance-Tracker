# Binance Finance Tracker

Aplicación personal de aprendizaje que convierte los correos de Binance en un dashboard financiero local. Conecta Gmail (o cualquier servidor IMAP) vía TLS, extrae depósitos y operaciones P2P usando expresiones regulares, los persiste en SQLite y los visualiza en una UI estilo monitor construida con FastAPI.

Demostración del proyecto.


https://github.com/user-attachments/assets/5289eaa5-0b4f-4d84-9219-e7ec8010f1be


El objetivo del proyecto es aprender a recolectar datos desde correos electrónicos (protocolo IMAP), procesarlos con regex y presentarlos en una aplicación web local.

## Características

- Conexión IMAP segura (TLS) usando App Password: nunca se usa la contraseña real del correo.
- Detección automática de depósitos y operaciones P2P (compra y venta) mediante expresiones regulares.
- Normalización de montos: las stablecoins (USDT, USDC) se suman como equivalentes en USD para mantener totales estándar.
- Persistencia en SQLite con UID único por correo: sin duplicados entre sincronizaciones.
- Filtro por mes 100% del lado del cliente (JavaScript): instantáneo, sin recargar la pagina.
- Botón "Sincronizar Datos" conectado al endpoint `POST /api/sync`. No hace falta reiniciar el servidor.
- Servidor local únicamente (`127.0.0.1`).

## Stack

Python 3.11 - FastAPI - Uvicorn - SQLAlchemy - SQLite - imap-tools - Jinja2 - JavaScript (fetch API)

## Quickstart

```bash
git clone https://github.com/<TU_USUARIO>/Binance-Finance-Tracker.git
cd Binance-Finance-Tracker

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # rellena tus credenciales
python -c "from database import init_db; init_db()"   # crea binance_tracker.db

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Abre http://127.0.0.1:8000 y pulsa "Sincronizar Datos". Tambien puedes sincronizar por consola:

```bash
curl -X POST http://127.0.0.1:8000/api/sync
```

## Configuracion (.env)

```
GMAIL_USER=tu_correo@gmail.com
GMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # App Password de Google (requiere 2FA activado)
```

Para Gmail necesitas la verificación en dos pasos activada y una App Password generada en https://myaccount.google.com/apppasswords. Si usas otro proveedor IMAP (Outlook, Yahoo, Zoho), cambia el host en `gmail_parser.py` (linea 13).

## Como funciona (resumen)

1. `gmail_parser.py` abre una sesión TLS contra `imap.gmail.com` y busca correos cuyo remitente contiene "binance" en las carpetas INBOX y pagos.
2. Las regex extraen cantidad y activo de cada correo y clasifican la operación: `DEPOSIT`, `P2P_BUY` o `P2P_SELL`.
3. Cada correo se guarda como una fila `Transaction` en SQLite, usando el UID del mensaje como clave anti-duplicados.
4. La ruta `/` renderiza `templates/index.html`. El filtro de mes y las estadísticas se calculan en el navegador a partir de un único JSON que llega del backend.

Por defecto se procesan máximo 20 correos por sincronización (configurable en `gmail_parser.py`, `limit=20`).

## Estructura

```
binance_tracker/
|- main.py             # FastAPI: ruta / y endpoint /api/sync
|- gmail_parser.py     # IMAP + regex + clasificacion
|- database.py         # Modelo SQLAlchemy Transaction + init_db()
|- config.py           # Carga de variables de entorno
|- templates/index.html
|- requirements.txt
|- .env                # (ignorado por git)
```

## Limitaciones

- Las regex dependen del texto exacto de los correos de Binance en español; los correos en ingles no se detectan.
- Solo se maneja USD como moneda fiat.
- Sin conversión a USD de criptomonedas distintas a stablecoins.
- Máximo 20 correos por sincronización (configurable).
- Exchange/Office 365 via MAPI no soportado (requeriria otra libreria, por ejemplo exchangelib o Microsoft Graph).

## Roadmap

- Gráfica de evolución mensual (Chart.js)
- Export a CSV
- Tests para las regex
- Endpoint `/api/stats` con agregación por mes

## Licencia

MIT

---

## English (short version)

Personal learning project that turns Binance notification emails into a local financial dashboard. It connects to Gmail (or any standard IMAP server) over TLS, extracts deposits and P2P trades with regular expressions, stores them in SQLite and displays them through a FastAPI + Jinja2 monitor-style UI. Stablecoin amounts (USDT/USDC) are normalized as USD so totals stay consistent.

Setup: clone, create a venv, `pip install -r requirements.txt`, fill `.env` with a Gmail App Password, initialize the DB, run uvicorn and press "Sincronizar Datos" (or `curl -X POST /api/sync`). Month filtering runs client-side in JavaScript with no page reload. Regexes match Binance emails in Spanish only; other IMAP providers work by changing one line in `gmail_parser.py`.

Personal learning project that turns Binance notification emails into a local financial dashboard. It connects to Gmail (or any standard IMAP server) over TLS, extracts deposits and P2P trades with regular expressions, stores them in SQLite and displays them through a FastAPI + Jinja2 monitor-style UI. Stablecoin amounts (USDT/USDC) are normalized as USD so totals stay consistent.

Setup: clone, create a venv, `pip install -r requirements.txt`, fill `.env` with a Gmail App Password, initialize the DB, run uvicorn and press "Sincronizar Datos" (or `curl -X POST /api/sync`). Month filtering runs client-side in JavaScript with no page reload. Regexes match Binance emails in Spanish only; other IMAP providers work by changing one line in `gmail_parser.py`.
