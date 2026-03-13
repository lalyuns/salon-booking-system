# Developer Manual

## 複製專案到新 Repo 的注意事項

如果你完整複製這份專案並上傳到新的 GitHub repo，以下項目會因為網址改變而需要重新設定。

---

## 一定要改的

### 1. GitHub Pages URL 改變

- 新的前端網址會變成：`https://新帳號.github.io/新repo名稱`
- 需要去 LINE Developers Console → **LIFF** → 把 **Endpoint URL** 改成新網址

### 2. LIFF ID

- LIFF 是綁定在 Endpoint URL 上的，改了 URL 之後 LIFF ID 可能需要重新建立，或直接更新 Endpoint URL 就好
- 確認後要把 `docs/index.html` 裡的 `liffId` 改掉：

```js
const liffId = "新的 LIFF ID";
```

### 3. Render 重新部署

- 新 repo 要重新在 Render 建立一個 Web Service 並連結
- 環境變數要重新填：

| 變數名稱 | 說明 |
|---|---|
| `DATABASE_URL` | MySQL 連線字串 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot 推播用 Token |
| `TZ` | 填 `Asia/Taipei` |

- 部署完會拿到新的 API 網址，要把 `docs/index.html` 裡的 `apiUrl` 改掉：

```js
const apiUrl = "https://新的render網址";
```

### 4. LINE Webhook URL

- LINE Developers Console → **Messaging API** → **Webhook URL** 改成新 Render 的網址：
  ```
  https://新的render網址/webhook
  ```

---

## 不需要重新申請的

| 項目 | 原因 |
|---|---|
| LINE Developers 帳號 | 同一個帳號沿用 |
| Channel Access Token | 跟 repo 無關，繼續用 |
| MySQL 資料庫 | 跟 repo 無關，繼續用 |
| Rich Menu | 跟 repo 無關，繼續用 |

---

## 整理：需要改動的檔案

| 檔案 | 改什麼 |
|---|---|
| `docs/index.html` | `liffId`、`apiUrl` |
| LINE Developers Console | LIFF Endpoint URL、Webhook URL |
| Render | 重新建立服務、填環境變數 |
