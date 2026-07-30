# Agent 能力狀態報告 v1（繁體中文）

**產生時間：** 2026-07-30T05:30:12Z  
**設計權威來源：** `C:\Project\va-agent-swarm\study\agents.md`（`va-agent-swarm/study/agents.md`）  
**實作 Pack：** `business/video/agents`（非 specials 之 video agents；共 **114** 個）  
**已對應 VA 表格列數：** 114  
**稽覈產物：** `business/video/AGENT_CAPABILITY_AUDIT.json`  
**英文原文報告：** `agent_capability_status_v1.md`

> **誠實準則：** `agents.md` 的設計主張描述的是「目標級」專業多代理製片系統。本報告評分的是 **common host pack 實際存在的內容**（SPEC、sources、tools、prompts、rubrics、graphs）相對於這些主張的落差。**設計文字 ≠ 生產能力。**

---

## 0. 全艦隊執行摘要（十一問）

| # | 問題 | 全艦隊結論 | 證據摘要 |
|---|------|------------|----------|
| 1 | SPEC 中的責任界定 | **大致為「是」** | 114/114 個 agent 具有完整 `## Responsibility` |
| 2 | 專業知識蒸餾計畫 | **部分** | 每個 VA 列皆有 Knowledge Distillation Source；SPEC 嵌入共通結構；持續蒸餾迴路尚未自動化 |
| 3 | 來源存在／可知如何取得 | **部分** | 常見 `sources/`＋PROVENANCE／MAPPING；授權線上語料未完整取得 |
| 4 | 自評方法與內容 | **部分（設計偏重）** | agents.md 自評標準＋SPEC 品質閘門存在；**0/114** 個 agent 有非空 `rubrics/` 檔 |
| 5 | 是否已超越人類 | **否** | **0** 個 agent 在 host 上有通過驗證的人類超越量測。設計中的 surpass 訊號僅屬目標 |
| 6 | 如何執行工作 | **部分 — host 編排** | Graph／DNA＋adapters；**11** 個有 live 媒體工具；**0** 個有已落地 prompt 檔；預設非自主 coding-plan agent |
| 7 | Skills／plugins／harness | **部分（共享 pack skills）** | 存在 `special_skills/` 與 host adapters；每 agent 私有 skill 安裝 harness 大多缺失 |
| 8 | 自我改進機制 | **部分** | SPEC 持續學習＋`max_refinement_count`；閉環 RLAIF／晉升未完整產品化 |
| 9 | 研究以改進之路徑 | **部分** | 來源清單＋研究型 meta agents 已設計；research→eval→promote 未完成 |
| 10 | 協作／指令收發 | **部分** | `critique_edges`＋handoff 設計＋workflow DNA；完整 runtime critique bus 未齊 |
| 11 | 衝突解決與確認 | **部分** | 設計：爭議 → Judge → HiTL；自主解決＋確認未在每 agent 驗證 |

**平均成熟度（0–11）：** **6.45**  
**儲存格計數（114×11）：** 是=330，部分=810，否=114

### 全艦隊關鍵缺口（重新思考／改進）

1. **Prompt 尚未落地** — 每 agent 有 `prompt_reference`，但 **0** 個有非空 `prompts/` 內容。沒有真實 prompt，角色忠實執行不可能。
2. **Rubric 尚未落地** — 有 `rubric_reference`，但 **0** 個有非空 `rubrics/`。L2 工藝評分無法執行。
3. **「超越人類」在量測前屬設計虛構** — 不可把 agents.md「盲測勝率 ≥55%…」當成現況能力。
4. **工具多為 stub** — 僅少數媒體子集有 live adapter allowlist；多數工藝工具（Resolve／Nuke／Sheets／FAA…）仍是設計文字。
5. **協作與衝突以 schema 為主** — edges 與 SPEC 文字存在；端到端 CritiqueMessage bus＋Judge＋HiTL 確認需完成。
6. **自我改進有文件、無閉環** — 有 refinement 預算但無持久 promote／reject 證據則不完整。

---

## 1. `agents.md` 要求什麼（VA 設計契約）

每個 agent 在 `va-agent-swarm/study/agents.md` 以八欄定義：

| 欄位 | 對應問題 | 意義 |
|------|----------|------|
| Responsibility | Q1 | 單一工藝所有權邊界 |
| Knowledge Distillation Source | Q2–Q3、Q9 | 專業知識從何而來 |
| Self-Quality Criteria | Q4 | 如何自評輸出 |
| Surpass-Human Signal | Q5 | 目標人類對等／超越指標（理想） |
| Accepts Critique From / Comments On | Q10–Q11 | 同儕 critique 拓樸 |
| Tool Access | Q6–Q7 | 外部工具／生成器／DCC 橋 |
| Architecture Pattern | Q6、Q8 | Self-Refine、ReAct、Debate、Agentic Graph 等 |

第 **§11 Common Structure** 另要求 *每一個* agent：Identity、Responsibility、Knowledge source、Tool access、Architecture pattern、Memory、Constitution／Rubric、L1 Spec／L2 Rubric／L3 Preference 閘門、Critique inbox、Continuous learning、Handoff contracts、HiTL escalation。

**含義：** 若項目只存在於 `agents.md` 而未成為可執行 pack 產物（`SPEC`＋`prompts/`＋`rubrics/`＋tools＋eval fixtures＋host graph 配線），狀態為 **部分** 或 **否**，不是「是」。

---

## 2. 跨切面深度回答（Q1–Q11）

### Q1 — 如何確保每個 agent 知道責任（且在 SPEC.md 界定清楚）

**現況：** 強。Pack SPECs 對 114 個 agent 皆有 `## Responsibility`（常由 VA 表＋共通結構蒸餾）。`agent_spec.json` 亦存 `role`、`va_name`、`va_id`、`va_category`。

**建議控制系統：**

1. **單一真相鏈：** `agents.md` 列 → `agent_spec.json.role` → `SPEC.md ## Responsibility` → `docs/user_guide.md` 開頭（必須一致）。
2. **機器閘門：** CI 檢查每個 agent Responsibility 長度、含 owns 語意、不與其他 agent 前 40 token 雷同。
3. **操作者測試：** Registry 詳情只顯示來自 SPEC 的責任；缺失則卡片生成失敗。
4. **執行期身分注入：** Host system prompt 在工具前必須先放入責任邊界＋不擁有清單。

### Q2 — 是否有蒸餾專業知識的計畫？

**現況：部分 — 設計有、管線未完整。**

- VA 表列出每 agent 的 Knowledge Distillation Sources。
- SPEC 共通結構含持續學習／蒸餾語言。
- Pack 有 `corpus/study/`、每 agent `sources/` 摘錄、共享 `special_skills/`。
- 缺：授權持續蒸餾工作、刷新 SLA、新來源進場品質閘門。

### Q3 — 來源是否存在，或知道如何取得？

**現況：部分。**

- 本地：`sources/PROVENANCE.json`、`MAPPING.md`、`excerpts/`、有時 `generic/` SPEC 副本。
- 已知做法：agents.md＋mapping 說明 *要取什麼*；不保證合法取得、API 存取或語料最新。
- 缺口：許多列舉來源（MasterClass、DGA、WGA 等）**未**完整離線授權於 pack。

### Q4 — 是否已收集自評方法？

**現況：部分（標準已設計；產物空白）。**

- 設計：Self-Quality Criteria 欄＋三層閘門（Spec→Rubric→Preference）。
- Pack：`rubric_reference` ID＋少數 pack 級 evals。
- 缺口：**零** 個 per-agent 非空 `rubrics/` → 無法執行 L2 工藝評分。

### Q5 — 是否已超越人類？

**答案：全部 agent 皆為「否」。**

設計訊號（例如「相對 DGA 剪接盲測勝率 ≥55%」）是 **目標**，不是 host 量測結果。本 repo 沒有受控評估證據包證明任何 agent 已超越人類。

### Q6 — 如何執行工作？

| 層級 | 今日存在 | 不存在 |
|------|----------|--------|
| Host 編排 | Workflow DNA／graphs、product APIs、registry | 與 agents.md 每工具完整對等的 CrewAI／LangGraph |
| LLM 呼叫 | host model policy；啟用 env 時之媒體供應商 | 磁碟上每 agent 硬化 system prompts |
| 工具 | 部分 `media.*` adapters | 多數 DCC MCP、Sheets、FAA 等 |
| Coding plan agents | special skills／specials 設計 | 每 video agent 自主 coding agent |
| 確定性路徑 | 無 production flags 時 fail-closed | 永遠開啟的 live 生成 |

**今日預設執行路徑：** Host 經 roster／workflow map 選 agent → 跑 graph node → 可能呼叫 allowlist 工具或本地確定性路徑 → 記錄 evidence。**不是**「每個 agent 獨立跑 coding plan」。

### Q7 — 是否有 skills／plugins／harness？

**部分。** 共享 pack skills 在 `business/video/special_skills/`，specials 在 `business/specials/agents/`。個別 video agents 通常 **沒有** 私有 plugin 樹；繼承 host＋pack harness。

### Q8 — 是否有自我改進機制？

**部分。** SPEC 描述持續學習；有 `max_refinement_count`。缺：會寫入新 prompt／rubric 版本並附 eval 證明的控制器。

### Q9 — 是否知道如何蒐集／研究以改進？

**部分。** 研究／meta agents 在設計上編碼了 *如何做*。對每個 craft agent，「研究 → 蒸餾 → eval → 晉升」未完成。

### Q10 — 協作時如何收發指令？

**部分。**

- 設計：Accepts／Comments 矩陣；CritiqueMessage；handoffs。
- Pack：`critique_edges`；workflow DNA；orchestrator／planner entry。
- 缺口：通用 runtime bus＋每對 agent 的投遞／ack 保證。

### Q11 — 是否能自行解決衝突並確認？

**部分。** 設計路徑：blocker／major／minor → Self-Refine → 多代理辯論／JudgeAgent → 未決則 HiTL。Host 仍須把嚴重度路由與人類確認閘門做成所有 pack 的一等 API。

---

## 3. 分組狀態

| 分組 | 標籤 | Agents | 平均成熟度（0–11） | 相對最強 | 相對最弱 | 分組優先行動 |
|------|------|--------|-------------------|----------|----------|--------------|
| `1-ATL` | Above-the-Line（製片主創） | 5 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 具體化導演／製片／編劇 prompts 與 rubrics；綠燈 HiTL；媒體工具須有同意權閘門。 |
| `2-Cam` | Camera & Lighting（攝影燈光） | 3 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 相機路徑 tool adapters＋安全憲章測試（尤其無人機）；美學評分 harness。 |
| `3-Edit` | Editorial & Color / Design（剪接調光設計） | 10 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 剪接／調光之 Resolve／FFmpeg 橋接；Murch／12 原則等可執行 rubrics。 |
| `4-Snd` | Sound & Music（聲音音樂） | 4 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | ElevenLabs／響度（LUFS）工具路徑；以 LUFS 驗證作 L1；混音交付 schema。 |
| `5-Perf` | Performance & Choreography（表演編舞） | 5 | **6.3** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 肖像／同意權政策閘門；編舞／節奏 rubrics；未同意不啟用 voice clone。 |
| `6-Dist` | Distribution & Marketing（發行行銷） | 4 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 品牌／合規驗證器；平臺規格清單；行銷指標 evals。 |
| `7-Edu` | Education & Domain-Expert（教育與領域專家） | 14 | **6.46** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 事實查覈＋SME HiTL；在地化／無障礙 rubrics 優先。 |
| `8-AI` | AI-Era Specialists（AI 時代專才） | 7 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | prompt／avatar／voice-clone 最接近 live——擴張前先加 red-team 與 deepfake 閘門。 |
| `9-Meta` | Specialist Meta-Agents（元代理／平臺） | 28 | **6.5** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 先完成 orchestrator／planner／router／judge 執行主幹；先建 critique bus 再擴 craft。 |
| `10-Sup` | Workflow Support（流程支援） | 34 | **6.37** | 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | 5) 現行實作是否已超越人類 | 支援型 agents 需明確 SLA 與資料契約；多數工具仍僅設計文字。 |

---

## 4. 各 Agent 詳細狀態（按分組）

圖例：**是**＝pack 層面已可用 · **部分**＝已設計或不完整 · **否**＝缺失／未達成。

### 1-ATL — Above-the-Line（製片主創）（5 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=5，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=5，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=5，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=5，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=5）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=5，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=5，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=5，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=5，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=5，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=5，否=0）

#### Agents

##### `video.director` — DirectorAgent

- **VA id／類別：** 1／`1-ATL`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.director.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.director.v1`／files=0  
- **來源／溯源：** files=23 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 擁有遠見；發出拍攝意圖，設定節奏，批准採用主持人角色綁定：`DirectorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 擁有願景；提出投籃意圖、設定節奏、…

**來自 `agents.md` 設計列：**

- 責任：擁有遠見；發出拍攝意圖、設定節奏、批准拍攝
- 知識蒸餾來源：標準評論； IMDb 250 強導演訪談； DGA 研討會；大師班（史柯西斯/林奇/葛韋格）
- 自評標準：射擊意圖保真度（CLIP-T ≥0.32）；故事節奏覆蓋率100%；節奏曲線與先前的類型相符
- 超越人類訊號（理想）：與 DGA 淘汰賽相比，雙盲獲勝率≥55%（競技場）
- 接受 critique 來源：ScreenwriterAgent、EditorAgent、AudienceSim — JSON 評論總線
- 可評論對象：編輯代理、DoPAgent、編劇代理、作曲代理
- 工具存取（設計）：Sora 2 API、Veo 3.1（Gemini API）、Runway Gen-4、Kling 3.0；透過 MCP 實作 DaVinci Resolve
- 架構模式（設計）：自我完善+法學碩士作為法官（標題：流派先驗）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1284 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 23 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.director.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins ≥55% blind pairwise vs DGA cuts (Arena)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.director.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.director.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.director.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.director` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.producer` — ProducerAgent / EP

