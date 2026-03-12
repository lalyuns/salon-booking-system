from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests as http_requests

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

class BookingRequest(BaseModel):
    user_line_id: str
    service_ids: List[int]
    date: str
    time: str


# ── 選項 C：LINE 通知輔助函式 ─────────────────────────────────────────────────
def send_line_notification(user_line_id: str, appointment: models.Appointment):
    """預約成功後，推送 LINE Flex Message 給客人"""
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    if not token or token == "your_token_here":
        return  # 未設定 token，靜默略過，不影響預約流程

    service_names = "、".join([s.name for s in appointment.services]) or "未選擇"
    date_str = appointment.start_time.strftime("%Y 年 %m 月 %d 日")
    time_str = appointment.start_time.strftime("%H:%M")

    flex_message = {
        "type": "flex",
        "altText": f"💈 預約成功！您的預約時間是 {date_str} {time_str}",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#00B900",
                "paddingAll": "15px",
                "contents": [
                    {
                        "type": "text",
                        "text": "💈 預約成功！",
                        "color": "#ffffff",
                        "weight": "bold",
                        "size": "xl",
                        "align": "center"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "📅 日期", "color": "#aaaaaa", "size": "sm", "flex": 2},
                            {"type": "text", "text": date_str, "color": "#333333", "size": "sm", "flex": 3, "wrap": True}
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "⏰ 時間", "color": "#aaaaaa", "size": "sm", "flex": 2},
                            {"type": "text", "text": time_str, "color": "#333333", "size": "sm", "flex": 3}
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "✂️ 服務", "color": "#aaaaaa", "size": "sm", "flex": 2},
                            {"type": "text", "text": service_names, "color": "#333333", "size": "sm", "flex": 3, "wrap": True}
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "期待您的光臨！✨",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "align": "center"
                    }
                ]
            }
        }
    }

    try:
        res = http_requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"to": user_line_id, "messages": [flex_message]},
            timeout=5
        )
        print(f"[LINE NOTIFY] status={res.status_code} body={res.text}")
    except Exception as e:
        print(f"[LINE NOTIFY] error={e}")


# ── 基礎路由 ──────────────────────────────────────────────────────────────────
@app.post("/webhook")
async def line_webhook(request: Request):
    """LINE Messaging API Webhook — 印出 user ID 方便測試"""
    body = await request.json()
    for event in body.get("events", []):
        user_id = event.get("source", {}).get("userId", "")
        print(f"[WEBHOOK] LINE User ID: {user_id}")
    return {"status": "ok"}


@app.get("/")
def read_root():
    tz = os.getenv("TZ", "未設定")
    return {"message": "預約系統後端啟動成功", "timezone": tz}


@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


# ── 選項 B：智慧時段演算法 ────────────────────────────────────────────────────
@app.get("/api/availability")
def get_availability(target_date: str = Query(...), db: Session = Depends(get_db)):
    """動態生成可用時段：排除已被預約佔用的時間區間"""

    # 1. 產生當天 10:00~18:00 每 30 分鐘一格的所有時段
    all_slots = []
    current = datetime.strptime(f"{target_date} 10:00", "%Y-%m-%d %H:%M")
    end_of_business = datetime.strptime(f"{target_date} 18:00", "%Y-%m-%d %H:%M")
    while current < end_of_business:
        all_slots.append(current)
        current += timedelta(minutes=30)

    # 2. 查詢當天所有有效預約
    day_start = datetime.strptime(f"{target_date} 00:00", "%Y-%m-%d %H:%M")
    day_end   = datetime.strptime(f"{target_date} 23:59", "%Y-%m-%d %H:%M")
    booked = db.query(models.Appointment).filter(
        models.Appointment.start_time >= day_start,
        models.Appointment.start_time <= day_end,
        models.Appointment.status == "active"
    ).all()

    # 3. 過濾：若某時段與任何現有預約有重疊就移除
    available = []
    for slot in all_slots:
        slot_end = slot + timedelta(minutes=30)
        conflict = any(
            slot < apt.end_time and slot_end > apt.start_time
            for apt in booked
        )
        if not conflict:
            available.append(slot.strftime("%H:%M"))

    return {"date": target_date, "available_slots": available}


# ── 建立預約（選項 C：預約後推送 LINE 通知）───────────────────────────────────
@app.post("/api/appointments")
def create_appointment(booking: BookingRequest, db: Session = Depends(get_db)):
    # 1. 檢查或建立用戶
    user = db.query(models.User).filter(models.User.line_id == booking.user_line_id).first()
    if not user:
        user = models.User(line_id=booking.user_line_id, name="LINE 客戶")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. 時間格式轉換
    start_time = datetime.strptime(f"{booking.date} {booking.time}", "%Y-%m-%d %H:%M")

    # 3. 取得設計師 ID
    boss = db.query(models.Designer).first()
    boss_id = boss.id if boss else 1

    # 4. 建立預約並綁定服務
    new_apt = models.Appointment(
        user_id=user.id,
        designer_id=boss_id,
        start_time=start_time,
        end_time=start_time + timedelta(hours=1)
    )
    selected_services = db.query(models.Service).filter(
        models.Service.id.in_(booking.service_ids)
    ).all()
    new_apt.services = selected_services

    db.add(new_apt)
    db.commit()
    db.refresh(new_apt)

    # 5. 推送 LINE 預約成功通知
    send_line_notification(booking.user_line_id, new_apt)

    return {"message": "預約成功！", "appointment_id": new_apt.id}


# ── 選項 A：查詢我的預約 ──────────────────────────────────────────────────────
@app.get("/api/appointments")
def get_user_appointments(user_line_id: str = Query(...), db: Session = Depends(get_db)):
    """回傳指定 LINE 用戶的所有有效預約"""
    user = db.query(models.User).filter(models.User.line_id == user_line_id).first()
    if not user:
        return []

    appointments = db.query(models.Appointment).filter(
        models.Appointment.user_id == user.id,
        models.Appointment.status == "active"
    ).order_by(models.Appointment.start_time).all()

    return [
        {
            "id": apt.id,
            "start_time": apt.start_time.strftime("%Y-%m-%d %H:%M"),
            "services": [s.name for s in apt.services],
            "status": apt.status
        }
        for apt in appointments
    ]


# ── 選項 A：取消預約 ──────────────────────────────────────────────────────────
@app.patch("/api/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    user_line_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """將指定預約的狀態改為 cancelled（只有本人可以取消）"""
    user = db.query(models.User).filter(models.User.line_id == user_line_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    apt = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.user_id == user.id,
        models.Appointment.status == "active"
    ).first()
    if not apt:
        raise HTTPException(status_code=404, detail="預約不存在或已取消")

    apt.status = "cancelled"
    db.commit()

    return {"message": "已成功取消預約"}
