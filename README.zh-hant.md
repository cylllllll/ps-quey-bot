[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-hant.md)

# Notion PS+ Game Query Bot (繁體中文)

一個輕量級的 Telegram 機器人，用於查詢你個人的 Notion 資料庫中的 PlayStation Plus 遊戲領取記錄。

## 功能特點
- **資料庫查詢**: 直接從 Notion 獲取遊戲的領取日期和狀態。
- **隱私優先**: 設計為在本地或私有 VPS 上運行，通過環境變數管理敏感資訊。
- **存取控制**: 通過配置設定白名單，支援群組和個人用戶區分管理。
- **自然互動**: 支援直接 @Bot 或回覆訊息進行查詢，無需輸入指令。
- **分頁顯示**: 查詢結果超過 5 條自動開啟分頁模式。
- **健壯性**: 包含完善的異常處理機制，保障服務穩定性。

## 前置準備
1. **Telegram Bot Token**: 通過 [BotFather](https://t.me/botfather) 建立機器人並獲取 Token。
2. **Notion 整合**:
   - 在 [Notion Developers](https://www.notion.so/my-integrations) 建立 Integration。
   - 將你的 Notion 資料庫與該 Integration 共用。
   - 獲取 **Integration Internal Token** 和 **Database ID**。

## 快速安裝
1. **複製代碼**:
   ```bash
   git clone <your-repo-url>
   cd bot-notion
   ```
2. **環境變數配置**: 複製 `config.example` 到 `.env`，填入你的 Token 和 ID。

## Docker 部署
1. **建構映像**: `docker build -t notion-bot .`
2. **執行容器**: `docker run -d --name notion-bot --env-file .env --restart unless-stopped notion-bot`

## 指令
- `/start`: 檢查機器人狀態。
- `/query <遊戲名稱>`: 搜尋資料庫中的遊戲。
- `/help`: 查看幫助。
