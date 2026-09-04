from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import init_db, get_db, Transaction
from gmail_parser import fetch_and_parse_emails
import os

app = FastAPI(title="Binance Tracker")

# Ensure templates directory exists for Jinja
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    txs = db.query(Transaction).order_by(Transaction.date.desc()).limit(10).all()
    
    total_deposits = sum(tx.amount for tx in db.query(Transaction).filter(Transaction.type == "DEPOSIT").all())
    total_p2p_buy = sum(tx.amount for tx in db.query(Transaction).filter(Transaction.type == "P2P_BUY").all())
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "transactions": txs,
            "total_deposits": total_deposits,
            "total_p2p_buy": total_p2p_buy
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
