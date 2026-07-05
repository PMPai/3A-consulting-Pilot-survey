# AI 導入需求評估系統 (3A-consulting-Pilot-survey)

> 協助中小企業以合理成本邁出 AI 導入第一步
> 三階段顧問服務中的 **Stage 1 需求評估** 數位化問卷與 ROI 分析平台

---

## 目錄

1. [系統簡介](#系統簡介)
2. [模組說明](#模組說明)
3. [啟動方式](#啟動方式)
4. [流程分支與合流建模](#流程分支與合流建模)
5. [ROI 計算方式（重點）](#roi-計算方式重點)
6. [評分制對照表](#評分制對照表)
7. [Stage 2 門檻條件](#stage-2-門檻條件)
8. [API 概覽](#api-概覽)
9. [資料備份](#資料備份)

---

## 系統簡介

本系統為顧問公司提供 **Stage 1 部門調研問卷** 的數位化平台，取代傳統紙本/Excel 評估流程。

### 三階段服務架構

| 階段 | 主導方 | 週期 | 本系統涵蓋 |
|:---|:---|:---|:---:|
| **Stage 1** 需求評估 | 顧問公司 | 4-6 週 | ✅ |
| **Stage 2** 先導導入 | 顧問公司 | 2-3 個月 | — |
| **Stage 3** 擴展陪伴 | 客戶公司 | 6 個月+ | — |

### 兩個使用入口

- **客戶端** (`/client/survey`)：填寫 9 頁分步驟問卷，盤點工作流程、上傳 SOP/流程圖
- **顧問端** (`/consultant/dashboard`)：檢視所有問卷、ROI 試算、Stage 2 門檻檢核、4 種圖表分析

### 設計理念

- **全評分制 (1-5 分)**：捨棄精確數字填寫，降低填寫門檻；系統內建「評分→金額」對照表自動換算
- **口語化用詞**：每題附引導舉例（例：「1=還在用紙本 / 3=一半紙本一半電腦 / 5=全部都在電腦系統裡」）
- **自動暫存**：每換頁即自動儲存至 SQLite，不需手動存檔
- **流程分支建模**：支援決策點、多分支條件、合流回主流程的完整建模
- **無認證**：內網部署，無需登入；客戶/顧問透過不同 URL 進入

---

## 模組說明

```
3A-consulting-Pilot-survey/
├── backend/                      後端（FastAPI + SQLite）
│   ├── main.py                   App 入口，掛載路由與靜態檔案（port 3535）
│   ├── database.py               SQLite 連線設定、SessionLocal、Base
│   ├── models.py                 12 張資料表 ORM（全評分制 INTEGER 1-5）
│   ├── schemas.py                Pydantic 輸入驗證 schema
│   ├── routers/
│   │   ├── surveys.py            問卷 CRUD + /full 完整巢狀資料匯整
│   │   ├── processes.py          工作流程 / 步驟 / 分支 / 附件上傳 / 錯誤成本
│   │   ├── meta.py               機會成本 / AI 準備度 / 期望
│   │   ├── roi.py                ROI 試算（評分→金額→年度效益）
│   │   └── gate.py               Stage 2 門檻 7 項自動檢核
│   ├── uploads/                  SOP / 流程圖實體檔案儲存目錄
│   └── survey.db                 SQLite 資料庫（啟動時自動建立 + 自動遷移）
│
├── frontend/                     前端（HTML + Bootstrap + Chart.js）
│   ├── index.html                入口頁（選擇客戶端 / 顧問端）
│   ├── client/
│   │   └── survey.html           客戶端問卷（9 頁分步驟、1-5 星評分、附件上傳、分支建模）
│   └── consultant/
│       ├── dashboard.html        顧問端總覽（樹狀導覽 + 搜尋 + 狀態統計）
│       └── detail.html           顧問端詳情（4 種圖表 + ROI 試算 + 門檻檢核 + 分支樹 + 結論）
│
├── start.bat                     一鍵啟動（建 venv、裝套件、開瀏覽器）
└── README.md                      本文件
```

### 後端資料表（12 張）

| 資料表 | 用途 | 主要欄位 |
|:---|:---|:---|
| `surveys` | 問卷主表 | company, dept_name, respondent_name, status |
| `processes` | 工作流程 | name, purpose, hours_score, rate_score (1-5) |
| `process_details` | 流程詳述 | automation_current, exception_handling |
| `process_steps` | 流程步驟逐項 | step_name, tool_used, judgment_level, is_decision, is_merge, branch_id |
| `step_branches` | 步驟分支定義 | branch_no, condition_desc, merge_to_step_no, is_endpoint |
| `process_uploads` | 附件 | filename, original_name, mime, size |
| `error_costs` | 錯誤成本 | err_count_score, err_cost_score (1-5) |
| `opportunity_costs` | 機會成本 | delay_loss_score, lost_opp_score, extra_rev_score (1-5) |
| `ai_readiness_scores` | AI 準備度 | r1~r8 (各 1-5) |
| `expectations` | 期望 | expected_saving_score, budget_range |
| `roi_calculations` | ROI 計算結果 | time/error/opp cost_yearly, saving_pct, benefit |
| `stage2_gate_checks` | 門檻檢核 | 7 項 boolean + conclusion + pilot 建議 |

### 顧問端圖表（4 種，Chart.js）

| 圖表 | 類型 | 用途 |
|:---|:---|:---|
| 流程潛在效益比較 | Bar Chart | 多流程年度效益並列比較 |
| AI 導入準備度 | Radar Chart | R1-R8 八項評分雷達 |
| 效益 vs 難度 | Scatter Chart | 流程定位（含四象限概念） |
| 成本結構比較 | Stacked Bar | 時間/錯誤/機會成本堆疊 |

---

## 啟動方式

### 方式一：一鍵啟動（推薦）

```bat
雙擊 start.bat
```

`start.bat` 會自動完成：
1. 檢查 Python 3.9+ 是否安裝
2. 建立虛擬環境 `backend/.venv`（首次執行）
3. 安裝相依套件（首次執行）
4. 啟動 uvicorn 伺服器於 `http://localhost:3535`
5. 自動開啟瀏覽器

### 方式二：手動啟動

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 3535
```

### 前置需求

- **Python 3.9+**（[下載](https://www.python.org/downloads/)）
- 任何現代瀏覽器（Chrome / Edge / Firefox）
- 無需外網連線（CDN 載入 Bootstrap/Chart.js 需首次有網路，之後可離線）

### 相依套件

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
sqlalchemy==2.0.27
python-multipart==0.0.9
```

---

## 流程分支與合流建模

業務流程常含「決策點」：一個步驟依條件分岔到不同後續路徑，最終再合流回主流程。本系統支援完整的 **Fork-Join** 建模。

### 三個角色

| 角色 | 標記 | 說明 |
|:---|:---|:---|
| **決策點 (Fork)** | 步驟勾「☑ 決策點」 | 此步驟會依條件分岔，需定義多個分支 |
| **分支 (Branch)** | 決策點下的子記錄 | 每分支 = 一個條件 + 合流去向 |
| **合流點 (Join)** | 步驟勾「☑ 合流點」 | 多個分支在此步驟會合，繼續主流程 |

### 分支欄位

每個分支包含：

| 欄位 | 說明 | 範例 |
|:---|:---|:---|
| `branch_no` | 分支序號 | 1, 2, 3... |
| `condition_desc` | 分支條件描述 | 「評分 ≥ 700」 |
| `merge_to_step_no` | 合流回主流程的步驟號 | 9（即步驟 9） |
| `is_endpoint` | 是否為流程結束點（不合流） | True / False |
| `next_action_text` | 自由文字備註 | 「轉至其他部門」 |

### 分支子步驟

分支條件成立後執行的中間步驟，靠 `process_steps.branch_id` 標示歸屬：
- `branch_id = NULL` → 主流程步驟
- `branch_id = <branch_id>` → 屬於該分支的子步驟

### 範例流程

```
主流程：
  [1] 收件
  [2] 初步審核
  [3] 評分                    ← 決策點
      ├─ 分支 1: 評分 ≥ 700  → 合流至步驟 9
      │     [4] 快速通關       ← branch_id = 分支1
      │     [5] 系統建檔       ← branch_id = 分支1
      ├─ 分支 2: 600-699     → 合流至步驟 9
      │     [6] 人工審核       ← branch_id = 分支2
      │     [7] 主管覆核       ← branch_id = 分支2
      └─ 分支 3: < 600       → [結束點]
            [8] 退件通知       ← branch_id = 分支3
  [9] 發通知                   ← 合流點（分支 1、2 在此會合）
  [10] 結案
```

### 客戶端 UI

在「流程詳述」頁的每個步驟 row 上：
1. 勾「☑ 決策點」→ 下方展開分支編輯區
2. 每分支一行：條件輸入 + 「合流至」下拉（選主流程步驟號）+ 「☑ 結束點」checkbox
3. 勾「結束點」時合流至改為灰色（代表此分支不合流）
4. 分支的子步驟：在主列表加步驟，並在「歸屬」下拉選擇該分支

### 顧問端呈現

```
步驟 3: 評分 [決策點] (半判斷 · ERP)
  ├─ 分支1：評分 ≥ 700 → 合流至步驟 9
  ├─ 分支2：600-699    → 合流至步驟 9
  └─ 分支3：< 600      → [結束]

步驟 4: 快速通關 [分支1] (純規則 · ERP)
步驟 5: 系統建檔 [分支1] (純規則 · CRM)
步驟 6: 人工審核 [分支2] (半判斷 · Excel)
步驟 7: 主管覆核 [分支2] (高度經驗 · 紙本)
步驟 8: 退件通知 [分支3] (純規則 · Email)

步驟 9: 發通知 [合流點] (純規則 · Email) ← 2 個分支在此合流
```

### 對 ROI 評估的加值

- **決策點數量 + 分支數量**：可量化流程複雜度（越多分支越難自動化）
- **分支條件是否明確**：輔助判斷 R4 規則明確度
- **是否有合流點**：自動化時需處理多路徑結果彙整，影響導入難度

### 向後相容

- 啟動時自動 ALTER TABLE 為既有 `process_steps` 補 `is_decision` / `is_merge` / `branch_id` 欄位
- 舊資料 `is_decision=False`、`is_merge=False`、`branch_id=NULL`，完全不影響原有功能

---

## ROI 計算方式（重點）

### 核心公式

```
年度潛在效益 = (年度時間成本 + 年度錯誤成本 + 年度機會成本) × 預期節省比例
```

### 三大成本計算

#### ① 年度時間成本

```
年度時間成本 = 月工時 × 時薪 × 12
```

由流程的 `hours_score` (1-5) 與 `rate_score` (1-5) 換算：

| hours_score | 月工時 (h) | | rate_score | 時薪 (NT$/h) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 10 | | 1 | 200 |
| 2 | 25 | | 2 | 300 |
| 3 | 50 | | 3 | 400 |
| 4 | 75 | | 4 | 500 |
| 5 | 100 | | 5 | 600 |

> **範例**：hours_score=4 (75h), rate_score=3 ($400) → 年度時間成本 = 75 × 400 × 12 = **$360,000**

#### ② 年度錯誤成本

```
年度錯誤成本 = 月錯誤次數 × 單次處理成本 × 12
```

由 `err_count_score` 與 `err_cost_score` (各 1-5) 換算：

| err_count_score | 月錯誤次數 | | err_cost_score | 單次成本 (NT$) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 1 | | 1 | 500 |
| 2 | 3 | | 2 | 2,000 |
| 3 | 8 | | 3 | 5,000 |
| 4 | 15 | | 4 | 10,000 |
| 5 | 25 | | 5 | 20,000 |

> **範例**：err_count=3 (8次), err_cost=2 ($2,000) → 年度錯誤成本 = 8 × 2,000 × 12 = **$192,000**

#### ③ 年度機會成本

```
年度機會成本 = (延遲損失/月 + 推掉機會/月 + 額外營收/月) × 12
```

由問卷的 `opportunity_costs` 三項評分 (各 1-5) 換算：

| score | delay_loss_score<br>延遲損失/月 | lost_opp_score<br>推掉機會/月 | extra_rev_score<br>額外營收/月 |
|:---:|:---:|:---:|:---:|
| 1 | 1,000 | 0 | 0 |
| 2 | 5,000 | 5,000 | 10,000 |
| 3 | 15,000 | 20,000 | 50,000 |
| 4 | 40,000 | 50,000 | 150,000 |
| 5 | 100,000 | 150,000 | 500,000 |

> **範例**：delay_loss=3 ($15k), lost_opp=2 ($5k), extra_rev=2 ($10k) → 年度機會成本 = (15,000 + 5,000 + 10,000) × 12 = **$360,000**

### 預期節省比例

由問卷「期望」頁的 `expected_saving_score` (1-5) 換算：

| expected_saving_score | 節省比例 |
|:---:|:---:|
| 1 | 10% |
| 2 | 30% |
| 3 | 50% |
| 4 | 70% |
| 5 | 90% |

### 完整試算範例

| 項目 | 評分 | 換算值 | 計算 |
|:---|:---:|:---:|:---|
| hours_score | 4 | 75 h/月 | — |
| rate_score | 3 | $400/h | — |
| err_count_score | 3 | 8 次/月 | — |
| err_cost_score | 2 | $2,000/次 | — |
| delay_loss_score | 3 | $15,000/月 | — |
| lost_opp_score | 2 | $5,000/月 | — |
| extra_rev_score | 2 | $10,000/月 | — |
| expected_saving_score | 4 | 70% | — |
| **年度時間成本** | | | 75 × 400 × 12 = **$360,000** |
| **年度錯誤成本** | | | 8 × 2,000 × 12 = **$192,000** |
| **年度機會成本** | | | (15k+5k+10k) × 12 = **$360,000** |
| **總成本** | | | 360k + 192k + 360k = $912,000 |
| **年度潛在效益** | | | 912,000 × 70% = **$638,400** |

### 顧問端可調整

顧問端 ROI 表格中可直接修改 `saving_pct`（節省比例），點「重新試算 ROI」即可重算所有流程。系統會：
1. 依修改後的 saving_pct 重算 `annual_potential_benefit`
2. 依效益高低重新排序 `priority`（優先序 1 = 效益最高）

### 導入難度與準備度分數

ROI 結果另計三項輔助分數（供門檻檢核用）：

| 分數 | 計算方式 |
|:---|:---|
| `difficulty_score` | (R1..R7 平均 × 7 + (6 - R8)) / 8，越高代表越難導入 |
| `rule_clarity_score` | R4 規則明確度（1-5） |
| `data_readiness_score` | (R1 + R2 + R3) / 3 資料準備度（1-5） |

---

## 評分制對照表

完整 1-5 分對照表整理：

| 評分 | 月工時 | 時薪 | 錯誤次數 | 錯誤成本 | 延遲損失 | 推掉機會 | 額外營收 | 節省比例 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 10h | $200 | 1 | $500 | $1k | $0 | $0 | 10% |
| 2 | 25h | $300 | 3 | $2,000 | $5k | $5k | $10k | 30% |
| 3 | 50h | $400 | 8 | $5,000 | $15k | $20k | $50k | 50% |
| 4 | 75h | $500 | 15 | $10,000 | $40k | $50k | $150k | 70% |
| 5 | 100h | $600 | 25 | $20,000 | $100k | $150k | $500k | 90% |

**問卷引導舉例**（節錄）：
- 時間花費：1=很少（10h 內） / 3=中等（50h） / 5=很多（80h+）
- 薪資等級：1=工讀生時薪 / 3=一般職員 / 5=資深主管
- 錯誤頻率：1=幾乎不出錯 / 3=偶爾會錯 / 5=常常出錯
- 收拾成本：1=改一下就好 / 3=要重做半天 / 5=要賠錢或被客訴
- 延遲損失：1=晚一點也沒差 / 3=會被唸要加班補 / 5=會丟客戶或被罰款
- 推掉業務：1=從來沒有 / 3=偶爾推掉 / 5=常常推掉且金額不小
- 預期節省：1=只省一點點(<20%) / 3=省一半 / 5=幾乎全交給它(>80%)

---

## Stage 2 門檻條件

系統自動檢核 7 項門檻，全部通過才建議進入 Stage 2：

| 門檻 | 標準 | 對應欄位 |
|:---|:---|:---|
| 年度潛在效益 | ≥ NT$500,000 | max(roi.annual_potential_benefit) |
| 導入難度 | ≤ 3.5 / 5 | difficulty_score |
| 規則明確度 (R4) | ≥ 3 / 5 | ai_readiness.r4_rule_clarity |
| 資料準備度 | ≥ 3 / 5 | avg(R1, R2, R3) |
| 高層支持 (R7) | ≥ 4 / 5 | ai_readiness.r7_leadership_support |
| 合規風險 (R8) | ≤ 3 / 5 | ai_readiness.r8_compliance_risk |
| 預算與效益匹配 | 是 | expectations.budget_range |

**結論**：`suitable`（適合）/ `not_suitable`（不適合）
**Pilot 建議**：系統自動推薦效益最高的流程，顧問可手動覆寫。

---

## API 概覽

| Method | Path | 說明 |
|:---|:---|:---|
| POST | `/api/surveys` | 建立問卷 |
| GET | `/api/surveys` | 列出所有問卷 |
| GET | `/api/surveys/{id}` | 取得單筆問卷 |
| PUT | `/api/surveys/{id}` | 更新問卷 |
| DELETE | `/api/surveys/{id}` | 刪除問卷 |
| GET | `/api/surveys/{id}/full` | 取得完整巢狀資料（顧問端用） |
| POST | `/api/surveys/{id}/processes` | 新增工作流程 |
| PUT | `/api/processes/{id}` | 更新流程 |
| DELETE | `/api/processes/{id}` | 刪除流程 |
| POST | `/api/processes/{id}/detail` | 新增/更新流程詳述 |
| POST | `/api/processes/{id}/steps` | 新增流程步驟（含 is_decision/is_merge/branch_id） |
| PUT | `/api/steps/{step_id}` | 更新步驟（用於設定 branch_id） |
| GET | `/api/processes/{id}/steps` | 列出步驟 |
| POST | `/api/steps/{step_id}/branches` | 新增分支（條件 + 合流點 + 結束點） |
| GET | `/api/steps/{step_id}/branches` | 列出該決策點所有分支 |
| DELETE | `/api/branches/{branch_id}` | 刪除分支（含子步驟清空 branch_id） |
| POST | `/api/processes/{id}/uploads` | 上傳 SOP/流程圖（multipart） |
| GET | `/api/processes/{id}/uploads` | 列出附件 |
| GET | `/api/uploads/{id}/download` | 下載附件 |
| DELETE | `/api/uploads/{id}` | 刪除附件 |
| POST | `/api/processes/{id}/error_costs` | 新增/更新錯誤成本 |
| POST | `/api/surveys/{id}/opportunity_costs` | 新增/更新機會成本 |
| POST | `/api/surveys/{id}/ai_readiness` | 新增/更新 AI 準備度 |
| POST | `/api/surveys/{id}/expectations` | 新增/更新期望 |
| POST | `/api/roi` | ROI 試算（score 或 manual 模式） |
| GET | `/api/surveys/{id}/rois` | 列出該問卷所有 ROI |
| POST | `/api/gate` | 門檻檢核 + 結論儲存 |

完整互動式 API 文文檔：啟動後開啟 `http://localhost:3535/docs`（Swagger UI）

---

## 資料備份

資料儲存於兩處，複製即可備份：

```
backend/survey.db      ← SQLite 資料庫（所有問卷資料）
backend/uploads/       ← 上傳的 SOP / 流程圖實體檔案
```

**還原方式**：停止伺服器 → 覆蓋上述兩處 → 重啟即可。

---

## 常見問題

### Q: 啟動時出現「找不到 Python」？
A: 請安裝 Python 3.9+ 並確認安裝時勾選「Add to PATH」。

### Q: port 3535 被占用？
A: 修改 `start.bat` 中的 `--port 3535` 為其他埠號，或執行 `netstat -ano | findstr :3535` 找出占用程序。

### Q: 中文顯示亂碼？
A: 確保瀏覽器編碼為 UTF-8。`start.bat` 已內建 `chcp 65001` 切換至 UTF-8。

### Q: 評分制能否改回填數字？
A: 可。修改 `frontend/client/survey.html` 將 `.rating` 元件改為 `input[type=number]`，並調整 `backend/routers/roi.py` 的計算邏輯即可。

### Q: 如何建立有分支的流程？
A: 在問卷「流程詳述」頁，於某步驟勾「☑ 決策點」，下方會展開分支編輯區。每個分支填入條件（如「評分 ≥ 700」）、選擇合流至哪個步驟、或勾「結束點」表示該分支結束不合流。分支的子步驟則在主步驟列表新增，並在「歸屬」下拉選擇該分支即可。

### Q: 舊資料會不會受分支功能影響？
A: 不會。啟動時自動為 `process_steps` 補上新欄位，舊步驟 `is_decision=False`、`branch_id=NULL`，行為與之前完全相同。

---

*本系統為顧問服務流程的 Stage 1 數位化實作。*
