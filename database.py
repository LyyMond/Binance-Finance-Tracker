from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL
import datetime

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String) # DEPOSIT, P2P_BUY, P2P_SELL
    amount = Column(Float)
    asset = Column(String)
    fiat_amount = Column(Float, nullable=True)
    fiat_asset = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(String) # COMPLETED

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
