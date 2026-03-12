from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# 引入剛寫好的資料庫與模型
from database import get_db
import models

load_dotenv()

app = FastAPI(title="Salon Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    tz = os.getenv("TZ", "未設定")
    return {"message": "預約系統後端啟動成功", "timezone": tz}

# 新增：取得所有服務項目的 API
@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    return services

@app.get("/api/availability")
def get_availability(target_date: str = Query(...)):
    # 測試用假資料：假設這些是當天剩下的可用時段
    slots = ["10:00", "10:30", "11:00", "13:30", "14:00", "15:00", "16:30"]
    return {"date": target_date, "available_slots": slots}