# CarBiz 訂單 bot setup

架構、決策與檔案結構寫在 `~/.claude-personal/plans/abstract-jingling-dragon.md`；
這份是「照這個順序做」的操作手冊。

**架構回顧**：LINE → cloudflared tunnel → 本機 Node HTTP server (bot/)
→ spawn `claude -p` → sheets.py 讀寫 Google Sheets → LINE push 回覆。
完全沒有雲端邏輯，Cloudflare 只是隧道服務。

## 一、Google Sheets service account（GCP）

1. 開一個 GCP project（或用現有的），啟用 **Google Sheets API** 與 **Google Drive API**。
2. IAM → Service Accounts → Create service account，名字隨意（例：`carbiz-bot`）。
   建立後點進去 → Keys → Add key → Create new key → JSON。下載到本機。
3. 把下載的 JSON 移到 `~/.carbiz/service-account.json`（`mkdir ~/.carbiz` 先）。
   權限收緊：`chmod 600 ~/.carbiz/service-account.json`。
4. 記下 service account 的 email（形如 `carbiz-bot@<project>.iam.gserviceaccount.com`）。
5. 進 Google Drive，把「CarBiz 訂單」folder 點右鍵 → **Share** → 把上面那個 email
   加為 Editor。記下 folder ID（URL 裡 `/folders/<這一段>`）。

## 二、LINE Official Account（LINE Developers Console）

1. https://developers.line.biz/console/ → Provider → 建 Messaging API channel。
2. Basic settings → 拿 **Channel secret**。
3. Messaging API → **Channel access token (long-lived)** → issue。
4. Messaging API → Webhook：先留空，等 tunnel URL 拿到再填。
5. Messaging API → 關掉「Auto-reply messages」與「Greeting messages」。
6. 加 bot 為好友，等 setup 完能傳訊測試。

## 三、Cloudflared tunnel

Cloudflared 免費、穩定、不需要自己有網域也能跑（快速隧道）。生產用建議
用具名隧道 + 自己的網域，本機開發用快速隧道就夠。

```bash
brew install cloudflared

# --- 快速隧道（開發用，URL 每次重啟會換）---
cloudflared tunnel --url http://localhost:8787
# 印出的 https://xxxxx.trycloudflare.com 拿去貼 LINE webhook

# --- 具名隧道（正式用，URL 固定）---
cloudflared tunnel login              # 瀏覽器選一個 CF 上的 zone
cloudflared tunnel create carbiz      # 產生 ~/.cloudflared/<uuid>.json
cloudflared tunnel route dns carbiz carbiz.你的網域
cat > ~/.cloudflared/config.yml <<YAML
tunnel: carbiz
credentials-file: /Users/carlox/.cloudflared/<uuid>.json
ingress:
  - hostname: carbiz.你的網域
    service: http://localhost:8787
  - service: http_status:404
YAML
cloudflared tunnel run carbiz
# LINE webhook 填 https://carbiz.你的網域/api/line/webhook
```

沒有自己網域可以擋一下：先用快速隧道，等頻繁 URL 變化受不了再申請具名。

## 四、本機 bot

```bash
cd bot/
npm install

cp .env.example .env
# 編輯 .env 填 LINE secret/token、SHEETS_FOLDER_ID
# ADMIN_LINE_USER_IDS 可先留空、跑起來後從 log 撈自己的 userId 再回填

npm run start
# 應該看到:
#   [carbiz-bot] listening on http://127.0.0.1:8787
#   [carbiz-bot] LINE webhook path: /api/line/webhook
```

裝成 launchd agent（開機自動啟動）：

```bash
cp bot/launchd/me.carlox.carbiz-bot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/me.carlox.carbiz-bot.plist
tail -f ~/Library/Logs/carbiz-bot.log
```

## 五、Python 工具（sheets 存取）

```bash
cd worker/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 第一次跑：產生 sheets-map 快取，讓 Claude 開場就知道 folder 結構
SHEETS_SERVICE_ACCOUNT_JSON=/Users/carlox/.carbiz/service-account.json \
SHEETS_FOLDER_ID=<你的 folder id> \
  python3 tools/sheets_map.py
```

`worker/tools/sheets.py` 是 Claude 執行時直接呼叫的 CLI，不需要單獨啟動。

## 六、端到端驗證

1. bot + tunnel 都啟動中
2. LINE 打「hi」→ 1:1 應該看到「打字中…」動畫；群組會回「收到,處理中…」
3. `tail -f ~/Library/Logs/carbiz-bot.log` 應該看到 `[task xxxxxxxx] start:`
4. 幾秒後 LINE 收到 bot 的回覆
5. 用非白名單帳號 → bot 回「您沒有權限使用這個機器人。」

## 七、更新 sheets-map（新增了 sheet、換了欄位）

```bash
cd worker && source .venv/bin/activate && python3 tools/sheets_map.py
```

之後可以加一個 launchd calendarInterval 每 6 小時自動跑。

## 常見問題

- **tunnel 快速隧道 URL 每次換**：正式用具名隧道，快速隧道只適合驗證期。
- **`claude` 找不到**：`.env` 的 `CLAUDE_BIN` 填絕對路徑，例如 `/usr/local/bin/claude`。
- **權限錯誤（Sheets）**：確認 folder share 對象是 SA email，不是你自己的 email。
- **loading 動畫沒出現**：只有 1:1 私聊有；群組退回文字「收到」。
