# StratWatch · 戰略視野

網路戰 × 軍事 × 地緣政治 × 新興科技的**交叉點**情報簡報。中英雙語，技術術語另建累積式詞彙表。

網站：https://cyc123456789.github.io/stratwatch/

## 架構

沿用 Daily-Digest 的「資料／版面分離」：**cloud routine 只寫 JSON，永遠不碰 `index.html`。**

| 檔案 | 誰寫 | 說明 |
|---|---|---|
| `index.html` | 人 | 固定版面，hash 路由 `#/`、`#/k/{kind}`、`#/r/{file}`、`#/glossary` |
| `reports/YYYY-MM-DD-{kind}.json` | routine | 一次執行一個檔 |
| `manifest.json` | routine | 報告索引，**日期新→舊排序** |
| `glossary.json` | routine | 累積式術語表，只增不改（已存在的 term 不動） |
| `check.py` | 人 | schema 驗證，commit 前必跑 |

## 三個節奏

| kind | cron (UTC) | 台北時間 | 內容 |
|---|---|---|---|
| `brief` | `0 19 */2 * *` | 每兩天 03:00 | 4–8 條訊號，每條附「對你的意義」 |
| `weekly` | `0 19 * * 0` | 每週一 03:00 | 單一主題深挖 + 反方觀點（`narrative`） |
| `monthly` | `0 19 1 * *` | 每月 2 日 03:00 | 上月趨勢全局 + `actions`（該調整什麼） |

## Schema

`reports/*.json`：

```jsonc
{
  "date": "2026-08-11",
  "kind": "brief",                       // brief | weekly | monthly
  "title":  {"zh": "…", "en": "…"},
  "focus":  {"zh": "…", "en": "…"},      // 一句話總結，同時當推播訊息
  "sections": [{
    "id": "nexus",                       // cyber | military | geo | tech | nexus
    "items": [{
      "severity":   "high",              // critical | high | medium | warning | info
      "confidence": "likely",            // confirmed | likely | unverified
      "title":       {"zh": "…", "en": "…"},
      "summary":     {"zh": "…", "en": "…"},
      "implication": {"zh": "…", "en": "…"},   // 「這對你意味什麼」，必填
      "counterpoint":{"zh": "…", "en": "…"},   // 選填，週報必附
      "source": "Reuters",
      "url": "https://…",
      "terms": ["C4ISR"]                 // 必須都存在於 glossary.json
    }]
  }],
  "narrative": {"zh": "…", "en": "…"},   // weekly / monthly 必填
  "actions":   [{"zh": "…", "en": "…"}]  // monthly 必填，2–5 條
}
```

`glossary.json`：

```jsonc
{"updated": "2026-08-11", "terms": [{
  "term": "C4ISR",
  "zh": "指管通情監偵",
  "expansion": "Command, Control, Communications, Computers, Intelligence, Surveillance and Reconnaissance",
  "def": {"zh": "…", "en": "…"},
  "category": "military",                // military | cyber | geo | tech
  "first_seen": "2026-08-11"
}]}
```

## 驗證

```bash
python3 check.py     # 通過才准 commit
```
