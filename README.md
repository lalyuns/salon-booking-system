# salon-booking-system

## 系統概述

整合 LINE LIFF 與 FastAPI 的美髮自動化預約系統。

## 技術堆疊

* 前端：LINE LIFF (GitHub Pages)
* 後端：Python FastAPI (Render / Zeabur)
* 資料庫：MySQL (Aiven)
* 通訊：LINE Messaging API

## 核心邏輯

* 運算單位：底層 5 分鐘，前端顯示 30 分鐘間隔。
* 預約規則：需提前 24 小時預約或取消。
* 服務機制：支援多選服務，自動加總時長並過濾可用時段。

## 資料庫結構

* **users**: LINE ID 與客戶資料。
* **designers**: 設計師清單。
* **services**: 服務項目與耗時。
* **appointments**: 預約主檔 (時段、狀態)。
* **appointment_services**: 預約與服務關聯表。

## 主要 API

* `GET /api/services`: 取得服務選單。
* `GET /api/availability`: 查詢特定日期可用時段。
* `POST /api/appointments`: 建立預約並發送 LINE 通知。
* `DELETE /api/appointments/{id}`: 取消預約 (含 24h 限制邏輯)。

## 環境變數 (.env)

* `LINE_CHANNEL_SECRET`
* `LINE_CHANNEL_ACCESS_TOKEN`
* `LIFF_ID`
* `DATABASE_URL`
