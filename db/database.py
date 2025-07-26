import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = "postgresql://neondb_owner:npg_FUt8daBwkoj5@ep-frosty-base-a8sizobb-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    print("Ok")
    Base.metadata.create_all(bind=engine)