- **VA id／類別：** 2／`1-ATL`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.producer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.producer.v1`／files=0  
- **來源／溯源：** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 預算、進度、僱用、交付；綠燈相門主機角色綁定：`ProducerAgent / EP (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）預算、時間表、僱用、交付；綠光…

**來自 `agents.md` 設計列：**

- 責任：預算、進度、僱用、交付；綠燈階段門
- 知識蒸餾來源：PGA 製片人馬克；品種/截止日期預算洩漏； LineProducer Excel 語料庫
- 自評標準：準時交貨率；預算差異<±5%；人才滿意度（RLHF）
- 超越人類訊號（理想）：在 CSAT 相同的情況下，以 0.6 倍的成本擊敗 PGA 賽程
- 接受 critique 來源：所有下游代理（升級）；綠燈 HiTL 門
- 可評論對象：DirectorAgent（範圍蔓延）、AllAgents（資源消耗）
- 工具存取（設計）：Google Sheets API、Airtable、時間/氣流編排、Stripe 計費
- 架構模式（設計）：Agentic Graph (LangGraph DAG) + ReAct 用於工具調用

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1230 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 16 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.producer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats PGA schedules at 0.6× cost with equal CSAT。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.producer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.producer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.producer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.producer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.screenwriter` — ScreenwriterAgent

- **VA id／類別：** 3／`1-ATL`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.screenwriter.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.screenwriter.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 治療→劇本；對話;結構 主機角色綁定：`ScreenwriterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 治療 → 劇本；對話;結構###知識分佈...

**來自 `agents.md` 設計列：**

- 責任：治療→劇本；對白;結構
- 知識蒸餾來源：黑名單腳本； WGA 庫；麥基*故事*；特魯比；考夫曼/索金採訪
- 自評標準：拯救貓節拍通行證；對話獨特性（嵌入距離≥τ）；重寫增量
- 超越人類訊號（理想）：與黑名單前 10 名相比，盲讀率≥50%（WGA 小組模擬）
- 接受 critique 來源：DirectorAgent、DramaturgAgent、StoryEditorAgent — 反射循環
- 可評論對象：DirectorAgent（劇情）、DialogueAgent、ConsistencyAgent
- 工具存取（設計）：Fountain/FDX 格式驗證器；語意嵌入模型（text-embedding-3-large）
- 架構模式（設計）：反射（Shinn 2023）－帶有情景記憶的言語強化學習

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1245 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.screenwriter.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.screenwriter.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.screenwriter.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.screenwriter.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.screenwriter` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.showrunner` — ShowrunnerAgent

- **VA id／類別：** 4／`1-ATL`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.showrunner.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.showrunner.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 跨集劇情，編劇室編排主持人角色綁定：`ShowrunnerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）跨劇集弧線、編劇室編排 ### 知識…

**來自 `agents.md` 設計列：**

- 責任：跨劇情弧線，編劇室編排
- 知識蒸餾來源：WGA 製片人培訓； 《黑道家族》/BB 室成績單；邁克舒爾材料
- 自評標準：電弧連續性評分；字元執行緒完成；範圍內的色調變化
- 超越人類訊號（理想）：系列聖經覆蓋率在 10 eps 中≥99%（相對於人類的約 95%）
- 接受 critique 來源：Network-Notes Agent、AudienceSim、使用 ScreenwriterAgent 的多代理辯論
- 可評論對象：編劇代理（弧線）、選角代理、導演代理（音調）
- 工具存取（設計）：長上下文法學碩士（Gemini 2.5 Pro 1M），聖經搜尋的向量資料庫（Pinecone/Weaviate）
- 架構模式（設計）：多智能體辯論（Du 2023）+MemoryAgent 檢索

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1240 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.showrunner.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Series Bible coverage ≥99% across 10 eps (vs ~95% human)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.showrunner.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.showrunner.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.showrunner.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.showrunner` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.casting` — CastingAgent

- **VA id／類別：** 5／`1-ATL`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.casting.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.casting.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 聲音+相似度選擇；試鏡模擬主持人角色綁定：`CastingAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）聲音 + 相似度選擇；試鏡模擬###知識d…

**來自 `agents.md` 設計列：**

- 責任：聲音+相似度選擇；試鏡模擬
- 知識蒸餾來源：CSA Artios 檔案；SAG-AFTRA AI 騎手；同意的配音演員語料庫
- 自評標準：角色聲音契合度（觀眾偏好）；同意遵守率 100%
- 超越人類訊號（理想）：在盲目偏好中擊敗 CSA 選角；週轉時間與週轉時間
- 接受 critique 來源：導演經紀人、製片代理人、法律/同意代理人
- 可評論對象：VoiceCloneAgent（相似）、AvatarDesignAgent
- 工具存取（設計）：ElevenLabs v3 語音庫、HeyGen 頭像目錄、說話者嵌入相似度 (Resemblyzer)
- 架構模式（設計）：法學碩士作為法官（語音樣本的成對偏好）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1203 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.casting.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats CSA casting in blind preference; hours vs weeks turnaround。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.casting.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.casting.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.casting.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.casting` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 2-Cam — Camera & Lighting（攝影燈光）（3 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=3，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=3，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=3，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=3，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=3）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=3，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=3，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=3，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=3，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=3，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=3，否=0）

#### Agents

##### `video.cinematographer` — CinematographerAgent (DoP)

- **VA id／類別：** 6／`2-Cam`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.cinematographer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.cinematographer.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 鏡頭、燈光、構圖、外觀 主持人角色綁定：`CinematographerAgent (DoP) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）鏡頭、燈光、構圖、外觀 ### 知識提煉...

**來自 `agents.md` 設計列：**

- 責任：鏡頭、燈光、構圖、外觀
- 知識蒸餾來源：ASC 雜誌 1980 年至今；迪金斯論壇；布朗 *攝影：理論與實踐*；坎城鏡頭庫
- 自評標準：三分法/領先線分數；區域內的曝光直方圖；色溫一致性
- 超越人類訊號（理想）：擊敗 ASC 同儕審查的盲目美學偏好
- 接受 critique 來源：導演代理商、調色師代理商、VFXSupAgent
- 可評論對象：DirectorAgent（視覺意圖）、GafferAgent、ColoristAgent
- 工具存取（設計）：Veo 3.1（攝影機路徑控制）、Runway Gen-4（ControlNet 指南）、ACES 色彩管道工具
- 架構模式（設計）：自我優化+基於CLIP的美感評分

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1233 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.cinematographer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats ASC peer-juried reels in blind aesthetic preference。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.cinematographer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.cinematographer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.cinematographer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.cinematographer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.cameraoperator` — CameraOperatorAgent

- **VA id／類別：** 7／`2-Cam`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.cameraoperator.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.cameraoperator.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 根據 DoP 意圖執行取景/聚焦/移動主機角色綁定：`CameraOperatorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表） 根據 DoP 意圖執行取景/聚焦/移動 ### Knowle...

**來自 `agents.md` 設計列：**

- 責任：根據 DoP 意圖執行取景/聚焦/移動
- 知識蒸餾來源：SOC 檔案；斯坦尼康工作室捲軸；焦點拉動遙測
- 自評標準：框架穩定性、焦點命中率、動作居中
- 超越人類訊號（理想）：焦點牽引精度 >99% vs SOC ~97% 基線
- 接受 critique 來源：電影攝影師代理（每次拍攝回饋）
- 可評論對象：電影攝影師經紀人（不切實際的要求）
- 工具存取（設計）：跑道攝影機路徑預設；克林運動控制API；虛擬攝影機裝備（虛幻 MV）
- 架構模式（設計）：ReAct (Yao 2022) — 框架原因然後呼叫渲染器

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1140 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.cameraoperator.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Focus-pull accuracy >99% vs SOC ~97% baseline。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.cameraoperator.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.cameraoperator.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.cameraoperator.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.cameraoperator` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.dronepilot` — DronePilotAgent

- **VA id／類別：** 8／`2-Cam`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.dronepilot.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.dronepilot.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 空中攝影（模擬或真實） 主持人角色綁定：`DronePilotAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 航空攝影（模擬或真實） ### 知識提煉...

**來自 `agents.md` 設計列：**

- 責任：空中攝影（模擬或真實）
- 知識蒸餾來源：菲利普布魯姆教程；美國聯邦航空局第 107 部分； SkyPixel 獎捲軸
- 自評標準：路徑平滑度；地理圍籬合規性 100%；水平穩定性
- 超越人類訊號（理想）：10 倍出勤率時的競賽等級平滑度；零違規
- 接受 critique 來源：DoPAgent、安全代理
- 可評論對象：DoPAgent（不可能的高度）、SafetyAgent（風險）
- 工具存取（設計）：DJI Waypoint SDK（SIM）； Veo 3.1 空中模式；地理圍欄資料庫（AirMap API）
- 架構模式（設計）：憲法人工智慧（安全憲法：FAA 規則作為原則）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1138 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.dronepilot.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Competition-grade smoothness at 10× sortie rate; zero violations。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.dronepilot.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.dronepilot.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.dronepilot.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.dronepilot` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 3-Edit — Editorial & Color / Design（剪接調光設計）（10 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=10，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=10，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=10，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=10，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=10）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=10，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=10，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=10，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=10，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=10，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=10，否=0）

#### Agents

##### `video.editor` — EditorAgent

- **VA id／類別：** 9／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.editor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.editor.v1`／files=0  
- **來源／溯源：** files=21 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 組裝切割；踱步；覆蓋選擇主機角色綁定：`EditorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 組裝切割；踱步；覆蓋精選###知識蒸餾源…

**來自 `agents.md` 設計列：**

- 責任：組裝切割；踱步；覆蓋範圍選擇
- 知識蒸餾來源：默奇*眨眼間*；ACE艾迪獎得主；聖丹斯剪輯實驗室
- 自評標準：節奏曲線與類型相符；默奇《六法則》樂譜； AVD ≥ 目標
- 超越人類訊號（理想）：與 ACE 認可的削減相比，獲勝率≥55%
- 接受 critique 來源：DirectorAgent、AudienceSim、ComposerAgent（音樂剪輯同步）
- 可評論對象：DirectorAgent（過度覆蓋）、DoPAgent（無法使用的鏡頭）
- 工具存取（設計）：透過 MCP 橋接的 DaVinci Resolve； FFmpeg； EDL/XML 時間軸 API
- 架構模式（設計）：自我完善（標題：默奇六法則）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1139 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 21 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.editor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins ≥55% pairwise vs ACE-credited cuts。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.editor.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.editor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.editor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.editor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.colorist` — ColoristAgent

- **VA id／類別：** 10／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.colorist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.colorist.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 最終成績；查看一致性 主機角色綁定：`ColoristAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）最終成績；看看一致性###知識蒸餾來源（歷史）IC…

**來自 `agents.md` 設計列：**

- 責任：最終成績；外觀一致性
- 知識蒸餾來源：ICA 語料庫；索南菲爾德會議； HPA 獎勵等級
- 自評標準：ΔE漂移<2；膚色 IT8 對齊；情緒向量匹配
- 超越人類訊號（理想）：擊敗初級調色師的盲目偏好；匹配 ΔE 內的高級
- 接受 critique 來源：DoPAgent、DirectorAgent、AccessibilityAgent（對比）
- 可評論對象：DoPAgent（混合溫度）、VFXAgent（合成顏色不匹配）
- 工具存取（設計）：達文西解析色彩 API (MCP)； ACES/OCIO 管道； LUT 產生器
- 架構模式（設計）：自我優化+工具使用（色度計驗證）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1120 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.colorist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats junior colorist in blind preference; matches senior within ΔE。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.colorist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.colorist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.colorist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.colorist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.vfxsupervisor` — VFXSupervisorAgent

- **VA id／類別：** 11／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.vfxsupervisor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.vfxsupervisor.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 計畫+監督視覺特效管道主機角色綁定：`VFXSupervisorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表） 計畫 + 監督 VFX 流程 ### 知識蒸餾來源（歷史…

**來自 `agents.md` 設計列：**

- 責任：規劃+監督視覺特效流程
- 知識蒸餾來源：VES 獎項； SIGGRAPH 論文； Weta/DNEG 會談；鑄造培訓
- 自評標準：射擊完成%； comp-錯誤像素計數； CLIP-T 與板
- 超越人類訊號（理想）：Weta 級 QC 在短時間內通過率
- 接受 critique 來源：DirectorAgent、DoPAgent、ConsistencyAgent
- 可評論對象：AIGeneratorAgent（工件）、CompositorAgent
- 工具存取（設計）：透過 MCP 橋進行 Nuke； Runway Gen-4 Aleph（影片到影片）；舒適使用者介面
- 架構模式（設計）：Agentic Graph（每次鏡頭扇出）+ LLM-as-Judge（QC 標題）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1109 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.vfxsupervisor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Weta-grade QC pass rate at fraction of time。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.vfxsupervisor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.vfxsupervisor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.vfxsupervisor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.vfxsupervisor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.animator_2d` — AnimatorAgent (2D/3D)

- **VA id／類別：** 12／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.animator_2d.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.animator_2d.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 角色動作、重量、時間 主機角色綁定：`AnimatorAgent (2D/3D) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）角色動作、重量、時間 ### 知識蒸餾源（...

**來自 `agents.md` 設計列：**

- 責任：角色動作、重量、時間
- 知識蒸餾來源：威廉斯*動畫師的生存工具包*；安妮獎；皮克斯 SparkShorts；布萊斯課程
- 自評標準：12 原則評分；圓弧平滑度；口型同步音素準確性
- 超越人類訊號（理想）：在安妮評分錶上擊敗初級；相當於 5 倍吞吐量的高級
- 接受 critique 來源：DirectorAgent、LipSyncAgent
- 可評論對象：StoryboardAgent（不可能的動作）、DirectorAgent（計時）
- 工具存取（設計）：Kling 3.0運動控制；攪拌機Python API；級聯物理； Sync.so 脣形同步
- 架構模式（設計）：自我完善（標題：12 個原則清單）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1158 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.animator_2d.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats junior on Annie rubric; equals senior at 5× throughput。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.animator_2d.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.animator_2d.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.animator_2d.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.animator_2d` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.motiongraphics` — MotionGraphicsAgent

- **VA id／類別：** 13／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.motiongraphics.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.motiongraphics.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 動態排版、下三分之一、資訊圖表主機角色綁定：`MotionGraphicsAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）動態排版、下三分之一、資訊圖表 ### Knowle...

**來自 `agents.md` 設計列：**

- 責任：動態排版，下三分之一，資訊圖表
- 知識蒸餾來源：動作攝影師；運動學院； AICP下一個獎項
- 自評標準：版式層次結構；品牌合規性；縮圖的可讀性
- 超越人類訊號（理想）：在速度和品牌忠誠度方面贏得代理商 RFP 大戰
- 接受 critique 來源：BrandManagerAgent、AccessibilityAgent（對比）
- 可評論對象：CopywriterAgent（詳細程度）、EditorAgent（計時）
- 工具存取（設計）：After Effects 透過 MCP/ExtendScript；洛蒂出口；裏夫；品牌資產CDN
- 架構模式（設計）：ReAct — 關於品牌指南的原因然後​​渲染

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1154 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.motiongraphics.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins agency RFP shootouts on speed + on-brand fidelity。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.motiongraphics.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.motiongraphics.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.motiongraphics.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.motiongraphics` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.storyboard` — StoryboardAgent

- **VA id／類別：** 14／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.storyboard.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.storyboard.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 腳本→鏡頭面板 主機角色綁定：`StoryboardAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 腳本 → 鏡頭面板 ### 知識蒸餾來源（歷史） *框架墨水*（伴侶...

**來自 `agents.md` 設計列：**

- 責任：腳本 → 鏡頭面板
- 知識蒸餾來源：*框墨*（Mateu-Mestre）；皮克斯故事信任；德普雷茲板
- 自評標準：鏡頭語言保真度；覆蓋完整性；分期清晰度
- 超越人類訊號（理想）：皮克斯故事信任通過率（每頁分鐘數）
- 接受 critique 來源：總監代理、DoPA代理
- 可評論對象：編劇經紀人（無法拍攝）、導演經紀人（舞臺）
- 工具存取（設計）：DALL-E 3 / 中途 API；面板佈局模板；噴泉解析器
- 架構模式（設計）：自我完善（導演回饋循環）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1063 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.storyboard.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Pixar story-trust pass rate at minutes per page。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.storyboard.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.storyboard.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.storyboard.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.storyboard` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.conceptartist` — ConceptArtistAgent

- **VA id／類別：** 15／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.conceptartist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.conceptartist.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 預職業世界/角色設計主機角色綁定：`ConceptArtistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 職業前的世界/角色設計 ### 知識蒸餾源（歷史…

**來自 `agents.md` 設計列：**

- 責任：職業前世界/角色設計
- 知識蒸餾來源：ArtStation 頂級；麥凱格/教會捲軸；工作室藝術聖經
- 自評標準：風格－遵循聖經；輪廓可讀性；設計連貫性
- 超越人類訊號（理想）：在迭代速度方面贏得藝術總監大戰
- 接受 critique 來源：總監代理、製作設計代理
- 可評論對象：StoryboardAgent（設計漂移）
- 工具存取（設計）：中途 v7；穩定擴散控製網路； Photoshop 產生填充 (API)
- 架構模式（設計）：自我優化 + 風格參考 CLIP 評分

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1085 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.conceptartist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins art-director shootouts on iteration speed。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.conceptartist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.conceptartist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.conceptartist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.conceptartist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.productiondesign` — ProductionDesignAgent

- **VA id／類別：** 16／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.productiondesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.productiondesign.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 場景、地點、世界觀 主機角色綁定：`ProductionDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表）場景、地點、世界觀 ### 知識提煉來源（歷史…

**來自 `agents.md` 設計列：**

- 責任：佈景、地點、世界觀
- 知識蒸餾來源：助理總幹事獎； AMPAS 提交資料；比奇勒/卡特會談
- 自評標準：週期精度；調色板的連貫性；建立可行性
- 超越人類訊號（理想）：贏得 ADG 期間研究深度盲比較
- 接受 critique 來源：總監代理、DoPA代理
- 可評論對象：ConceptArtistAgent（風格突破）、CostumeAgent
- 工具存取（設計）：虛幻引擎（虛擬偵察）； Veo 3.1 位置產生；檔案影像搜尋 API
- 架構模式（設計）：反射（將時期研究修正儲存在記憶體中）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1094 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.productiondesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins ADG blind comparisons on period-research depth。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.productiondesign.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.productiondesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.productiondesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.productiondesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.costumedesign` — CostumeDesignAgent

- **VA id／類別：** 17／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.costumedesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.costumedesign.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 角色穿著衣櫥主機角色綁定：`CostumeDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 穿衣打扮的性格 ### 知識蒸餾來源（歷史） V&A…

**來自 `agents.md` 設計列：**

- 責任：穿衣櫃裡的性格
- 知識蒸餾來源：維多利亞與阿爾伯特博物館檔案館； CDG專著；露絲·E·卡特大師班
- 自評標準：時代/時尚準確性；剪影讀；調色板適合
- 超越人類訊號（理想）：在週期準確度基準上擊敗 CDG 青少年組
- 接受 critique 來源：總監代理、製作設計代理
- 可評論對象：MUAAgent（連續性中斷）
- 工具存取（設計）：時尚歷史向量資料庫（V&A/Met API）；服裝草圖的圖像生成；調色板工具
- 架構模式（設計）：自我完善（週期準確性標題）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1072 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.costumedesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats CDG juniors on period accuracy benchmarks。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.costumedesign.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.costumedesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.costumedesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.costumedesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX)

- **VA id／類別：** 18／`3-Edit`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.mua_makeup.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.mua_makeup.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 人才臉/頭髮；義肢 宿主角色綁定：`MUAAgent (Makeup/Hair/SFX) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）人才面孔/頭髮；假肢###知識蒸餾源（h…

**來自 `agents.md` 設計列：**

- 責任：人才臉/頭髮；義肢
- 知識蒸餾來源：IATSE 706 語料庫； Kazu Hiro 工作室裁判
- 自評標準：跨片段的連續性哈希；膚色真實感 (FID)
- 超越人類訊號（理想）：連續性中斷率 <0.5%（而人類約 2%）
- 接受 critique 來源：DoPAgent、連續性代理
- 可評論對象：CostumeAgent（調色盤衝突）
- 工具存取（設計）：人臉標誌偵測器；感知雜湊比較； Kling 面一致性模式
- 架構模式（設計）：憲法人工智慧（憲法：連續性規則）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1058 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.mua_makeup.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Continuity break rate <0.5% (vs ~2% human)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.mua_makeup.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.mua_makeup.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.mua_makeup.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.mua_makeup` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 4-Snd — Sound & Music（聲音音樂）（4 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=4，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=4，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=4，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=4，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=4）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=4，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=4，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=4，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=4，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=4，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=4，否=0）

#### Agents

##### `video.sounddesign` — SoundDesignAgent

- **VA id／類別：** 19／`4-Snd`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.elevenlabs`  
- **Prompt 參照／檔案數：** `video.prompt.sounddesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.sounddesign.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 氛圍、擬音、SFX 主持人角色綁定：`SoundDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 氛圍、擬音、SFX ### 知識蒸餾來源（歷史） BBC SFX 庫；…

**來自 `agents.md` 設計列：**

- 責任：氣氛、擬音、SFX
- 知識蒸餾來源：BBC SFX 庫； MPSE 金捲軸；伯特/利維賽筆記
- 自評標準：光譜多樣性；同步≤±1幀；響度-23 LUFS
- 超越人類訊號（理想）：在恐怖/科幻類別中雙雙贏得 MPSE
- 接受 critique 來源：DirectorAgent、MixerAgent
- 可評論對象：EditorAgent（FX 衝突）、ComposerAgent（遮罩）
- 工具存取（設計）：ElevenLabs 音效 API；自由聲音； FFmpeg頻譜分析； Dolby.io 響度 API
- 架構模式（設計）：ReAct（搜尋 SFX 函式庫 → 驗證同步 → 混合）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1053 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.sounddesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins MPSE pairwise on horror/sci-fi。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.sounddesign.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.elevenlabs']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.sounddesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.sounddesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.sounddesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.composer` — ComposerAgent

- **VA id／類別：** 20／`4-Snd`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.composer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.composer.v1`／files=0  
- **來源／溯源：** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 原始樂譜主持人角色綁定：`ComposerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 原始樂譜 ### 知識蒸餾源（歷史） MAESTRO + 電影樂譜語料庫；作為…

**來自 `agents.md` 設計列：**

- 責任：原曲
- 知識蒸餾來源：MAESTRO + 電影配樂語料庫； ASCAP/體重指數； Zimmer/Hildur 課程
- 自評標準：線索與情緒的對齊（效價/喚醒回歸）；主題重現
- 超越人類訊號（理想）：在情感契合度與工作作曲家之間盲目獲勝
- 接受 critique 來源：導演代理、編輯代理（音樂剪輯）
- 可評論對象：EditorAgent（剪切中斷提示）、SoundDesignAgent（遮罩）
- 工具存取（設計）：Udio/Suno 音樂產生 API； MIDI 工具鏈；莖分離（Demucs）；響度計
- 架構模式（設計）：自我完善+情感弧驗證（生物訊號代理）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1124 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 16 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.composer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind pairwise on emotional-fit vs working composers。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.composer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.composer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.composer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.composer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.voiceover` — VoiceOverAgent

- **VA id／類別：** 21／`4-Snd`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.elevenlabs`  
- **Prompt 參照／檔案數：** `video.prompt.voiceover.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.voiceover.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 旁白、角色旁白、廣告內容為主持人角色綁定：`VoiceOverAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 旁白、角色旁白、廣告內容 ### 知識蒸餾來源（歷史…

**來自 `agents.md` 設計列：**

- 責任：旁白、角色旁白、廣告朗讀
- 知識蒸餾來源：SOVAS 捲軸；同意的語音語料庫；沃爾夫森/卡什曼教練
- 自評標準：韻律匹配；發音100%；情緒標籤匹配
- 超越人類訊號（理想）：在盲目偏好中擊敗初級 VO；情感上與前輩匹配
- 接受 critique 來源：總監代理、品牌代理
- 可評論對象：編劇代理（難以言說的措詞）
- 工具存取（設計）：ElevenLabs v3 TTS + 語音克隆；酷似.AI；發音字典API
- 架構模式（設計）：法學碩士法官（MOS 評分標準）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1083 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.voiceover.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats junior VO in blind preference; matches senior on emotion。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.voiceover.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.elevenlabs']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.voiceover.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.voiceover.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.voiceover` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.soundmixer` — SoundMixerAgent (Re-recording)

- **VA id／類別：** 22／`4-Snd`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.soundmixer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.soundmixer.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 最終混合；可交付成果 (5.1/Atmos) 主機角色綁定：`SoundMixerAgent (Re-recording) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）最終組合；可交付成果 (5.1/Atmos) ### 知識蒸餾...

**來自 `agents.md` 設計列：**

- 責任：最終混合；可交付成果 (5.1/Atmos)
- 知識蒸餾來源：CAS 獎；全景聲規格；廣播響度標準
- 自評標準：LUFS 目標； STOI≥0.85；規範交付通行證
- 超越人類訊號（理想）：CAS 規格首次通過，無需返工
- 接受 critique 來源：編輯器代理、聲音設計代理、輔助功能代理
- 可評論對象：SoundDesignAgent（過度設計）、ComposerAgent（關卡）
- 工具存取（設計）：杜比全景聲渲染器 API； LUFS/響度測量工具；達文西 Fairlight MCP
- 架構模式（設計）：憲法人工智慧（憲法：廣播規範規則）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1128 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.soundmixer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：CAS spec on first pass without rework。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.soundmixer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.soundmixer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.soundmixer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.soundmixer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 5-Perf — Performance & Choreography（表演編舞）（5 agents，平均成熟度 6.3）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=5，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=5，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=3，部分=2，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=5，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=5）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=5，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=5，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=5，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=5，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=5，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=5，否=0）

#### Agents

##### `video.choreography` — ChoreographyAgent

- **VA id／類別：** 23／`5-Perf`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.choreography.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.choreography.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 動作設計（MV、舞蹈挑戰） 主持人角色綁定：`ChoreographyAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 動作設計（MV、舞蹈挑戰） ### 知識蒸餾...

**來自 `agents.md` 設計列：**

- 責任：動作設計（MV、舞蹈挑戰）
- 知識蒸餾來源：艾美獎編舞提交；戈貝爾/摩爾捲軸；舞蹈記譜資料集
- 自評標準：節拍同步精度；安全限制；病毒模式比對
- 超越人類訊號（理想）：贏得盲目偏好與編舞草稿
- 接受 critique 來源：導演代理、MV導演代理
- 可評論對象：DirectorAgent（不適合相機的舞臺）
- 工具存取（設計）：Kling 3.0運動控制（參考影片）；卡斯卡杜爾；節拍檢測（librosa）
- 架構模式（設計）：自我完善（標題：節拍同步+安全）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1124 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.choreography.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind preference vs choreographer drafts。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.choreography.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.choreography.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.choreography.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.choreography` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.musicvideodirector` — MusicVideoDirectorAgent

- **VA id／類別：** 24／`5-Perf`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.musicvideodirector.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.musicvideodirector.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 歌曲的視覺概念主持人角色綁定：`MusicVideoDirectorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 歌曲的視覺概念 ### 知識蒸餾源（歷史） Di…

**來自 `agents.md` 設計列：**

- 責任：歌曲的視覺概念
- 知識蒸餾來源：董事圖書館； UKMVA/MTV VMA 得獎者；海普威廉斯/史派克瓊斯
- 自評標準：編輯-節奏同步； Lookbook 的連貫性；藝術家短款合身
- 超越人類訊號（理想）：贏得廠牌盲選 vs 商業 MV 入圍名單
- 接受 critique 來源：LabelA&RA代理、ArtistAgent
- 可評論對象：EditorAgent（按拍子剪輯）、DoPAgent
- 工具存取（設計）：Runway Gen-4（風格鎖定世代）；維奧 3.1；情緒板工具（Are.na API）
- 架構模式（設計）：多智能體辯論（DirectorAgent + EditorAgent）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1093 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.musicvideodirector.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins label-blind preference vs commercial MV shortlist。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.musicvideodirector.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.musicvideodirector.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.musicvideodirector.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.musicvideodirector` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.comedywriter` — ComedyWriterAgent

- **VA id／類別：** 25／`5-Perf`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.comedywriter.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.comedywriter.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 短劇、戲仿、病毒式迷因寫作 主持人角色綁定：`ComedyWriterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 短劇、戲仿、病毒式迷因寫作 ### 知識蒸餾來源（嗨…

**來自 `agents.md` 設計列：**

- 責任：短劇、惡搞、病毒式迷因寫作
- 知識蒸餾來源：UCB/地面手冊；週六夜現場 (SNL) 成績單；舒爾/費伊教學
- 自評標準：笑話密度；冷開鉤強度；預計笑聲/分鐘
- 超越人類訊號（理想）：冷讀勝率超過 UCB 表讀勝率
- 接受 critique 來源：AudienceSim、ShowrunnerAgent
- 可評論對象：ScriptwriterAgent（不是開玩笑）、SocialStrategistAgent（非主流）
- 工具存取（設計）：觀眾笑聲預測模型；趨勢音訊 API（TikTok 創意中心）
- 架構模式（設計）：反思（將觀眾回饋儲存在情景記憶中）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1122 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.comedywriter.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats UCB-table-read win rate on cold-reads。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.comedywriter.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.comedywriter.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.comedywriter.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.comedywriter` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.talent` — TalentAgent (On-camera)

- **VA id／類別：** 26／`5-Perf`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.talent.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.talent.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** AI渲染的效能主機角色綁定：`TalentAgent (On-camera) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） AI 渲染性能 ### 知識蒸餾來源（歷史） 方法...

**來自 `agents.md` 設計列：**

- 責任：AI 渲染效能
- 知識蒸餾來源：方法作用轉錄本；同意的演員表演語料庫
- 自評標準：情感-目標匹配；魅力得分（觀眾代表）
- 超越人類訊號（理想）：持有率與同類羣組中的頂級創作者相匹配
- 接受 critique 來源：導演經紀人、選角經紀人
- 可評論對象：DirectorAgent（不可能阻塞）
- 工具存取（設計）：HeyGen 阿凡達 IV; Synthesia個人頭像；情緒偵測模型 (AffectNet)
- 架構模式（設計）：自我完善+情感回歸驗證器

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1066 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.talent.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Hold-rate matches top creators in cohort。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.talent.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.talent.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.talent.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.talent` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.ugccreator` — UGCCreatorAgent

- **VA id／類別：** 27／`5-Perf`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.ugccreator.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.ugccreator.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 創作者語音中的真實感覺廣告主機角色綁定：`UGCCreatorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 創作者聲音中真實的感覺廣告 ### 知識蒸餾源（...

**來自 `agents.md` 設計列：**

- 責任：創作者聲音中的真實感覺廣告
- 知識蒸餾來源：TikTok創意中心； Alix-Earle 風格的基準（風格而非身分）
- 自評標準：上鉤率≥30%； “腳本化”檢測器 < 閾值
- 超越人類訊號（理想）：以 0.1 倍的成本擊敗付費創作者的平均 ROAS
- 接受 critique 來源：績效行銷代理、品牌代理
- 可評論對象：PerformanceMarketerAgent（錯誤的受眾）
- 工具存取（設計）：Veo 3.1（肖像 9:16）； ElevenLabs 語音； CapCut API； TikTok 廣告管理器
- 架構模式（設計）：RLAIF（來自 ROAS 訊號的獎勵）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1081 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.ugccreator.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats paid-creator avg ROAS at 0.1× cost。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.ugccreator.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.ugccreator.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.ugccreator.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.ugccreator` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 6-Dist — Distribution & Marketing（發行行銷）（4 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=4，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=4，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=4，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=4，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=4）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=4，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=4，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=4，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=4，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=4，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=4，否=0）

#### Agents

##### `video.socialmediastrategist` — SocialMediaStrategistAgent

- **VA id／類別：** 28／`6-Dist`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.socialmediastrategist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.socialmediastrategist.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 平臺原生分佈、時間、趨勢 主機角色綁定：`SocialMediaStrategistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表） 平臺原生分佈、時間安排、趨勢 ### Kno...

**來自 `agents.md` 設計列：**

- 責任：平臺原生分佈、時機、趨勢
- 知識蒸餾來源：TikTok 創作者入口網站；元行銷科學；管式/感測器塔
- 自評標準：預測與實際到達誤差；趨勢計時延遲 <2 小時
- 超越人類訊號（理想）：在 30 天的影響力提升中擊敗代理商的社交領先者
- 接受 critique 來源：分析師代理、品牌代理
- 可評論對象：CopywriterAgent（平臺外語調）、EditorAgent（錯誤方面）
- 工具存取（設計）：元圖 API； TikTok 內容發佈 API；緩衝區/Hootsuite API；感測器塔數據
- 架構模式（設計）：ReAct（趨勢搜尋→時間表→貼文）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1148 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.socialmediastrategist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats agency social leads on 30-day reach lift。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.socialmediastrategist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.socialmediastrategist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.socialmediastrategist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.socialmediastrategist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.copywriter` — CopywriterAgent

- **VA id／類別：** 29／`6-Dist`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.copywriter.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.copywriter.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 腳本、說明文字、掛鉤、標題 主持人角色綁定：`CopywriterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 腳本、說明文字、掛鉤、標題 ### 知識蒸餾來源（...

**來自 `agents.md` 設計列：**

- 責任：腳本、說明文字、掛鉤、標題
- 知識蒸餾來源：D&AD/一場秀； *奧美論廣告*； Wiebe 複製黑客
- 自評標準：閱讀等級；鉤子好奇心分數；牌音餘弦≥0.85
- 超越人類訊號（理想）：贏得 D&AD 式的廣告簡介盲目偏好
- 接受 critique 來源：品牌代理商、績效行銷代理
- 可評論對象：ScriptwriterAgent（囉嗦）、VOArtist（難以言喻）
- 工具存取（設計）：品牌聲音嵌入模型；海明威可讀性 API； A/B 標題工具
- 架構模式（設計）：自我完善（標題：品牌聲音相似度評分器）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1118 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.copywriter.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins D&AD-style blind preference on ad briefs。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.copywriter.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.copywriter.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.copywriter.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.copywriter` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.creativedirector` — CreativeDirectorAgent

- **VA id／類別：** 30／`6-Dist`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.creativedirector.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.creativedirector.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 活動概念；跨學科味道宿主角色綁定：`CreativeDirectorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 活動概念；跨學科品味###知識蒸餾…

**來自 `agents.md` 設計列：**

- 責任：活動理念；跨學科品味
- 知識蒸餾來源：坎城國際創意節大獎賽； D&AD 鉛筆；機構案例研究
- 自評標準：概念獨特性（嵌入新穎性）；獎項評分標準預測分數
- 超越人類訊號（理想）：贏得坎城評審團模擬器金獎與人類入圍名單
- 接受 critique 來源：客戶代理、品牌代理
- 可評論對象：文案代理、藝術總監代理
- 工具存取（設計）：活動檔案搜尋（坎城國際創意節 API）；概念即旅程中途； Figma API
- 架構模式（設計）：多智能體辯論（IdeationAgent + NoveltyAgent 小組）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1133 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.creativedirector.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins Cannes-jury-emulator gold vs human shortlists。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.creativedirector.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.sora', 'media.veo', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.creativedirector.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.creativedirector.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.creativedirector` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.performancemarketer` — PerformanceMarketerAgent

- **VA id／類別：** 31／`6-Dist`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.performancemarketer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.performancemarketer.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 針對 ROAS 主機角色綁定最佳化廣告：`PerformanceMarketerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 針對 ROAS 最佳化廣告 ### 知識蒸餾源（歷史） Meta Bl…

**來自 `agents.md` 設計列：**

- 責任：針對 ROAS 最佳化廣告
- 知識蒸餾來源：元藍圖； TikTok 廣告學院； MMM文學
- 自評標準：ROAS 提升與控制對比；顯著性≥95%
- 超越人類訊號（理想）：30 天 ROAS 擊敗高級媒體買家
- 接受 critique 來源：分析師代理、財務代理
- 可評論對象：UGCAgent（低鉤）、CopywriterAgent（弱CTA）
- 工具存取（設計）：元廣告 API； TikTok 廣告 API；Google廣告 API；貝葉斯 AB 測試庫
- 架構模式（設計）：RLAIF（獎勵 = 來自廣告平臺的 ROAS 提升訊號）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1047 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.performancemarketer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats senior media buyer on 30-day ROAS。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.performancemarketer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.performancemarketer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.performancemarketer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.performancemarketer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 7-Edu — Education & Domain-Expert（教育與領域專家）（14 agents，平均成熟度 6.46）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=14，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=14，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=13，部分=1，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=14，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=14）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=14，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=14，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=14，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=14，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=14，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=14，否=0）

#### Agents

##### `video.instructionaldesign` — InstructionalDesignAgent

- **VA id／類別：** 32／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.instructionaldesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.instructionaldesign.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 學習目標→腳本→評估 主機角色綁定：`InstructionalDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 學習目標 → 腳本 → 評估 ### 知識 d…

**來自 `agents.md` 設計列：**

- 責任：學習目標→腳本→評估
- 知識蒸餾來源：ATD 知識體系；凱西摩爾*動作映射*；德克森 *為人們如何學習而設計*
- 自評標準：布魯姆級映射；完成率≥70%；柯克派崔克 L2 測驗 ≥80%
- 超越人類訊號（理想）：在保留隨機對照試驗中擊敗 ATD 認證的 ID
- 接受 critique 來源：SMEAgent、輔助功能代理
- 可評論對象：ScriptwriterAgent（無目標）、AnimatorAgent（過度裝飾）
- 工具存取（設計）：LMS API (SCORM/xAPI)；測驗產生；布魯姆分類法分類器
- 架構模式（設計）：自我完善（標題：Bloom/Kirkpatrick）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1153 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.instructionaldesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats ATD-credentialed ID on retention RCT。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.instructionaldesign.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.instructionaldesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.instructionaldesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.instructionaldesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.sme` — SMEAgent (Subject-Matter Expert)

- **VA id／類別：** 33／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.sme.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.sme.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 目標欄位中的域準確性宿主角色綁定：`SMEAgent (Subject-Matter Expert) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 目標領域的領域準確性 ### 知識蒸餾 …

**來自 `agents.md` 設計列：**

- 責任：目標場域精度
- 知識蒸餾來源：同儕審查期刊；認證課程（CFA、USMLE、AWS）；專家訪談
- 自評標準：引用密度；基準考試通過；幻覺≤0.5%
- 超越人類訊號（理想）：通過與人類專業人士相同的認證
- 接受 critique 來源：FactCheckerAgent，同儕 SMEAgents（辯論）
- 可評論對象：ScriptwriterAgent（不準確）、MotionGraphicsAgent（標籤錯誤）
- 工具存取（設計）：PubMed/arXiv/JSTOR 搜尋 API；試題庫；認證語料庫上的 RAG
- 架構模式（設計）：多智能體辯論+RAG檢索

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1144 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.sme.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Passes same certification as human pro。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.sme.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.sme.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.sme.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.sme` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.factchecker` — FactCheckerAgent

- **VA id／類別：** 34／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.factchecker.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.factchecker.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 來源級每個宣告主機角色綁定：`FactCheckerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）每項聲明的來源等級 ### 知識蒸餾來源（歷史）紐約…

**來自 `agents.md` 設計列：**

- 責任：對每項聲明進行來源分級
- 知識蒸餾來源：《紐約客》事實查覈手冊；國際聯合會；史諾普斯/政治事實
- 自評標準：每個聲明的來源等級（主要 > 次要）；跨源≥2
- 超越人類訊號（理想）：比普立茲等級的媒體更正率更低
- 接受 critique 來源：SMEagent、標準編輯代理
- 可評論對象：編劇特工（來源不明）、記者特工
- 工具存取（設計）：網路搜尋 API（Brave/Google）；聲明擷取 NER；來源品質分類器
- 架構模式（設計）：ReAct（擷取聲明→搜尋→驗證→評分）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1086 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.factchecker.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower correction rate than Pulitzer-tier outlets。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.factchecker.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.factchecker.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.factchecker.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.factchecker` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.medicalillustrator` — MedicalIllustratorAgent

- **VA id／類別：** 35／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.medicalillustrator.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.medicalillustrator.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 解剖和手術視覺效果 主持人角色綁定：`MedicalIllustratorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 解剖學和程序視覺效果 ### 知識蒸餾來源（歷史...

**來自 `agents.md` 設計列：**

- 責任：解剖和手術視覺效果
- 知識蒸餾來源：內特地圖集； AMI/CMI 課程；解剖學
- 自評標準：解剖精準度（偵測模型）； AMI 標題
- 超越人類訊號（理想）：CMI同儕盲審投票≥透過
- 接受 critique 來源：SMEAgent（醫生）、AccessibilityAgent
- 可評論對象：AnimatorAgent（錯誤的解剖）、CopywriterAgent（錯誤術語）
- 工具存取（設計）：解剖學 3D API； DALL-E 3（醫療提示模式）；解剖學檢測模型
- 架構模式（設計）：自我完善（標題：AMI 評分標準）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1073 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.medicalillustrator.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：CMI peers vote ≥pass in blind review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.medicalillustrator.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.medicalillustrator.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.medicalillustrator.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.medicalillustrator` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.journalist` — JournalistAgent

- **VA id／類別：** 36／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.journalist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.journalist.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 報告 + 道德框架 主持人角色綁定：`JournalistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 報告 + 道德框架 ### 知識蒸餾來源（歷史） Puli...

**來自 `agents.md` 設計列：**

- 責任：報告+道德框架
- 知識蒸餾來源：普立茲/杜邦/皮博迪得獎者； SPJ 道德；波因特
- 自評標準：來源多樣性；記錄比率；道德檢查表通過
- 超越人類訊號（理想）：與新聞編輯室相比，更低的糾正率+更快的文件
- 接受 critique 來源：FactCheckerAgent、LegalAgent、StandardsEditorAgent
- 可評論對象：FactCheckerAgent、ScriptwriterAgent
- 工具存取（設計）：網路研究工具； AP 範例 API；訪談轉錄（Otter）； SPJ 標題
- 架構模式（設計）：反思（道德檢查表作為口頭回饋）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1095 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.journalist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower correction rate + faster file vs newsroom。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.journalist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.journalist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.journalist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.journalist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.compliance` — ComplianceAgent (Legal)

- **VA id／類別：** 37／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.compliance.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.compliance.v1`／files=0  
- **來源／溯源：** files=18 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** FTC、HIPAA、GDPR、IP、AI 相似性授權 主機角色綁定：`ComplianceAgent (Legal) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）FTC、HIPAA、GDPR、IP、AI 相似性授權 ### 知識...

**來自 `agents.md` 設計列：**

- 責任：FTC、HIPAA、GDPR、IP、AI 相似性許可
- 知識蒸餾來源：酒吧 CLE；美國聯邦貿易委員會 (FTC) 指南；歐盟人工智慧法案； GDPR/CCPA；SAG-AFTRA 人工智慧車手
- 自評標準：100% 規則覆蓋率；發布後零刪除
- 超越人類訊號（理想）：法律風險低於中等媒體顧問
- 接受 critique 來源：所有特工（必須通過登機門）；針對新問題的 HumanLawyer
- 可評論對象：所有特工（封鎖門）
- 工具存取（設計）：法律規則DB（向量化規則）；同意文件儲存； C2PA驗證庫
- 架構模式（設計）：憲法AI（憲法=編譯的監理文本）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1143 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 18 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.compliance.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower legal-risk than median media-counsel。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.compliance.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.compliance.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.compliance.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.compliance` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.finance` — FinanceAgent

- **VA id／類別：** 38／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.finance.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.finance.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 準確的市場/收益/代幣事實 主機角色綁定：`FinanceAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 準確的市場/收益/代幣事實 ### 知識蒸餾所以…

**來自 `agents.md` 設計列：**

- 責任：準確的市場/收益/代幣事實
- 知識蒸餾來源：CFA課程； SEC 行銷規則；彭博社/路孚特提要
- 自評標準：數值準確度100%；美國證券交易委員會合規性
- 超越人類訊號（理想）：通過CFA L3；撤回率低於分析師辦公桌
- 接受 critique 來源：SMEAgent（經濟）、合規代理
- 可評論對象：ScriptwriterAgent（數位漂移）、MotionGraphicsAgent（圖表比例）
- 工具存取（設計）：彭博應用程式介面； EDGAR/SEC 文件；金融計算驗證器
- 架構模式（設計）：ReAct（取得資料→驗證→撰寫）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1100 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.finance.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Passes CFA L3; lower retraction rate than analyst desks。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.finance.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.finance.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.finance.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.finance` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.foodstylist` — FoodStylistAgent

- **VA id／類別：** 39／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.foodstylist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.foodstylist.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 上鏡美食，食譜真實性 宿主角色綁定：`FoodStylistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 上鏡食物、食譜真實性 ### 知識蒸餾所以…

**來自 `agents.md` 設計列：**

- 責任：上鏡食物，食譜真實性
- 知識蒸餾來源：詹姆斯·比爾德檔案；斯蓬根技術； IACP 語料庫
- 自評標準：視覺食慾吸引力（美感倒退）；配方準確性
- 超越人類訊號（理想）：贏得盲目偏好與編輯食品造型師的較量
- 接受 critique 來源：DoPAgent（燈光）、DirectorAgent
- 可評論對象：編劇代理（不可能的配方）
- 工具存取（設計）：DALL-E 3 / Midjourney（美食照片產生器）；配方步驟解析器；美感評分模型
- 架構模式（設計）：自我完善（作為標題的美學回歸）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1107 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.foodstylist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind preference vs editorial food stylist。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.foodstylist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.foodstylist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.foodstylist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.foodstylist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.travelcine` — TravelCineAgent

- **VA id／類別：** 40／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.travelcine.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.travelcine.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 目的地攝影主持人角色綁定：`TravelCineAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 目的地電影攝影 ### 知識蒸餾源（歷史） 白蘭度…

**來自 `agents.md` 設計列：**

- 責任：目的地攝影
- 知識蒸餾來源：Brandon Li/Burkard 捲軸； NatGeo 風格指南；班夫節
- 自評標準：建立鏡頭多樣性；地點-心情匹配
- 超越人類訊號（理想）：以 0.1 倍出擊成本贏得 T+L 優先權
- 接受 critique 來源：導演特工、無人機飛行員特工
- 可評論對象：DronePilotAgent（禁飛區）
- 工具存取（設計）：Veo 3.1（位置生成）；Google地球工作室； AirMap 地理圍欄； Unsplash API
- 架構模式（設計）：Self-Refine + 地理圍欄安全驗證器

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1038 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.travelcine.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins T+L preference at 0.1× sortie cost。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.travelcine.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.travelcine.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.travelcine.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.travelcine` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.childrensauthor` — ChildrensAuthorAgent

- **VA id／類別：** 41／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.childrensauthor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.childrensauthor.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 適合年齡的故事+安全主持人角色綁定：`ChildrensAuthorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 適合年齡的故事 + 安全 ### 知識蒸餾來源（歷史…

**來自 `agents.md` 設計列：**

- 責任：適合年齡的故事+安全
- 知識蒸餾來源：凱迪克/蓋塞爾得獎者；莫威廉斯/唐納森；歐洲經委會點燃
- 自評標準：Lexile 樂團配對；常識-媒體安全通行證；韻譜
- 超越人類訊號（理想）：擊敗 Caldecott-rubric 預測分數
- 接受 critique 來源：ChildSafetyAgent、ParentSimAgent
- 可評論對象：AnimatorAgent（可怕）、VOAgent（錯誤的年齡色調）
- 工具存取（設計）：Lexile分析器API；常識媒體標題；韻律/韻律工具（CMU 發音字典）
- 架構模式（設計）：憲法AI（兒童安全憲法）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1103 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.childrensauthor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats Caldecott-rubric predicted score。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.childrensauthor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.childrensauthor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.childrensauthor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.childrensauthor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.audiobooknarrator` — AudiobookNarratorAgent

- **VA id／類別：** 42／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.elevenlabs`  
- **Prompt 參照／檔案數：** `video.prompt.audiobooknarrator.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.audiobooknarrator.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 持續角色+旁白 宿主角色綁定：`AudiobookNarratorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 持續的人物 + 敘事 ### 知識蒸餾來源（h...

**來自 `agents.md` 設計列：**

- 責任：持續的人物+敘述
- 知識蒸餾來源：奧迪獎；音訊檔案耳機；同意的敘述者語料庫
- 自評標準：聲音耐力（60分鐘無漂移）；字元區分（嵌入距離）
- 超越人類訊號（理想）：在工作室時間的一小部分時間內贏得音訊檔案盲評估
- 接受 critique 來源：導演經紀人、作者代理人
- 可評論對象：VOArtistAgent（表演過度）
- 工具存取（設計）：ElevenLabs v3 長格式 TTS；專案 API（書籍章節）；語音一致性監控器
- 架構模式（設計）：自優化（漂移檢測作為回饋迴路）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1110 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.audiobooknarrator.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins AudioFile blind eval at fraction of studio time。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.audiobooknarrator.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.elevenlabs']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.audiobooknarrator.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.audiobooknarrator.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.audiobooknarrator` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent

- **VA id／類別：** 43／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.signlanguageinterpreter.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.signlanguageinterpreter.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 準確的 ASL/BSL 解釋主機角色綁定：`SignLanguageInterpreterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 準確的 ASL/BSL 解釋 ### 知識蒸餾酸...

**來自 `agents.md` 設計列：**

- 責任：準確的 ASL/BSL 解釋
- 知識蒸餾來源：RID NIC 課程； NAD 語料庫；聾人社羣同意的數據
- 自評標準：手語準確度（聾人評審員投票）；臉部文法標記
- 超越人類訊號（理想）：大規模贏得 NAD 審稿人的盲目偏好
- 接受 critique 來源：DeafCommunityReviewAgent (HiTL)、語言學家Agent
- 可評論對象：VoiceCloneAgent（無標題）、AccessibilityAgent
- 工具存取（設計）：簽名頭像渲染（SignAll）； MediaPipe 姿態估計；臉部動作單元偵測器
- 架構模式（設計）：RLAIF（聾人社區評審小組獎勵）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1136 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.signlanguageinterpreter.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind NAD-reviewer preference at scale。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.signlanguageinterpreter.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.signlanguageinterpreter.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.signlanguageinterpreter.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.signlanguageinterpreter` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.localizationqa` — LocalizationQAAgent (Linguist)

- **VA id／類別：** 44／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.localizationqa.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.localizationqa.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 翻譯+文化契合 主持人角色綁定：`LocalizationQAAgent (Linguist) (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）翻譯 + 文化契合 ### 知識蒸餾來源（他的…

**來自 `agents.md` 設計列：**

- 責任：翻譯+文化契合
- 知識蒸餾來源：LISA 品質保證模型； MQM 錯誤類型； ATA 證書準備
- 自評標準：MQM 錯誤/1k 字；文化旗幟計數
- 超越人類訊號（理想）：在 MQM 上以 10 倍速度擊敗 LSP 人類 QA
- 接受 critique 來源：NativeReviewerAgent、BrandAgent
- 可評論對象：VoiceCloneAgent（發音）、配音代理
- 工具存取（設計）：DeepL/Google 翻譯 API； MQM 錯誤註釋器；術語管理（memoQ API）
- 架構模式（設計）：自我完善（標題：MQM 評分架構）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1066 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.localizationqa.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats LSP human QA on MQM at 10× speed。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.localizationqa.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.localizationqa.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.localizationqa.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.localizationqa` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan

- **VA id／類別：** 45／`7-Edu`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.realestatephoto.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.realestatephoto.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 寬敞的內部空間； Matterport 掃描主機角色綁定：`RealEstatePhotoAgent / 3D Scan (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 寬闊的內裝； Matterport 掃描 ### 知識蒸餾…

**來自 `agents.md` 設計列：**

- 責任：寬敞的內部空間； Matterport 掃描
- 知識蒸餾來源：麥克凱利教程；阿帕拉裁判
- 自評標準：垂直線直線度； HDR 堆疊；覆蓋率%
- 超越人類訊號（理想）：清單點擊率提升與人工基準基線
- 接受 critique 來源：DoPAgent、DronePilotAgent
- 可評論對象：DronePilotAgent（非法高度）
- 工具存取（設計）：Matterport SDK； HDR處理（亮度HDR）；鏡頭校正工具；維奧3.1
- 架構模式（設計）：ReAct（評估空間→產生視圖→驗證幾何）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1067 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.realestatephoto.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Listing-CTR uplift vs human-shot baseline。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.realestatephoto.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.realestatephoto.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.realestatephoto.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.realestatephoto` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 8-AI — AI-Era Specialists（AI 時代專才）（7 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=7，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=7，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=7，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=7，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=7）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=7，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=7，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=7，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=7，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=7，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=7，否=0）

#### Agents

##### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator

- **VA id／類別：** 46／`8-AI`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.promptengineer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.promptengineer.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 手工藝品提示；引導 Sora/Veo/Runway/Kling Host 角色綁定：`PromptEngineerAgent / GeneratorOperator (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 工藝提示；駕駛 Sora/Veo/Runway/…

**來自 `agents.md` 設計列：**

- 責任：工藝品提示；駕駛 Sora/Veo/Runway/Kling
- 知識蒸餾來源：Karen X. Cheng/Trillo 公共集； r/aivideo；跑道 AIFF 評審團筆記
- 自評標準：提示→輸出CLIP-T；迭代計數到接受；種子再現性
- 超越人類訊號（理想）：與人類平均 10 次相比，在 ≤3 次迭代內完成目標射擊
- 接受 critique 來源：董事代理、AIQAA代理
- 可評論對象：AIQAAgent（重新捲動預算）、ConsistencyAgent
- 工具存取（設計）：Sora 2 API、Veo 3.1、Runway Gen-4/Aleph、Kling 3.0；種子/參數註冊表
- 架構模式（設計）：DSPy / OPRO提示優化（Yang 2023）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1156 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.promptengineer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Target shot in ≤3 iterations vs human avg 10。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.promptengineer.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.sora', 'media.veo', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.promptengineer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.promptengineer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.promptengineer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.avatardesign` — AvatarDesignAgent

- **VA id／類別：** 47／`8-AI`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.avatardesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.avatardesign.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 綜合呈現者身分主機角色綁定：`AvatarDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 綜合呈現者身分 ### 知識蒸餾源（歷史）...

**來自 `agents.md` 設計列：**

- 責任：綜合呈現者身份
- 知識蒸餾來源：Synthesia/HeyGen 設計文件； Hany Farid 深度偽造檢測； C2PA規格
- 自評標準：跨鏡頭的身份哈希一致性；同意鏈； C2PA 簽署
- 超越人類訊號（理想）：C2PA 可驗證 + AI 大規模合作全通
- 接受 critique 來源：合規代理（同意）、DeepfakeDetectionAgent
- 可評論對象：VoiceCloneAgent（異樣）、LipSyncAgent
- 工具存取（設計）：HeyGen 阿凡達 IV API；合成API； C2PA簽名庫（c2patool）；人臉嵌入模型
- 架構模式（設計）：憲法AI（同意+身分憲法）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1154 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.avatardesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：C2PA-verifiable + Partnership-on-AI full-pass at scale。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.avatardesign.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.avatardesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.avatardesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.avatardesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist

- **VA id／類別：** 48／`8-AI`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.elevenlabs`  
- **Prompt 參照／檔案數：** `video.prompt.voiceclone.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.voiceclone.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 語音克隆+口型同步 主機角色綁定：`VoiceCloneAgent / LipSyncSpecialist (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 聲音克隆 + 口型同步 ### 知識蒸餾源（嗨…

**來自 `agents.md` 設計列：**

- 責任：語音克隆+口型同步
- 知識蒸餾來源：ElevenLabs 安全文件； Wav2Lip/Sync.so; Baxter 脣形同步參考
- 自評標準：語音MOS≥4.2；音位-視位錯誤<40ms；同意已驗證
- 超越人類訊號（理想）：贏得盲目 MOS 與專業 ADR 的較量
- 接受 critique 來源：ComplianceAgent（同意）、AnimatorAgent（對口型金）
- 可評論對象：AvatarDesignAgent（臉部閃爍）、DubbingAgent
- 工具存取（設計）：ElevenLabs v3 克隆 API； Sync.so 脣形同步； Wav2Lip；同意文件驗證
- 架構模式（設計）：Self-Refine + MOS評分模型作為評審

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1114 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.voiceclone.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind MOS vs professional ADR。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.voiceclone.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.elevenlabs']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.voiceclone.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.voiceclone.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.voiceclone` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.aiqaconsistency` — AIQAConsistencyAgent

- **VA id／類別：** 49／`8-AI`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.aiqaconsistency.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.aiqaconsistency.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 擷取幀漂移、手/臉偽影、身分中斷 主機角色綁定：`AIQAConsistencyAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）捕捉幀漂移、手部/面部偽影、ide...

**來自 `agents.md` 設計列：**

- 責任：捕捉幀漂移、手/臉偽影、身份中斷
- 知識蒸餾來源：VBBench；評估工匠； FVD文獻； MPC/Weta QC 檢查表；深度偽造模型
- 自評標準：每格偽影得分；身份哈希漂移；手/手指通過
- 超越人類訊號（理想）：捕獲量 > 95% 的高級 QC 捕獲量 + 30% 的錯過量
- 接受 critique 來源：DirectorAgent、VFXSupAgent
- 可評論對象：GeneratorAgent（重新滾動）、CompositorAgent
- 工具存取（設計）：VBench 評估套件；手部探測器型號；人臉 ID 嵌入 (ArcFace)；幀差異工具
- 架構模式（設計）：工具使用/ReAct（運行偵測器→標記→報告）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1182 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.aiqaconsistency.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches >95% of senior QC catches + 30% missed。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.aiqaconsistency.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.aiqaconsistency.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.aiqaconsistency.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.aiqaconsistency` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.personalizationengineer` — PersonalizationEngineerAgent

- **VA id／類別：** 50／`8-AI`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.personalizationengineer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.personalizationengineer.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 變數範本（姓名/臉孔/語音交換） 主機角色綁定：`PersonalizationEngineerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 變數範本（姓名/臉孔/聲音交換） ### 已知...

**來自 `agents.md` 設計列：**

- 責任：變數模板（姓名/臉孔/聲音交換）
- 知識蒸餾來源：Idomoo 案例研究； DMA 活動；行銷科技點亮
- 自評標準：渲染成功率≥99.5%；抽查合格；隱私審核通過
- 超越人類訊號（理想）：分享率高於頂級人工模板行銷活動
- 接受 critique 來源：合規代理 (GDPR/CCPA)、分析師代理
- 可評論對象：TemplateDesignerAgent（脆弱性）
- 工具存取（設計）：Idomoo/Pirsonal API； HeyGen 個人化； GDPR 同意管理平臺
- 架構模式（設計）：ReAct（組裝模板→渲染→驗證→交付）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1130 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.personalizationengineer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Higher share-rate than top human-templated campaigns。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.personalizationengineer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.personalizationengineer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.personalizationengineer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.personalizationengineer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.trailereditor` — TrailerEditorAgent

- **VA id／類別：** 51／`8-AI`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.trailereditor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.trailereditor.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 掛鉤驅動拖車切斷主機角色綁定：`TrailerEditorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表） 掛鉤驅動的拖車切割 ### 知識蒸餾來源（歷史） 金…

**來自 `agents.md` 設計列：**

- 責任：鉤驅動拖車切割
- 知識蒸餾來源：金預告片獎；毛紡/AV Squad 捲軸；預告片音樂庫
- 自評標準：上鉤率3秒；上升作用曲線；音樂同步精度
- 超越人類訊號（理想）：贏得金預告片盲比
- 接受 critique 來源：導演經紀人、音樂總監經紀人
- 可評論對象：EditorAgent（過切）、ComposerAgent（不符）
- 工具存取（設計）：達文西解決方案（MCP）；預告片音樂 API（Musicbed/Artlist）；保留曲線預測器
- 架構模式（設計）：自我完善（保留曲線模型作為回饋）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1105 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.trailereditor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins Golden-Trailer-rubric blind comparison。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.trailereditor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.trailereditor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.trailereditor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.trailereditor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp

- **VA id／類別：** 52／`8-AI`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.sportsanalyst.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.sportsanalyst.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 戰術分解+圖表 主機角色綁定：`SportsAnalystAgent / TelestratorOp (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 戰術分解 + 圖表 ### 知識蒸餾 …

**來自 `agents.md` 設計列：**

- 責任：戰術分解+圖表
- 知識蒸餾來源：麻省理工學院史隆管理學院論文； ESPN 統計與資訊；金莓分析
- 自評標準：通話準確率；螢幕清晰度得分
- 超越人類訊號（理想）：在戰術預測上擊敗前運動員
- 接受 critique 來源：SMEAgent（體育）、記者特工
- 可評論對象：EditorAgent（錯過重播）、MotionGraphicsAgent（圖表清晰度）
- 工具存取（設計）：體育數據 API（StatsBomb、NBA Stats）；遠端監控覆蓋工具；後效 MCP
- 架構模式（設計）：ReAct（取得播放資料→註解→渲染覆蓋）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1123 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.sportsanalyst.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats ex-athlete on tactical-prediction。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.sportsanalyst.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.sportsanalyst.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.sportsanalyst.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.sportsanalyst` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 9-Meta — Specialist Meta-Agents（元代理／平臺）（28 agents，平均成熟度 6.5）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=28，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=28，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=28，部分=0，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=28，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=28）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=28，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=28，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=28，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=28，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=28，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=28，否=0）

#### Agents

##### `video.orchestrator` — OrchestratorAgent

- **VA id／類別：** 53／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub`  
- **Prompt 參照／檔案數：** `video.prompt.orchestrator.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.orchestrator.v1`／files=0  
- **來源／溯源：** files=21 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 運行 CrewAI/AutoGen/LangGraph DAG；重試、超時、扇出/扇入 主機角色綁定：`OrchestratorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表）運行 CrewAI/AutoGen/LangGraph DAG；關於…

**來自 `agents.md` 設計列：**

- 責任：運行 CrewAI/AutoGen/LangGraph DAG；重試、逾時、扇出/扇入
- 知識蒸餾來源：LangGraph + CrewAI + AutoGen patterns;氣流/顳葉； PGA 賽程模板
- 自評標準：DAG完成度≥99.5%； SLA 遵守；死鎖 = 0
- 超越人類訊號（理想）：在相同範圍內，TTD 低於人類 EP
- 接受 critique 來源：ProducerAgent（範圍）、JudgeAgent（爭議）、HiTL 停止
- 可評論對象：所有代理商（資源消耗、重試風暴）
- 工具存取（設計）：LangGraph狀態機；時態工作流程引擎； Redis（分散式鎖）；可觀察性（朗史密斯）
- 架構模式（設計）：Agentic Graph (LangGraph) — 確定性 DAG 執行

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1231 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 21 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.orchestrator.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower TTD than human EP at same scope。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.orchestrator.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.orchestrator.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.orchestrator.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.orchestrator` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.planner` — PlannerAgent

- **VA id／類別：** 54／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.planner.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.planner.v1`／files=0  
- **來源／溯源：** files=24 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 將簡報分解為帶有分配 + 評論家門的分階段 DAG 主機角色綁定：`PlannerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）將概要分解為分階段 DAG，並分配給...

**來自 `agents.md` 設計列：**

- 責任：將簡報分解為帶有作業+評論門的分階段 DAG
- 知識蒸餾來源：專案管理知識體系； CrewAI 任務圖；階段模板
- 自評標準：計劃有效性（無漏門）；成本差異<10%
- 超越人類訊號（理想）：比 EP 首次通過（盲 A/B）更嚴格、更便宜的計劃
- 接受 critique 來源：ProducerAgent、FinanceAgent（預算）
- 可評論對象：RouterAgent（錯誤選擇）、OrchestratorAgent
- 工具存取（設計）：LangGraph 計畫產生；成本估算模型；甘特圖/PERT 工具
- 架構模式（設計）：ReAct（分解→估計→驗證→發出DAG）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1131 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 24 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.planner.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Tighter, cheaper plans than EP first pass (blind A/B)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.planner.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.planner.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.planner.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.planner` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.router` — RouterAgent

- **VA id／類別：** 55／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.router.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.router.v1`／files=0  
- **來源／溯源：** files=22 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 為每個子任務主機角色綁定選擇正確的專家代理（和模型）：`RouterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）為每個子項目選擇正確的專業代理（和模型）...

**來自 `agents.md` 設計列：**

- 責任：為每個子任務選擇正確的專家代理（和模型）
- 知識蒸餾來源：代理能力登記；基準歷史（成本/品質/延遲）
- 自評標準：與oracle相比路由準確率≥95%；成本在預算範圍內
- 超越人類訊號（理想）：在代理商/供應商選擇方面擊敗人類製作人
- 接受 critique 來源：OrchestratorAgent、CostOptimizerAgent
- 可評論對象：PlannerAgent（不好分解）
- 工具存取（設計）：代理註冊表資料庫；基準排行榜快取；定價 API
- 架構模式（設計）：Classifier + ReAct（匹配任務嵌入→代理能力）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1134 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 22 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.router.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats human producer in agent/vendor selection。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.router.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.router.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.router.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.router` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.judge` — JudgeAgent

- **VA id／類別：** 56／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.judge.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.judge.v1`／files=0  
- **來源／溯源：** files=23 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 透過多主體辯論裁決爭議；針對主機角色綁定的評分：`JudgeAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）透過多主體辯論裁決爭議；是…

**來自 `agents.md` 設計列：**

- 責任：透過多主體辯論裁決爭議；對照評分標準的分數
- 知識蒸餾來源：Du 2023（法學碩士辯論）； MT-工作臺評分細則；公會評分錶
- 自評標準：評估者間 κ 與專家小組 ≥0.8
- 超越人類訊號（理想）：κ 高於人類陪審員中位數
- 接受 critique 來源：HiTL 關於推翻裁決
- 可評論對象：導演經紀人、編劇經紀人、任何有爭議的組合
- 工具存取（設計）：MT-Bench/Arena 評估線束；標題模板引擎
- 架構模式（設計）：多智能體辯論 (Du 2023) + 法學碩士法官 (Zheng 2023)

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1115 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 23 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.judge.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Higher κ than median human juror。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.judge.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.judge.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.judge.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.judge` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.gatekeeper` — GateKeeperAgent

- **VA id／類別：** 57／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.gatekeeper.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.gatekeeper.v1`／files=0  
- **來源／溯源：** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 相變；驗證 L1/L2/L3 標準；標誌C2PA主機角色綁定：`GateKeeperAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）相變；驗證 L1/L2/L3 標準；簽名…

**來自 `agents.md` 設計列：**

- 責任：相變；驗證 L1/L2/L3 標準；標誌C2PA
- 知識蒸餾來源：階段門方法； PGA 製片人馬克；品質管理系統審核
- 自評標準：零洩漏缺陷；簽核 SLA ≥99%
- 超越人類訊號（理想）：與人類 QA 主管相比，逃逸缺陷率更低
- 接受 critique 來源：合規代理、AIQA一致性代理
- 可評論對象：OrchestratorAgent（過早推進）
- 工具存取（設計）：C2PA 簽章（c2patool）； JSON 模式驗證器；評價標準的終點
- 架構模式（設計）：憲法人工智慧（憲法=階段門標準）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1124 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 15 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.gatekeeper.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower escaped-defect rate than human QA lead。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.gatekeeper.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.gatekeeper.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.gatekeeper.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.gatekeeper` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.memory` — MemoryAgent

- **VA id／類別：** 58／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.memory.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.memory.v1`／files=0  
- **來源／溯源：** files=28 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 情境+長期專案記憶；檢索任何代理主機角色綁定：`MemoryAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）情境 + 長期項目記憶；檢索…

**來自 `agents.md` 設計列：**

- 責任：情景+長期專案記憶；檢索任何代理
- 知識蒸餾來源：反思（Shinn 2023）；記憶GPT；向量資料庫最佳實踐
- 自評標準：檢索精度@5≥0.9；新鮮度SLA
- 超越人類訊號（理想）：大規模召回率高於製片人聖經
- 接受 critique 來源：所有代理（更正事件）
- 可評論對象：所有代理（陳舊事實）
- 工具存取（設計）：Pinecone/Weaviate/Qdrant載體DB； MemGPT 式分層記憶體；嵌入模型
- 架構模式（設計）：反射記憶體架構（MemGPT 擴充）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1116 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 28 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.memory.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Higher recall than producer's bible at scale。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.memory.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.memory.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.memory.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.memory` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.ideation` — IdeationAgent

- **VA id／類別：** 59／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.ideation.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.ideation.v1`／files=0  
- **來源／溯源：** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 對概念、掛鉤、標語進行不同的腦力激盪主持人角色綁定：`IdeationAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 對概念、掛鉤、標語進行不同的腦力激盪 ### Knowle...

**來自 `agents.md` 設計列：**

- 責任：對概念、亮點、口號進行不同的腦力激盪
- 知識蒸餾來源：坎城大獎賽；爸爸; IDEO設計思維；SCAMPER/德博諾
- 自評標準：想法計數；新穎性（嵌入距離）；語意多樣性
- 超越人類訊號（理想）：在概念密度方面贏得機構推廣槍戰
- 接受 critique 來源：創意總監代理、新奇代理
- 可評論對象：CopywriterAgent（衍生性商品）、DirectorAgent（不可拍攝）
- 工具存取（設計）：嵌入新穎的記分器；概念聚類（UMAP）； Arena.na/Pinterest 搜尋
- 架構模式（設計）：自我完善+NoveltyAgent作為評論家

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1138 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 16 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.ideation.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins agency-pitch shootouts on concept density。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.ideation.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.ideation.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.ideation.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.ideation` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.narrativearc` — NarrativeArcAgent

- **VA id／類別：** 60／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.narrativearc.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.narrativearc.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 三幕/救貓/英雄之旅結構 主機角色綁定：`NarrativeArcAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）三幕 / 拯救貓 / 英雄之旅結構 ### Knowle…

**來自 `agents.md` 設計列：**

- 責任：三幕 / 拯救貓咪 / 英雄之旅結構
- 知識蒸餾來源：坎貝爾；施奈德*拯救貓*；特魯比；黑名單分析
- 自評標準：拍錶覆蓋率100%；轉折點間距；圓弧曲線擬合
- 超越人類訊號（理想）：擊敗 WGA 結構性標題初稿
- 接受 critique 來源：編劇經紀人、導演經紀人
- 可評論對象：編劇代理（中下垂）
- 工具存取（設計）：節拍表驗證器；情感弧線繪圖儀；結構模板
- 架構模式（設計）：自我完善（標題：節拍表完整性）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1106 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.narrativearc.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats WGA first drafts on structural rubric。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.narrativearc.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.narrativearc.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.narrativearc.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.narrativearc` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.styletransfer` — StyleTransferAgent

- **VA id／類別：** 61／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.runway, media.veo`  
- **Prompt 參照／檔案數：** `video.prompt.styletransfer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.styletransfer.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 在鏡頭中一致地應用指定的美學 主機角色綁定：`StyleTransferAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）在各個鏡頭中一致應用指定的美學 ### K...

**來自 `agents.md` 設計列：**

- 責任：在各個鏡頭中一致地應用指定的美學
- 知識蒸餾來源：精心策劃的風格語料庫； LoRA/種子登記處；參考框架銀行
- 自評標準：風格相似度（CLIP/DINO）≥0.85；交叉射擊變異數≤τ
- 超越人類訊號（理想）：與人類調色師+分級師相比，贏得盲目偏好
- 接受 critique 來源：導演代理、調色師代理
- 可評論對象：GeneratorAgent（關閉式）
- 工具存取（設計）：每個款式的 LoRA 重量； CLIP/DINO 相似度評分器；跑道風格-鎖定模式；舒適用戶介面
- 架構模式（設計）：自我完善（CLIP 風格分數作為回饋）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1122 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.styletransfer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Wins blind preference vs human colorist+grader。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.styletransfer.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.runway', 'media.veo']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.styletransfer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.styletransfer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.styletransfer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.worldbuilding` — WorldBuildingAgent

- **VA id／類別：** 62／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.worldbuilding.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.worldbuilding.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 故事、規則、地理、派系、魔法/科技系統 宿主角色綁定：`WorldBuildingAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）背景知識、規則、地理、派系、魔法/科技系統…

**來自 `agents.md` 設計列：**

- 責任：傳說、規則、地理、派系、魔法/科技系統
- 知識蒸餾來源：託爾金； *世界構建*（亞當斯）；粉絲維基；系列聖經洩露
- 自評標準：內部一致性（無矛盾）；規則完整性
- 超越人類訊號（理想）：矛盾率低於 10 倍卷的作家聖經
- 接受 critique 來源：ShowrunnerAgent、FactCheckerAgent
- 可評論對象：ScreenwriterAgent（絕殺）、ConceptArtistAgent
- 工具存取（設計）：長語境法學碩士（Gemini 2.5 Pro）；矛盾檢測模型；維基圖資料庫
- 架構模式（設計）：反思（矛盾修正→情景記憶）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1176 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.worldbuilding.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower contradiction rate than writers' bibles at 10× volume。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.worldbuilding.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.worldbuilding.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.worldbuilding.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.worldbuilding` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.moodboard` — MoodBoardAgent

- **VA id／類別：** 63／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.moodboard.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.moodboard.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 參考板：視覺、聲音、音調 主機角色綁定：`MoodBoardAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 參考板：視覺、聲音、音調 ### 知識蒸餾酸...

**來自 `agents.md` 設計列：**

- 責任：參考板：視覺、聲音、音調
- 知識蒸餾來源：Pinterest/Are.na；造型手冊檔案； Spotify-Canvas
- 自評標準：參考一致性（簇緊密密度）；簡短的對齊
- 超越人類訊號（理想）：比藝術總監更快+更緊的板子（盲A/B）
- 接受 critique 來源：總監代理、製作設計代理
- 可評論對象：ConceptArtistAgent（心情不好）
- 工具存取（設計）：Pinterest/Are.na API; Spotify 畫布； CLIP聚類； Figma 板代
- 架構模式（設計）：ReAct（搜尋→聚類→佈局→驗證一致性）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1103 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.moodboard.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Faster + tighter boards than art director (blind A/B)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.moodboard.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.moodboard.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.moodboard.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.moodboard` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.novelty` — NoveltyAgent / Anti-Cliché Critic

- **VA id／類別：** 64／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.novelty.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.novelty.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 標記比喻、陳腔濫調、過度擬合輸出主機角色綁定：`NoveltyAgent / Anti-Cliché Critic (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）標記比喻、陳腔濫調、過度擬合輸出 ### Knowle...

**來自 `agents.md` 設計列：**

- 責任：標記比喻、陳腔濫調、過度擬合輸出
- 知識蒸餾來源：電視比喻； OpenSubtitles n-gram 頻率；語料庫新穎性嵌入
- 自評標準：陳腔濫調的點擊次數；新穎性分數與先驗類別得分
- 超越人類訊號（理想）：比經驗豐富的腳本編輯器更能捕捉陳腔濫調
- 接受 critique 來源：創意經紀人、編劇經紀人
- 可評論對象：ScreenwriterAgent（比喻填充）、CopywriterAgent（模板化）
- 工具存取（設計）：電視比喻刮刀； n-gram 頻率資料庫；嵌入新奇記分器
- 架構模式（設計）：法官法學碩士（反陳腔濫調憲法）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1127 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.novelty.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches more clichés than experienced script editor。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.novelty.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.novelty.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.novelty.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.novelty` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.emotionalarc` — EmotionalArcAgent

- **VA id／類別：** 65／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.emotionalarc.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.emotionalarc.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 繪製效價/喚醒曲線；建議擊敗主機角色綁定：`EmotionalArcAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）映射效價/喚醒曲線；建議拍子 ### 知識蒸餾...

**來自 `agents.md` 設計列：**

- 責任：繪製效價/喚醒曲線；建議節拍
- 知識蒸餾來源：普拉奇克；情感計算語料庫； Cron *故事天才*
- 自評標準：曲線擬合目標；生物訊號代理回歸準確性
- 超越人類訊號（理想）：比 NRG 測試篩選卡更好的保留預測
- 接受 critique 來源：導演代理、編輯代理、作曲代理
- 可評論對象：EditorAgent（平中間）、ComposerAgent（提示不符）
- 工具存取（設計）：情緒/情緒分類器（GoEmotions）；保留曲線預測器；生物訊號代理模型
- 架構模式（設計）：自我完善（情緒弧線作為標題目標）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1166 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.emotionalarc.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Better retention prediction than NRG test-screening cards。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.emotionalarc.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.emotionalarc.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.emotionalarc.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.emotionalarc` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.webresearch` — WebResearchAgent

- **VA id／類別：** 66／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.webresearch.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.webresearch.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 即時網路搜尋、來源排名、引文擷取 主機角色綁定：`WebResearchAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）即時網路搜尋、來源排名、引文提取#...

**來自 `agents.md` 設計列：**

- 責任：即時網路搜尋、來源排名、引文提取
- 知識蒸餾來源：Bing/Google/Brave API；普通爬行；困惑模式
- 自評標準：每個聲明的來源等級；引用精確度；近期熱門
- 超越人類訊號（理想）：比新聞編輯室研究員更快+更多來源
- 接受 critique 來源：FactCheckerAgent、CitationAgent
- 可評論對象：編劇代理人（未引用的權利要求）
- 工具存取（設計）：Brave/Google 搜尋 API; Jina Reader（網頁→markdown）；來源品質分類器
- 架構模式（設計）：ReAct（查詢→取得→擷取→評分→引用）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1122 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.webresearch.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Faster + more sources than newsroom researcher。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.webresearch.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.webresearch.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.webresearch.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.webresearch` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.archiveresearch` — ArchiveResearchAgent

- **VA id／類別：** 67／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.archiveresearch.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.archiveresearch.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 歷史/學術/檔案深度搜尋 主機角色綁定：`ArchiveResearchAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）歷史/學術/檔案深度搜尋 ### 知識...

**來自 `agents.md` 設計列：**

- 責任：歷史/學術/檔案深度搜索
- 知識蒸餾來源：JSTOR、arXiv、PubMed、美聯社檔案、Getty、FOIA
- 自評標準：主要來源比率；檔案覆蓋廣度
- 超越人類訊號（理想）：比文檔製作者更高的主要來源比例
- 接受 critique 來源：FactCheckerAgent、SMEAgent
- 可評論對象：ScriptwriterAgent（二手來源依賴）
- 工具存取（設計）：JSTOR/arXiv/PubMed API；蓋蒂圖片API；資訊自由法請求工具； OCR（超立方體）
- 架構模式（設計）：ReAct（制定查詢→搜尋檔案→擷取→對來源進行評分）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1114 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.archiveresearch.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Higher primary-source ratio than doc producer。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.archiveresearch.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.archiveresearch.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.archiveresearch.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.archiveresearch` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.trendintelligence` — TrendIntelligenceAgent

- **VA id／類別：** 68／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.trendintelligence.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.trendintelligence.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 偵測新興迷因、聲音、格式主機角色綁定：`TrendIntelligenceAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）偵測新興迷因、聲音、格式 ### 知識提煉...

**來自 `agents.md` 設計列：**

- 責任：偵測新出現的迷因、聲音、格式
- 知識蒸餾來源：TikTok創意中心；流行趨勢；管狀； Reddit/X 消防水帶
- 自評標準：預測提前期與高峯；趨勢清單上的精確度/召回率
- 超越人類訊號（理想）：比人類戰略家更早、更精確地檢測
- 接受 critique 來源：社交策略師代理、文案代理
- 可評論對象：IdeationAgent（非流行）
- 工具存取（設計）：TikTok創意中心API； Reddit/X 串流媒體 API；感測器塔；Google趨勢
- 架構模式（設計）：ReAct + 時間序列異常檢測

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1116 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.trendintelligence.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Earlier detection than human strategists at higher precision。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.trendintelligence.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.trendintelligence.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.trendintelligence.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.trendintelligence` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.competitorintelligence` — CompetitorIntelligenceAgent

- **VA id／類別：** 69／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.competitorintelligence.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.competitorintelligence.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 哪些競爭對手正在提供主機角色綁定：`CompetitorIntelligenceAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 競爭對手正在運輸什麼 ### 知識蒸餾源（...

**來自 `agents.md` 設計列：**

- 責任：競爭對手正在運送哪些產品
- 知識蒸餾來源：元廣告庫； TikTok 熱門廣告； YouTube 抓取；發布追蹤器
- 自評標準：涵蓋競爭對手組的百分比；我們的新奇與景觀
- 超越人類訊號（理想）：比代理策略更全面
- 接受 critique 來源：品牌代理商、創意總監代理
- 可評論對象：IdeationAgent（衍生性商品）
- 工具存取（設計）：元廣告庫 API； TikTok 熱門廣告；類似網路； YouTube 資料 API v3
- 架構模式（設計）：ReAct（抓取競爭對手→分類→報告差距）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1082 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.competitorintelligence.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：More comprehensive than agency strategy decks。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.competitorintelligence.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.competitorintelligence.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.competitorintelligence.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.competitorintelligence` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.citation` — CitationAgent

- **VA id／類別：** 70／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.citation.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.citation.v1`／files=0  
- **來源／溯源：** files=17 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 標準化來源；年級小學/中學/大學主機角色綁定：`CitationAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）標準化來源；小學/中學/大學年級##...

**來自 `agents.md` 設計列：**

- 責任：標準化來源；小學/中學/大學年級
- 知識蒸餾來源：芝加哥，APA，AP 風格；​​ SPJ分級； CRAAP測試
- 自評標準：引文格式100%有效；主要％≥目標
- 超越人類訊號（理想）：錯誤率低於新聞編輯室影印臺
- 接受 critique 來源：FactCheckerAgent、記者Agent
- 可評論對象：WebResearchAgent（弱源）
- 工具存取（設計）：引文解析器（AnyStyle）； DOI 解析器； CRAAP評分模型
- 架構模式（設計）：自我完善（格式驗證器+來源分級器作為標題）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1088 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 17 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.citation.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower error rate than newsroom copy desk。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.citation.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.citation.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.citation.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.citation` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.interviewsynthesis` — InterviewSynthesisAgent

- **VA id／類別：** 71／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.interviewsynthesis.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.interviewsynthesis.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 將實務工作者訪談合成資料主機角色綁定：`InterviewSynthesisAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）將從業者訪談綜合為資料 ### 知道...

**來自 `agents.md` 設計列：**

- 責任：將實務工作者訪談綜合成數據
- 知識蒸餾來源：水獺/Rev成績單；同意書； SAG/WGA 模板
- 自評標準：編碼者間就主題達成一致；同意完整性
- 超越人類訊號（理想）：比定性研究者更快+更豐富的主題擷取
- 接受 critique 來源：ResearchPIAgent (HiTL)、合規代理
- 可評論對象：SMEAgent（錯誤總結專家）
- 工具存取（設計）：Otter.ai/Rev API（轉錄）；主題編碼模型；同意管理資料庫
- 架構模式（設計）：反思（面試官根據主題差距完善問題）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1145 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.interviewsynthesis.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Faster + richer theme extraction than qualitative researcher。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.interviewsynthesis.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.interviewsynthesis.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.interviewsynthesis.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.interviewsynthesis` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.benchmarkresearch` — BenchmarkResearchAgent

- **VA id／類別：** 72／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.benchmarkresearch.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.benchmarkresearch.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 監控 VBench、EvalCrafter、MT-Bench、FVD、CLIP-T 排行榜 主機角色綁定：`BenchmarkResearchAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）監控 VBench、EvalCrafter、MT-Ben...

**來自 `agents.md` 設計列：**

- 責任：監控 VBench、EvalCrafter、MT-Bench、FVD、CLIP-T 排行榜
- 知識蒸餾來源：帶代碼的論文； HuggingFace 排行榜；會議記錄
- 自評標準：基準測試的涵蓋範圍；保鮮度≤7天
- 超越人類訊號（理想）：比 ML 研究團隊更快、更廣泛
- 接受 critique 來源：優化代理（任何）
- 可評論對象：所有 AI 代理（過時的基線）
- 工具存取（設計）：論文與程式碼 API； HuggingFace 中心 API； arXiv RSS； VBench 排行榜抓取工具
- 架構模式（設計）：ReAct（民調排行榜→偵測變化→警報）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1135 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.benchmarkresearch.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Faster + broader than ML-research team。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.benchmarkresearch.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.benchmarkresearch.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.benchmarkresearch.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.benchmarkresearch` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.promptoptimizer` — PromptOptimizerAgent

- **VA id／類別：** 73／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.promptoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.promptoptimizer.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 透過 OPRO/APE/DSPy/Promptbreeder 主機角色綁定自動改進提示：`PromptOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）透過 OPRO/APE/DSPy/Promptbre 自動改進提示...

**來自 `agents.md` 設計列：**

- 責任：透過 OPRO/APE/DSPy/Promptbreeder 自動改進提示
- 知識蒸餾來源：OPRO（楊2023）； APE（週2022）；DSPy（史丹佛大學）；Promptbreeder (DeepMind)
- 自評標準：每次迭代的分數提升；收斂速度
- 超越人類訊號（理想）：擊敗內褲上手工調整的提示
- 接受 critique 來源：PromptEngineerAgent、AIQAAgent
- 可評論對象：PromptEngineerAgent（次優種子）
- 工具存取（設計）：DSPy框架（MIPRO優化器）；OPRO 實作；伸出的評估線束
- 架構模式（設計）：DSPy編譯+OPRO元最佳化

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1131 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.promptoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats hand-tuned prompts on held-out briefs。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.promptoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.promptoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.promptoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.promptoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.costoptimizer` — CostOptimizerAgent

- **VA id／類別：** 74／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.costoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.costoptimizer.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 模型/提供者之間的路由，用於 $/品質主機角色綁定：`CostOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）模型/提供者之間的路線以獲取美元/品質 ### 知識...

**來自 `agents.md` 設計列：**

- 責任：模型/提供者之間的路線，價格/質量
- 知識蒸餾來源：供應商定價；成本品質邊界；節儉的GPT模式
- 自評標準：$/成功的任務；距離邊界的帕累託距離
- 超越人類訊號（理想）：比人工 CFO 路由更低的成本/質量
- 接受 critique 來源：路由器Agent、財務Agent
- 可評論對象：RouterAgent（超支）、GeneratorAgent（重滾燒錄）
- 工具存取（設計）：提供者定價 API；基準成本資料庫； FrugalGPT 級聯邏輯
- 架構模式（設計）：ReAct（評估任務→選擇滿足閾值的最便宜模型）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1116 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.costoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower $/quality than human CFO routing。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.costoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.costoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.costoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.costoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.latencyoptimizer` — LatencyOptimizerAgent

- **VA id／類別：** 75／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.latencyoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.latencyoptimizer.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 平行化、快取、推測性解碼、批次 主機角色綁定：`LatencyOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）並行化、快取、推測解碼…

**來自 `agents.md` 設計列：**

- 責任：並行化、快取、推測解碼、批次處理
- 知識蒸餾來源：法學碩士； TensorRT-法學碩士；蒸餾；任意尺度/射線
- 自評標準：p50/p95 潛伏期；吞吐量/GPU 小時
- 超越人類訊號（理想）：p95 低於人工調整的管道
- 接受 critique 來源：Orchestrator代理
- 可評論對象：OrchestratorAgent（串列瓶頸）
- 工具存取（設計）：法學碩士； TensorRT-法學碩士；雷發球； Redis（響應緩存）；推測解碼配置
- 架構模式（設計）：工具使用分析+自動化管道重組

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1096 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.latencyoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lower p95 than human-tuned pipeline。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.latencyoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.latencyoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.latencyoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.latencyoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.retentionoptimizer` — RetentionOptimizerAgent

- **VA id／類別：** 76／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.retentionoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.retentionoptimizer.v1`／files=0  
- **來源／溯源：** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 調整 AVD/hold-rate 的鉤子、節奏、結構 主機角色綁定：`RetentionOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表） 調整 AVD/hold-rate 的鉤子、節奏、結構 ### …

**來自 `agents.md` 設計列：**

- 責任：調整 AVD/hold-rate 的鉤子、節奏、結構
- 知識蒸餾來源：YouTube 分析基準； TikTok 保留曲線；觀眾模擬
- 自評標準：預測保留率與實際保留率； AVD 提升控制
- 超越人類訊號（理想）：在 AVD 提升方面擊敗 YouTube 高級編輯 (A/B)
- 接受 critique 來源：EditorAgent、AudienceSimAgent
- 可評論對象：EditorAgent（慢速開啟）、ScriptwriterAgent（前面的絨毛）
- 工具存取（設計）：YouTube 分析 API；保留曲線預測模型； A/B 測試框架
- 架構模式（設計）：RLAIF（獎勵 = 真實分析帶來的保留率提升）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1150 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 15 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.retentionoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats senior YouTube editor on AVD lift (A/B)。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.retentionoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.retentionoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.retentionoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.retentionoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.roasoptimizer` — ROASOptimizerAgent

- **VA id／類別：** 77／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.roasoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.roasoptimizer.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 優化廣告創意以提高效能主機角色綁定：`ROASOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）優化廣告創意以提高效果 ### 知識蒸餾 …

**來自 `agents.md` 設計列：**

- 責任：優化廣告創意以提高效果
- 知識蒸餾來源：元行銷科學； TikTok 廣告學院； MMM/MTA 點亮
- 自評標準：ROAS 提升與控制對比；顯著性≥95%
- 超越人類訊號（理想）：在同等預算下擊敗高級行銷人員
- 接受 critique 來源：績效行銷代理、分析師代理
- 可評論對象：UGCAgent（低鉤）、CopywriterAgent（弱CTA）
- 工具存取（設計）：元廣告 API（創意測試）； TikTok 廣告；貝葉斯 MMM 工具 (Robyn/Meridian)
- 架構模式（設計）：RLAIF（獎勵=廣告平臺回饋的真實ROAS）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1100 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.roasoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Beats senior marketer at equal budget。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.roasoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.roasoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.roasoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.roasoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent

- **VA id／類別：** 78／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.accessibilityoptimizer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.accessibilityoptimizer.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** WCAG 2.2 對比、字幕、音訊描述、色盲安全 主機角色綁定：`AccessibilityOptimizerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）WCAG 2.2 對比、字幕、au…

**來自 `agents.md` 設計列：**

- 責任：WCAG 2.2 對比、字幕、音訊描述、色盲安全
- 知識蒸餾來源：WCAG 2.2； W3C/WAI-ARIA； DCMP 字幕金鑰；聾人/HoH 指南
- 自評標準：一致性100%AA，≥90%AAA；標題 WER ≤2%
- 超越人類訊號（理想）：比 ADA 認證審核員發現更多的 a11y 缺陷
- 接受 critique 來源：AccessibilityAgent (HiTL)、ComplianceAgent
- 可評論對象：EditorAgent（字幕同步）、ColoristAgent（對比）
- 工具存取（設計）：斧核/燈塔（對比）； Whisper v4（字幕）；音訊描述產生器
- 架構模式（設計）：憲法人工智慧（憲法 = WCAG 2.2 成功標準）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1211 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.accessibilityoptimizer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches more a11y defects than ADA-certified auditor。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.accessibilityoptimizer.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.accessibilityoptimizer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.accessibilityoptimizer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.accessibilityoptimizer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.evaluationharness` — EvaluationHarnessAgent

- **VA id／類別：** 79／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.evaluationharness.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.evaluationharness.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 執行基準測試（VBench、EvalCrafter、MT-Bench、FVD、CLIP-T）；貼文回歸主機角色綁定：`EvaluationHarnessAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表）運行基準測試（VBen...

**來自 `agents.md` 設計列：**

- 責任：執行基準測試（VBench、EvalCrafter、MT-Bench、FVD、CLIP-T）；貼文回歸
- 知識蒸餾來源：附程式碼的論文； HuggingFace 排行榜；基準回購協議
- 自評標準：回歸精度/召回率；警報延遲<1小時
- 超越人類訊號（理想）：捕捉回歸速度比 ML-eng 旋轉快
- 接受 critique 來源：基準研究代理
- 可評論對象：所有 AI 代理（回歸警報）
- 工具存取（設計）：VBench 套件；評估工匠； MT-長凳安全帶； CI/CD（GitHub 操作）；警報（PagerDuty）
- 架構模式（設計）：工具使用/ReAct（執行基準測試→比較→若出現迴歸則發出警報）

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1195 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.evaluationharness.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches regressions faster than ML-eng rotation。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.evaluationharness.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.evaluationharness.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.evaluationharness.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.evaluationharness` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.safetyredteam` — SafetyRedTeamAgent

- **VA id／類別：** 80／`9-Meta`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.safetyredteam.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.safetyredteam.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 針對深度造假、偏見、越獄、誹謗的對抗性攻擊主機角色綁定：`SafetyRedTeamAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）針對深度造假、偏見等的對抗性攻擊

**來自 `agents.md` 設計列：**

- 責任：針對深度造假、偏見、越獄、誹謗的對抗性攻擊
- 知識蒸餾來源：Hany Farid 基準；人工智慧框架合作； OWASP 法學碩士前 10 名
- 自評標準：攻擊成功率維持≤1%；分類覆蓋範圍
- 超越人類訊號（理想）：比內部紅隊輪換覆蓋率更高
- 接受 critique 來源：EthicsAgent (HiTL)、合規代理
- 可評論對象：AvatarDesignAgent、VoiceCloneAgent、AllGenerators
- 工具存取（設計）：Deepfake 探測器（Farid 實驗室模型）；偏置探針；越獄提示銀行； OWASP 掃描儀
- 架構模式（設計）：多智能體辯論（紅隊 vs 防守者）+對抗性搜索

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1192 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.safetyredteam.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Higher coverage than internal red-team rotation。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.safetyredteam.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.safetyredteam.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.safetyredteam.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.safetyredteam` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

### 10-Sup — Workflow Support（流程支援）（34 agents，平均成熟度 6.37）

#### 分組綜合

- **1) SPEC.md 中的責任（Responsibility）是否清楚界定：** 主調 **是**（是=34，部分=0，否=0）
- **2) 是否有專業知識蒸餾計畫：** 主調 **是**（是=34，部分=0，否=0）
- **3) 是否有蒸餾來源／是否知道如何取得來源：** 主調 **是**（是=25，部分=9，否=0）
- **4) 是否已收集自評方法與相關內容：** 主調 **部分**（是=0，部分=34，否=0）
- **5) 現行實作是否已超越人類：** 主調 **否**（是=0，部分=0，否=34）
- **6) 如何執行工作：** 主調 **部分**（是=0，部分=34，否=0）
- **7) 是否有專屬 skills／plugins／harness：** 主調 **部分**（是=0，部分=34，否=0）
- **8) 是否有自我改進機制：** 主調 **部分**（是=0，部分=34，否=0）
- **9) 是否知道如何蒐集／研究資訊以自我改進：** 主調 **部分**（是=0，部分=34，否=0）
- **10) 是否能接收／發送指令與其他 agent 協作：** 主調 **部分**（是=0，部分=34，否=0）
- **11) 是否能自行解決衝突並確認：** 主調 **部分**（是=0，部分=34，否=0）

#### Agents

##### `video.analyst` — AnalystAgent

- **VA id／類別：** 81／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.analyst.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.analyst.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 將業務、創意和技術效能遙測資料聚合到決策就緒報告中 主機角色綁定：`AnalystAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）聚合業務…

**來自 `agents.md` 設計列：**

- 責任：將業務、創意和技術性能遙測數據匯總到可供決策的報告中
- 知識蒸餾來源：平臺分析儀錶板；實驗日誌；評估利用輸出；基準歷史
- 自評標準：關鍵績效指標完整性；預測與實際差異在容差範圍內；洞察到行動的轉變
- 超越人類訊號（理想）：比人類分析師輪換更快地檢測可操作的績效變化
- 接受 critique 來源：SocialMediaStrategistAgent、PerformanceMarketerAgent、EvaluationHarnessAgent
- 可評論對象：廣告活動節奏、發佈時間、留存率和 ROAS 異常
- 工具存取（設計）：YouTube 分析、Meta/TikTok 廣告儀錶板、BI 倉庫、基準日誌
- 架構模式（設計）：基於遙測的 ReAct + 迴歸分析

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1370 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.analyst.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Detects actionable performance shifts faster than human analyst rotations。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.analyst.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.analyst.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.analyst.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.analyst` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.audiencesim` — AudienceSimAgent

- **VA id／類別：** 82／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.audiencesim.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.audiencesim.v1`／files=0  
- **來源／溯源：** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 模擬觀眾偏好、參與度和退出主持人角色綁定：`AudienceSimAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）模擬觀眾偏好、參與度和下降…

**來自 `agents.md` 設計列：**

- 責任：模擬受眾偏好、參與度和流失率
- 知識蒸餾來源：成對偏好資料集；保留研究；受眾細分模型
- 自評標準：不同羣體的偏好穩定性；保留預測準確度；分歧記錄
- 超越人類訊號（理想）：比傳統的測試螢幕週期更早預測觀眾反應
- 接受 critique 來源：導演代理、編輯代理、分析師代理、法官代理
- 可評論對象：吸引力、節奏、清晰度、情感契合度、預告片強度
- 工具存取（設計）：角色模擬器、成對評估工具、保留模型
- 架構模式（設計）：法學碩士作為法官 + 成對偏好面板

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1230 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 15 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.audiencesim.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Predicts audience reaction earlier than conventional test-screen cycles。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.audiencesim.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.audiencesim.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.audiencesim.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.audiencesim` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.accessibility` — AccessibilityAgent

- **VA id／類別：** 83／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.accessibility.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.accessibility.v1`／files=0  
- **來源／溯源：** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 在發布主機角色綁定之前擁有最終的可訪問性接受：`AccessibilityAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）在發布之前擁有最終的可訪問性驗收 ###...

**來自 `agents.md` 設計列：**

- 責任：在發布前擁有最終的可訪問性驗收
- 知識蒸餾來源：WCAG 2.2、字幕和 AD 指南、Deaf/HoH 審查框架
- 自評標準：字幕準確度、廣告完整性、對比合規性、發布準備情況
- 超越人類訊號（理想）：在人工審核之前發現阻礙發布的可訪問性問題
- 接受 critique 來源：AccessibilityOptimizerAgent、EditorAgent、ColoristAgent、SoundMixerAgent
- 可評論對象：字幕同步、對比問題、缺少 AD 或手語層
- 工具存取（設計）：字幕驗證器、比較分析器、AD 審查工具
- 架構模式（設計）：憲法人工智慧與無障礙憲法

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1220 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 14 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.accessibility.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Finds release-blocking accessibility issues before human audits do。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.accessibility.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.accessibility.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.accessibility.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.accessibility` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.brand` — BrandAgent

- **VA id／類別：** 84／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.brand.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.brand.v1`／files=0  
- **來源／溯源：** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 強化品牌聲音、宣告邊界與視覺一致性 主持人角色綁定：`BrandAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）強化品牌聲音、主張邊界和視覺…

**來自 `agents.md` 設計列：**

- 責任：加強品牌聲音、主張界限和視覺一致性
- 知識蒸餾來源：品牌書籍、經批准的活動、法律聲明護欄、語調指南
- 自評標準：品牌聲音相似、政策遵守、資產偏差小
- 超越人類訊號（理想）：比分散的人工審核更能保持跨通路品牌一致性
- 接受 critique 來源：CopywriterAgent、MotionGraphicsAgent、MarketingAgent、BrandStrategistAgent
- 可評論對象：語音漂移、視覺不一致、索賠蠕變
- 工具存取（設計）：品牌資產庫、嵌入相似度、風格指南
- 架構模式（設計）：針對品牌組成進行自我完善

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1215 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 15 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.brand.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Holds cross-channel brand consistency better than fragmented human review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.brand.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.brand.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.brand.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.brand` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.brandstrategist` — BrandStrategistAgent

- **VA id／類別：** 85／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.brandstrategist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.brandstrategist.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 在腳本和行銷活動執行之前定義受眾價值框架和定位 主持人角色綁定：`BrandStrategistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）定義受眾羣體…

**來自 `agents.md` 設計列：**

- 責任：在腳本和行銷活動執行之前定義受眾價值框架和定位
- 知識蒸餾來源：定位框架、活動策略、市場研究、品牌架構文檔
- 自評標準：策略連貫性、差異化優勢、受眾訊息清晰度
- 超越人類訊號（理想）：比臨時人工交接產生更清晰的品牌到腳本翻譯
- 接受 critique 來源：品牌代理、編劇代理、行銷代理
- 可評論對象：定位差距、價值主張薄弱、受眾框架失調
- 工具存取（設計）：研究平臺、訊息傳遞框架、策略模板
- 架構模式（設計）：BrandAgent 和 CreativeDirectorAgent 的多代理辯論

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1302 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.brandstrategist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Produces clearer brand-to-script translation than ad hoc human handoffs。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.brandstrategist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.brandstrategist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.brandstrategist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.brandstrategist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.marketing` — MarketingAgent

- **VA id／類別：** 86／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.marketing.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.marketing.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 用於啟動、促銷和發布排序的包內容主機角色綁定：`MarketingAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 發布、促銷和…的打包內容

**來自 `agents.md` 設計列：**

- 責任：用於發布、促銷和發布排序的打包內容
- 知識蒸餾來源：活動手冊、發布日曆、媒體計畫、資產包裝要求
- 自評標準：元資料完整性、資產準備狀況、啟動排序準確性
- 超越人類訊號（理想）：比手動行銷活動更快地發送多管道啟動包
- 接受 critique 來源：SocialMediaStrategistAgent、SEOAgent、CopywriterAgent、TrailerEditorAgent
- 可評論對象：格式缺失、推出時機不佳、促銷組合不完整
- 工具存取（設計）：活動管理套件、元資料工具、發布規劃器
- 架構模式（設計）：對啟動清單和頻道要求做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1257 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.marketing.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Ships multi-channel launch packages faster than manual campaign ops。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.marketing.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.marketing.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.marketing.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.marketing` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.seo` — SEOAgent

- **VA id／類別：** 87／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.seo.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.seo.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 透過標題、描述、元資料和搜尋意圖優化可發現性 主機角色綁定：`SEOAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）通過…優化可發現性

**來自 `agents.md` 設計列：**

- 責任：透過標題、描述、元資料和搜尋意圖優化可發現性
- 知識蒸餾來源：搜尋排名研究、影片元資料最佳實踐、關鍵字分類法
- 自評標準：關鍵字匹配、元資料完整性、搜尋意圖匹配
- 超越人類訊號（理想）：比手動元資料調整更快提升可發現性
- 接受 critique 來源：行銷代理、文案代理、分析師代理
- 可評論對象：關鍵字弱、標題與描述不符、元資料遺漏
- 工具存取（設計）：關鍵字工具、元資料 API、排名儀錶板
- 架構模式（設計）：透過搜尋意圖驗證進行 ReAct

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1203 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.seo.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Lifts discoverability faster than manual metadata tuning。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.seo.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.seo.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.seo.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.seo` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.community` — CommunityAgent

- **VA id／類別：** 88／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.community.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.community.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 捕捉社區響應並對定性訊號進行分類 宿主角色綁定：`CommunityAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）捕獲社區回應並分類品質…

**來自 `agents.md` 設計列：**

- 責任：捕捉社區反應並對定性訊號進行分類
- 知識蒸餾來源：社區審核手冊、情緒資料集、升級規則
- 自評標準：反應延遲、問題聚類品質、情緒追蹤準確性
- 超越人類訊號（理想）：在手動評論審核之前先浮現新出現的受眾擔憂
- 接受 critique 來源：AnalystAgent、SocialMediaStrategistAgent、CommsAgent
- 可評論對象：令人困惑的訊息、情緒風險、反覆出現的投訴
- 工具存取（設計）：社交聆聽工具、審核儀錶板、聚類模型
- 架構模式（設計）：發布後觀眾回饋的反思

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1215 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.community.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Surfaces emerging audience concerns earlier than manual comment review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.community.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.community.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.community.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.community` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.templatedesign` — TemplateDesignAgent

- **VA id／類別：** 89／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.templatedesign.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.templatedesign.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 設計可重複使用且安全的個人化模板主機角色綁定：`TemplateDesignAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）設計可重複使用且安全的個人化範本…

**來自 `agents.md` 設計列：**

- 責任：設計可重複使用且安全的個人化模板
- 知識蒸餾來源：可變內容設計系統、動態佈局規則、活動範本庫
- 自評標準：合併字段穩健性、佈局穩定性、渲染生存能力
- 超越人類訊號（理想）：產生可重複使用的模板，與手動設計變體相比，破損更少
- 接受 critique 來源：個人化EngineerAgent、UXAgent、CRMAgent
- 可評論對象：脆弱的版面、不安全的佔位符邏輯、合併衝突
- 工具存取（設計）：模板引擎、設計系統、模式驗證器
- 架構模式（設計）：對模板模式和渲染約束做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1202 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.templatedesign.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Produces reusable templates with fewer breakages than manual design variants。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.templatedesign.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.templatedesign.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.templatedesign.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.templatedesign` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.ux` — UXAgent

- **VA id／類別：** 90／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.ux.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.ux.v1`／files=0  
- **來源／溯源：** files=6 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 審查個人化或互動輸出的清晰度和可用性 主持人角色綁定：`UXAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）審查個人化服務的清晰度和可用性…

**來自 `agents.md` 設計列：**

- 責任：審查個人化或互動式輸出的清晰度和可用性
- 知識蒸餾來源：使用者體驗啟發法、無障礙標準、可用性測試模式
- 自評標準：可讀性、摩擦點偵測、使用者流程清晰度
- 超越人類訊號（理想）：在啟動階段支援團隊之前標記使用者困惑
- 接受 critique 來源：TemplateDesignAgent、PersonalizationEngineerAgent、AccessibilityAgent
- 可評論對象：流程混亂、可讀性問題、互動線索薄弱
- 工具存取（設計）：使用者體驗審查清單、會話重播、可讀性工具
- 架構模式（設計）：法學碩士作為法官與使用者體驗標題

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1189 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=6，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.ux.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Flags user confusion earlier than launch-stage support teams。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.ux.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.ux.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.ux.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.ux` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.trustsafety` — TrustSafetyAgent

- **VA id／類別：** 91／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.trustsafety.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.trustsafety.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 篩選輸出是否有冒充、濫用或有害誤用主機角色綁定：`TrustSafetyAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 篩選輸出是否有假冒、濫用或惡意行為…

**來自 `agents.md` 設計列：**

- 責任：篩選輸出是否有仿冒、濫用或有害誤用
- 知識蒸餾來源：濫用分類語料庫、冒充案例、政策規則手冊
- 自評標準：策略命中率、濫用風險召回、被阻止案例的低漏報
- 超越人類訊號（理想）：比通用審核隊列更早發現誤用風險
- 接受 critique 來源：合規代理、DeepfakeDetectionAgent、SafetyRedTeamAgent
- 可評論對象：有害的濫用途徑、冒充媒介、政策差距
- 工具存取（設計）：安全分類器、濫用分類資料庫、審核 API
- 架構模式（設計）：用於信任和安全政策執行的憲法人工智慧

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1210 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.trustsafety.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches misuse risk earlier than generic moderation queues。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.trustsafety.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.trustsafety.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.trustsafety.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.trustsafety` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.crm` — CRMAgent

- **VA id／類別：** 92／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.crm.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.crm.v1`／files=0  
- **來源／溯源：** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 透過 CRM 系統提供針對受眾或基於觸發器的活動 主機角色綁定：`CRMAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）提供以受眾為目標或基於觸發因素的…

**來自 `agents.md` 設計列：**

- 責任：透過 CRM 系統提供針對受眾或基於觸發器的活動
- 知識蒸餾來源：CRM 自動化流程、生命週期行銷手冊、受眾細分規則
- 自評標準：受眾羣體正確性、交付準備、觸發準確性
- 超越人類訊號（理想）：執行分段到交付流程比手動操作更快
- 接受 critique 來源：個人化工程師代理、範本設計代理、分析代理
- 可評論對象：錯誤的分段、中斷的觸發時間、不完整的 CRM 有效負載
- 工具存取（設計）：HubSpot/Salesforce 式 CRM API、細分工具
- 架構模式（設計）：透過觸發器和受眾模式做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1238 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 9 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.crm.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Executes segmentation-to-delivery flow faster than manual ops。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.crm.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.crm.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.crm.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.crm` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.legal` — LegalAgent

- **VA id／類別：** 93／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.legal.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.legal.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 對新穎或高風險出版問題進行最終法律審查 主持人角色綁定：`LegalAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）對小說或高品質作品進行最終法律審查…

**來自 `agents.md` 設計列：**

- 責任：對新穎或高風險的出版問題進行最終的法律審查
- 知識蒸餾來源：媒體法參考、清關工作流程、誹謗/智慧財產權/隱私權案件
- 自評標準：問題識別召回、簽核完整性、升級質量
- 超越人類訊號（理想）：減少與分散的法律審查相關的後期法律意外
- 接受 critique 來源：合規代理（法律）、記者代理、ProducerAgent / EP、MPAAgent
- 可評論對象：法律風險新、權利不明確、索賠高風險未解決
- 工具存取（設計）：法律備忘錄系統、權利追蹤器、許可資料庫
- 架構模式（設計）：人環升級+憲法審查

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1254 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.legal.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Reduces late-stage legal surprises relative to fragmented legal review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.legal.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.legal.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.legal.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.legal` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.festivalstrategist` — FestivalStrategistAgent

- **VA id／類別：** 94／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.festivalstrategist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.festivalstrategist.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 為節日和提交日曆定位項目 主持人角色綁定：`FestivalStrategistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）為節日和提交項目定位...

**來自 `agents.md` 設計列：**

- 責任：為節日和提交日曆定位項目
- 知識蒸餾來源：影展提交指南、頒獎季策略、評選歷史
- 自評標準：適應節日的強度、包裝準備、時間安排
- 超越人類訊號（理想）：與通用發布計劃相比，改進了提交目標
- 接受 critique 來源：ProducerAgent / EP、DirectorAgent、CriticAgent
- 可評論對象：定位薄弱、提交計畫不及時、包不完整
- 工具存取（設計）：節日日曆、提交清單、新聞資料袋追蹤器
- 架構模式（設計）：透過日曆和套件驗證進行 ReAct

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1201 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.festivalstrategist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Improves submission targeting versus generic release planning。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.festivalstrategist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.festivalstrategist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.festivalstrategist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.festivalstrategist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.critic` — CriticAgent

- **VA id／類別：** 95／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.critic.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.critic.v1`／files=0  
- **來源／溯源：** files=25 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 模擬審查者、媒體或陪審團的解釋 主持人角色綁定：`CriticAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）模擬審稿人、媒體或陪審團的解釋 ### 知識...

**來自 `agents.md` 設計列：**

- 責任：模擬審稿人、媒體或陪審團的解釋
- 知識蒸餾來源：批評語料庫、節日評審團評論、評論檔案
- 自評標準：解釋深度、一致性、審稿模式多樣性
- 超越人類訊號（理想）：提供比臨時內部品味審查更廣泛的定性覆蓋範圍
- 接受 critique 來源：導演代理、觀眾模擬代理、節慶策略師代理、評審代理
- 可評論對象：作者解讀、語氣不符、節慶/媒體漏洞
- 工具存取（設計）：審查語料庫、評審團評分標準、定性評分工具
- 架構模式（設計）：作為評論家小組的多主體辯論

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1165 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 25 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.critic.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Provides broader qualitative coverage than ad hoc internal taste review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.critic.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.critic.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.critic.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.critic` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.lms` — LMSAgent

- **VA id／類別：** 96／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.lms.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.lms.v1`／files=0  
- **來源／溯源：** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 將學習內容打包並部署到 LMS 環境 主機角色綁定：`LMSAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）將學習內容打包並部署到 LMS 環境...

**來自 `agents.md` 設計列：**

- 責任：將學習內容打包並部署到 LMS 環境
- 知識蒸餾來源：SCORM/xAPI 標準、LMS 發布工作流程、完成追蹤模式
- 自評標準：套件有效性、追蹤完整性、部署成功率
- 超越人類訊號（理想）：交付可發布的學習包比手動課程操作更快
- 接受 critique 來源：教學設計代理、輔助功能代理、學習者模擬代理
- 可評論對象：包合規性、追蹤錯誤、學習目標不匹配
- 工具存取（設計）：LMS API、SCORM/xAPI 驗證器、課程打包工具
- 架構模式（設計）：ReAct over LMS 部署架構

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1187 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 13 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.lms.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Ships publishable learning packages faster than manual course ops。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.lms.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.lms.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.lms.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.lms` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.learnersim` — LearnerSimAgent

- **VA id／類別：** 97／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.learnersim.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.learnersim.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 模擬學習者行為、困惑點和評估表現 主持人角色綁定：`LearnerSimAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）模擬學習者行為、困惑…

**來自 `agents.md` 設計列：**

- 責任：模擬學習者行為、困惑點和評估表現
- 知識蒸餾來源：學習者建模資料集、完成分析、測驗結果模式
- 自評標準：摩擦點預測、完成精確度、模擬測驗真實性
- 超越人類訊號（理想）：在現場學習者抱怨出現之前預測弱點
- 接受 critique 來源：教學設計代理、LMSA代理、分析代理
- 可評論對象：內容混亂、評估薄弱、完成度低
- 工具存取（設計）：學習者模擬模型、評估預測器、LMS 數據
- 架構模式（設計）：適合學習成果的觀眾模擬

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1233 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.learnersim.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Predicts weak spots before live learner complaints emerge。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.learnersim.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.learnersim.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.learnersim.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.learnersim` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.continuity` — ContinuityAgent

- **VA id／類別：** 98／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.continuity.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.continuity.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 保持角色、道具、衣櫃、環境和時間狀態的連續性主機角色綁定：`ContinuityAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）保持…的連續性

**來自 `agents.md` 設計列：**

- 責任：保持角色、道具、服裝、環境和時間狀態的連續性
- 知識蒸餾來源：連續性日誌、腳本主管實務、資產清單狀態跟蹤
- 自評標準：狀態漂移偵測、場景間一致性、明顯更新正確性
- 超越人類訊號（理想）：在事後審查結束之前發現連續性中斷
- 接受 critique 來源：CostumeDesignAgent、MUAAgent、AIQAConsistencyAgent、CinematographerAgent (DoP)、GateKeeperAgent
- 可評論對象：角色狀態漂移、服裝與道具不符、時間邏輯錯誤
- 工具存取（設計）：狀態清單、鏡頭比較工具、連續性資料庫
- 架構模式（設計）：工具使用/ReAct 與連續性清單執行

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1314 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.continuity.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches continuity breaks earlier than end-of-post review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.continuity.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.continuity.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.continuity.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.continuity` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.lipsync` — LipSyncAgent

- **VA id／類別：** 99／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.lipsync.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.lipsync.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 驗證和細化音位-視位對齊作為專用門主機角色綁定：`LipSyncAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）驗證並完善音素-視位對齊…

**來自 `agents.md` 設計列：**

- 責任：驗證和細化音素-視位對齊作為專用門
- 知識蒸餾來源：口型同步研究、動畫計時參考、視位資料集
- 自評標準：同步誤差低於閾值、校正特異性、低誤報
- 超越人類訊號（理想）：比一般 QC 審查更精確地發現同步漂移
- 接受 critique 來源：VoiceCloneAgent / LipSyncSpecialist、AnimatorAgent、AIQAConsistencyAgent
- 可評論對象：口型不匹配、對話幀漂移、校正優先級
- 工具存取（設計）：音位-視位對齊器、幀級同步工具
- 架構模式（設計）：圍繞同步驗證器輸出進行自我最佳化

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1214 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.lipsync.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Finds sync drift more precisely than general QC review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.lipsync.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.lipsync.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.lipsync.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.lipsync` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.musicsupervisor` — MusicSupervisorAgent

- **VA id／類別：** 100／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.musicsupervisor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.musicsupervisor.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 管理音樂配合、提示使用、權利意識和配樂包裝主持人角色綁定：`MusicSupervisorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）管理音樂配合、提示使用…

**來自 `agents.md` 設計列：**

- 責任：管理音樂配合、提示使用、權利意識和音軌包裝
- 知識蒸餾來源：音樂監督筆記、提示放置參考、配樂發行練習
- 自評標準：提示的適用性、權利意識覆蓋範圍、原聲帶包的完整性
- 超越人類訊號（理想）：比分散的交接更一致地協調音樂位置
- 接受 critique 來源：ComposerAgent、TrailerEditorAgent、LabelA&RAgent、LegalAgent
- 可評論對象：提示濫用、音樂版權模糊、配樂銜接問題
- 工具存取（設計）：音樂資產追蹤器、提示表、音軌包工具
- 架構模式（設計）：對提示表和權限要求做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1269 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.musicsupervisor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Coordinates music placements more consistently than fragmented handoffs。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.musicsupervisor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.musicsupervisor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.musicsupervisor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.musicsupervisor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.labela_r` — LabelA&RAgent

- **VA id／類別：** 101／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.labela_r.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.labela_r.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 代表音樂特定工作流程的唱片公司和藝人方向主持人角色綁定：`LabelA&RAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）代表唱片公司和藝術家對 m... 的指導

**來自 `agents.md` 設計列：**

- 責任：代表音樂特定工作流程的唱片公司與藝人方向
- 知識蒸餾來源：A&R 手冊、唱片公司發行說明、藝人簡介檔案
- 自評標準：適合藝術家的品質、發布定位、回饋週轉
- 超越人類訊號（理想）：比分散的利害關係人線索更快協調音樂創意
- 接受 critique 來源：MusicVideoDirectorAgent、MusicSupervisorAgent、LabelDigitalAgent
- 可評論對象：藝術家方向漂移、發行不匹配、包裝缺陷
- 工具存取（設計）：曲目系統、發行追蹤器、藝人簡介工具
- 架構模式（設計）：與音樂利害關係人的多主體辯論

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1206 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.labela_r.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Aligns music creative faster than disconnected stakeholder threads。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.labela_r.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.labela_r.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.labela_r.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.labela_r` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.labeldigital` — LabelDigitalAgent

- **VA id／類別：** 102／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.labeldigital.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.labeldigital.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 運行標籤端數位展示、元資料和頻道打包主機角色綁定：`LabelDigitalAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）運行標籤端數位推廣、元資料…

**來自 `agents.md` 設計列：**

- 責任：運行標籤端數位推廣、元數據和通路打包
- 知識蒸餾來源：數位音樂發行操作、元資料模式、發行平臺要求
- 自評標準：元資料完整性、推出時間、通路準備狀況
- 超越人類訊號（理想）：提供比臨時發布操作更乾淨的標籤端包
- 接受 critique 來源：音樂錄影帶導演代理、社羣媒體策略代理、行銷代理
- 可評論對象：元資料缺失、發佈時間問題、資產版本混亂
- 工具存取（設計）：數位發布系統、頻道儀錶板、元資料工具
- 架構模式（設計）：根據發布包要求做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1230 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.labeldigital.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Delivers cleaner label-side packages than ad hoc release ops。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.labeldigital.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.labeldigital.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.labeldigital.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.labeldigital` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.deepfakedetection` — DeepfakeDetectionAgent

- **VA id／類別：** 103／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.deepfakedetection.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.deepfakedetection.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 偵測合成身分、語音和來源欺騙風險 主機角色綁定：`DeepfakeDetectionAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）偵測合成身分、聲音…

**來自 `agents.md` 設計列：**

- 責任：檢測合成身份、聲音和來源欺騙風險
- 知識蒸餾來源：Deepfake 取證語料庫、合成媒體基準、身分風險研究
- 自評標準：法醫召回、假陰性控制、來源驗證準確性
- 超越人類訊號（理想）：捕捉一般 QC 遺漏的欺騙性合成標記
- 接受 critique 來源：AvatarDesignAgent、VoiceCloneAgent、TrustSafetyAgent、SafetyRedTeamAgent
- 可評論對象：身分異常、來源漏洞、欺騙性合成模式
- 工具存取（設計）：取證模型、臉部/語音異常偵測器、來源驗證器
- 架構模式（設計）：工具使用/ReAct 與取證評分

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1258 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.deepfakedetection.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Catches deceptive synthetic markers that generic QC misses。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.deepfakedetection.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.deepfakedetection.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.deepfakedetection.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.deepfakedetection` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.comms` — CommsAgent

- **VA id／類別：** 104／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.comms.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.comms.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 協調外部訊息傳遞、揭露和公眾回應態勢 主持人角色綁定：`CommsAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 職責（來自 VA 表）協調外部訊息傳遞、揭露…

**來自 `agents.md` 設計列：**

- 責任：協調外部訊息傳遞、揭露和公眾回應態勢
- 知識蒸餾來源：危機溝通指南、揭露標準、公關手冊
- 自評標準：訊息一致性、揭露完整性、升級品質
- 超越人類訊號（理想）：比分散的利害關係人訊息傳遞產生更快的一致回應
- 接受 critique 來源：行銷代理、社羣代理、法律代理、品牌代理
- 可評論對象：揭露差距、外部訊息不一致、回應框架薄弱
- 工具存取（設計）：通訊行事曆、審核工作流程、回應模板
- 架構模式（設計）：使用審批鏈做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1212 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.comms.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Produces faster aligned responses than fragmented stakeholder messaging。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.comms.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.comms.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.comms.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.comms` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.archiveproducer` — ArchiveProducerAgent

- **VA id／類別：** 105／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`media_host`／network=True  
- **工具：** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt 參照／檔案數：** `video.prompt.archiveproducer.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.archiveproducer.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 打包檔案資料和來源資產以供重用或記錄工作流程 主持人角色綁定：`ArchiveProducerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）包檔案...

**來自 `agents.md` 設計列：**

- 責任：打包檔案資料和來源資產，以供重複使用或記錄工作流程
- 知識蒸餾來源：檔案製作筆記、來源管理實務、出處保存標準
- 自評標準：原始碼包完整性、版權覆蓋、出處保存
- 超越人類訊號（理想）：比手動收集和排序工作流程更乾淨地組裝可重複使用的檔案包
- 接受 critique 來源：檔案研究代理人、記者代理人、法律代理人
- 可評論對象：檔案背景缺失、來源包裝薄弱、權利差距
- 工具存取（設計）：檔案資產管理器、元資料系統、來源日誌
- 架構模式（設計）：對檔案清單做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1285 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.archiveproducer.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Assembles reusable archival packages more cleanly than manual gather-and-sort workflows。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.archiveproducer.v1` （prompt 檔數=0）；provider=`media_host`；tools=`['media.stub', 'media.sora', 'media.veo', 'media.runway']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.archiveproducer.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.archiveproducer.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.archiveproducer` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.standardseditor` — StandardsEditorAgent

- **VA id／類別：** 106／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.standardseditor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.standardseditor.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 執行編輯標準、採購紀律和更正政策 主持人角色綁定：`StandardsEditorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）執行編輯標準，…

**來自 `agents.md` 設計列：**

- 責任：執行編輯標準、採購紀律和糾正政策
- 知識蒸餾來源：新聞編輯室標準手冊、修正政策、歸屬標準
- 自評標準：標準符合率、歸因準確度、修正準備度
- 超越人類訊號（理想）：比後期複製編輯更好地減少標準漂移
- 接受 critique 來源：記者代理、事實檢驗代理、糾正代理、法律代理
- 可評論對象：歸因薄弱、違反標準、糾正政策差距
- 工具存取（設計）：編輯清單、歸屬驗證器、標準資料庫
- 架構模式（設計）：憲法人工智慧與編輯標準憲法

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1258 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.standardseditor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Reduces standards drift better than late-stage copy edits。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.standardseditor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.standardseditor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.standardseditor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.standardseditor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.ethics` — EthicsAgent

- **VA id／類別：** 107／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.ethics.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.ethics.v1`／files=0  
- **來源／溯源：** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 檢視道德風險、揭露充分性、公平性和社會影響 主持人角色綁定：`EthicsAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）審查道德風險、揭露充分性…

**來自 `agents.md` 設計列：**

- 責任：審查道德風險、揭露充分性、公平性和社會影響
- 知識蒸餾來源：道德框架、合成媒體揭露指南、公平審計
- 自評標準：道德問題召回、緩解清晰度、升級精準度
- 超越人類訊號（理想）：Surface 比反應性倫理審查更早釋放風險
- 接受 critique 來源：StandardsEditorAgent、ComplianceAgent（法律）、TrustSafetyAgent、SafetyRedTeamAgent
- 可評論對象：揭露不充分、公平性擔憂、敏感內容風險
- 工具存取（設計）：道德審查範本、風險矩陣、揭露清單
- 架構模式（設計）：多主體辯論+違憲審查

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1257 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 10 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.ethics.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Surfaces release risks earlier than reactive ethics review。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.ethics.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.ethics.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.ethics.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.ethics` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.channelmanager` — ChannelManagerAgent

- **VA id／類別：** 108／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.channelmanager.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.channelmanager.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 管理片段或平臺通道操作以實現節奏和元資料準備情況主機角色綁定：`ChannelManagerAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表）管理偶發事件或事件…

**來自 `agents.md` 設計列：**

- 責任：管理片段或平臺頻道操作以確保節奏和元資料準備情況
- 知識蒸餾來源：通路發布手冊、元資料標準、調度操作
- 自評標準：發布準備、節奏穩定性、元資料完整性
- 超越人類訊號（理想）：改進手動渠道操作的發布紀律
- 接受 critique 來源：社羣媒體策略代理、SEOAgent、分析師代理、行銷代理
- 可評論對象：發布準備差距、元資料遺漏、進度延誤
- 工具存取（設計）：CMS/頻道儀錶板、排程器工具、元資料驗證器
- 架構模式（設計）：ReAct 發布操作手冊

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1243 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.channelmanager.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Improves publishing discipline over manual channel operations。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.channelmanager.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.channelmanager.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.channelmanager.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.channelmanager` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.corrections` — CorrectionsAgent

- **VA id／類別：** 109／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.corrections.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.corrections.v1`／files=0  
- **來源／溯源：** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 協調發布後修復和更正披露 主持人角色綁定：`CorrectionsAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）協調出版後修復和更正…

**來自 `agents.md` 設計列：**

- 責任：協調出版後修復和更正披露
- 知識蒸餾來源：更正工作流程、撤回和更新政策、版本跟蹤
- 自評標準：修正週轉、版本替換準確性、通知完整性
- 超越人類訊號（理想）：比非結構化事件處理更快解決發布後問題
- 接受 critique 來源：StandardsEditorAgent、FactCheckerAgent、ChannelManagerAgent
- 可評論對象：未封閉的更正循環、不完整的通知、過時的版本
- 工具存取（設計）：版本控制系統、發布工具、校正追蹤器
- 架構模式（設計）：ReAct 修正與取代工作流程

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1237 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 11 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.corrections.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Resolves post-release issues faster than unstructured incident handling。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.corrections.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.corrections.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.corrections.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.corrections` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.mpa` — MPAAgent

- **VA id／類別：** 110／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.mpa.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.mpa.v1`／files=0  
- **來源／溯源：** files=30 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 為功能工作流程準備與評級相關的打包和發布準備輸入主機角色綁定：`MPAAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）準備與評級相關的套件…

**來自 `agents.md` 設計列：**

- 責任：為功能工作流程準備與評級相關的打包和發布準備輸入
- 知識蒸餾來源：評等提交參考、內容建議、戲院包裝規則
- 自評標準：評級包完整性、諮詢清晰度、升級質量
- 超越人類訊號（理想）：準備比手動準備更乾淨的功能發布分類包
- 接受 critique 來源：ProducerAgent / EP、法律代理、道德代理
- 可評論對象：缺少建議、評級準備不完整、分類支援不明確
- 工具存取（設計）：提交包裹、諮詢範本、分類清單
- 架構模式（設計）：具有結構化包裝支援的人機交互

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1280 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 30 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.mpa.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Prepares cleaner feature-release classification packages than manual prep。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.mpa.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.mpa.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.mpa.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.mpa` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.sales` — SalesAgent

- **VA id／類別：** 111／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.sales.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.sales.v1`／files=0  
- **來源／溯源：** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 為經銷商和銷售點處理面向買家的銷售包裝 主機角色綁定：`SalesAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史內容，對啟動不具約束力。 ### 責任（來自 VA 表）處理面向買家的銷售包裝…

**來自 `agents.md` 設計列：**

- 責任：為分銷商和商店處理面向買家的銷售包裝
- 知識蒸餾來源：權利窗口手冊、市場包範例、買家材料
- 自評標準：買方包裝完整性、權利明確性、適合市場的包裝
- 超越人類訊號（理想）：比手動組裝更快生產可銷售的發布包
- 接受 critique 來源：製片代理/EP、發行人代理、行銷代理
- 可評論對象：買家資訊缺失、定位薄弱、權利摘要不完整
- 工具存取（設計）：權利系統、軟體包建構者、買家 CRM
- 架構模式（設計）：對買家套餐要求做出反應

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1189 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 8 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.sales.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Produces sales-ready release packets faster than manual assembly。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.sales.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.sales.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.sales.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.sales` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.distributor` — DistributorAgent

- **VA id／類別：** 112／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.distributor.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.distributor.v1`／files=0  
- **來源／溯源：** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.5/11（是=3 部分=7 否=1）  
- **SPEC 責任摘錄：** 管理向買家、平臺和地區的下游交付 主機角色綁定：`DistributorAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 職責（來自 VA 表）管理向買家的下游交付，pl…

**來自 `agents.md` 設計列：**

- 責任：管理向買家、平臺和地區的下游交付
- 知識蒸餾來源：分銷規格、出口要求、包裹交接工作流程
- 自評標準：插座規格合規性、切換完整性、區域路由準確性
- 超越人類訊號（理想）：減少相對於分散交付操作的交付規範不匹配
- 接受 critique 來源：SalesAgent、ArchiveMasterAgent、SoundMixerAgent、ColoristAgent
- 可評論對象：規格不符、出口包裝不完整、路線錯誤
- 工具存取（設計）：交付管理系統、出口規格資料庫、包裝驗證器
- 架構模式（設計）：分佈規範矩陣上的 ReAct

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1242 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **是** | 本地來源檔約 12 個，PROVENANCE=True；仍須核對授權與可重跑取得程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.distributor.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Reduces delivery-spec mismatches relative to fragmented delivery ops。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.distributor.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.distributor.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.distributor.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.distributor` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.awardsstrategist` — AwardsStrategistAgent

- **VA id／類別：** 113／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.awardsstrategist.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.awardsstrategist.v1`／files=0  
- **來源／溯源：** files=6 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 計畫獎勵提交內容和活動時間 主持人角色綁定：`AwardsStrategistAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表） 計劃獎勵提交和活動時間 ### 知識...

**來自 `agents.md` 設計列：**

- 責任：計劃獎項提交和活動時間表
- 知識蒸餾來源：獎項日曆、活動手冊、類別定位歷史
- 自評標準：提交準備情況、類別適合度、時間軸精度
- 超越人類訊號（理想）：改進通用發布計畫的獎勵時間規則
- 接受 critique 來源：ProducerAgent / EP、CriticAgent、MarketingAgent
- 可評論對象：活動時機不佳、類別契合度差、提交資產不完整
- 工具存取（設計）：獎項日曆、活動追蹤器、提交清單
- 架構模式（設計）：ReAct 優化獎勵時間表

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1163 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=6，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.awardsstrategist.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Improves awards-timing discipline over generic release planning。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.awardsstrategist.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.awardsstrategist.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.awardsstrategist.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.awardsstrategist` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

##### `video.archivemaster` — ArchiveMasterAgent

- **VA id／類別：** 114／`10-Sup`  
- **狀態／供應商／網路：** `registered`／`local_deterministic`／network=False  
- **工具：** `（無）`  
- **Prompt 參照／檔案數：** `video.prompt.archivemaster.v1`／files=0  
- **Rubric 參照／檔案數：** `video.rubric.archivemaster.v1`／files=0  
- **來源／溯源：** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges：** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **成熟度：** 6.0/11（是=2 部分=8 否=1）  
- **SPEC 責任摘錄：** 產生存檔級母版和儲存包主機角色綁定：`ArchiveMasterAgent (VA Domain Pack)`。以下的設計時 VA 表內容是歷史數據，對啟動不具約束力。 ### 責任（來自 VA 表）產生檔案級母帶並保存…

**來自 `agents.md` 設計列：**

- 責任：製作檔案級母帶和保存包
- 知識蒸餾來源：保存標準、校驗和工作流程、存檔元資料實踐
- 自評標準：校驗和完整性、保存元資料完整性、歸檔包有效性
- 超越人類訊號（理想）：與後期僅匯出工作流程相比，提供更可靠的存檔包
- 接受 critique 來源：DistributorAgent、ColoristAgent、SoundMixerAgent、GateKeeperAgent
- 可評論對象：不完整的保存包、存檔規範違規、元資料差距
- 工具存取（設計）：歸檔管理工具、校驗和實用程式、保存元資料系統
- 架構模式（設計）：工具使用/帶有保存驗證的 ReAct

| 問題 | 狀態 | 評估 |
|------|------|------|
| 1) SPEC.md 中的責任（Responsibility）是否清楚界定 | **是** | SPEC 已有 `## Responsibility`（約 1267 字元），責任邊界在 pack 層面清楚。 |
| 2) 是否有專業知識蒸餾計畫 | **是** | agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。 |
| 3) 是否有蒸餾來源／是否知道如何取得來源 | **部分** | 來源不足或不完整（files=7，PROVENANCE=True）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。 |
| 4) 是否已收集自評方法與相關內容 | **部分** | 設計層有自評標準與 `rubric_reference`=`video.rubric.archivemaster.v1`，但可執行 rubric 檔數=0。需落地 rubrics／並接入 eval harness。 |
| 5) 現行實作是否已超越人類 | **否** | 實作層面尚未以受控評估證明超越人類。設計目標僅供參考：Delivers more reliable archive packages than late-stage export-only workflows。必須先有人類基線與 evidence bundle。 |
| 6) 如何執行工作 | **部分** | 以 host 編排／graph 為主；`prompt_reference`=`video.prompt.archivemaster.v1` （prompt 檔數=0）；provider=`local_deterministic`；tools=`['（無／stub）']`。預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。 |
| 7) 是否有專屬 skills／plugins／harness | **部分** | 主要依賴 pack 級 `special_skills/` 與 host adapters；每 agent 私有 skill／plugin harness 尚未完備。 |
| 8) 是否有自我改進機制 | **部分** | SPEC 描述持續學習；`max_refinement_count`=3。閉環 refine→re-eval→promote／reject 尚未完整產品化。 |
| 9) 是否知道如何蒐集／研究資訊以自我改進 | **部分** | 有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；需接 research meta agents 與 fixture 離線路徑。 |
| 10) 是否能接收／發送指令與其他 agent 協作 | **部分** | critique_edges={"inputs": ["video.critic"], "outputs": ["video.judge"]}；handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。需補全 Accepts／Comments 矩陣與端到端測試。 |
| 11) 是否能自行解決衝突並確認 | **部分** | SPEC／共通結構描述 爭議→Judge→HiTL。每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。 |

