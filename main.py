from fastapi import FastAPI
from dotenv import load_dotenv
import os

# 載入 .env 檔案內的環境變數
load_dotenv()

app = FastAPI(title="Salon Booking API")

@app.get("/")
def read_root():
    tz = os.getenv("TZ", "未設定")
    return {"message": "預約系統後端啟動成功", "timezone": tz}