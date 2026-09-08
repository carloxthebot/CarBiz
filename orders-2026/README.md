# 2026 年度採購分析

`index.html` 是一頁式靜態網頁，把訂單帳本 158 個品項按類別、品牌、車型拆解，
並附各品牌官方網站與 22 項的官方正式品名與產品照。直接用瀏覽器打開就是成品。

## 重新產生

```bash
python3 analyze.py      # 訂單帳本 → analysis.json（分類、品牌、車型、客戶代號）
python3 build_repo.py   # analysis.json + links.json + products.json → index.html
```

`analyze.py` 讀的是 `worker/state/data/新_訂單.json`（由 `worker/tools/sheets_map.py`
從 Google Sheets 快取而來），所以要先跑過那支才有資料。

## 資料檔

| 檔案 | 內容 |
|---|---|
| `analysis.json` | 分類後的品項（analyze.py 產生，不要手改） |
| `links.json` | 品牌官網與產品頁（人工查證，每個 URL 都實際抓取過） |
| `products.json` | 官方正式品名、產品圖網址、與帳本落差的註記 |
| `img/` | 產品照，取自各製造商官網後縮到 640px |

## 客戶去識別

帳本的品名欄混著產品、客戶暱稱與備註。`customers.py` 把人名抽出來換成固定代號
（C01–C16），**發佈出去的頁面不含任何真名**，對照表只在本機帳本裡。

兩個容易踩的坑寫在 `customers.py` 的 docstring：`GS-FUJI` 是 TWS 的顏色代碼不是客戶
FUJI；`(皓.土.陽+菁*1+豆腐2+預備)` 是一筆多人分帳，逐字刪人名會留下 `1+2+預備`
這種殘骸，所以整組收成代號。

## 已知的資料落差

`products.json` 裡的 `note` 欄記錄查證時發現的帳本與官方不一致，頁面上以 ⚠ 顯示。
最值得追的三筆：

- 料號 `ECYDYVNH`（¥682,801）在 ENDLESS 官方目錄查無此號
- `ＥＣＺＤＹＶＭＧ` 是全形字打的，且官方為 `ECZ8ZVMG` 或 `ECYDYVMG`
- 帳本的 `CROWNCROSS` 不是品牌，是 Toyota Crown Crossover 這台車；品牌其實是 MODELLISTA
