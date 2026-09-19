import re
from datetime import datetime
from imap_tools import MailBox, AND
from config import GMAIL_USER, GMAIL_PASSWORD
from database import Transaction

def fetch_and_parse_emails(db_session):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        return {"status": "error", "message": "Faltan credenciales de Gmail"}
    
    parsed_count = 0
    try:
        with MailBox('imap.gmail.com').login(GMAIL_USER, GMAIL_PASSWORD) as mailbox:
            # Buscar correos de Binance
            # Usualmente vienen de directmail.binance.com o binance.com
            for msg in mailbox.fetch(AND(from_="binance"), limit=50, reverse=True):
                # Verificar si ya existe el email_id en la base de datos
                exists = db_session.query(Transaction).filter(Transaction.email_id == msg.uid).first()
                if exists:
                    continue
                
                text_content = msg.text or msg.html
                
                tx_type = None
                amount = 0.0
                asset = ""
                
                # Parseo de Depósitos
                # Ej: "Tu depósito de 109 USDC ya está disponible en tu cuenta de Binance."
                deposit_match = re.search(r'Tu dep[oó]sito de\s*([\d\.,]+)\s*([A-Za-z0-9]+)\s*ya est[aá] disponible', text_content, re.IGNORECASE)
                if deposit_match:
                    tx_type = "DEPOSIT"
                    amount_str = deposit_match.group(1).replace(',', '')
                    amount = float(amount_str)
                    asset = deposit_match.group(2).upper()
                
                # Parseo de Órdenes P2P
                # Ej: "El comprador ha marcado la orden P2P 0272 por la cantidad de 3.14 USDT como pagada."
                elif not deposit_match:
                    p2p_match = re.search(r'por la cantidad de\s*([\d\.,]+)\s*([A-Za-z0-9]+)', text_content, re.IGNORECASE)
                    if p2p_match and "P2P" in text_content:
                        amount_str = p2p_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        asset = p2p_match.group(2).upper()
                        
                        # Si el correo nos pide liberar (el comprador marcó como pagado), nosotros estamos vendiendo.
                        if "libera las criptomonedas" in msg.subject.lower() or "el comprador" in text_content.lower():
                            tx_type = "P2P_SELL"
                        else:
                            # Asumimos compra si dice el vendedor ha liberado o similar
                            tx_type = "P2P_BUY"

                if tx_type:
                    new_tx = Transaction(
                        email_id=msg.uid,
                        date=msg.date,
                        type=tx_type,
                        amount=amount,
                        asset=asset,
                        status="COMPLETED"
                    )
                    db_session.add(new_tx)
                    parsed_count += 1
            
            db_session.commit()
            return {"status": "success", "parsed": parsed_count}
    except Exception as e:
        return {"status": "error", "message": str(e)}
