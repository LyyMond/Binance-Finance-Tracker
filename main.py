from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import init_db, get_db, Transaction
from gmail_parser import fetch_and_parse_emails
import os
import json

app = FastAPI(title="Binance Tracker")

# Ensure templates directory exists for Jinja
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    tx_all = db.query(Transaction).order_by(Transaction.date.desc()).all()
    
    # Sumamos P2P_SELL unicamente para los gastos (liberación de criptomonedas)
    total_deposits = sum(tx.amount for tx in tx_all if tx.type == "DEPOSIT")
    total_p2p = sum(tx.amount for tx in tx_all if tx.type == "P2P_SELL")
    
    # Preparar datos para el frontend (JavaScript)
    tx_list = []
    for tx in tx_all:
        if not tx.date:
            continue
        # month_key format: YYYY-MM
        month_key = tx.date.strftime('%Y-%m')
        tx_list.append({
            "date_str": tx.date.strftime('%y-%m-%d %H:%M'),
            "month_key": month_key,
            "type": tx.type,
            "amount": tx.amount,
            "asset": tx.asset
        })
        
    tx_json = json.dumps(tx_list)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "total_deposits": total_deposits,
            "total_p2p": total_p2p,
            "tx_json": tx_json
        }
    )

@app.post("/api/sync")
async def sync_emails(db: Session = Depends(get_db)):
    result = fetch_and_parse_emails(db)
    return result

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    txs = db.query(Transaction).all()
    return {"transactions": len(txs)}