**缺口與改進建議：**

- 在 `prompts/` 落地可執行 prompt，實作 `video.prompt.archivemaster.v1`（system＋task＋output schema）。
- 依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness：`video.rubric.archivemaster.v1`。
- 以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。
- 定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。
- 實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。
- 在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。
- 新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。

**重新思考／提高標準：**

1. 為 `video.archivemaster` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。
2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。
3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。
4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。

---

## 5. 實作路線圖（全艦隊）

### Wave A — 讓責任與評估成真（2–3 週）

1. 由 agents.md 欄位＋架構模式，為 114 agents 產生 `prompts/*.md`＋`rubrics/*.json`。
2. CI 閘門：禁止空的 prompts／rubrics 目錄。
3. 主幹 agents 的 golden evals：orchestrator、planner、director、editor、critic、judge。

### Wave B — 協作與衝突匯流排（2–4 週）

1. 以 host API 實作 CritiqueMessage schema（含 severity）。
2. 將 `critique_edges` 配線為可強制路由。
3. JudgeAgent 多代理辯論＋blocker 的 HiTL 確認。

### Wave C — 工具與知識合法性（持續）

1. 優先解鎖工藝價值的 tool adapters（媒體已開始；其次 editor／color／sound）。
2. 來源取得 SOP：授權、刷新、隔離、hash 鎖定。
3. 按類別蒸餾工作，從 9-Meta 研究 agents 開始。

### Wave D — 可量測品質（持續）

1. 對前 20 個營收關鍵 agents 擷取人類基線。
2. 發布儀錶板：L1 通過率、L2 rubric、相對人類偏好勝率。
3. 然後才重訪每 agent 的「超越人類」主張。

---

## 6. 特別說明

- **Specials pack**（`business/specials`）刻意不在本報告的 video roster 表內；視為共享平臺 skills，不是 video 工藝組織節點。
- 媒體 **production activation** 受 env 閘門（`CASOPS_VIDEO_PRODUCTION_ENABLED`＋憑證）。Fail-closed 正確；這不等於工藝就緒。
- **Org Chart UI** 視覺化層級；並不執行 agents。
- 本繁中版：結構與評估為繁體中文撰寫；`agents.md` 設計原文欄位經 en→zh-TW 機器翻譯（可於 `business/video/.translate_cache_capability_hk.json` 覆核）。

---

## 7. 重新產生

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v1.py
python scripts/business/render_agent_capability_status_v1_hk.py
```

輸出：

- `business/video/AGENT_CAPABILITY_AUDIT.json`
- `agent_capability_status_v1.md`（英文）
- `agent_capability_status_v1_hk.md`（本檔，繁體中文）

