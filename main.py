from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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

# 宣告前端會傳過來的資料格式
class BookingRequest(BaseModel):
    user_line_id: str
    service_ids: List[int]
    date: str
    time: str

@app.get("/")
def read_root():
    tz = os.getenv("TZ", "未設定")
    return {"message": "預約系統後端啟動成功", "timezone": tz}

@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.get("/api/availability")
def get_availability(target_date: str = Query(...)):
    # 目前為測試用固定時段，之後會替換為真實演算法
    slots = ["10:00", "10:30", "11:00", "13:30", "14:00", "15:00", "16:30"]
    return {"date": target_date, "available_slots": slots}

# 🌟 新增：接收預約資料並存入資料庫
@app.post("/api/appointments")
def create_appointment(booking: BookingRequest, db: Session = Depends(get_db)):
    # 1. 檢查這個 LINE 用戶是否來過，沒有就幫他建一筆客戶資料
    user = db.query(models.User).filter(models.User.line_id == booking.user_line_id).first()
    if not user:
        user = models.User(line_id=booking.user_line_id, name="LINE 客戶")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. 將字串時間轉換為 Python 可以理解的時間格式
    start_time = datetime.strptime(f"{booking.date} {booking.time}", "%Y-%m-%d %H:%M")
    
    # 3. 建立主要的預約紀錄
    new_apt = models.Appointment(
        user_id=user.id,
        designer_id=1,  # 預設給老闆 (ID=1)
        start_time=start_time,
        end_time=start_time + timedelta(hours=1) # 暫設皆為一小時
    )
    db.add(new_apt)
    db.commit()
    db.refresh(new_apt)

    # 4. 把預約跟多個「服務項目」綁定起來 (多對多寫入)
    for s_id in booking.service_ids:
        stmt = models.appointment_services.insert().values(appointment_id=new_apt.id, service_id=s_id)
        db.execute(stmt)
    db.commit()

    return {"message": "預約成功！", "appointment_id": new_apt.id}