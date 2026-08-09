# 宏觀訊號 · Macro Signals

跨領域訊號的交叉觀察：政策與貿易、供應鏈與系統韌性、技術前沿、區域態勢。中英雙語，術語另建累積式詞彙表。

## 架構

排程 push 到 main 之後由 Cloudflare Pages 自動部署。
資料與版面分離：**排程只寫 JSON，永遠不碰 `index.html`。**

| 檔案 | 誰寫 | 說明 |
|---|---|---|
| `index.html` | 人 | 固定版面，hash 路由 `#/`（開最新一份）、`#/r/{file}`、`#/glossary` |
| `reports/YYYY-MM-DD-{kind}.json` | 排程 | 一次執行一個檔 |
| `manifest.json` | 排程 | 報告索引，**日期新→舊排序** |
| `glossary.json` | 排程 | 累積式術語表，只增不改（已存在的 term 不動） |
| `check.py` | 人 | schema 驗證，commit 前必跑 |

## 三個節奏

| kind | cron (UTC) | 台北時間 | 內容 |
|---|---|---|---|
| `brief` | `0 19 */2 * *` | 每兩天 03:00 | 4–8 條訊號，每條附「對你的意義」 |
| `weekly` | `0 19 * * 0` | 每週一 03:00 | 單一主題深挖 + 反方觀點（`narrative`） |
| `monthly` | `0 19 1 * *` | 每月 2 日 03:00 | 上月趨勢全局 + `actions` |

## Schema

`reports/*.json`：

```jsonc
{
  "date": "2026-08-11",
  "kind": "brief",                       // brief | weekly | monthly
  "title":  {"zh": "…", "en": "…"},
  "focus":  {"zh": "…", "en": "…"},      // 一句話總結，同時當推播訊息
  "sections": [{
    "id": "nexus",                       // nexus 交叉 | cyber 系統 | military 態勢 | geo 政策 | tech 技術
    "items": [{
      "severity":   "high",              // critical | high | medium | warning | info
      "confidence": "likely",            // confirmed | likely | unverified
      "title":       {"zh": "…", "en": "…"},
      "summary":     {"zh": "…", "en": "…"},
      "implication": {"zh": "…", "en": "…"},   // 「這對你意味什麼」，必填
      "counterpoint":{"zh": "…", "en": "…"},   // 選填，週報必附
      "source": "Reuters",
      "url": "https://…",
      "terms": ["EDR"]                   // 必須都存在於 glossary.json
    }]
  }],
  "narrative": {"zh": "…", "en": "…"},   // weekly / monthly 必填
  "actions":   [{"zh": "…", "en": "…"}]  // monthly 必填，2–5 條
}
```

`glossary.json`：

```jsonc
{"updated": "2026-08-11", "terms": [{
  "term": "EDR",
  "zh": "端點偵測與回應",
  "expansion": "Endpoint Detection and Response",
  "def": {"zh": "…", "en": "…"},
  "category": "cyber",                   // military | cyber | geo | tech
  "first_seen": "2026-08-11"
}]}
```

## 驗證

```bash
python3 check.py     # 通過才准 commit
```
