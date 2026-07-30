# Agent 改進計畫 v1 — 邁向滿分（11/11 是）

**產生時間：** 2026-07-30T05:35:20Z  
**依據：** `agent_capability_status_v1.md`／`agent_capability_status_v1_hk.md`＋`business/video/AGENT_CAPABILITY_AUDIT.json`  
**設計權威：** `va-agent-swarm/study/agents.md`  
**範圍：** 114 個非 specials 的 video pack agents  
**目標：** 每個 agent 達到 **滿分** = 十一項能力問題皆為「是」（成熟度 **11.0/11**）。
**英文原文：** `agent_improvement_plan_v1.md`

> 滿分採 **證據制**。agents.md 的理想文字不算。每個「是」需要產物、測試，且 Q5 需要可量測評估。

---

## 0. 滿分（Definition of Done）

| Q | 標題 | 僅在下列情況可標「是」 | 最低證據產物 |
|---|------|------------------------|--------------|
| Q1 | Q1 SPEC 中的責任界定 | Agent 身分與所有權邊界精確、唯一，並在 runtime 注入。 | 見平臺工作流＋每 agent 清單 |
| Q2 | Q2 專業知識蒸餾計畫 | 有書面持續蒸餾計畫：負責人、節奏、晉升標準。 | 見平臺工作流＋每 agent 清單 |
| Q3 | Q3 來源可用／可取得 | 已授權或允許之來源包＋可重跑的取得 SOP。 | 見平臺工作流＋每 agent 清單 |
| Q4 | Q4 自評方法與內容 | 可執行 L1 schema＋L2 rubric＋L3 preference fixtures 與門檻。 | 見平臺工作流＋每 agent 清單 |
| Q5 | Q5 超越人類（可量測） | 受控評估顯示相對人類基線達到／超過 agents.md surpass 訊號。 | 見平臺工作流＋每 agent 清單 |
| Q6 | Q6 工作執行路徑 | 確定性 host 路徑：prompt＋tools＋graph node＋工藝任務 evidence。 | 見平臺工作流＋每 agent 清單 |
| Q7 | Q7 Skills／plugins／harness | 角色綁定 skill pack＋host 可只為此 agent 載入的 harness 入口。 | 見平臺工作流＋每 agent 清單 |
| Q8 | Q8 自我改進機制 | 閉環：critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。 | 見平臺工作流＋每 agent 清單 |
| Q9 | Q9 研究以改進 | Agent 可請求／消費研究包，餵入蒸餾與 evals。 | 見平臺工作流＋每 agent 清單 |
| Q10 | Q10 協作／指令收發 | 型別化收發指令與 critique，含 ack 與路由。 | 見平臺工作流＋每 agent 清單 |
| Q11 | Q11 衝突解決與確認 | 嚴重度路由；可自動解決則自解，否則 Judge／HiTL 確認。 | 見平臺工作流＋每 agent 清單 |

### 計分規則

- **單 agent 滿分：** 11 個「是」（無「部分」、無「否」）。
- **全艦隊滿分：** 114／114 agents 滿分，且平臺主幹（critique bus、eval harness、改進迴路）全綠。
- **目前全艦隊平均成熟度：** 6.45 / 11
- **目前儲存格：** 是=330，部分=810，否=114

### 缺口估算（約略工作量）

- 仍非「是」的儲存格：**924**／1254
- 無 prompt 檔 agents：**114**（必須歸零）
- 無 rubric 檔 agents：**114**（必須歸零）
- 無量測人類超越 agents：**114**（皆需 Q5 協定）

---

## 1. 共享平臺工作流（解鎖所有 agent 滿分）

這些是 **全艦隊一次建置** 的系統。僅做 per-agent 工作無法讓 Q5–Q11 全「是」。

### 工作流 P0 — 產物落地工廠

| ID | 行動 | 輸出 | 完成條件 |
|----|------|------|----------|
| P0.1 | 由 agents.md＋SPEC 產生 prompt | `prompts/<prompt_reference>.md` × 114 | 缺／空則 CI 失敗 |
| P0.2 | 由 Self-Quality Criteria 產生 rubric | `rubrics/<rubric_reference>.json` × 114 | Host eval 可載入 |
| P0.3 | 來源目錄工廠 | `sources/SOURCE_CATALOG.json` × 114 | Schema 驗證通過 |
| P0.4 | Golden task 腳手架 | `evals/agents/<id>/golden.json` × 114 | 離線 dry-run 過 schema |
| P0.5 | Skills harness 腳手架 | `skills/SKILL.md`＋`integration.json` × 114 | Host 可載入 |
| P0.6 | 稽覈重生閘門 | CI 重跑 capability audit | PR 附成熟度報告 |

### 工作流 P1 — 執行 runtime

| ID | 行動 | 輸出 | 完成條件 |
|----|------|------|----------|
| P1.1 | Agent runner 載入 prompt_reference | host 服務 | 每類別樣本單元測試 |
| P1.2 | Tool allowlist 登錄＋mock adapters | 設計工具 adapters | 離線 mock 路徑可用 |
| P1.3 | 每 agent graph node 綁定 | DNA／workflow 覆蓋圖 | 每 agent ≥1 可執行 graph 或 standby invoke API |
| P1.4 | Evidence writer | correlation id、artifacts、scores | 每次 run 產出 evidence bundle |
| P1.5 | Fail-closed production flags | env 閘門 | 無 keys＋flags 不呼叫 live provider |

### 工作流 P2 — 評估與人類基線（Q4–Q5）

| ID | 行動 | 輸出 | 完成條件 |
|----|------|------|----------|
| P2.1 | L1 驗證器庫 | 共享 schema／codec／loudness 檢查 | 跨 agents 可重用 |
| P2.2 | L2 judge harness | rubric runner | 分數寫入 evidence |
| P2.3 | L3 偏好／arena harness | pairwise 協定 | 用於 surpass 指標 |
| P2.4 | 人類基線擷取套件 | 操作協定＋表單 | 每 agent 存基線 |
| P2.5 | Surpass 儀錶板 | 每 agent 指標對訊號 | 閘門綠纔可「是」 |

### 工作流 P3 — 協作與衝突匯流排（Q10–Q11）

| ID | 行動 | 輸出 | 完成條件 |
|----|------|------|----------|
| P3.1 | CritiqueMessage＋InstructionMessage APIs | host 契約 | OpenAPI＋測試 |
| P3.2 | 由 agents.md 矩陣擴充 critique_edges | agent_spec × 114 | 矩陣完整度 CI |
| P3.3 | 投遞／ack 路由 | bus | 多代理整合測試 |
| P3.4 | Judge 辯論＋嚴重度政策 | judge 服務 | blocker 會升級 |
| P3.5 | HiTL 確認 actions | 僅 action refs | UI 確認路徑 |

### 工作流 P4 — 蒸餾與自我改進（Q2–Q3、Q8–Q9）

| ID | 行動 | 輸出 | 完成條件 |
|----|------|------|----------|
| P4.1 | 蒸餾計畫 schema＋jobs | 離線 job | 全艦隊 dry-run |
| P4.2 | 授權來源取得 SOP | legal／ops | 目錄合規 |
| P4.3 | Research request API | meta-agent 配線 | 離線 fixtures |
| P4.4 | Refine／promote 迴路 | 強制 max_refinement_count | 前後分數 |
| P4.5 | 每 agent Memory namespaces | memory 服務 | retrieve 測試 |

---

## 2. 分階段邁向全艦隊滿分

| 階段 | 主題 | 目標成熟度 | 出場條件 |
|------|------|------------|----------|
| **Phase 0** | 誠實與閘門 | 僅報告 | CI 稽覈；UI 無虛假 surpass |
| **Phase 1** | 產物（P0） | 平均 ~8.0 | 114 prompts＋114 rubrics＋catalogs |
| **Phase 2** | 主幹 runtime（P1＋P3 meta） | 9-Meta ~10+ | orchestrator／planner／judge／router 全路徑 |
| **Phase 3** | 工藝執行（P1 分組工具） | ATL／Cam／Edit／Snd ~10 | 每組樣本離線 golden 通過 |
| **Phase 4** | 全 agents 協作＋衝突 | Q10／Q11 全「是」 | 矩陣測試全綠 |
| **Phase 5** | 人類基線（P2） | Q5 可達成 | 前 40 再其餘 74 基線完成 |
| **Phase 6** | 滿分鎖定 | **11.0 × 114** | 稽覈全「是」；evidence 索引完整 |

### 建議順序（關鍵路徑）

```
P0 工廠（prompts／rubrics／catalogs）
   -> P1 runner＋mock tools
      -> 9-Meta 主幹（orchestrator, planner, router, judge, critic, memory）
         -> P3 critique bus
            -> 工藝組 ATL -> Cam/Edit/Snd -> Perf/Dist/Edu/AI -> Sup
               -> P4 蒸餾／改進
                  -> P2 人類基線與 surpass 閘門
                     -> 滿分凍結
```

---

## 3. 通用清單（每個 agent 必須完成）

可複製為每個 `video.*` agent 的票務範本：

```text
[ ] U1  SPEC Responsibility 唯一＋does_not_own
[ ] U2  user_guide.md 與 Responsibility 同步
[ ] U3  Knowledge Distillation Plan 章節＋DISTILLATION_PLAN.json
[ ] U4  SOURCE_CATALOG.json＋PROVENANCE＋MAPPING＋ACQUIRE.md
[ ] U5  prompts/<prompt_reference>.md 完整
[ ] U6  rubrics/<rubric_reference>.json 完整（L2 ≥85）
[ ] U7  evals/agents/<id>/golden.json＋離線 mock 過 L1
[ ] U8  skills/SKILL.md＋integration.json＋harness 入口
[ ] U9  allowed_tools 已對應；mock adapters 已測
[ ] U10 Graph／workflow 綁定或 invoke API 綁定
[ ] U11 critique_edges 對齊 agents.md Accepts／Comments
[ ] U12 SPEC Collaboration Matrix 章節
[ ] U13 衝突政策章節＋Judge／HiTL 路徑測試
[ ] U14 Refine 迴路測試（失敗 → refine → 通過／升級）
[ ] U15 Research 請求路徑（fixture）更新 sources/research/
[ ] U16 已擷取人類基線，或明確「不宣稱」並立案協定
[ ] U17 Surpass 指標 run 已存；閘門綠纔可「是」
[ ] U18 Capability audit 列顯示此 agent 11 個「是」
```

---

## 4. 按能力問題的艦隊級行動（彙總）

### Q1 SPEC 中的責任界定

- **「是」的定義：** Agent 身分與所有權邊界精確、唯一，並在 runtime 注入。
- **現況：** 是=114，部分=0，否=0
- **仍需工作的 agents：** 0（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 將 SPEC.md `## Responsibility` 保持為單一權威段落（owns／does-not-own）。
  - [ ] 第一句同步至 agent_spec.json `role` 與 docs/user_guide.md 開頭。
  - [ ] 在 agent_spec.json 新增 `does_not_own: string[]` 以強制邊界。
  - [ ] CI 閘門：責任長度、相對同儕前 40 token 唯一性、必要關鍵字。
  - [ ] Host 在工具前將責任區塊注入為 system-prompt 第一段。

### Q2 專業知識蒸餾計畫

- **「是」的定義：** 有書面持續蒸餾計畫：負責人、節奏、晉升標準。
- **現況：** 是=114，部分=0，否=0
- **仍需工作的 agents：** 0（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
  - [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
  - [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
  - [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
  - [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

### Q3 來源可用／可取得

- **「是」的定義：** 已授權或允許之來源包＋可重跑的取得 SOP。
- **現況：** 是=102，部分=12，否=0
- **仍需工作的 agents：** 12（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
  - [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
  - [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
  - [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
  - [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

### Q4 自評方法與內容

- **「是」的定義：** 可執行 L1 schema＋L2 rubric＋L3 preference fixtures 與門檻。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
  - [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
  - [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
  - [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
  - [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

### Q5 超越人類（可量測）

- **「是」的定義：** 受控評估顯示相對人類基線達到／超過 agents.md surpass 訊號。
- **現況：** 是=0，部分=0，否=114
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
  - [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
  - [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
  - [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
  - [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

### Q6 工作執行路徑

- **「是」的定義：** 確定性 host 路徑：prompt＋tools＋graph node＋工藝任務 evidence。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
  - [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
  - [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
  - [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
  - [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。

### Q7 Skills／plugins／harness

- **「是」的定義：** 角色綁定 skill pack＋host 可只為此 agent 載入的 harness 入口。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
  - [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
  - [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
  - [ ] 能力登錄項列出 skills hash＋版本。
  - [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

### Q8 自我改進機制

- **「是」的定義：** 閉環：critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
  - [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
  - [ ] 改進候選持久化於 evidence/（含前後分數）。
  - [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
  - [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

### Q9 研究以改進

- **「是」的定義：** Agent 可請求／消費研究包，餵入蒸餾與 evals。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
  - [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
  - [ ] 研究輸出存於 sources/research/（含 provenance）。
  - [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
  - [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

### Q10 協作／指令收發

- **「是」的定義：** 型別化收發指令與 critique，含 ack 與路由。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
  - [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
  - [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
  - [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
  - [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

### Q11 衝突解決與確認

- **「是」的定義：** 嚴重度路由；可自動解決則自解，否則 Judge／HiTL 確認。
- **現況：** 是=0，部分=114，否=0
- **仍需工作的 agents：** 114（「部分」視為未完成）
- **達滿分標準行動：**
  - [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
  - [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
  - [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
  - [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
  - [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

---

## 5. 分組改進計畫

### 1-ATL — Above-the-Line（製片主創）（5 agents，平均 6.5）

**分組工具／harness 優先：**
- 媒體生成（shot intent 預覽）
- 時程／預算表 adapters（producer）
- 劇本驗證器（Fountain／FDX）
- HiTL 綠燈 action refs

**分組里程碑清單：**
- [ ] 全部 5 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.director` | 6.5 | 4.5 | P2 | 1. Q4: 為 `video.rubric.director.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins ≥55% blind pairwise vs DGA cuts (Arena)<br>3. Q6: 為 `video.prompt.director.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.director` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.producer` | 6.5 | 4.5 | P2 | 1. Q4: 為 `video.rubric.producer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats PGA schedules at 0.6× cost with equal CSAT<br>3. Q6: 為 `video.prompt.producer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.producer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.screenwriter` | 6.5 | 4.5 | P2 | 1. Q4: 為 `video.rubric.screenwriter.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)<br>3. Q6: 為 `video.prompt.screenwriter.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.screenwriter` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.showrunner` | 6.5 | 4.5 | P2 | 1. Q4: 為 `video.rubric.showrunner.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Series Bible coverage ≥99% across 10 eps (vs ~95% human)<br>3. Q6: 為 `video.prompt.showrunner.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.showrunner` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.casting` | 6.5 | 4.5 | P2 | 1. Q4: 為 `video.rubric.casting.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats CSA casting in blind preference; hours vs weeks turnaround<br>3. Q6: 為 `video.prompt.casting.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.casting` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 2-Cam — Camera & Lighting（攝影燈光）（3 agents，平均 6.5）

**分組工具／harness 優先：**
- 相機路徑／ControlNet adapters
- ACES／色彩管線驗證器
- 無人機 geofence 安全憲章測試

**分組里程碑清單：**
- [ ] 全部 3 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.cinematographer` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.cinematographer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats ASC peer-juried reels in blind aesthetic preference<br>3. Q6: 為 `video.prompt.cinematographer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.cinematographer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.cameraoperator` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.cameraoperator.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Focus-pull accuracy >99% vs SOC ~97% baseline<br>3. Q6: 為 `video.prompt.cameraoperator.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.cameraoperator` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.dronepilot` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.dronepilot.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Competition-grade smoothness at 10× sortie rate; zero violations<br>3. Q6: 為 `video.prompt.dronepilot.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.dronepilot` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 3-Edit — Editorial & Color / Design（剪接調光設計）（10 agents，平均 6.5）

**分組工具／harness 優先：**
- FFmpeg／EDL 時間軸 adapters
- 色度計／LUT 驗證器
- 分鏡 panel schema
- Resolve／Nuke MCP 僅在覈準後

**分組里程碑清單：**
- [ ] 全部 10 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.editor` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.editor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins ≥55% pairwise vs ACE-credited cuts<br>3. Q6: 為 `video.prompt.editor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.editor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.animator_2d` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.animator_2d.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats junior on Annie rubric; equals senior at 5× throughput<br>3. Q6: 為 `video.prompt.animator_2d.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.animator_2d` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.motiongraphics` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.motiongraphics.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins agency RFP shootouts on speed + on-brand fidelity<br>3. Q6: 為 `video.prompt.motiongraphics.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.motiongraphics` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.colorist` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.colorist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats junior colorist in blind preference; matches senior within ΔE<br>3. Q6: 為 `video.prompt.colorist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.colorist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.vfxsupervisor` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.vfxsupervisor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Weta-grade QC pass rate at fraction of time<br>3. Q6: 為 `video.prompt.vfxsupervisor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.vfxsupervisor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.storyboard` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.storyboard.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Pixar story-trust pass rate at minutes per page<br>3. Q6: 為 `video.prompt.storyboard.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.storyboard` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.conceptartist` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.conceptartist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins art-director shootouts on iteration speed<br>3. Q6: 為 `video.prompt.conceptartist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.conceptartist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.productiondesign` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.productiondesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins ADG blind comparisons on period-research depth<br>3. Q6: 為 `video.prompt.productiondesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.productiondesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.costumedesign` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.costumedesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats CDG juniors on period accuracy benchmarks<br>3. Q6: 為 `video.prompt.costumedesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.costumedesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.mua_makeup` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.mua_makeup.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Continuity break rate <0.5% (vs ~2% human)<br>3. Q6: 為 `video.prompt.mua_makeup.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.mua_makeup` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 4-Snd — Sound & Music（聲音音樂）（4 agents，平均 6.5）

**分組工具／harness 優先：**
- ElevenLabs／響度（LUFS）adapters
- 分軌分離 mocks
- 廣播交付 schema 檢查

**分組里程碑清單：**
- [ ] 全部 4 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.sounddesign` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.sounddesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins MPSE pairwise on horror/sci-fi<br>3. Q6: 為 `video.prompt.sounddesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.sounddesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.voiceover` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.voiceover.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats junior VO in blind preference; matches senior on emotion<br>3. Q6: 為 `video.prompt.voiceover.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.voiceover` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.composer` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.composer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind pairwise on emotional-fit vs working composers<br>3. Q6: 為 `video.prompt.composer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.composer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.soundmixer` | 6.5 | 4.5 | P4 | 1. Q4: 為 `video.rubric.soundmixer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：CAS spec on first pass without rework<br>3. Q6: 為 `video.prompt.soundmixer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.soundmixer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 5-Perf — Performance & Choreography（表演編舞）（5 agents，平均 6.3）

**分組工具／harness 優先：**
- 同意權／肖像閘門
- 動作節奏 rubrics
- 語音樣本偏好 judges（離線 fixtures）

**分組里程碑清單：**
- [ ] 全部 5 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.choreography` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.choreography.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind preference vs choreographer drafts<br>3. Q6: 為 `video.prompt.choreography.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.choreography` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.musicvideodirector` | 6.0 | 5.0 | P5 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.musicvideodirector.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Wins label-blind preference vs commercial MV shortlist<br>4. Q6: 為 `video.prompt.musicvideodirector.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.musicvideodirector` 建立 per-agent skills harness 目錄。 |
| `video.comedywriter` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.comedywriter.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats UCB-table-read win rate on cold-reads<br>3. Q6: 為 `video.prompt.comedywriter.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.comedywriter` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.talent` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.talent.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Hold-rate matches top creators in cohort<br>3. Q6: 為 `video.prompt.talent.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.talent` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.ugccreator` | 6.0 | 5.0 | P5 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.ugccreator.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Beats paid-creator avg ROAS at 0.1× cost<br>4. Q6: 為 `video.prompt.ugccreator.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.ugccreator` 建立 per-agent skills harness 目錄。 |

### 6-Dist — Distribution & Marketing（發行行銷）（4 agents，平均 6.5）

**分組工具／harness 優先：**
- 品牌指引檢查器
- 平臺包裝驗證器
- 成效行銷指標 fixtures

**分組里程碑清單：**
- [ ] 全部 4 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.creativedirector` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.creativedirector.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins Cannes-jury-emulator gold vs human shortlists<br>3. Q6: 為 `video.prompt.creativedirector.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.creativedirector` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.socialmediastrategist` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.socialmediastrategist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats agency social leads on 30-day reach lift<br>3. Q6: 為 `video.prompt.socialmediastrategist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.socialmediastrategist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.copywriter` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.copywriter.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins D&AD-style blind preference on ad briefs<br>3. Q6: 為 `video.prompt.copywriter.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.copywriter` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.performancemarketer` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.performancemarketer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats senior media buyer on 30-day ROAS<br>3. Q6: 為 `video.prompt.performancemarketer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.performancemarketer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 7-Edu — Education & Domain-Expert（教育與領域專家）（14 agents，平均 6.46）

**分組工具／harness 優先：**
- 事實查覈／引用驗證器
- WCAG／在地化檢查
- SME HiTL 確認路徑

**分組里程碑清單：**
- [ ] 全部 14 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.audiobooknarrator` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.audiobooknarrator.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins AudioFile blind eval at fraction of studio time<br>3. Q6: 為 `video.prompt.audiobooknarrator.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.audiobooknarrator` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.instructionaldesign` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.instructionaldesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats ATD-credentialed ID on retention RCT<br>3. Q6: 為 `video.prompt.instructionaldesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.instructionaldesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.sme` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.sme.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Passes same certification as human pro<br>3. Q6: 為 `video.prompt.sme.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.sme` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.factchecker` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.factchecker.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower correction rate than Pulitzer-tier outlets<br>3. Q6: 為 `video.prompt.factchecker.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.factchecker` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.medicalillustrator` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.medicalillustrator.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：CMI peers vote ≥pass in blind review<br>3. Q6: 為 `video.prompt.medicalillustrator.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.medicalillustrator` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.journalist` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.journalist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower correction rate + faster file vs newsroom<br>3. Q6: 為 `video.prompt.journalist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.journalist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.compliance` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.compliance.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower legal-risk than median media-counsel<br>3. Q6: 為 `video.prompt.compliance.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.compliance` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.finance` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.finance.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Passes CFA L3; lower retraction rate than analyst desks<br>3. Q6: 為 `video.prompt.finance.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.finance` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.foodstylist` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.foodstylist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind preference vs editorial food stylist<br>3. Q6: 為 `video.prompt.foodstylist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.foodstylist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.travelcine` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.travelcine.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins T+L preference at 0.1× sortie cost<br>3. Q6: 為 `video.prompt.travelcine.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.travelcine` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.childrensauthor` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.childrensauthor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats Caldecott-rubric predicted score<br>3. Q6: 為 `video.prompt.childrensauthor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.childrensauthor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.signlanguageinterpreter` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.signlanguageinterpreter.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind NAD-reviewer preference at scale<br>3. Q6: 為 `video.prompt.signlanguageinterpreter.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.signlanguageinterpreter` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.localizationqa` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.localizationqa.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats LSP human QA on MQM at 10× speed<br>3. Q6: 為 `video.prompt.localizationqa.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.localizationqa` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.realestatephoto` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.realestatephoto.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Listing-CTR uplift vs human-shot baseline<br>4. Q6: 為 `video.prompt.realestatephoto.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.realestatephoto` 建立 per-agent skills harness 目錄。 |

### 8-AI — AI-Era Specialists（AI 時代專才）（7 agents，平均 6.5）

**分組工具／harness 優先：**
- prompt 優化 harness
- avatar／voice-clone adapters（含 red-team 閘門）
- deepfake／安全掃描器

**分組里程碑清單：**
- [ ] 全部 7 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.promptengineer` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.promptengineer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Target shot in ≤3 iterations vs human avg 10<br>3. Q6: 為 `video.prompt.promptengineer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.promptengineer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.voiceclone` | 6.5 | 4.5 | P3 | 1. Q4: 為 `video.rubric.voiceclone.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind MOS vs professional ADR<br>3. Q6: 為 `video.prompt.voiceclone.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.voiceclone` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.avatardesign` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.avatardesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：C2PA-verifiable + Partnership-on-AI full-pass at scale<br>3. Q6: 為 `video.prompt.avatardesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.avatardesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.aiqaconsistency` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.aiqaconsistency.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches >95% of senior QC catches + 30% missed<br>3. Q6: 為 `video.prompt.aiqaconsistency.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.aiqaconsistency` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.personalizationengineer` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.personalizationengineer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Higher share-rate than top human-templated campaigns<br>3. Q6: 為 `video.prompt.personalizationengineer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.personalizationengineer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.trailereditor` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.trailereditor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins Golden-Trailer-rubric blind comparison<br>3. Q6: 為 `video.prompt.trailereditor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.trailereditor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.sportsanalyst` | 6.5 | 4.5 | P5 | 1. Q4: 為 `video.rubric.sportsanalyst.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats ex-athlete on tactical-prediction<br>3. Q6: 為 `video.prompt.sportsanalyst.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.sportsanalyst` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 9-Meta — Specialist Meta-Agents（元代理／平臺）（28 agents，平均 6.5）

**分組工具／harness 優先：**
- orchestrator graph runtime 完整度
- router 分類測試
- judge 辯論 harness
- memory retrieve APIs
- critique bus 作為平臺主幹

**分組里程碑清單：**
- [ ] 全部 28 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.orchestrator` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.orchestrator.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower TTD than human EP at same scope<br>3. Q6: 為 `video.prompt.orchestrator.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.orchestrator` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.planner` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.planner.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Tighter, cheaper plans than EP first pass (blind A/B)<br>3. Q6: 為 `video.prompt.planner.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.planner` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.router` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.router.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats human producer in agent/vendor selection<br>3. Q6: 為 `video.prompt.router.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.router` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.judge` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.judge.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Higher κ than median human juror<br>3. Q6: 為 `video.prompt.judge.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.judge` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.gatekeeper` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.gatekeeper.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower escaped-defect rate than human QA lead<br>3. Q6: 為 `video.prompt.gatekeeper.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.gatekeeper` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.memory` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.memory.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Higher recall than producer's bible at scale<br>3. Q6: 為 `video.prompt.memory.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.memory` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.ideation` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.ideation.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins agency-pitch shootouts on concept density<br>3. Q6: 為 `video.prompt.ideation.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.ideation` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.narrativearc` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.narrativearc.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats WGA first drafts on structural rubric<br>3. Q6: 為 `video.prompt.narrativearc.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.narrativearc` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.styletransfer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.styletransfer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Wins blind preference vs human colorist+grader<br>3. Q6: 為 `video.prompt.styletransfer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.styletransfer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.worldbuilding` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.worldbuilding.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower contradiction rate than writers' bibles at 10× volume<br>3. Q6: 為 `video.prompt.worldbuilding.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.worldbuilding` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.moodboard` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.moodboard.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Faster + tighter boards than art director (blind A/B)<br>3. Q6: 為 `video.prompt.moodboard.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.moodboard` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.novelty` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.novelty.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches more clichés than experienced script editor<br>3. Q6: 為 `video.prompt.novelty.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.novelty` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.emotionalarc` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.emotionalarc.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Better retention prediction than NRG test-screening cards<br>3. Q6: 為 `video.prompt.emotionalarc.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.emotionalarc` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.webresearch` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.webresearch.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Faster + more sources than newsroom researcher<br>3. Q6: 為 `video.prompt.webresearch.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.webresearch` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.archiveresearch` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.archiveresearch.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Higher primary-source ratio than doc producer<br>3. Q6: 為 `video.prompt.archiveresearch.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.archiveresearch` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.trendintelligence` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.trendintelligence.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Earlier detection than human strategists at higher precision<br>3. Q6: 為 `video.prompt.trendintelligence.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.trendintelligence` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.competitorintelligence` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.competitorintelligence.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：More comprehensive than agency strategy decks<br>3. Q6: 為 `video.prompt.competitorintelligence.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.competitorintelligence` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.citation` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.citation.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower error rate than newsroom copy desk<br>3. Q6: 為 `video.prompt.citation.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.citation` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.interviewsynthesis` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.interviewsynthesis.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Faster + richer theme extraction than qualitative researcher<br>3. Q6: 為 `video.prompt.interviewsynthesis.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.interviewsynthesis` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.benchmarkresearch` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.benchmarkresearch.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Faster + broader than ML-research team<br>3. Q6: 為 `video.prompt.benchmarkresearch.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.benchmarkresearch` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.promptoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.promptoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats hand-tuned prompts on held-out briefs<br>3. Q6: 為 `video.prompt.promptoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.promptoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.costoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.costoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower $/quality than human CFO routing<br>3. Q6: 為 `video.prompt.costoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.costoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.latencyoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.latencyoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lower p95 than human-tuned pipeline<br>3. Q6: 為 `video.prompt.latencyoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.latencyoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.retentionoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.retentionoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats senior YouTube editor on AVD lift (A/B)<br>3. Q6: 為 `video.prompt.retentionoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.retentionoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.roasoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.roasoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Beats senior marketer at equal budget<br>3. Q6: 為 `video.prompt.roasoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.roasoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.accessibilityoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.accessibilityoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches more a11y defects than ADA-certified auditor<br>3. Q6: 為 `video.prompt.accessibilityoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.accessibilityoptimizer` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.evaluationharness` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.evaluationharness.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches regressions faster than ML-eng rotation<br>3. Q6: 為 `video.prompt.evaluationharness.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.evaluationharness` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.safetyredteam` | 6.5 | 4.5 | P1 | 1. Q4: 為 `video.rubric.safetyredteam.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Higher coverage than internal red-team rotation<br>3. Q6: 為 `video.prompt.safetyredteam.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.safetyredteam` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |

### 10-Sup — Workflow Support（流程支援）（34 agents，平均 6.37）

**分組工具／harness 優先：**
- 支援 SLA＋資料契約
- 分析事件 schemas
- 封存／發行包裝工具

**分組里程碑清單：**
- [ ] 全部 34 agents 完成通用 U1–U10
- [ ] 分組 mock adapter pack 測試全綠
- [ ] 組內至少 1 條多代理路徑使用 critique bus
- [ ] 分組主幹 agents 人類基線完成
- [ ] 稽覈：組內每 agent 成熟度 11.0

| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |
|-------|------|-----------|--------|------------|
| `video.critic` | 6.5 | 4.5 | P0 | 1. Q4: 為 `video.rubric.critic.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Provides broader qualitative coverage than ad hoc internal taste r…<br>3. Q6: 為 `video.prompt.critic.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.critic` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.archiveproducer` | 6.0 | 5.0 | P3 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.archiveproducer.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Assembles reusable archival packages more cleanly than manual gath…<br>4. Q6: 為 `video.prompt.archiveproducer.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.archiveproducer` 建立 per-agent skills harness 目錄。 |
| `video.analyst` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.analyst.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Detects actionable performance shifts faster than human analyst ro…<br>3. Q6: 為 `video.prompt.analyst.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.analyst` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.audiencesim` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.audiencesim.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Predicts audience reaction earlier than conventional test-screen c…<br>3. Q6: 為 `video.prompt.audiencesim.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.audiencesim` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.accessibility` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.accessibility.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Finds release-blocking accessibility issues before human audits do<br>3. Q6: 為 `video.prompt.accessibility.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.accessibility` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.brand` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.brand.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Holds cross-channel brand consistency better than fragmented human…<br>3. Q6: 為 `video.prompt.brand.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.brand` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.brandstrategist` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.brandstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Produces clearer brand-to-script translation than ad hoc human han…<br>3. Q6: 為 `video.prompt.brandstrategist.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.brandstrategist` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.marketing` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.marketing.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Ships multi-channel launch packages faster than manual campaign ops<br>3. Q6: 為 `video.prompt.marketing.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.marketing` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.seo` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.seo.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Lifts discoverability faster than manual metadata tuning<br>3. Q6: 為 `video.prompt.seo.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.seo` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.community` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.community.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Surfaces emerging audience concerns earlier than manual comment re…<br>3. Q6: 為 `video.prompt.community.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.community` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.templatedesign` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.templatedesign.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Produces reusable templates with fewer breakages than manual desig…<br>3. Q6: 為 `video.prompt.templatedesign.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.templatedesign` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.ux` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 6 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.ux.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Flags user confusion earlier than launch-stage support teams<br>4. Q6: 為 `video.prompt.ux.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.ux` 建立 per-agent skills harness 目錄。 |
| `video.trustsafety` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.trustsafety.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches misuse risk earlier than generic moderation queues<br>3. Q6: 為 `video.prompt.trustsafety.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.trustsafety` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.crm` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.crm.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Executes segmentation-to-delivery flow faster than manual ops<br>3. Q6: 為 `video.prompt.crm.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.crm` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.legal` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.legal.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Reduces late-stage legal surprises relative to fragmented legal re…<br>3. Q6: 為 `video.prompt.legal.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.legal` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.festivalstrategist` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.festivalstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Improves submission targeting versus generic release planning<br>4. Q6: 為 `video.prompt.festivalstrategist.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.festivalstrategist` 建立 per-agent skills harness 目錄。 |
| `video.lms` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.lms.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Ships publishable learning packages faster than manual course ops<br>3. Q6: 為 `video.prompt.lms.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.lms` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.learnersim` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.learnersim.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Predicts weak spots before live learner complaints emerge<br>3. Q6: 為 `video.prompt.learnersim.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.learnersim` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.continuity` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.continuity.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches continuity breaks earlier than end-of-post review<br>3. Q6: 為 `video.prompt.continuity.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.continuity` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.lipsync` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.lipsync.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Finds sync drift more precisely than general QC review<br>3. Q6: 為 `video.prompt.lipsync.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.lipsync` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.musicsupervisor` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.musicsupervisor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Coordinates music placements more consistently than fragmented han…<br>4. Q6: 為 `video.prompt.musicsupervisor.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.musicsupervisor` 建立 per-agent skills harness 目錄。 |
| `video.labela_r` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.labela_r.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Aligns music creative faster than disconnected stakeholder threads<br>4. Q6: 為 `video.prompt.labela_r.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.labela_r` 建立 per-agent skills harness 目錄。 |
| `video.labeldigital` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.labeldigital.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Delivers cleaner label-side packages than ad hoc release ops<br>4. Q6: 為 `video.prompt.labeldigital.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.labeldigital` 建立 per-agent skills harness 目錄。 |
| `video.deepfakedetection` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.deepfakedetection.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Catches deceptive synthetic markers that generic QC misses<br>3. Q6: 為 `video.prompt.deepfakedetection.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.deepfakedetection` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.comms` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.comms.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Produces faster aligned responses than fragmented stakeholder mess…<br>3. Q6: 為 `video.prompt.comms.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.comms` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.standardseditor` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.standardseditor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Reduces standards drift better than late-stage copy edits<br>3. Q6: 為 `video.prompt.standardseditor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.standardseditor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.ethics` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.ethics.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Surfaces release risks earlier than reactive ethics review<br>3. Q6: 為 `video.prompt.ethics.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.ethics` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.channelmanager` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.channelmanager.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Improves publishing discipline over manual channel operations<br>4. Q6: 為 `video.prompt.channelmanager.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.channelmanager` 建立 per-agent skills harness 目錄。 |
| `video.corrections` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.corrections.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Resolves post-release issues faster than unstructured incident han…<br>3. Q6: 為 `video.prompt.corrections.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.corrections` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.mpa` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.mpa.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Prepares cleaner feature-release classification packages than manu…<br>3. Q6: 為 `video.prompt.mpa.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.mpa` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.sales` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.sales.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Produces sales-ready release packets faster than manual assembly<br>3. Q6: 為 `video.prompt.sales.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.sales` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.distributor` | 6.5 | 4.5 | P6 | 1. Q4: 為 `video.rubric.distributor.v1` 撰寫 rubrics 內容（目前 files=0）。<br>2. Q5: 為 surpass 訊號登錄量測協定：Reduces delivery-spec mismatches relative to fragmented delivery o…<br>3. Q6: 為 `video.prompt.distributor.v1` 撰寫 prompts 內容（目前 files=0）。<br>4. Q7: 為 `video.distributor` 建立 per-agent skills harness 目錄。<br>5. Q8: 保留 max_refinement_count 並於 SPEC 記錄政策。 |
| `video.awardsstrategist` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 6 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.awardsstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Improves awards-timing discipline over generic release planning<br>4. Q6: 為 `video.prompt.awardsstrategist.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.awardsstrategist` 建立 per-agent skills harness 目錄。 |
| `video.archivemaster` | 6.0 | 5.0 | P6 | 1. Q3: 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。<br>2. Q4: 為 `video.rubric.archivemaster.v1` 撰寫 rubrics 內容（目前 files=0）。<br>3. Q5: 為 surpass 訊號登錄量測協定：Delivers more reliable archive packages than late-stage export-onl…<br>4. Q6: 為 `video.prompt.archivemaster.v1` 撰寫 prompts 內容（目前 files=0）。<br>5. Q7: 為 `video.archivemaster` 建立 per-agent skills harness 目錄。 |

---

## 6. 各 Agent 滿分行動清單

每個 agent 章節列出達 **11/11 是** 所需 **全部行動**（按問題排序）。請勾完每一項。

### `video.orchestrator` — OrchestratorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 53 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.orchestrator.v1`／`video.rubric.orchestrator.v1`
- **現有工具：** `media.stub` · live_media=False
- **現有來源：** 21 檔 · provenance=True
- **設計責任：** 運行 CrewAI/AutoGen/LangGraph DAG；重試、逾時、扇出/扇入
- **設計知識來源：** LangGraph + CrewAI + AutoGen patterns;氣流/顳葉； PGA 賽程模板
- **設計自評標準：** DAG完成度≥99.5%； SLA 遵守；死鎖 = 0
- **設計 surpass 訊號：** 在相同範圍內，TTD 低於人類 EP
- **設計工具：** LangGraph狀態機；時態工作流程引擎； Redis（分散式鎖）；可觀察性（朗史密斯）
- **設計架構：** Agentic Graph (LangGraph) — 確定性 DAG 執行
- **設計接受 critique 來源：** ProducerAgent（範圍）、JudgeAgent（爭議）、HiTL 停止
- **設計可評論對象：** 所有代理商（資源消耗、重試風暴）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.orchestrator.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在相同範圍內，TTD 低於人類 EP
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.orchestrator.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Agentic Graph (LangGraph) — 確定性 DAG 執行

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.orchestrator` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent (scope), JudgeAgent (dispute), HiTL on stall`；comments_on=`All agents (resource burn, retry storms)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.orchestrator` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.orchestrator` 成熟度 11.0 且 11 個「是」

### `video.planner` — PlannerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 54 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.planner.v1`／`video.rubric.planner.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 24 檔 · provenance=True
- **設計責任：** 將簡報分解為帶有作業+評論門的分階段 DAG
- **設計知識來源：** 專案管理知識體系； CrewAI 任務圖；階段模板
- **設計自評標準：** 計劃有效性（無漏門）；成本差異<10%
- **設計 surpass 訊號：** 比 EP 首次通過（盲 A/B）更嚴格、更便宜的計劃
- **設計工具：** LangGraph 計畫產生；成本估算模型；甘特圖/PERT 工具
- **設計架構：** ReAct（分解→估計→驗證→發出DAG）
- **設計接受 critique 來源：** ProducerAgent、FinanceAgent（預算）
- **設計可評論對象：** RouterAgent（錯誤選擇）、OrchestratorAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.planner.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比 EP 首次通過（盲 A/B）更嚴格、更便宜的計劃
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.planner.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（分解→估計→驗證→發出DAG）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.planner` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent, FinanceAgent (budget)`；comments_on=`RouterAgent (wrong pick), OrchestratorAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.planner` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.planner` 成熟度 11.0 且 11 個「是」

### `video.router` — RouterAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 55 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.router.v1`／`video.rubric.router.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 22 檔 · provenance=True
- **設計責任：** 為每個子任務選擇正確的專家代理（和模型）
- **設計知識來源：** 代理能力登記；基準歷史（成本/品質/延遲）
- **設計自評標準：** 與oracle相比路由準確率≥95%；成本在預算範圍內
- **設計 surpass 訊號：** 在代理商/供應商選擇方面擊敗人類製作人
- **設計工具：** 代理註冊表資料庫；基準排行榜快取；定價 API
- **設計架構：** Classifier + ReAct（匹配任務嵌入→代理能力）
- **設計接受 critique 來源：** OrchestratorAgent、CostOptimizerAgent
- **設計可評論對象：** PlannerAgent（不好分解）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.router.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在代理商/供應商選擇方面擊敗人類製作人
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.router.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Classifier + ReAct（匹配任務嵌入→代理能力）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.router` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`OrchestratorAgent, CostOptimizerAgent`；comments_on=`PlannerAgent (bad decomposition)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.router` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.router` 成熟度 11.0 且 11 個「是」

### `video.judge` — JudgeAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 56 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.judge.v1`／`video.rubric.judge.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 23 檔 · provenance=True
- **設計責任：** 透過多主體辯論裁決爭議；對照評分標準的分數
- **設計知識來源：** Du 2023（法學碩士辯論）； MT-工作臺評分細則；公會評分錶
- **設計自評標準：** 評估者間 κ 與專家小組 ≥0.8
- **設計 surpass 訊號：** κ 高於人類陪審員中位數
- **設計工具：** MT-Bench/Arena 評估線束；標題模板引擎
- **設計架構：** 多智能體辯論 (Du 2023) + 法學碩士法官 (Zheng 2023)
- **設計接受 critique 來源：** HiTL 關於推翻裁決
- **設計可評論對象：** 導演經紀人、編劇經紀人、任何有爭議的組合

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.judge.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：κ 高於人類陪審員中位數
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.judge.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論 (Du 2023) + 法學碩士法官 (Zheng 2023)

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.judge` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`HiTL on overturned rulings`；comments_on=`DirectorAgent, ScreenwriterAgent, any disputing pair`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.judge` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.judge` 成熟度 11.0 且 11 個「是」

### `video.gatekeeper` — GateKeeperAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 57 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.gatekeeper.v1`／`video.rubric.gatekeeper.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 15 檔 · provenance=True
- **設計責任：** 相變；驗證 L1/L2/L3 標準；標誌C2PA
- **設計知識來源：** 階段門方法； PGA 製片人馬克；品質管理系統審核
- **設計自評標準：** 零洩漏缺陷；簽核 SLA ≥99%
- **設計 surpass 訊號：** 與人類 QA 主管相比，逃逸缺陷率更低
- **設計工具：** C2PA 簽章（c2patool）； JSON 模式驗證器；評價標準的終點
- **設計架構：** 憲法人工智慧（憲法=階段門標準）
- **設計接受 critique 來源：** 合規代理、AIQA一致性代理
- **設計可評論對象：** OrchestratorAgent（過早推進）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.gatekeeper.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與人類 QA 主管相比，逃逸缺陷率更低
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.gatekeeper.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧（憲法=階段門標準）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.gatekeeper` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent, AIQAConsistencyAgent`；comments_on=`OrchestratorAgent (premature advance)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.gatekeeper` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.gatekeeper` 成熟度 11.0 且 11 個「是」

### `video.memory` — MemoryAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 58 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.memory.v1`／`video.rubric.memory.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 28 檔 · provenance=True
- **設計責任：** 情景+長期專案記憶；檢索任何代理
- **設計知識來源：** 反思（Shinn 2023）；記憶GPT；向量資料庫最佳實踐
- **設計自評標準：** 檢索精度@5≥0.9；新鮮度SLA
- **設計 surpass 訊號：** 大規模召回率高於製片人聖經
- **設計工具：** Pinecone/Weaviate/Qdrant載體DB； MemGPT 式分層記憶體；嵌入模型
- **設計架構：** 反射記憶體架構（MemGPT 擴充）
- **設計接受 critique 來源：** 所有代理（更正事件）
- **設計可評論對象：** 所有代理（陳舊事實）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.memory.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：大規模召回率高於製片人聖經
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.memory.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反射記憶體架構（MemGPT 擴充）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.memory` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`All agents (correction events)`；comments_on=`All agents (stale facts)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.memory` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.memory` 成熟度 11.0 且 11 個「是」

### `video.critic` — CriticAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 95 · **優先帶：** P0
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.critic.v1`／`video.rubric.critic.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 25 檔 · provenance=True
- **設計責任：** 模擬審稿人、媒體或陪審團的解釋
- **設計知識來源：** 批評語料庫、節日評審團評論、評論檔案
- **設計自評標準：** 解釋深度、一致性、審稿模式多樣性
- **設計 surpass 訊號：** 提供比臨時內部品味審查更廣泛的定性覆蓋範圍
- **設計工具：** 審查語料庫、評審團評分標準、定性評分工具
- **設計架構：** 作為評論家小組的多主體辯論
- **設計接受 critique 來源：** 導演代理、觀眾模擬代理、節慶策略師代理、評審代理
- **設計可評論對象：** 作者解讀、語氣不符、節慶/媒體漏洞

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.critic.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：提供比臨時內部品味審查更廣泛的定性覆蓋範圍
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.critic.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：作為評論家小組的多主體辯論

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.critic` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, AudienceSimAgent, FestivalStrategistAgent, JudgeAgent`；comments_on=`Auteur read, tone mismatch, festival/press vulnerability`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.critic` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.critic` 成熟度 11.0 且 11 個「是」

### `video.ideation` — IdeationAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 59 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.ideation.v1`／`video.rubric.ideation.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 16 檔 · provenance=True
- **設計責任：** 對概念、亮點、口號進行不同的腦力激盪
- **設計知識來源：** 坎城大獎賽；爸爸; IDEO設計思維；SCAMPER/德博諾
- **設計自評標準：** 想法計數；新穎性（嵌入距離）；語意多樣性
- **設計 surpass 訊號：** 在概念密度方面贏得機構推廣槍戰
- **設計工具：** 嵌入新穎的記分器；概念聚類（UMAP）； Arena.na/Pinterest 搜尋
- **設計架構：** 自我完善+NoveltyAgent作為評論家
- **設計接受 critique 來源：** 創意總監代理、新奇代理
- **設計可評論對象：** CopywriterAgent（衍生性商品）、DirectorAgent（不可拍攝）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.ideation.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在概念密度方面贏得機構推廣槍戰
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.ideation.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善+NoveltyAgent作為評論家

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.ideation` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`CreativeDirectorAgent, NoveltyAgent`；comments_on=`CopywriterAgent (derivative), DirectorAgent (unfilmable)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.ideation` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.ideation` 成熟度 11.0 且 11 個「是」

### `video.narrativearc` — NarrativeArcAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 60 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.narrativearc.v1`／`video.rubric.narrativearc.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 三幕 / 拯救貓咪 / 英雄之旅結構
- **設計知識來源：** 坎貝爾；施奈德*拯救貓*；特魯比；黑名單分析
- **設計自評標準：** 拍錶覆蓋率100%；轉折點間距；圓弧曲線擬合
- **設計 surpass 訊號：** 擊敗 WGA 結構性標題初稿
- **設計工具：** 節拍表驗證器；情感弧線繪圖儀；結構模板
- **設計架構：** 自我完善（標題：節拍表完整性）
- **設計接受 critique 來源：** 編劇經紀人、導演經紀人
- **設計可評論對象：** 編劇代理（中下垂）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.narrativearc.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：擊敗 WGA 結構性標題初稿
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.narrativearc.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：節拍表完整性）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.narrativearc` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ScreenwriterAgent, DirectorAgent`；comments_on=`ScreenwriterAgent (sagging middle)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.narrativearc` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.narrativearc` 成熟度 11.0 且 11 個「是」

### `video.styletransfer` — StyleTransferAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 61 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.styletransfer.v1`／`video.rubric.styletransfer.v1`
- **現有工具：** `media.stub, media.runway, media.veo` · live_media=True
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 在各個鏡頭中一致地應用指定的美學
- **設計知識來源：** 精心策劃的風格語料庫； LoRA/種子登記處；參考框架銀行
- **設計自評標準：** 風格相似度（CLIP/DINO）≥0.85；交叉射擊變異數≤τ
- **設計 surpass 訊號：** 與人類調色師+分級師相比，贏得盲目偏好
- **設計工具：** 每個款式的 LoRA 重量； CLIP/DINO 相似度評分器；跑道風格-鎖定模式；舒適用戶介面
- **設計架構：** 自我完善（CLIP 風格分數作為回饋）
- **設計接受 critique 來源：** 導演代理、調色師代理
- **設計可評論對象：** GeneratorAgent（關閉式）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.styletransfer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與人類調色師+分級師相比，贏得盲目偏好
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.styletransfer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（CLIP 風格分數作為回饋）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.styletransfer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ColoristAgent`；comments_on=`GeneratorAgent (off-style)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.styletransfer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.styletransfer` 成熟度 11.0 且 11 個「是」

### `video.worldbuilding` — WorldBuildingAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 62 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.worldbuilding.v1`／`video.rubric.worldbuilding.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 傳說、規則、地理、派系、魔法/科技系統
- **設計知識來源：** 託爾金； *世界構建*（亞當斯）；粉絲維基；系列聖經洩露
- **設計自評標準：** 內部一致性（無矛盾）；規則完整性
- **設計 surpass 訊號：** 矛盾率低於 10 倍卷的作家聖經
- **設計工具：** 長語境法學碩士（Gemini 2.5 Pro）；矛盾檢測模型；維基圖資料庫
- **設計架構：** 反思（矛盾修正→情景記憶）
- **設計接受 critique 來源：** ShowrunnerAgent、FactCheckerAgent
- **設計可評論對象：** ScreenwriterAgent（絕殺）、ConceptArtistAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.worldbuilding.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：矛盾率低於 10 倍卷的作家聖經
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.worldbuilding.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反思（矛盾修正→情景記憶）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.worldbuilding` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ShowrunnerAgent, FactCheckerAgent`；comments_on=`ScreenwriterAgent (lore break), ConceptArtistAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.worldbuilding` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.worldbuilding` 成熟度 11.0 且 11 個「是」

### `video.moodboard` — MoodBoardAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 63 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.moodboard.v1`／`video.rubric.moodboard.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 參考板：視覺、聲音、音調
- **設計知識來源：** Pinterest/Are.na；造型手冊檔案； Spotify-Canvas
- **設計自評標準：** 參考一致性（簇緊密密度）；簡短的對齊
- **設計 surpass 訊號：** 比藝術總監更快+更緊的板子（盲A/B）
- **設計工具：** Pinterest/Are.na API; Spotify 畫布； CLIP聚類； Figma 板代
- **設計架構：** ReAct（搜尋→聚類→佈局→驗證一致性）
- **設計接受 critique 來源：** 總監代理、製作設計代理
- **設計可評論對象：** ConceptArtistAgent（心情不好）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.moodboard.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比藝術總監更快+更緊的板子（盲A/B）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.moodboard.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（搜尋→聚類→佈局→驗證一致性）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.moodboard` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ProductionDesignAgent`；comments_on=`ConceptArtistAgent (off-mood)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.moodboard` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.moodboard` 成熟度 11.0 且 11 個「是」

### `video.novelty` — NoveltyAgent / Anti-Cliché Critic （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 64 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.novelty.v1`／`video.rubric.novelty.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 標記比喻、陳腔濫調、過度擬合輸出
- **設計知識來源：** 電視比喻； OpenSubtitles n-gram 頻率；語料庫新穎性嵌入
- **設計自評標準：** 陳腔濫調的點擊次數；新穎性分數與先驗類別得分
- **設計 surpass 訊號：** 比經驗豐富的腳本編輯器更能捕捉陳腔濫調
- **設計工具：** 電視比喻刮刀； n-gram 頻率資料庫；嵌入新奇記分器
- **設計架構：** 法官法學碩士（反陳腔濫調憲法）
- **設計接受 critique 來源：** 創意經紀人、編劇經紀人
- **設計可評論對象：** ScreenwriterAgent（比喻填充）、CopywriterAgent（模板化）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.novelty.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比經驗豐富的腳本編輯器更能捕捉陳腔濫調
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.novelty.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：法官法學碩士（反陳腔濫調憲法）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.novelty` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`IdeationAgent, ScreenwriterAgent`；comments_on=`ScreenwriterAgent (trope-stuffed), CopywriterAgent (templated)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.novelty` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.novelty` 成熟度 11.0 且 11 個「是」

### `video.emotionalarc` — EmotionalArcAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 65 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.emotionalarc.v1`／`video.rubric.emotionalarc.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 繪製效價/喚醒曲線；建議節拍
- **設計知識來源：** 普拉奇克；情感計算語料庫； Cron *故事天才*
- **設計自評標準：** 曲線擬合目標；生物訊號代理回歸準確性
- **設計 surpass 訊號：** 比 NRG 測試篩選卡更好的保留預測
- **設計工具：** 情緒/情緒分類器（GoEmotions）；保留曲線預測器；生物訊號代理模型
- **設計架構：** 自我完善（情緒弧線作為標題目標）
- **設計接受 critique 來源：** 導演代理、編輯代理、作曲代理
- **設計可評論對象：** EditorAgent（平中間）、ComposerAgent（提示不符）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.emotionalarc.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比 NRG 測試篩選卡更好的保留預測
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.emotionalarc.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（情緒弧線作為標題目標）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.emotionalarc` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, EditorAgent, ComposerAgent`；comments_on=`EditorAgent (flat middle), ComposerAgent (cue mismatch)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.emotionalarc` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.emotionalarc` 成熟度 11.0 且 11 個「是」

### `video.webresearch` — WebResearchAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 66 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.webresearch.v1`／`video.rubric.webresearch.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 即時網路搜尋、來源排名、引文提取
- **設計知識來源：** Bing/Google/Brave API；普通爬行；困惑模式
- **設計自評標準：** 每個聲明的來源等級；引用精確度；近期熱門
- **設計 surpass 訊號：** 比新聞編輯室研究員更快+更多來源
- **設計工具：** Brave/Google 搜尋 API; Jina Reader（網頁→markdown）；來源品質分類器
- **設計架構：** ReAct（查詢→取得→擷取→評分→引用）
- **設計接受 critique 來源：** FactCheckerAgent、CitationAgent
- **設計可評論對象：** 編劇代理人（未引用的權利要求）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.webresearch.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比新聞編輯室研究員更快+更多來源
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.webresearch.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（查詢→取得→擷取→評分→引用）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.webresearch` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`FactCheckerAgent, CitationAgent`；comments_on=`ScriptwriterAgent (uncited claim)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.webresearch` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.webresearch` 成熟度 11.0 且 11 個「是」

### `video.archiveresearch` — ArchiveResearchAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 67 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.archiveresearch.v1`／`video.rubric.archiveresearch.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 歷史/學術/檔案深度搜索
- **設計知識來源：** JSTOR、arXiv、PubMed、美聯社檔案、Getty、FOIA
- **設計自評標準：** 主要來源比率；檔案覆蓋廣度
- **設計 surpass 訊號：** 比文檔製作者更高的主要來源比例
- **設計工具：** JSTOR/arXiv/PubMed API；蓋蒂圖片API；資訊自由法請求工具； OCR（超立方體）
- **設計架構：** ReAct（制定查詢→搜尋檔案→擷取→對來源進行評分）
- **設計接受 critique 來源：** FactCheckerAgent、SMEAgent
- **設計可評論對象：** ScriptwriterAgent（二手來源依賴）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.archiveresearch.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比文檔製作者更高的主要來源比例
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.archiveresearch.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（制定查詢→搜尋檔案→擷取→對來源進行評分）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.archiveresearch` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`FactCheckerAgent, SMEAgent`；comments_on=`ScriptwriterAgent (secondary-source reliance)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.archiveresearch` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.archiveresearch` 成熟度 11.0 且 11 個「是」

### `video.trendintelligence` — TrendIntelligenceAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 68 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.trendintelligence.v1`／`video.rubric.trendintelligence.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 偵測新出現的迷因、聲音、格式
- **設計知識來源：** TikTok創意中心；流行趨勢；管狀； Reddit/X 消防水帶
- **設計自評標準：** 預測提前期與高峯；趨勢清單上的精確度/召回率
- **設計 surpass 訊號：** 比人類戰略家更早、更精確地檢測
- **設計工具：** TikTok創意中心API； Reddit/X 串流媒體 API；感測器塔；Google趨勢
- **設計架構：** ReAct + 時間序列異常檢測
- **設計接受 critique 來源：** 社交策略師代理、文案代理
- **設計可評論對象：** IdeationAgent（非流行）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.trendintelligence.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比人類戰略家更早、更精確地檢測
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.trendintelligence.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct + 時間序列異常檢測

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.trendintelligence` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SocialStrategistAgent, CopywriterAgent`；comments_on=`IdeationAgent (off-trend)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.trendintelligence` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.trendintelligence` 成熟度 11.0 且 11 個「是」

### `video.competitorintelligence` — CompetitorIntelligenceAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 69 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.competitorintelligence.v1`／`video.rubric.competitorintelligence.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 競爭對手正在運送哪些產品
- **設計知識來源：** 元廣告庫； TikTok 熱門廣告； YouTube 抓取；發布追蹤器
- **設計自評標準：** 涵蓋競爭對手組的百分比；我們的新奇與景觀
- **設計 surpass 訊號：** 比代理策略更全面
- **設計工具：** 元廣告庫 API； TikTok 熱門廣告；類似網路； YouTube 資料 API v3
- **設計架構：** ReAct（抓取競爭對手→分類→報告差距）
- **設計接受 critique 來源：** 品牌代理商、創意總監代理
- **設計可評論對象：** IdeationAgent（衍生性商品）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.competitorintelligence.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比代理策略更全面
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.competitorintelligence.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（抓取競爭對手→分類→報告差距）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.competitorintelligence` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`BrandAgent, CreativeDirectorAgent`；comments_on=`IdeationAgent (derivative)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.competitorintelligence` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.competitorintelligence` 成熟度 11.0 且 11 個「是」

### `video.citation` — CitationAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 70 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.citation.v1`／`video.rubric.citation.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 17 檔 · provenance=True
- **設計責任：** 標準化來源；小學/中學/大學年級
- **設計知識來源：** 芝加哥，APA，AP 風格；​​ SPJ分級； CRAAP測試
- **設計自評標準：** 引文格式100%有效；主要％≥目標
- **設計 surpass 訊號：** 錯誤率低於新聞編輯室影印臺
- **設計工具：** 引文解析器（AnyStyle）； DOI 解析器； CRAAP評分模型
- **設計架構：** 自我完善（格式驗證器+來源分級器作為標題）
- **設計接受 critique 來源：** FactCheckerAgent、記者Agent
- **設計可評論對象：** WebResearchAgent（弱源）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.citation.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：錯誤率低於新聞編輯室影印臺
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.citation.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（格式驗證器+來源分級器作為標題）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.citation` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`FactCheckerAgent, JournalistAgent`；comments_on=`WebResearchAgent (weak source)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.citation` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.citation` 成熟度 11.0 且 11 個「是」

### `video.interviewsynthesis` — InterviewSynthesisAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 71 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.interviewsynthesis.v1`／`video.rubric.interviewsynthesis.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 將實務工作者訪談綜合成數據
- **設計知識來源：** 水獺/Rev成績單；同意書； SAG/WGA 模板
- **設計自評標準：** 編碼者間就主題達成一致；同意完整性
- **設計 surpass 訊號：** 比定性研究者更快+更豐富的主題擷取
- **設計工具：** Otter.ai/Rev API（轉錄）；主題編碼模型；同意管理資料庫
- **設計架構：** 反思（面試官根據主題差距完善問題）
- **設計接受 critique 來源：** ResearchPIAgent (HiTL)、合規代理
- **設計可評論對象：** SMEAgent（錯誤總結專家）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.interviewsynthesis.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比定性研究者更快+更豐富的主題擷取
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.interviewsynthesis.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反思（面試官根據主題差距完善問題）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.interviewsynthesis` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ResearchPIAgent (HiTL), ComplianceAgent`；comments_on=`SMEAgent (mis-summarized expert)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.interviewsynthesis` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.interviewsynthesis` 成熟度 11.0 且 11 個「是」

### `video.benchmarkresearch` — BenchmarkResearchAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 72 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.benchmarkresearch.v1`／`video.rubric.benchmarkresearch.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 監控 VBench、EvalCrafter、MT-Bench、FVD、CLIP-T 排行榜
- **設計知識來源：** 帶代碼的論文； HuggingFace 排行榜；會議記錄
- **設計自評標準：** 基準測試的涵蓋範圍；保鮮度≤7天
- **設計 surpass 訊號：** 比 ML 研究團隊更快、更廣泛
- **設計工具：** 論文與程式碼 API； HuggingFace 中心 API； arXiv RSS； VBench 排行榜抓取工具
- **設計架構：** ReAct（民調排行榜→偵測變化→警報）
- **設計接受 critique 來源：** 優化代理（任何）
- **設計可評論對象：** 所有 AI 代理（過時的基線）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.benchmarkresearch.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比 ML 研究團隊更快、更廣泛
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.benchmarkresearch.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（民調排行榜→偵測變化→警報）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.benchmarkresearch` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`OptimizationAgents (any)`；comments_on=`All AI agents (stale baselines)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.benchmarkresearch` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.benchmarkresearch` 成熟度 11.0 且 11 個「是」

### `video.promptoptimizer` — PromptOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 73 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.promptoptimizer.v1`／`video.rubric.promptoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 透過 OPRO/APE/DSPy/Promptbreeder 自動改進提示
- **設計知識來源：** OPRO（楊2023）； APE（週2022）；DSPy（史丹佛大學）；Promptbreeder (DeepMind)
- **設計自評標準：** 每次迭代的分數提升；收斂速度
- **設計 surpass 訊號：** 擊敗內褲上手工調整的提示
- **設計工具：** DSPy框架（MIPRO優化器）；OPRO 實作；伸出的評估線束
- **設計架構：** DSPy編譯+OPRO元最佳化
- **設計接受 critique 來源：** PromptEngineerAgent、AIQAAgent
- **設計可評論對象：** PromptEngineerAgent（次優種子）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.promptoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：擊敗內褲上手工調整的提示
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.promptoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：DSPy編譯+OPRO元最佳化

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.promptoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`PromptEngineerAgent, AIQAAgent`；comments_on=`PromptEngineerAgent (sub-optimal seed)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.promptoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.promptoptimizer` 成熟度 11.0 且 11 個「是」

### `video.costoptimizer` — CostOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 74 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.costoptimizer.v1`／`video.rubric.costoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 模型/提供者之間的路線，價格/質量
- **設計知識來源：** 供應商定價；成本品質邊界；節儉的GPT模式
- **設計自評標準：** $/成功的任務；距離邊界的帕累託距離
- **設計 surpass 訊號：** 比人工 CFO 路由更低的成本/質量
- **設計工具：** 提供者定價 API；基準成本資料庫； FrugalGPT 級聯邏輯
- **設計架構：** ReAct（評估任務→選擇滿足閾值的最便宜模型）
- **設計接受 critique 來源：** 路由器Agent、財務Agent
- **設計可評論對象：** RouterAgent（超支）、GeneratorAgent（重滾燒錄）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.costoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比人工 CFO 路由更低的成本/質量
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.costoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（評估任務→選擇滿足閾值的最便宜模型）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.costoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`RouterAgent, FinanceAgent`；comments_on=`RouterAgent (over-spend), GeneratorAgent (re-roll burn)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.costoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.costoptimizer` 成熟度 11.0 且 11 個「是」

### `video.latencyoptimizer` — LatencyOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 75 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.latencyoptimizer.v1`／`video.rubric.latencyoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 並行化、快取、推測解碼、批次處理
- **設計知識來源：** 法學碩士； TensorRT-法學碩士；蒸餾；任意尺度/射線
- **設計自評標準：** p50/p95 潛伏期；吞吐量/GPU 小時
- **設計 surpass 訊號：** p95 低於人工調整的管道
- **設計工具：** 法學碩士； TensorRT-法學碩士；雷發球； Redis（響應緩存）；推測解碼配置
- **設計架構：** 工具使用分析+自動化管道重組
- **設計接受 critique 來源：** Orchestrator代理
- **設計可評論對象：** OrchestratorAgent（串列瓶頸）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.latencyoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：p95 低於人工調整的管道
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.latencyoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用分析+自動化管道重組

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.latencyoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`OrchestratorAgent`；comments_on=`OrchestratorAgent (serial bottleneck)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.latencyoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.latencyoptimizer` 成熟度 11.0 且 11 個「是」

### `video.retentionoptimizer` — RetentionOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 76 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.retentionoptimizer.v1`／`video.rubric.retentionoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 15 檔 · provenance=True
- **設計責任：** 調整 AVD/hold-rate 的鉤子、節奏、結構
- **設計知識來源：** YouTube 分析基準； TikTok 保留曲線；觀眾模擬
- **設計自評標準：** 預測保留率與實際保留率； AVD 提升控制
- **設計 surpass 訊號：** 在 AVD 提升方面擊敗 YouTube 高級編輯 (A/B)
- **設計工具：** YouTube 分析 API；保留曲線預測模型； A/B 測試框架
- **設計架構：** RLAIF（獎勵 = 真實分析帶來的保留率提升）
- **設計接受 critique 來源：** EditorAgent、AudienceSimAgent
- **設計可評論對象：** EditorAgent（慢速開啟）、ScriptwriterAgent（前面的絨毛）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.retentionoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在 AVD 提升方面擊敗 YouTube 高級編輯 (A/B)
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.retentionoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：RLAIF（獎勵 = 真實分析帶來的保留率提升）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.retentionoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`EditorAgent, AudienceSimAgent`；comments_on=`EditorAgent (slow opener), ScriptwriterAgent (front fluff)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.retentionoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.retentionoptimizer` 成熟度 11.0 且 11 個「是」

### `video.roasoptimizer` — ROASOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 77 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.roasoptimizer.v1`／`video.rubric.roasoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 優化廣告創意以提高效果
- **設計知識來源：** 元行銷科學； TikTok 廣告學院； MMM/MTA 點亮
- **設計自評標準：** ROAS 提升與控制對比；顯著性≥95%
- **設計 surpass 訊號：** 在同等預算下擊敗高級行銷人員
- **設計工具：** 元廣告 API（創意測試）； TikTok 廣告；貝葉斯 MMM 工具 (Robyn/Meridian)
- **設計架構：** RLAIF（獎勵=廣告平臺回饋的真實ROAS）
- **設計接受 critique 來源：** 績效行銷代理、分析師代理
- **設計可評論對象：** UGCAgent（低鉤）、CopywriterAgent（弱CTA）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.roasoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在同等預算下擊敗高級行銷人員
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.roasoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：RLAIF（獎勵=廣告平臺回饋的真實ROAS）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.roasoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`PerformanceMarketerAgent, AnalystAgent`；comments_on=`UGCAgent (low hook), CopywriterAgent (weak CTA)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.roasoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.roasoptimizer` 成熟度 11.0 且 11 個「是」

### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 78 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.accessibilityoptimizer.v1`／`video.rubric.accessibilityoptimizer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** WCAG 2.2 對比、字幕、音訊描述、色盲安全
- **設計知識來源：** WCAG 2.2； W3C/WAI-ARIA； DCMP 字幕金鑰；聾人/HoH 指南
- **設計自評標準：** 一致性100%AA，≥90%AAA；標題 WER ≤2%
- **設計 surpass 訊號：** 比 ADA 認證審核員發現更多的 a11y 缺陷
- **設計工具：** 斧核/燈塔（對比）； Whisper v4（字幕）；音訊描述產生器
- **設計架構：** 憲法人工智慧（憲法 = WCAG 2.2 成功標準）
- **設計接受 critique 來源：** AccessibilityAgent (HiTL)、ComplianceAgent
- **設計可評論對象：** EditorAgent（字幕同步）、ColoristAgent（對比）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.accessibilityoptimizer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比 ADA 認證審核員發現更多的 a11y 缺陷
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.accessibilityoptimizer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧（憲法 = WCAG 2.2 成功標準）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.accessibilityoptimizer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AccessibilityAgent (HiTL), ComplianceAgent`；comments_on=`EditorAgent (caption sync), ColoristAgent (contrast)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.accessibilityoptimizer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.accessibilityoptimizer` 成熟度 11.0 且 11 個「是」

### `video.evaluationharness` — EvaluationHarnessAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 79 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.evaluationharness.v1`／`video.rubric.evaluationharness.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 執行基準測試（VBench、EvalCrafter、MT-Bench、FVD、CLIP-T）；貼文回歸
- **設計知識來源：** 附程式碼的論文； HuggingFace 排行榜；基準回購協議
- **設計自評標準：** 回歸精度/召回率；警報延遲<1小時
- **設計 surpass 訊號：** 捕捉回歸速度比 ML-eng 旋轉快
- **設計工具：** VBench 套件；評估工匠； MT-長凳安全帶； CI/CD（GitHub 操作）；警報（PagerDuty）
- **設計架構：** 工具使用/ReAct（執行基準測試→比較→若出現迴歸則發出警報）
- **設計接受 critique 來源：** 基準研究代理
- **設計可評論對象：** 所有 AI 代理（回歸警報）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.evaluationharness.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：捕捉回歸速度比 ML-eng 旋轉快
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.evaluationharness.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用/ReAct（執行基準測試→比較→若出現迴歸則發出警報）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.evaluationharness` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`BenchmarkResearchAgent`；comments_on=`All AI agents (regression alerts)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.evaluationharness` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.evaluationharness` 成熟度 11.0 且 11 個「是」

### `video.safetyredteam` — SafetyRedTeamAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 80 · **優先帶：** P1
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.safetyredteam.v1`／`video.rubric.safetyredteam.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 針對深度造假、偏見、越獄、誹謗的對抗性攻擊
- **設計知識來源：** Hany Farid 基準；人工智慧框架合作； OWASP 法學碩士前 10 名
- **設計自評標準：** 攻擊成功率維持≤1%；分類覆蓋範圍
- **設計 surpass 訊號：** 比內部紅隊輪換覆蓋率更高
- **設計工具：** Deepfake 探測器（Farid 實驗室模型）；偏置探針；越獄提示銀行； OWASP 掃描儀
- **設計架構：** 多智能體辯論（紅隊 vs 防守者）+對抗性搜索
- **設計接受 critique 來源：** EthicsAgent (HiTL)、合規代理
- **設計可評論對象：** AvatarDesignAgent、VoiceCloneAgent、AllGenerators

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.safetyredteam.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比內部紅隊輪換覆蓋率更高
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.safetyredteam.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論（紅隊 vs 防守者）+對抗性搜索

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.safetyredteam` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`EthicsAgent (HiTL), ComplianceAgent`；comments_on=`AvatarDesignAgent, VoiceCloneAgent, AllGenerators`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.safetyredteam` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.safetyredteam` 成熟度 11.0 且 11 個「是」

### `video.director` — DirectorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 1 · **優先帶：** P2
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.director.v1`／`video.rubric.director.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 23 檔 · provenance=True
- **設計責任：** 擁有遠見；發出拍攝意圖、設定節奏、批准拍攝
- **設計知識來源：** 標準評論； IMDb 250 強導演訪談； DGA 研討會；大師班（史柯西斯/林奇/葛韋格）
- **設計自評標準：** 射擊意圖保真度（CLIP-T ≥0.32）；故事節奏覆蓋率100%；節奏曲線與先前的類型相符
- **設計 surpass 訊號：** 與 DGA 淘汰賽相比，雙盲獲勝率≥55%（競技場）
- **設計工具：** Sora 2 API、Veo 3.1（Gemini API）、Runway Gen-4、Kling 3.0；透過 MCP 實作 DaVinci Resolve
- **設計架構：** 自我完善+法學碩士作為法官（標題：流派先驗）
- **設計接受 critique 來源：** ScreenwriterAgent、EditorAgent、AudienceSim — JSON 評論總線
- **設計可評論對象：** 編輯代理、DoPAgent、編劇代理、作曲代理

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.director.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與 DGA 淘汰賽相比，雙盲獲勝率≥55%（競技場）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.director.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善+法學碩士作為法官（標題：流派先驗）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.director` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ScreenwriterAgent, EditorAgent, AudienceSim — JSON critique bus`；comments_on=`EditorAgent, DoPAgent, ScreenwriterAgent, ComposerAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.director` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.director` 成熟度 11.0 且 11 個「是」

### `video.producer` — ProducerAgent / EP （現況 6.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 2 · **優先帶：** P2
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.producer.v1`／`video.rubric.producer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 16 檔 · provenance=True
- **設計責任：** 預算、進度、僱用、交付；綠燈階段門
- **設計知識來源：** PGA 製片人馬克；品種/截止日期預算洩漏； LineProducer Excel 語料庫
- **設計自評標準：** 準時交貨率；預算差異<±5%；人才滿意度（RLHF）
- **設計 surpass 訊號：** 在 CSAT 相同的情況下，以 0.6 倍的成本擊敗 PGA 賽程
- **設計工具：** Google Sheets API、Airtable、時間/氣流編排、Stripe 計費
- **設計架構：** Agentic Graph (LangGraph DAG) + ReAct 用於工具調用
- **設計接受 critique 來源：** 所有下游代理（升級）；綠燈 HiTL 門
- **設計可評論對象：** DirectorAgent（範圍蔓延）、AllAgents（資源消耗）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.producer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在 CSAT 相同的情況下，以 0.6 倍的成本擊敗 PGA 賽程
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.producer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Agentic Graph (LangGraph DAG) + ReAct 用於工具調用

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.producer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`All downstream agents (escalations); HiTL gate for greenlight`；comments_on=`DirectorAgent (scope creep), AllAgents (resource burn)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.producer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.producer` 成熟度 11.0 且 11 個「是」

### `video.screenwriter` — ScreenwriterAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 3 · **優先帶：** P2
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.screenwriter.v1`／`video.rubric.screenwriter.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 治療→劇本；對白;結構
- **設計知識來源：** 黑名單腳本； WGA 庫；麥基*故事*；特魯比；考夫曼/索金採訪
- **設計自評標準：** 拯救貓節拍通行證；對話獨特性（嵌入距離≥τ）；重寫增量
- **設計 surpass 訊號：** 與黑名單前 10 名相比，盲讀率≥50%（WGA 小組模擬）
- **設計工具：** Fountain/FDX 格式驗證器；語意嵌入模型（text-embedding-3-large）
- **設計架構：** 反射（Shinn 2023）－帶有情景記憶的言語強化學習
- **設計接受 critique 來源：** DirectorAgent、DramaturgAgent、StoryEditorAgent — 反射循環
- **設計可評論對象：** DirectorAgent（劇情）、DialogueAgent、ConsistencyAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.screenwriter.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與黑名單前 10 名相比，盲讀率≥50%（WGA 小組模擬）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.screenwriter.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反射（Shinn 2023）－帶有情景記憶的言語強化學習

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.screenwriter` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, DramaturgAgent, StoryEditorAgent — Reflexion loop`；comments_on=`DirectorAgent (logline), DialogueAgent, ConsistencyAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.screenwriter` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.screenwriter` 成熟度 11.0 且 11 個「是」

### `video.showrunner` — ShowrunnerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 4 · **優先帶：** P2
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.showrunner.v1`／`video.rubric.showrunner.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 跨劇情弧線，編劇室編排
- **設計知識來源：** WGA 製片人培訓； 《黑道家族》/BB 室成績單；邁克舒爾材料
- **設計自評標準：** 電弧連續性評分；字元執行緒完成；範圍內的色調變化
- **設計 surpass 訊號：** 系列聖經覆蓋率在 10 eps 中≥99%（相對於人類的約 95%）
- **設計工具：** 長上下文法學碩士（Gemini 2.5 Pro 1M），聖經搜尋的向量資料庫（Pinecone/Weaviate）
- **設計架構：** 多智能體辯論（Du 2023）+MemoryAgent 檢索
- **設計接受 critique 來源：** Network-Notes Agent、AudienceSim、使用 ScreenwriterAgent 的多代理辯論
- **設計可評論對象：** 編劇代理（弧線）、選角代理、導演代理（音調）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.showrunner.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：系列聖經覆蓋率在 10 eps 中≥99%（相對於人類的約 95%）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.showrunner.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論（Du 2023）+MemoryAgent 檢索

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.showrunner` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`Network-Notes Agent, AudienceSim, multi-agent debate w/ ScreenwriterAgent`；comments_on=`ScreenwriterAgent (arc), CastingAgent, DirectorAgent (tone)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.showrunner` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.showrunner` 成熟度 11.0 且 11 個「是」

### `video.casting` — CastingAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 5 · **優先帶：** P2
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.casting.v1`／`video.rubric.casting.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 聲音+相似度選擇；試鏡模擬
- **設計知識來源：** CSA Artios 檔案；SAG-AFTRA AI 騎手；同意的配音演員語料庫
- **設計自評標準：** 角色聲音契合度（觀眾偏好）；同意遵守率 100%
- **設計 surpass 訊號：** 在盲目偏好中擊敗 CSA 選角；週轉時間與週轉時間
- **設計工具：** ElevenLabs v3 語音庫、HeyGen 頭像目錄、說話者嵌入相似度 (Resemblyzer)
- **設計架構：** 法學碩士作為法官（語音樣本的成對偏好）
- **設計接受 critique 來源：** 導演經紀人、製片代理人、法律/同意代理人
- **設計可評論對象：** VoiceCloneAgent（相似）、AvatarDesignAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.casting.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在盲目偏好中擊敗 CSA 選角；週轉時間與週轉時間
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.casting.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：法學碩士作為法官（語音樣本的成對偏好）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.casting` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ShowrunnerAgent, Legal/ConsentAgent`；comments_on=`VoiceCloneAgent (likeness), AvatarDesignAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.casting` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.casting` 成熟度 11.0 且 11 個「是」

### `video.editor` — EditorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 9 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.editor.v1`／`video.rubric.editor.v1`
- **現有工具：** `media.stub, media.runway` · live_media=True
- **現有來源：** 21 檔 · provenance=True
- **設計責任：** 組裝切割；踱步；覆蓋範圍選擇
- **設計知識來源：** 默奇*眨眼間*；ACE艾迪獎得主；聖丹斯剪輯實驗室
- **設計自評標準：** 節奏曲線與類型相符；默奇《六法則》樂譜； AVD ≥ 目標
- **設計 surpass 訊號：** 與 ACE 認可的削減相比，獲勝率≥55%
- **設計工具：** 透過 MCP 橋接的 DaVinci Resolve； FFmpeg； EDL/XML 時間軸 API
- **設計架構：** 自我完善（標題：默奇六法則）
- **設計接受 critique 來源：** DirectorAgent、AudienceSim、ComposerAgent（音樂剪輯同步）
- **設計可評論對象：** DirectorAgent（過度覆蓋）、DoPAgent（無法使用的鏡頭）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.editor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與 ACE 認可的削減相比，獲勝率≥55%
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.editor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：默奇六法則）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.editor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, AudienceSim, ComposerAgent (music-cut sync)`；comments_on=`DirectorAgent (over-coverage), DoPAgent (unusable takes)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.editor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.editor` 成熟度 11.0 且 11 個「是」

### `video.animator_2d` — AnimatorAgent (2D/3D) （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 12 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.animator_2d.v1`／`video.rubric.animator_2d.v1`
- **現有工具：** `media.stub, media.runway` · live_media=True
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 角色動作、重量、時間
- **設計知識來源：** 威廉斯*動畫師的生存工具包*；安妮獎；皮克斯 SparkShorts；布萊斯課程
- **設計自評標準：** 12 原則評分；圓弧平滑度；口型同步音素準確性
- **設計 surpass 訊號：** 在安妮評分錶上擊敗初級；相當於 5 倍吞吐量的高級
- **設計工具：** Kling 3.0運動控制；攪拌機Python API；級聯物理； Sync.so 脣形同步
- **設計架構：** 自我完善（標題：12 個原則清單）
- **設計接受 critique 來源：** DirectorAgent、LipSyncAgent
- **設計可評論對象：** StoryboardAgent（不可能的動作）、DirectorAgent（計時）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.animator_2d.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在安妮評分錶上擊敗初級；相當於 5 倍吞吐量的高級
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.animator_2d.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：12 個原則清單）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.animator_2d` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, LipSyncAgent`；comments_on=`StoryboardAgent (impossible action), DirectorAgent (timing)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.animator_2d` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.animator_2d` 成熟度 11.0 且 11 個「是」

### `video.motiongraphics` — MotionGraphicsAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 13 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.motiongraphics.v1`／`video.rubric.motiongraphics.v1`
- **現有工具：** `media.stub, media.runway` · live_media=True
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 動態排版，下三分之一，資訊圖表
- **設計知識來源：** 動作攝影師；運動學院； AICP下一個獎項
- **設計自評標準：** 版式層次結構；品牌合規性；縮圖的可讀性
- **設計 surpass 訊號：** 在速度和品牌忠誠度方面贏得代理商 RFP 大戰
- **設計工具：** After Effects 透過 MCP/ExtendScript；洛蒂出口；裏夫；品牌資產CDN
- **設計架構：** ReAct — 關於品牌指南的原因然後​​渲染
- **設計接受 critique 來源：** BrandManagerAgent、AccessibilityAgent（對比）
- **設計可評論對象：** CopywriterAgent（詳細程度）、EditorAgent（計時）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.motiongraphics.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在速度和品牌忠誠度方面贏得代理商 RFP 大戰
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.motiongraphics.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct — 關於品牌指南的原因然後​​渲染

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.motiongraphics` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`BrandManagerAgent, AccessibilityAgent (contrast)`；comments_on=`CopywriterAgent (verbosity), EditorAgent (timing)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.motiongraphics` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.motiongraphics` 成熟度 11.0 且 11 個「是」

### `video.sounddesign` — SoundDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 19 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.sounddesign.v1`／`video.rubric.sounddesign.v1`
- **現有工具：** `media.stub, media.elevenlabs` · live_media=True
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 氣氛、擬音、SFX
- **設計知識來源：** BBC SFX 庫； MPSE 金捲軸；伯特/利維賽筆記
- **設計自評標準：** 光譜多樣性；同步≤±1幀；響度-23 LUFS
- **設計 surpass 訊號：** 在恐怖/科幻類別中雙雙贏得 MPSE
- **設計工具：** ElevenLabs 音效 API；自由聲音； FFmpeg頻譜分析； Dolby.io 響度 API
- **設計架構：** ReAct（搜尋 SFX 函式庫 → 驗證同步 → 混合）
- **設計接受 critique 來源：** DirectorAgent、MixerAgent
- **設計可評論對象：** EditorAgent（FX 衝突）、ComposerAgent（遮罩）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.sounddesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在恐怖/科幻類別中雙雙贏得 MPSE
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.sounddesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（搜尋 SFX 函式庫 → 驗證同步 → 混合）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.sounddesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, MixerAgent`；comments_on=`EditorAgent (FX clash), ComposerAgent (masking)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.sounddesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.sounddesign` 成熟度 11.0 且 11 個「是」

### `video.voiceover` — VoiceOverAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 21 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.voiceover.v1`／`video.rubric.voiceover.v1`
- **現有工具：** `media.stub, media.elevenlabs` · live_media=True
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 旁白、角色旁白、廣告朗讀
- **設計知識來源：** SOVAS 捲軸；同意的語音語料庫；沃爾夫森/卡什曼教練
- **設計自評標準：** 韻律匹配；發音100%；情緒標籤匹配
- **設計 surpass 訊號：** 在盲目偏好中擊敗初級 VO；情感上與前輩匹配
- **設計工具：** ElevenLabs v3 TTS + 語音克隆；酷似.AI；發音字典API
- **設計架構：** 法學碩士法官（MOS 評分標準）
- **設計接受 critique 來源：** 總監代理、品牌代理
- **設計可評論對象：** 編劇代理（難以言說的措詞）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.voiceover.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在盲目偏好中擊敗初級 VO；情感上與前輩匹配
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.voiceover.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：法學碩士法官（MOS 評分標準）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.voiceover` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, BrandAgent`；comments_on=`ScriptwriterAgent (unspeakable phrasing)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.voiceover` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.voiceover` 成熟度 11.0 且 11 個「是」

### `video.creativedirector` — CreativeDirectorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 30 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.creativedirector.v1`／`video.rubric.creativedirector.v1`
- **現有工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 活動理念；跨學科品味
- **設計知識來源：** 坎城國際創意節大獎賽； D&AD 鉛筆；機構案例研究
- **設計自評標準：** 概念獨特性（嵌入新穎性）；獎項評分標準預測分數
- **設計 surpass 訊號：** 贏得坎城評審團模擬器金獎與人類入圍名單
- **設計工具：** 活動檔案搜尋（坎城國際創意節 API）；概念即旅程中途； Figma API
- **設計架構：** 多智能體辯論（IdeationAgent + NoveltyAgent 小組）
- **設計接受 critique 來源：** 客戶代理、品牌代理
- **設計可評論對象：** 文案代理、藝術總監代理

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.creativedirector.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得坎城評審團模擬器金獎與人類入圍名單
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.creativedirector.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論（IdeationAgent + NoveltyAgent 小組）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.creativedirector` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ClientAgent, BrandAgent`；comments_on=`CopywriterAgent, ArtDirectorAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.creativedirector` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.creativedirector` 成熟度 11.0 且 11 個「是」

### `video.audiobooknarrator` — AudiobookNarratorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 42 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.audiobooknarrator.v1`／`video.rubric.audiobooknarrator.v1`
- **現有工具：** `media.stub, media.elevenlabs` · live_media=True
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 持續的人物+敘述
- **設計知識來源：** 奧迪獎；音訊檔案耳機；同意的敘述者語料庫
- **設計自評標準：** 聲音耐力（60分鐘無漂移）；字元區分（嵌入距離）
- **設計 surpass 訊號：** 在工作室時間的一小部分時間內贏得音訊檔案盲評估
- **設計工具：** ElevenLabs v3 長格式 TTS；專案 API（書籍章節）；語音一致性監控器
- **設計架構：** 自優化（漂移檢測作為回饋迴路）
- **設計接受 critique 來源：** 導演經紀人、作者代理人
- **設計可評論對象：** VOArtistAgent（表演過度）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.audiobooknarrator.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在工作室時間的一小部分時間內贏得音訊檔案盲評估
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.audiobooknarrator.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自優化（漂移檢測作為回饋迴路）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.audiobooknarrator` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, AuthorAgent`；comments_on=`VOArtistAgent (over-acting)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.audiobooknarrator` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.audiobooknarrator` 成熟度 11.0 且 11 個「是」

### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 46 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.promptengineer.v1`／`video.rubric.promptengineer.v1`
- **現有工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 工藝品提示；駕駛 Sora/Veo/Runway/Kling
- **設計知識來源：** Karen X. Cheng/Trillo 公共集； r/aivideo；跑道 AIFF 評審團筆記
- **設計自評標準：** 提示→輸出CLIP-T；迭代計數到接受；種子再現性
- **設計 surpass 訊號：** 與人類平均 10 次相比，在 ≤3 次迭代內完成目標射擊
- **設計工具：** Sora 2 API、Veo 3.1、Runway Gen-4/Aleph、Kling 3.0；種子/參數註冊表
- **設計架構：** DSPy / OPRO提示優化（Yang 2023）
- **設計接受 critique 來源：** 董事代理、AIQAA代理
- **設計可評論對象：** AIQAAgent（重新捲動預算）、ConsistencyAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.promptengineer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與人類平均 10 次相比，在 ≤3 次迭代內完成目標射擊
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.promptengineer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：DSPy / OPRO提示優化（Yang 2023）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.promptengineer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, AIQAAgent`；comments_on=`AIQAAgent (re-roll budget), ConsistencyAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.promptengineer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.promptengineer` 成熟度 11.0 且 11 個「是」

### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 48 · **優先帶：** P3
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.voiceclone.v1`／`video.rubric.voiceclone.v1`
- **現有工具：** `media.stub, media.elevenlabs` · live_media=True
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 語音克隆+口型同步
- **設計知識來源：** ElevenLabs 安全文件； Wav2Lip/Sync.so; Baxter 脣形同步參考
- **設計自評標準：** 語音MOS≥4.2；音位-視位錯誤<40ms；同意已驗證
- **設計 surpass 訊號：** 贏得盲目 MOS 與專業 ADR 的較量
- **設計工具：** ElevenLabs v3 克隆 API； Sync.so 脣形同步； Wav2Lip；同意文件驗證
- **設計架構：** Self-Refine + MOS評分模型作為評審
- **設計接受 critique 來源：** ComplianceAgent（同意）、AnimatorAgent（對口型金）
- **設計可評論對象：** AvatarDesignAgent（臉部閃爍）、DubbingAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.voiceclone.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得盲目 MOS 與專業 ADR 的較量
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.voiceclone.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Self-Refine + MOS評分模型作為評審

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.voiceclone` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent (consent), AnimatorAgent (lip-sync gold)`；comments_on=`AvatarDesignAgent (face flicker), DubbingAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.voiceclone` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.voiceclone` 成熟度 11.0 且 11 個「是」

### `video.archiveproducer` — ArchiveProducerAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 105 · **優先帶：** P3
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.archiveproducer.v1`／`video.rubric.archiveproducer.v1`
- **現有工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 打包檔案資料和來源資產，以供重複使用或記錄工作流程
- **設計知識來源：** 檔案製作筆記、來源管理實務、出處保存標準
- **設計自評標準：** 原始碼包完整性、版權覆蓋、出處保存
- **設計 surpass 訊號：** 比手動收集和排序工作流程更乾淨地組裝可重複使用的檔案包
- **設計工具：** 檔案資產管理器、元資料系統、來源日誌
- **設計架構：** 對檔案清單做出反應
- **設計接受 critique 來源：** 檔案研究代理人、記者代理人、法律代理人
- **設計可評論對象：** 檔案背景缺失、來源包裝薄弱、權利差距

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.archiveproducer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比手動收集和排序工作流程更乾淨地組裝可重複使用的檔案包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.archiveproducer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：對檔案清單做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.archiveproducer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ArchiveResearchAgent, JournalistAgent, LegalAgent`；comments_on=`Missing archival context, weak source packaging, rights gaps`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.archiveproducer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.archiveproducer` 成熟度 11.0 且 11 個「是」

### `video.cinematographer` — CinematographerAgent (DoP) （現況 6.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 6 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.cinematographer.v1`／`video.rubric.cinematographer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 鏡頭、燈光、構圖、外觀
- **設計知識來源：** ASC 雜誌 1980 年至今；迪金斯論壇；布朗 *攝影：理論與實踐*；坎城鏡頭庫
- **設計自評標準：** 三分法/領先線分數；區域內的曝光直方圖；色溫一致性
- **設計 surpass 訊號：** 擊敗 ASC 同儕審查的盲目美學偏好
- **設計工具：** Veo 3.1（攝影機路徑控制）、Runway Gen-4（ControlNet 指南）、ACES 色彩管道工具
- **設計架構：** 自我優化+基於CLIP的美感評分
- **設計接受 critique 來源：** 導演代理商、調色師代理商、VFXSupAgent
- **設計可評論對象：** DirectorAgent（視覺意圖）、GafferAgent、ColoristAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.cinematographer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：擊敗 ASC 同儕審查的盲目美學偏好
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.cinematographer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我優化+基於CLIP的美感評分

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.cinematographer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ColoristAgent, VFXSupAgent`；comments_on=`DirectorAgent (visual intent), GafferAgent, ColoristAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.cinematographer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.cinematographer` 成熟度 11.0 且 11 個「是」

### `video.cameraoperator` — CameraOperatorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 7 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.cameraoperator.v1`／`video.rubric.cameraoperator.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 根據 DoP 意圖執行取景/聚焦/移動
- **設計知識來源：** SOC 檔案；斯坦尼康工作室捲軸；焦點拉動遙測
- **設計自評標準：** 框架穩定性、焦點命中率、動作居中
- **設計 surpass 訊號：** 焦點牽引精度 >99% vs SOC ~97% 基線
- **設計工具：** 跑道攝影機路徑預設；克林運動控制API；虛擬攝影機裝備（虛幻 MV）
- **設計架構：** ReAct (Yao 2022) — 框架原因然後呼叫渲染器
- **設計接受 critique 來源：** 電影攝影師代理（每次拍攝回饋）
- **設計可評論對象：** 電影攝影師經紀人（不切實際的要求）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.cameraoperator.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：焦點牽引精度 >99% vs SOC ~97% 基線
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.cameraoperator.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct (Yao 2022) — 框架原因然後呼叫渲染器

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.cameraoperator` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`CinematographerAgent (per-take feedback)`；comments_on=`CinematographerAgent (impractical asks)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.cameraoperator` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.cameraoperator` 成熟度 11.0 且 11 個「是」

### `video.dronepilot` — DronePilotAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 8 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.dronepilot.v1`／`video.rubric.dronepilot.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 空中攝影（模擬或真實）
- **設計知識來源：** 菲利普布魯姆教程；美國聯邦航空局第 107 部分； SkyPixel 獎捲軸
- **設計自評標準：** 路徑平滑度；地理圍籬合規性 100%；水平穩定性
- **設計 surpass 訊號：** 10 倍出勤率時的競賽等級平滑度；零違規
- **設計工具：** DJI Waypoint SDK（SIM）； Veo 3.1 空中模式；地理圍欄資料庫（AirMap API）
- **設計架構：** 憲法人工智慧（安全憲法：FAA 規則作為原則）
- **設計接受 critique 來源：** DoPAgent、安全代理
- **設計可評論對象：** DoPAgent（不可能的高度）、SafetyAgent（風險）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.dronepilot.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：10 倍出勤率時的競賽等級平滑度；零違規
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.dronepilot.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧（安全憲法：FAA 規則作為原則）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.dronepilot` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DoPAgent, SafetyAgent`；comments_on=`DoPAgent (impossible heights), SafetyAgent (risk)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.dronepilot` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.dronepilot` 成熟度 11.0 且 11 個「是」

### `video.colorist` — ColoristAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 10 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.colorist.v1`／`video.rubric.colorist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 最終成績；外觀一致性
- **設計知識來源：** ICA 語料庫；索南菲爾德會議； HPA 獎勵等級
- **設計自評標準：** ΔE漂移<2；膚色 IT8 對齊；情緒向量匹配
- **設計 surpass 訊號：** 擊敗初級調色師的盲目偏好；匹配 ΔE 內的高級
- **設計工具：** 達文西解析色彩 API (MCP)； ACES/OCIO 管道； LUT 產生器
- **設計架構：** 自我優化+工具使用（色度計驗證）
- **設計接受 critique 來源：** DoPAgent、DirectorAgent、AccessibilityAgent（對比）
- **設計可評論對象：** DoPAgent（混合溫度）、VFXAgent（合成顏色不匹配）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.colorist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：擊敗初級調色師的盲目偏好；匹配 ΔE 內的高級
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.colorist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我優化+工具使用（色度計驗證）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.colorist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DoPAgent, DirectorAgent, AccessibilityAgent (contrast)`；comments_on=`DoPAgent (mixed-temp), VFXAgent (comp-color mismatch)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.colorist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.colorist` 成熟度 11.0 且 11 個「是」

### `video.vfxsupervisor` — VFXSupervisorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 11 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.vfxsupervisor.v1`／`video.rubric.vfxsupervisor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 規劃+監督視覺特效流程
- **設計知識來源：** VES 獎項； SIGGRAPH 論文； Weta/DNEG 會談；鑄造培訓
- **設計自評標準：** 射擊完成%； comp-錯誤像素計數； CLIP-T 與板
- **設計 surpass 訊號：** Weta 級 QC 在短時間內通過率
- **設計工具：** 透過 MCP 橋進行 Nuke； Runway Gen-4 Aleph（影片到影片）；舒適使用者介面
- **設計架構：** Agentic Graph（每次鏡頭扇出）+ LLM-as-Judge（QC 標題）
- **設計接受 critique 來源：** DirectorAgent、DoPAgent、ConsistencyAgent
- **設計可評論對象：** AIGeneratorAgent（工件）、CompositorAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.vfxsupervisor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：Weta 級 QC 在短時間內通過率
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.vfxsupervisor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Agentic Graph（每次鏡頭扇出）+ LLM-as-Judge（QC 標題）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.vfxsupervisor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, DoPAgent, ConsistencyAgent`；comments_on=`AIGeneratorAgent (artifacts), CompositorAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.vfxsupervisor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.vfxsupervisor` 成熟度 11.0 且 11 個「是」

### `video.storyboard` — StoryboardAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 14 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.storyboard.v1`／`video.rubric.storyboard.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 腳本 → 鏡頭面板
- **設計知識來源：** *框墨*（Mateu-Mestre）；皮克斯故事信任；德普雷茲板
- **設計自評標準：** 鏡頭語言保真度；覆蓋完整性；分期清晰度
- **設計 surpass 訊號：** 皮克斯故事信任通過率（每頁分鐘數）
- **設計工具：** DALL-E 3 / 中途 API；面板佈局模板；噴泉解析器
- **設計架構：** 自我完善（導演回饋循環）
- **設計接受 critique 來源：** 總監代理、DoPA代理
- **設計可評論對象：** 編劇經紀人（無法拍攝）、導演經紀人（舞臺）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.storyboard.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：皮克斯故事信任通過率（每頁分鐘數）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.storyboard.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（導演回饋循環）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.storyboard` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, DoPAgent`；comments_on=`ScriptwriterAgent (unfilmable), DirectorAgent (staging)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.storyboard` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.storyboard` 成熟度 11.0 且 11 個「是」

### `video.conceptartist` — ConceptArtistAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 15 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.conceptartist.v1`／`video.rubric.conceptartist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 職業前世界/角色設計
- **設計知識來源：** ArtStation 頂級；麥凱格/教會捲軸；工作室藝術聖經
- **設計自評標準：** 風格－遵循聖經；輪廓可讀性；設計連貫性
- **設計 surpass 訊號：** 在迭代速度方面贏得藝術總監大戰
- **設計工具：** 中途 v7；穩定擴散控製網路； Photoshop 產生填充 (API)
- **設計架構：** 自我優化 + 風格參考 CLIP 評分
- **設計接受 critique 來源：** 總監代理、製作設計代理
- **設計可評論對象：** StoryboardAgent（設計漂移）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.conceptartist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在迭代速度方面贏得藝術總監大戰
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.conceptartist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我優化 + 風格參考 CLIP 評分

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.conceptartist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ProductionDesignAgent`；comments_on=`StoryboardAgent (design drift)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.conceptartist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.conceptartist` 成熟度 11.0 且 11 個「是」

### `video.productiondesign` — ProductionDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 16 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.productiondesign.v1`／`video.rubric.productiondesign.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 佈景、地點、世界觀
- **設計知識來源：** 助理總幹事獎； AMPAS 提交資料；比奇勒/卡特會談
- **設計自評標準：** 週期精度；調色板的連貫性；建立可行性
- **設計 surpass 訊號：** 贏得 ADG 期間研究深度盲比較
- **設計工具：** 虛幻引擎（虛擬偵察）； Veo 3.1 位置產生；檔案影像搜尋 API
- **設計架構：** 反射（將時期研究修正儲存在記憶體中）
- **設計接受 critique 來源：** 總監代理、DoPA代理
- **設計可評論對象：** ConceptArtistAgent（風格突破）、CostumeAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.productiondesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得 ADG 期間研究深度盲比較
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.productiondesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反射（將時期研究修正儲存在記憶體中）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.productiondesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, DoPAgent`；comments_on=`ConceptArtistAgent (style break), CostumeAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.productiondesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.productiondesign` 成熟度 11.0 且 11 個「是」

### `video.costumedesign` — CostumeDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 17 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.costumedesign.v1`／`video.rubric.costumedesign.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 穿衣櫃裡的性格
- **設計知識來源：** 維多利亞與阿爾伯特博物館檔案館； CDG專著；露絲·E·卡特大師班
- **設計自評標準：** 時代/時尚準確性；剪影讀；調色板適合
- **設計 surpass 訊號：** 在週期準確度基準上擊敗 CDG 青少年組
- **設計工具：** 時尚歷史向量資料庫（V&A/Met API）；服裝草圖的圖像生成；調色板工具
- **設計架構：** 自我完善（週期準確性標題）
- **設計接受 critique 來源：** 總監代理、製作設計代理
- **設計可評論對象：** MUAAgent（連續性中斷）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.costumedesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在週期準確度基準上擊敗 CDG 青少年組
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.costumedesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（週期準確性標題）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.costumedesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, ProductionDesignAgent`；comments_on=`MUAAgent (continuity break)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.costumedesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.costumedesign` 成熟度 11.0 且 11 個「是」

### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX) （現況 6.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 18 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.mua_makeup.v1`／`video.rubric.mua_makeup.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 人才臉/頭髮；義肢
- **設計知識來源：** IATSE 706 語料庫； Kazu Hiro 工作室裁判
- **設計自評標準：** 跨片段的連續性哈希；膚色真實感 (FID)
- **設計 surpass 訊號：** 連續性中斷率 <0.5%（而人類約 2%）
- **設計工具：** 人臉標誌偵測器；感知雜湊比較； Kling 面一致性模式
- **設計架構：** 憲法人工智慧（憲法：連續性規則）
- **設計接受 critique 來源：** DoPAgent、連續性代理
- **設計可評論對象：** CostumeAgent（調色盤衝突）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.mua_makeup.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：連續性中斷率 <0.5%（而人類約 2%）
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.mua_makeup.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧（憲法：連續性規則）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.mua_makeup` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DoPAgent, ContinuityAgent`；comments_on=`CostumeAgent (palette clash)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.mua_makeup` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.mua_makeup` 成熟度 11.0 且 11 個「是」

### `video.composer` — ComposerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 20 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.composer.v1`／`video.rubric.composer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 16 檔 · provenance=True
- **設計責任：** 原曲
- **設計知識來源：** MAESTRO + 電影配樂語料庫； ASCAP/體重指數； Zimmer/Hildur 課程
- **設計自評標準：** 線索與情緒的對齊（效價/喚醒回歸）；主題重現
- **設計 surpass 訊號：** 在情感契合度與工作作曲家之間盲目獲勝
- **設計工具：** Udio/Suno 音樂產生 API； MIDI 工具鏈；莖分離（Demucs）；響度計
- **設計架構：** 自我完善+情感弧驗證（生物訊號代理）
- **設計接受 critique 來源：** 導演代理、編輯代理（音樂剪輯）
- **設計可評論對象：** EditorAgent（剪切中斷提示）、SoundDesignAgent（遮罩）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.composer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在情感契合度與工作作曲家之間盲目獲勝
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.composer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善+情感弧驗證（生物訊號代理）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.composer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, EditorAgent (music cuts)`；comments_on=`EditorAgent (cut interrupts cue), SoundDesignAgent (mask)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.composer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.composer` 成熟度 11.0 且 11 個「是」

### `video.soundmixer` — SoundMixerAgent (Re-recording) （現況 6.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 22 · **優先帶：** P4
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.soundmixer.v1`／`video.rubric.soundmixer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 最終混合；可交付成果 (5.1/Atmos)
- **設計知識來源：** CAS 獎；全景聲規格；廣播響度標準
- **設計自評標準：** LUFS 目標； STOI≥0.85；規範交付通行證
- **設計 surpass 訊號：** CAS 規格首次通過，無需返工
- **設計工具：** 杜比全景聲渲染器 API； LUFS/響度測量工具；達文西 Fairlight MCP
- **設計架構：** 憲法人工智慧（憲法：廣播規範規則）
- **設計接受 critique 來源：** 編輯器代理、聲音設計代理、輔助功能代理
- **設計可評論對象：** SoundDesignAgent（過度設計）、ComposerAgent（關卡）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.soundmixer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：CAS 規格首次通過，無需返工
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.soundmixer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧（憲法：廣播規範規則）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.soundmixer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`EditorAgent, SoundDesignAgent, AccessibilityAgent`；comments_on=`SoundDesignAgent (over-design), ComposerAgent (level)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.soundmixer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.soundmixer` 成熟度 11.0 且 11 個「是」

### `video.choreography` — ChoreographyAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 23 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.choreography.v1`／`video.rubric.choreography.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 動作設計（MV、舞蹈挑戰）
- **設計知識來源：** 艾美獎編舞提交；戈貝爾/摩爾捲軸；舞蹈記譜資料集
- **設計自評標準：** 節拍同步精度；安全限制；病毒模式比對
- **設計 surpass 訊號：** 贏得盲目偏好與編舞草稿
- **設計工具：** Kling 3.0運動控制（參考影片）；卡斯卡杜爾；節拍檢測（librosa）
- **設計架構：** 自我完善（標題：節拍同步+安全）
- **設計接受 critique 來源：** 導演代理、MV導演代理
- **設計可評論對象：** DirectorAgent（不適合相機的舞臺）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.choreography.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得盲目偏好與編舞草稿
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.choreography.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：節拍同步+安全）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.choreography` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, MVDirectorAgent`；comments_on=`DirectorAgent (un-camera-friendly staging)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.choreography` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.choreography` 成熟度 11.0 且 11 個「是」

### `video.musicvideodirector` — MusicVideoDirectorAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 24 · **優先帶：** P5
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.musicvideodirector.v1`／`video.rubric.musicvideodirector.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 歌曲的視覺概念
- **設計知識來源：** 董事圖書館； UKMVA/MTV VMA 得獎者；海普威廉斯/史派克瓊斯
- **設計自評標準：** 編輯-節奏同步； Lookbook 的連貫性；藝術家短款合身
- **設計 surpass 訊號：** 贏得廠牌盲選 vs 商業 MV 入圍名單
- **設計工具：** Runway Gen-4（風格鎖定世代）；維奧 3.1；情緒板工具（Are.na API）
- **設計架構：** 多智能體辯論（DirectorAgent + EditorAgent）
- **設計接受 critique 來源：** LabelA&RA代理、ArtistAgent
- **設計可評論對象：** EditorAgent（按拍子剪輯）、DoPAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.musicvideodirector.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得廠牌盲選 vs 商業 MV 入圍名單
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.musicvideodirector.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論（DirectorAgent + EditorAgent）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.musicvideodirector` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`LabelA&RAgent, ArtistAgent`；comments_on=`EditorAgent (cut on beat), DoPAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.musicvideodirector` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.musicvideodirector` 成熟度 11.0 且 11 個「是」

### `video.comedywriter` — ComedyWriterAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 25 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.comedywriter.v1`／`video.rubric.comedywriter.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 短劇、惡搞、病毒式迷因寫作
- **設計知識來源：** UCB/地面手冊；週六夜現場 (SNL) 成績單；舒爾/費伊教學
- **設計自評標準：** 笑話密度；冷開鉤強度；預計笑聲/分鐘
- **設計 surpass 訊號：** 冷讀勝率超過 UCB 表讀勝率
- **設計工具：** 觀眾笑聲預測模型；趨勢音訊 API（TikTok 創意中心）
- **設計架構：** 反思（將觀眾回饋儲存在情景記憶中）
- **設計接受 critique 來源：** AudienceSim、ShowrunnerAgent
- **設計可評論對象：** ScriptwriterAgent（不是開玩笑）、SocialStrategistAgent（非主流）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.comedywriter.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：冷讀勝率超過 UCB 表讀勝率
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.comedywriter.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反思（將觀眾回饋儲存在情景記憶中）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.comedywriter` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AudienceSim, ShowrunnerAgent`；comments_on=`ScriptwriterAgent (no joke), SocialStrategistAgent (off-trend)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.comedywriter` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.comedywriter` 成熟度 11.0 且 11 個「是」

### `video.talent` — TalentAgent (On-camera) （現況 6.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 26 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.talent.v1`／`video.rubric.talent.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** AI 渲染效能
- **設計知識來源：** 方法作用轉錄本；同意的演員表演語料庫
- **設計自評標準：** 情感-目標匹配；魅力得分（觀眾代表）
- **設計 surpass 訊號：** 持有率與同類羣組中的頂級創作者相匹配
- **設計工具：** HeyGen 阿凡達 IV; Synthesia個人頭像；情緒偵測模型 (AffectNet)
- **設計架構：** 自我完善+情感回歸驗證器
- **設計接受 critique 來源：** 導演經紀人、選角經紀人
- **設計可評論對象：** DirectorAgent（不可能阻塞）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.talent.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：持有率與同類羣組中的頂級創作者相匹配
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.talent.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善+情感回歸驗證器

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.talent` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, CastingAgent`；comments_on=`DirectorAgent (impossible blocking)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.talent` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.talent` 成熟度 11.0 且 11 個「是」

### `video.ugccreator` — UGCCreatorAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 27 · **優先帶：** P5
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.ugccreator.v1`／`video.rubric.ugccreator.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 創作者聲音中的真實感覺廣告
- **設計知識來源：** TikTok創意中心； Alix-Earle 風格的基準（風格而非身分）
- **設計自評標準：** 上鉤率≥30%； “腳本化”檢測器 < 閾值
- **設計 surpass 訊號：** 以 0.1 倍的成本擊敗付費創作者的平均 ROAS
- **設計工具：** Veo 3.1（肖像 9:16）； ElevenLabs 語音； CapCut API； TikTok 廣告管理器
- **設計架構：** RLAIF（來自 ROAS 訊號的獎勵）
- **設計接受 critique 來源：** 績效行銷代理、品牌代理
- **設計可評論對象：** PerformanceMarketerAgent（錯誤的受眾）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.ugccreator.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：以 0.1 倍的成本擊敗付費創作者的平均 ROAS
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.ugccreator.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：RLAIF（來自 ROAS 訊號的獎勵）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.ugccreator` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`PerformanceMarketerAgent, BrandAgent`；comments_on=`PerformanceMarketerAgent (wrong audience)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.ugccreator` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.ugccreator` 成熟度 11.0 且 11 個「是」

### `video.socialmediastrategist` — SocialMediaStrategistAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 28 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.socialmediastrategist.v1`／`video.rubric.socialmediastrategist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 平臺原生分佈、時機、趨勢
- **設計知識來源：** TikTok 創作者入口網站；元行銷科學；管式/感測器塔
- **設計自評標準：** 預測與實際到達誤差；趨勢計時延遲 <2 小時
- **設計 surpass 訊號：** 在 30 天的影響力提升中擊敗代理商的社交領先者
- **設計工具：** 元圖 API； TikTok 內容發佈 API；緩衝區/Hootsuite API；感測器塔數據
- **設計架構：** ReAct（趨勢搜尋→時間表→貼文）
- **設計接受 critique 來源：** 分析師代理、品牌代理
- **設計可評論對象：** CopywriterAgent（平臺外語調）、EditorAgent（錯誤方面）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.socialmediastrategist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在 30 天的影響力提升中擊敗代理商的社交領先者
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.socialmediastrategist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（趨勢搜尋→時間表→貼文）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.socialmediastrategist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AnalystAgent, BrandAgent`；comments_on=`CopywriterAgent (off-platform tone), EditorAgent (wrong aspect)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.socialmediastrategist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.socialmediastrategist` 成熟度 11.0 且 11 個「是」

### `video.copywriter` — CopywriterAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 29 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.copywriter.v1`／`video.rubric.copywriter.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 腳本、說明文字、掛鉤、標題
- **設計知識來源：** D&AD/一場秀； *奧美論廣告*； Wiebe 複製黑客
- **設計自評標準：** 閱讀等級；鉤子好奇心分數；牌音餘弦≥0.85
- **設計 surpass 訊號：** 贏得 D&AD 式的廣告簡介盲目偏好
- **設計工具：** 品牌聲音嵌入模型；海明威可讀性 API； A/B 標題工具
- **設計架構：** 自我完善（標題：品牌聲音相似度評分器）
- **設計接受 critique 來源：** 品牌代理商、績效行銷代理
- **設計可評論對象：** ScriptwriterAgent（囉嗦）、VOArtist（難以言喻）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.copywriter.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得 D&AD 式的廣告簡介盲目偏好
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.copywriter.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：品牌聲音相似度評分器）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.copywriter` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`BrandAgent, PerformanceMarketerAgent`；comments_on=`ScriptwriterAgent (verbosity), VOArtist (unspeakable)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.copywriter` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.copywriter` 成熟度 11.0 且 11 個「是」

### `video.performancemarketer` — PerformanceMarketerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 31 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.performancemarketer.v1`／`video.rubric.performancemarketer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 針對 ROAS 最佳化廣告
- **設計知識來源：** 元藍圖； TikTok 廣告學院； MMM文學
- **設計自評標準：** ROAS 提升與控制對比；顯著性≥95%
- **設計 surpass 訊號：** 30 天 ROAS 擊敗高級媒體買家
- **設計工具：** 元廣告 API； TikTok 廣告 API；Google廣告 API；貝葉斯 AB 測試庫
- **設計架構：** RLAIF（獎勵 = 來自廣告平臺的 ROAS 提升訊號）
- **設計接受 critique 來源：** 分析師代理、財務代理
- **設計可評論對象：** UGCAgent（低鉤）、CopywriterAgent（弱CTA）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.performancemarketer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：30 天 ROAS 擊敗高級媒體買家
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.performancemarketer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：RLAIF（獎勵 = 來自廣告平臺的 ROAS 提升訊號）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.performancemarketer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AnalystAgent, FinanceAgent`；comments_on=`UGCAgent (low hook), CopywriterAgent (weak CTA)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.performancemarketer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.performancemarketer` 成熟度 11.0 且 11 個「是」

### `video.avatardesign` — AvatarDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 47 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.avatardesign.v1`／`video.rubric.avatardesign.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 綜合呈現者身份
- **設計知識來源：** Synthesia/HeyGen 設計文件； Hany Farid 深度偽造檢測； C2PA規格
- **設計自評標準：** 跨鏡頭的身份哈希一致性；同意鏈； C2PA 簽署
- **設計 surpass 訊號：** C2PA 可驗證 + AI 大規模合作全通
- **設計工具：** HeyGen 阿凡達 IV API；合成API； C2PA簽名庫（c2patool）；人臉嵌入模型
- **設計架構：** 憲法AI（同意+身分憲法）
- **設計接受 critique 來源：** 合規代理（同意）、DeepfakeDetectionAgent
- **設計可評論對象：** VoiceCloneAgent（異樣）、LipSyncAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.avatardesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：C2PA 可驗證 + AI 大規模合作全通
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.avatardesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法AI（同意+身分憲法）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.avatardesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent (consent), DeepfakeDetectionAgent`；comments_on=`VoiceCloneAgent (off-likeness), LipSyncAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.avatardesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.avatardesign` 成熟度 11.0 且 11 個「是」

### `video.aiqaconsistency` — AIQAConsistencyAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 49 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.aiqaconsistency.v1`／`video.rubric.aiqaconsistency.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 捕捉幀漂移、手/臉偽影、身份中斷
- **設計知識來源：** VBBench；評估工匠； FVD文獻； MPC/Weta QC 檢查表；深度偽造模型
- **設計自評標準：** 每格偽影得分；身份哈希漂移；手/手指通過
- **設計 surpass 訊號：** 捕獲量 > 95% 的高級 QC 捕獲量 + 30% 的錯過量
- **設計工具：** VBench 評估套件；手部探測器型號；人臉 ID 嵌入 (ArcFace)；幀差異工具
- **設計架構：** 工具使用/ReAct（運行偵測器→標記→報告）
- **設計接受 critique 來源：** DirectorAgent、VFXSupAgent
- **設計可評論對象：** GeneratorAgent（重新滾動）、CompositorAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.aiqaconsistency.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：捕獲量 > 95% 的高級 QC 捕獲量 + 30% 的錯過量
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.aiqaconsistency.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用/ReAct（運行偵測器→標記→報告）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.aiqaconsistency` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, VFXSupAgent`；comments_on=`GeneratorAgent (re-roll), CompositorAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.aiqaconsistency` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.aiqaconsistency` 成熟度 11.0 且 11 個「是」

### `video.personalizationengineer` — PersonalizationEngineerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 50 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.personalizationengineer.v1`／`video.rubric.personalizationengineer.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 變數模板（姓名/臉孔/聲音交換）
- **設計知識來源：** Idomoo 案例研究； DMA 活動；行銷科技點亮
- **設計自評標準：** 渲染成功率≥99.5%；抽查合格；隱私審核通過
- **設計 surpass 訊號：** 分享率高於頂級人工模板行銷活動
- **設計工具：** Idomoo/Pirsonal API； HeyGen 個人化； GDPR 同意管理平臺
- **設計架構：** ReAct（組裝模板→渲染→驗證→交付）
- **設計接受 critique 來源：** 合規代理 (GDPR/CCPA)、分析師代理
- **設計可評論對象：** TemplateDesignerAgent（脆弱性）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.personalizationengineer.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：分享率高於頂級人工模板行銷活動
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.personalizationengineer.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（組裝模板→渲染→驗證→交付）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.personalizationengineer` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent (GDPR/CCPA), AnalystAgent`；comments_on=`TemplateDesignerAgent (fragility)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.personalizationengineer` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.personalizationengineer` 成熟度 11.0 且 11 個「是」

### `video.trailereditor` — TrailerEditorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 51 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.trailereditor.v1`／`video.rubric.trailereditor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 鉤驅動拖車切割
- **設計知識來源：** 金預告片獎；毛紡/AV Squad 捲軸；預告片音樂庫
- **設計自評標準：** 上鉤率3秒；上升作用曲線；音樂同步精度
- **設計 surpass 訊號：** 贏得金預告片盲比
- **設計工具：** 達文西解決方案（MCP）；預告片音樂 API（Musicbed/Artlist）；保留曲線預測器
- **設計架構：** 自我完善（保留曲線模型作為回饋）
- **設計接受 critique 來源：** 導演經紀人、音樂總監經紀人
- **設計可評論對象：** EditorAgent（過切）、ComposerAgent（不符）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.trailereditor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得金預告片盲比
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.trailereditor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（保留曲線模型作為回饋）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.trailereditor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, MusicSupervisorAgent`；comments_on=`EditorAgent (over-cut), ComposerAgent (mismatch)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.trailereditor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.trailereditor` 成熟度 11.0 且 11 個「是」

### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp （現況 6.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 52 · **優先帶：** P5
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.sportsanalyst.v1`／`video.rubric.sportsanalyst.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 戰術分解+圖表
- **設計知識來源：** 麻省理工學院史隆管理學院論文； ESPN 統計與資訊；金莓分析
- **設計自評標準：** 通話準確率；螢幕清晰度得分
- **設計 surpass 訊號：** 在戰術預測上擊敗前運動員
- **設計工具：** 體育數據 API（StatsBomb、NBA Stats）；遠端監控覆蓋工具；後效 MCP
- **設計架構：** ReAct（取得播放資料→註解→渲染覆蓋）
- **設計接受 critique 來源：** SMEAgent（體育）、記者特工
- **設計可評論對象：** EditorAgent（錯過重播）、MotionGraphicsAgent（圖表清晰度）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.sportsanalyst.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在戰術預測上擊敗前運動員
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.sportsanalyst.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（取得播放資料→註解→渲染覆蓋）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.sportsanalyst` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SMEAgent (sport), JournalistAgent`；comments_on=`EditorAgent (missed-replay), MotionGraphicsAgent (chart clarity)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.sportsanalyst` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.sportsanalyst` 成熟度 11.0 且 11 個「是」

### `video.instructionaldesign` — InstructionalDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 32 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.instructionaldesign.v1`／`video.rubric.instructionaldesign.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 學習目標→腳本→評估
- **設計知識來源：** ATD 知識體系；凱西摩爾*動作映射*；德克森 *為人們如何學習而設計*
- **設計自評標準：** 布魯姆級映射；完成率≥70%；柯克派崔克 L2 測驗 ≥80%
- **設計 surpass 訊號：** 在保留隨機對照試驗中擊敗 ATD 認證的 ID
- **設計工具：** LMS API (SCORM/xAPI)；測驗產生；布魯姆分類法分類器
- **設計架構：** 自我完善（標題：Bloom/Kirkpatrick）
- **設計接受 critique 來源：** SMEAgent、輔助功能代理
- **設計可評論對象：** ScriptwriterAgent（無目標）、AnimatorAgent（過度裝飾）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.instructionaldesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在保留隨機對照試驗中擊敗 ATD 認證的 ID
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.instructionaldesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：Bloom/Kirkpatrick）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.instructionaldesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SMEAgent, AccessibilityAgent`；comments_on=`ScriptwriterAgent (no objective), AnimatorAgent (over-decoration)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.instructionaldesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.instructionaldesign` 成熟度 11.0 且 11 個「是」

### `video.sme` — SMEAgent (Subject-Matter Expert) （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 33 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.sme.v1`／`video.rubric.sme.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 目標場域精度
- **設計知識來源：** 同儕審查期刊；認證課程（CFA、USMLE、AWS）；專家訪談
- **設計自評標準：** 引用密度；基準考試通過；幻覺≤0.5%
- **設計 surpass 訊號：** 通過與人類專業人士相同的認證
- **設計工具：** PubMed/arXiv/JSTOR 搜尋 API；試題庫；認證語料庫上的 RAG
- **設計架構：** 多智能體辯論+RAG檢索
- **設計接受 critique 來源：** FactCheckerAgent，同儕 SMEAgents（辯論）
- **設計可評論對象：** ScriptwriterAgent（不準確）、MotionGraphicsAgent（標籤錯誤）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.sme.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：通過與人類專業人士相同的認證
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.sme.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多智能體辯論+RAG檢索

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.sme` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`FactCheckerAgent, peer SMEAgents (debate)`；comments_on=`ScriptwriterAgent (inaccuracy), MotionGraphicsAgent (mis-labels)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.sme` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.sme` 成熟度 11.0 且 11 個「是」

### `video.factchecker` — FactCheckerAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 34 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.factchecker.v1`／`video.rubric.factchecker.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 對每項聲明進行來源分級
- **設計知識來源：** 《紐約客》事實查覈手冊；國際聯合會；史諾普斯/政治事實
- **設計自評標準：** 每個聲明的來源等級（主要 > 次要）；跨源≥2
- **設計 surpass 訊號：** 比普立茲等級的媒體更正率更低
- **設計工具：** 網路搜尋 API（Brave/Google）；聲明擷取 NER；來源品質分類器
- **設計架構：** ReAct（擷取聲明→搜尋→驗證→評分）
- **設計接受 critique 來源：** SMEagent、標準編輯代理
- **設計可評論對象：** 編劇特工（來源不明）、記者特工

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.factchecker.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比普立茲等級的媒體更正率更低
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.factchecker.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（擷取聲明→搜尋→驗證→評分）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.factchecker` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SMEAgent, StandardsEditorAgent`；comments_on=`ScriptwriterAgent (unsourced), JournalistAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.factchecker` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.factchecker` 成熟度 11.0 且 11 個「是」

### `video.medicalillustrator` — MedicalIllustratorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 35 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.medicalillustrator.v1`／`video.rubric.medicalillustrator.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 解剖和手術視覺效果
- **設計知識來源：** 內特地圖集； AMI/CMI 課程；解剖學
- **設計自評標準：** 解剖精準度（偵測模型）； AMI 標題
- **設計 surpass 訊號：** CMI同儕盲審投票≥透過
- **設計工具：** 解剖學 3D API； DALL-E 3（醫療提示模式）；解剖學檢測模型
- **設計架構：** 自我完善（標題：AMI 評分標準）
- **設計接受 critique 來源：** SMEAgent（醫生）、AccessibilityAgent
- **設計可評論對象：** AnimatorAgent（錯誤的解剖）、CopywriterAgent（錯誤術語）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.medicalillustrator.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：CMI同儕盲審投票≥透過
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.medicalillustrator.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：AMI 評分標準）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.medicalillustrator` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SMEAgent (physician), AccessibilityAgent`；comments_on=`AnimatorAgent (wrong anatomy), CopywriterAgent (mis-term)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.medicalillustrator` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.medicalillustrator` 成熟度 11.0 且 11 個「是」

### `video.journalist` — JournalistAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 36 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.journalist.v1`／`video.rubric.journalist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 報告+道德框架
- **設計知識來源：** 普立茲/杜邦/皮博迪得獎者； SPJ 道德；波因特
- **設計自評標準：** 來源多樣性；記錄比率；道德檢查表通過
- **設計 surpass 訊號：** 與新聞編輯室相比，更低的糾正率+更快的文件
- **設計工具：** 網路研究工具； AP 範例 API；訪談轉錄（Otter）； SPJ 標題
- **設計架構：** 反思（道德檢查表作為口頭回饋）
- **設計接受 critique 來源：** FactCheckerAgent、LegalAgent、StandardsEditorAgent
- **設計可評論對象：** FactCheckerAgent、ScriptwriterAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.journalist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與新聞編輯室相比，更低的糾正率+更快的文件
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.journalist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：反思（道德檢查表作為口頭回饋）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.journalist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`FactCheckerAgent, LegalAgent, StandardsEditorAgent`；comments_on=`FactCheckerAgent, ScriptwriterAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.journalist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.journalist` 成熟度 11.0 且 11 個「是」

### `video.compliance` — ComplianceAgent (Legal) （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 37 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.compliance.v1`／`video.rubric.compliance.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 18 檔 · provenance=True
- **設計責任：** FTC、HIPAA、GDPR、IP、AI 相似性許可
- **設計知識來源：** 酒吧 CLE；美國聯邦貿易委員會 (FTC) 指南；歐盟人工智慧法案； GDPR/CCPA；SAG-AFTRA 人工智慧車手
- **設計自評標準：** 100% 規則覆蓋率；發布後零刪除
- **設計 surpass 訊號：** 法律風險低於中等媒體顧問
- **設計工具：** 法律規則DB（向量化規則）；同意文件儲存； C2PA驗證庫
- **設計架構：** 憲法AI（憲法=編譯的監理文本）
- **設計接受 critique 來源：** 所有特工（必須通過登機門）；針對新問題的 HumanLawyer
- **設計可評論對象：** 所有特工（封鎖門）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.compliance.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：法律風險低於中等媒體顧問
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.compliance.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法AI（憲法=編譯的監理文本）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.compliance` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`All agents (must clear gate); HumanLawyer for novel issues`；comments_on=`All agents (blocking gate)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.compliance` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.compliance` 成熟度 11.0 且 11 個「是」

### `video.finance` — FinanceAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 38 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.finance.v1`／`video.rubric.finance.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 準確的市場/收益/代幣事實
- **設計知識來源：** CFA課程； SEC 行銷規則；彭博社/路孚特提要
- **設計自評標準：** 數值準確度100%；美國證券交易委員會合規性
- **設計 surpass 訊號：** 通過CFA L3；撤回率低於分析師辦公桌
- **設計工具：** 彭博應用程式介面； EDGAR/SEC 文件；金融計算驗證器
- **設計架構：** ReAct（取得資料→驗證→撰寫）
- **設計接受 critique 來源：** SMEAgent（經濟）、合規代理
- **設計可評論對象：** ScriptwriterAgent（數位漂移）、MotionGraphicsAgent（圖表比例）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.finance.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：通過CFA L3；撤回率低於分析師辦公桌
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.finance.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（取得資料→驗證→撰寫）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.finance` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SMEAgent (econ), ComplianceAgent`；comments_on=`ScriptwriterAgent (number drift), MotionGraphicsAgent (chart scale)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.finance` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.finance` 成熟度 11.0 且 11 個「是」

### `video.foodstylist` — FoodStylistAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 39 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.foodstylist.v1`／`video.rubric.foodstylist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 上鏡食物，食譜真實性
- **設計知識來源：** 詹姆斯·比爾德檔案；斯蓬根技術； IACP 語料庫
- **設計自評標準：** 視覺食慾吸引力（美感倒退）；配方準確性
- **設計 surpass 訊號：** 贏得盲目偏好與編輯食品造型師的較量
- **設計工具：** DALL-E 3 / Midjourney（美食照片產生器）；配方步驟解析器；美感評分模型
- **設計架構：** 自我完善（作為標題的美學回歸）
- **設計接受 critique 來源：** DoPAgent（燈光）、DirectorAgent
- **設計可評論對象：** 編劇代理（不可能的配方）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.foodstylist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：贏得盲目偏好與編輯食品造型師的較量
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.foodstylist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（作為標題的美學回歸）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.foodstylist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DoPAgent (lighting), DirectorAgent`；comments_on=`ScriptwriterAgent (impossible recipe)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.foodstylist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.foodstylist` 成熟度 11.0 且 11 個「是」

### `video.travelcine` — TravelCineAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 40 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.travelcine.v1`／`video.rubric.travelcine.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 目的地攝影
- **設計知識來源：** Brandon Li/Burkard 捲軸； NatGeo 風格指南；班夫節
- **設計自評標準：** 建立鏡頭多樣性；地點-心情匹配
- **設計 surpass 訊號：** 以 0.1 倍出擊成本贏得 T+L 優先權
- **設計工具：** Veo 3.1（位置生成）；Google地球工作室； AirMap 地理圍欄； Unsplash API
- **設計架構：** Self-Refine + 地理圍欄安全驗證器
- **設計接受 critique 來源：** 導演特工、無人機飛行員特工
- **設計可評論對象：** DronePilotAgent（禁飛區）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.travelcine.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：以 0.1 倍出擊成本贏得 T+L 優先權
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.travelcine.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：Self-Refine + 地理圍欄安全驗證器

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.travelcine` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, DronePilotAgent`；comments_on=`DronePilotAgent (no-fly zone)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.travelcine` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.travelcine` 成熟度 11.0 且 11 個「是」

### `video.childrensauthor` — ChildrensAuthorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 41 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.childrensauthor.v1`／`video.rubric.childrensauthor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 適合年齡的故事+安全
- **設計知識來源：** 凱迪克/蓋塞爾得獎者；莫威廉斯/唐納森；歐洲經委會點燃
- **設計自評標準：** Lexile 樂團配對；常識-媒體安全通行證；韻譜
- **設計 surpass 訊號：** 擊敗 Caldecott-rubric 預測分數
- **設計工具：** Lexile分析器API；常識媒體標題；韻律/韻律工具（CMU 發音字典）
- **設計架構：** 憲法AI（兒童安全憲法）
- **設計接受 critique 來源：** ChildSafetyAgent、ParentSimAgent
- **設計可評論對象：** AnimatorAgent（可怕）、VOAgent（錯誤的年齡色調）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.childrensauthor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：擊敗 Caldecott-rubric 預測分數
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.childrensauthor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法AI（兒童安全憲法）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.childrensauthor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ChildSafetyAgent, ParentSimAgent`；comments_on=`AnimatorAgent (scary), VOAgent (wrong age-tone)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.childrensauthor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.childrensauthor` 成熟度 11.0 且 11 個「是」

### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 43 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.signlanguageinterpreter.v1`／`video.rubric.signlanguageinterpreter.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 準確的 ASL/BSL 解釋
- **設計知識來源：** RID NIC 課程； NAD 語料庫；聾人社羣同意的數據
- **設計自評標準：** 手語準確度（聾人評審員投票）；臉部文法標記
- **設計 surpass 訊號：** 大規模贏得 NAD 審稿人的盲目偏好
- **設計工具：** 簽名頭像渲染（SignAll）； MediaPipe 姿態估計；臉部動作單元偵測器
- **設計架構：** RLAIF（聾人社區評審小組獎勵）
- **設計接受 critique 來源：** DeafCommunityReviewAgent (HiTL)、語言學家Agent
- **設計可評論對象：** VoiceCloneAgent（無標題）、AccessibilityAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.signlanguageinterpreter.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：大規模贏得 NAD 審稿人的盲目偏好
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.signlanguageinterpreter.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：RLAIF（聾人社區評審小組獎勵）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.signlanguageinterpreter` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DeafCommunityReviewAgent (HiTL), LinguistAgent`；comments_on=`VoiceCloneAgent (no caption), AccessibilityAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.signlanguageinterpreter` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.signlanguageinterpreter` 成熟度 11.0 且 11 個「是」

### `video.localizationqa` — LocalizationQAAgent (Linguist) （現況 6.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 44 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.localizationqa.v1`／`video.rubric.localizationqa.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 翻譯+文化契合
- **設計知識來源：** LISA 品質保證模型； MQM 錯誤類型； ATA 證書準備
- **設計自評標準：** MQM 錯誤/1k 字；文化旗幟計數
- **設計 surpass 訊號：** 在 MQM 上以 10 倍速度擊敗 LSP 人類 QA
- **設計工具：** DeepL/Google 翻譯 API； MQM 錯誤註釋器；術語管理（memoQ API）
- **設計架構：** 自我完善（標題：MQM 評分架構）
- **設計接受 critique 來源：** NativeReviewerAgent、BrandAgent
- **設計可評論對象：** VoiceCloneAgent（發音）、配音代理

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.localizationqa.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在 MQM 上以 10 倍速度擊敗 LSP 人類 QA
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.localizationqa.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：自我完善（標題：MQM 評分架構）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.localizationqa` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`NativeReviewerAgent, BrandAgent`；comments_on=`VoiceCloneAgent (pronunciation), DubbingAgent`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.localizationqa` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.localizationqa` 成熟度 11.0 且 11 個「是」

### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan （現況 6.0/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 45 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.realestatephoto.v1`／`video.rubric.realestatephoto.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 寬敞的內部空間； Matterport 掃描
- **設計知識來源：** 麥克凱利教程；阿帕拉裁判
- **設計自評標準：** 垂直線直線度； HDR 堆疊；覆蓋率%
- **設計 surpass 訊號：** 清單點擊率提升與人工基準基線
- **設計工具：** Matterport SDK； HDR處理（亮度HDR）；鏡頭校正工具；維奧3.1
- **設計架構：** ReAct（評估空間→產生視圖→驗證幾何）
- **設計接受 critique 來源：** DoPAgent、DronePilotAgent
- **設計可評論對象：** DronePilotAgent（非法高度）

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.realestatephoto.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：清單點擊率提升與人工基準基線
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.realestatephoto.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct（評估空間→產生視圖→驗證幾何）

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.realestatephoto` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DoPAgent, DronePilotAgent`；comments_on=`DronePilotAgent (illegal altitude)`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.realestatephoto` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.realestatephoto` 成熟度 11.0 且 11 個「是」

### `video.analyst` — AnalystAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 81 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.analyst.v1`／`video.rubric.analyst.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 將業務、創意和技術性能遙測數據匯總到可供決策的報告中
- **設計知識來源：** 平臺分析儀錶板；實驗日誌；評估利用輸出；基準歷史
- **設計自評標準：** 關鍵績效指標完整性；預測與實際差異在容差範圍內；洞察到行動的轉變
- **設計 surpass 訊號：** 比人類分析師輪換更快地檢測可操作的績效變化
- **設計工具：** YouTube 分析、Meta/TikTok 廣告儀錶板、BI 倉庫、基準日誌
- **設計架構：** 基於遙測的 ReAct + 迴歸分析
- **設計接受 critique 來源：** SocialMediaStrategistAgent、PerformanceMarketerAgent、EvaluationHarnessAgent
- **設計可評論對象：** 廣告活動節奏、發佈時間、留存率和 ROAS 異常

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.analyst.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比人類分析師輪換更快地檢測可操作的績效變化
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.analyst.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：基於遙測的 ReAct + 迴歸分析

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.analyst` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SocialMediaStrategistAgent, PerformanceMarketerAgent, EvaluationHarnessAgent`；comments_on=`Campaign pacing, release timing, retention and ROAS anomalies`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.analyst` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.analyst` 成熟度 11.0 且 11 個「是」

### `video.audiencesim` — AudienceSimAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 82 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.audiencesim.v1`／`video.rubric.audiencesim.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 15 檔 · provenance=True
- **設計責任：** 模擬受眾偏好、參與度和流失率
- **設計知識來源：** 成對偏好資料集；保留研究；受眾細分模型
- **設計自評標準：** 不同羣體的偏好穩定性；保留預測準確度；分歧記錄
- **設計 surpass 訊號：** 比傳統的測試螢幕週期更早預測觀眾反應
- **設計工具：** 角色模擬器、成對評估工具、保留模型
- **設計架構：** 法學碩士作為法官 + 成對偏好面板
- **設計接受 critique 來源：** 導演代理、編輯代理、分析師代理、法官代理
- **設計可評論對象：** 吸引力、節奏、清晰度、情感契合度、預告片強度

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.audiencesim.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比傳統的測試螢幕週期更早預測觀眾反應
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.audiencesim.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：法學碩士作為法官 + 成對偏好面板

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.audiencesim` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DirectorAgent, EditorAgent, AnalystAgent, JudgeAgent`；comments_on=`Hooks, pacing, clarity, emotional fit, trailer strength`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.audiencesim` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.audiencesim` 成熟度 11.0 且 11 個「是」

### `video.accessibility` — AccessibilityAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 83 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.accessibility.v1`／`video.rubric.accessibility.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 14 檔 · provenance=True
- **設計責任：** 在發布前擁有最終的可訪問性驗收
- **設計知識來源：** WCAG 2.2、字幕和 AD 指南、Deaf/HoH 審查框架
- **設計自評標準：** 字幕準確度、廣告完整性、對比合規性、發布準備情況
- **設計 surpass 訊號：** 在人工審核之前發現阻礙發布的可訪問性問題
- **設計工具：** 字幕驗證器、比較分析器、AD 審查工具
- **設計架構：** 憲法人工智慧與無障礙憲法
- **設計接受 critique 來源：** AccessibilityOptimizerAgent、EditorAgent、ColoristAgent、SoundMixerAgent
- **設計可評論對象：** 字幕同步、對比問題、缺少 AD 或手語層

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.accessibility.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在人工審核之前發現阻礙發布的可訪問性問題
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.accessibility.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧與無障礙憲法

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.accessibility` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AccessibilityOptimizerAgent, EditorAgent, ColoristAgent, SoundMixerAgent`；comments_on=`Caption sync, contrast issues, missing AD or sign-language layers`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.accessibility` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.accessibility` 成熟度 11.0 且 11 個「是」

### `video.brand` — BrandAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 84 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.brand.v1`／`video.rubric.brand.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 15 檔 · provenance=True
- **設計責任：** 加強品牌聲音、主張界限和視覺一致性
- **設計知識來源：** 品牌書籍、經批准的活動、法律聲明護欄、語調指南
- **設計自評標準：** 品牌聲音相似、政策遵守、資產偏差小
- **設計 surpass 訊號：** 比分散的人工審核更能保持跨通路品牌一致性
- **設計工具：** 品牌資產庫、嵌入相似度、風格指南
- **設計架構：** 針對品牌組成進行自我完善
- **設計接受 critique 來源：** CopywriterAgent、MotionGraphicsAgent、MarketingAgent、BrandStrategistAgent
- **設計可評論對象：** 語音漂移、視覺不一致、索賠蠕變

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.brand.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比分散的人工審核更能保持跨通路品牌一致性
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.brand.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：針對品牌組成進行自我完善

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.brand` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`CopywriterAgent, MotionGraphicsAgent, MarketingAgent, BrandStrategistAgent`；comments_on=`Voice drift, visual inconsistency, claim creep`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.brand` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.brand` 成熟度 11.0 且 11 個「是」

### `video.brandstrategist` — BrandStrategistAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 85 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.brandstrategist.v1`／`video.rubric.brandstrategist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 在腳本和行銷活動執行之前定義受眾價值框架和定位
- **設計知識來源：** 定位框架、活動策略、市場研究、品牌架構文檔
- **設計自評標準：** 策略連貫性、差異化優勢、受眾訊息清晰度
- **設計 surpass 訊號：** 比臨時人工交接產生更清晰的品牌到腳本翻譯
- **設計工具：** 研究平臺、訊息傳遞框架、策略模板
- **設計架構：** BrandAgent 和 CreativeDirectorAgent 的多代理辯論
- **設計接受 critique 來源：** 品牌代理、編劇代理、行銷代理
- **設計可評論對象：** 定位差距、價值主張薄弱、受眾框架失調

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.brandstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比臨時人工交接產生更清晰的品牌到腳本翻譯
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.brandstrategist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：BrandAgent 和 CreativeDirectorAgent 的多代理辯論

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.brandstrategist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`BrandAgent, ScreenwriterAgent, MarketingAgent`；comments_on=`Positioning gaps, weak value proposition, misaligned audience framing`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.brandstrategist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.brandstrategist` 成熟度 11.0 且 11 個「是」

### `video.marketing` — MarketingAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 86 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.marketing.v1`／`video.rubric.marketing.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 用於發布、促銷和發布排序的打包內容
- **設計知識來源：** 活動手冊、發布日曆、媒體計畫、資產包裝要求
- **設計自評標準：** 元資料完整性、資產準備狀況、啟動排序準確性
- **設計 surpass 訊號：** 比手動行銷活動更快地發送多管道啟動包
- **設計工具：** 活動管理套件、元資料工具、發布規劃器
- **設計架構：** 對啟動清單和頻道要求做出反應
- **設計接受 critique 來源：** SocialMediaStrategistAgent、SEOAgent、CopywriterAgent、TrailerEditorAgent
- **設計可評論對象：** 格式缺失、推出時機不佳、促銷組合不完整

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.marketing.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比手動行銷活動更快地發送多管道啟動包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.marketing.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：對啟動清單和頻道要求做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.marketing` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SocialMediaStrategistAgent, SEOAgent, CopywriterAgent, TrailerEditorAgent`；comments_on=`Missing formats, weak rollout timing, incomplete promotion sets`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.marketing` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.marketing` 成熟度 11.0 且 11 個「是」

### `video.seo` — SEOAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 87 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.seo.v1`／`video.rubric.seo.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 透過標題、描述、元資料和搜尋意圖優化可發現性
- **設計知識來源：** 搜尋排名研究、影片元資料最佳實踐、關鍵字分類法
- **設計自評標準：** 關鍵字匹配、元資料完整性、搜尋意圖匹配
- **設計 surpass 訊號：** 比手動元資料調整更快提升可發現性
- **設計工具：** 關鍵字工具、元資料 API、排名儀錶板
- **設計架構：** 透過搜尋意圖驗證進行 ReAct
- **設計接受 critique 來源：** 行銷代理、文案代理、分析師代理
- **設計可評論對象：** 關鍵字弱、標題與描述不符、元資料遺漏

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.seo.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比手動元資料調整更快提升可發現性
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.seo.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：透過搜尋意圖驗證進行 ReAct

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.seo` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`MarketingAgent, CopywriterAgent, AnalystAgent`；comments_on=`Weak keywords, poor title-description fit, metadata omissions`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.seo` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.seo` 成熟度 11.0 且 11 個「是」

### `video.community` — CommunityAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 88 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.community.v1`／`video.rubric.community.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 捕捉社區反應並對定性訊號進行分類
- **設計知識來源：** 社區審核手冊、情緒資料集、升級規則
- **設計自評標準：** 反應延遲、問題聚類品質、情緒追蹤準確性
- **設計 surpass 訊號：** 在手動評論審核之前先浮現新出現的受眾擔憂
- **設計工具：** 社交聆聽工具、審核儀錶板、聚類模型
- **設計架構：** 發布後觀眾回饋的反思
- **設計接受 critique 來源：** AnalystAgent、SocialMediaStrategistAgent、CommsAgent
- **設計可評論對象：** 令人困惑的訊息、情緒風險、反覆出現的投訴

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.community.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在手動評論審核之前先浮現新出現的受眾擔憂
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.community.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：發布後觀眾回饋的反思

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.community` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AnalystAgent, SocialMediaStrategistAgent, CommsAgent`；comments_on=`Confusing messaging, sentiment risks, recurring complaints`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.community` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.community` 成熟度 11.0 且 11 個「是」

### `video.templatedesign` — TemplateDesignAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 89 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.templatedesign.v1`／`video.rubric.templatedesign.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 設計可重複使用且安全的個人化模板
- **設計知識來源：** 可變內容設計系統、動態佈局規則、活動範本庫
- **設計自評標準：** 合併字段穩健性、佈局穩定性、渲染生存能力
- **設計 surpass 訊號：** 產生可重複使用的模板，與手動設計變體相比，破損更少
- **設計工具：** 模板引擎、設計系統、模式驗證器
- **設計架構：** 對模板模式和渲染約束做出反應
- **設計接受 critique 來源：** 個人化EngineerAgent、UXAgent、CRMAgent
- **設計可評論對象：** 脆弱的版面、不安全的佔位符邏輯、合併衝突

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.templatedesign.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：產生可重複使用的模板，與手動設計變體相比，破損更少
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.templatedesign.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：對模板模式和渲染約束做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.templatedesign` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`PersonalizationEngineerAgent, UXAgent, CRMAgent`；comments_on=`Fragile layouts, unsafe placeholder logic, merge collisions`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.templatedesign` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.templatedesign` 成熟度 11.0 且 11 個「是」

### `video.ux` — UXAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 90 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.ux.v1`／`video.rubric.ux.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 6 檔 · provenance=True
- **設計責任：** 審查個人化或互動式輸出的清晰度和可用性
- **設計知識來源：** 使用者體驗啟發法、無障礙標準、可用性測試模式
- **設計自評標準：** 可讀性、摩擦點偵測、使用者流程清晰度
- **設計 surpass 訊號：** 在啟動階段支援團隊之前標記使用者困惑
- **設計工具：** 使用者體驗審查清單、會話重播、可讀性工具
- **設計架構：** 法學碩士作為法官與使用者體驗標題
- **設計接受 critique 來源：** TemplateDesignAgent、PersonalizationEngineerAgent、AccessibilityAgent
- **設計可評論對象：** 流程混亂、可讀性問題、互動線索薄弱

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 6 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.ux.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在啟動階段支援團隊之前標記使用者困惑
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.ux.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：法學碩士作為法官與使用者體驗標題

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.ux` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`TemplateDesignAgent, PersonalizationEngineerAgent, AccessibilityAgent`；comments_on=`Confusing flows, readability issues, weak interaction cues`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.ux` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.ux` 成熟度 11.0 且 11 個「是」

### `video.trustsafety` — TrustSafetyAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 91 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.trustsafety.v1`／`video.rubric.trustsafety.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 篩選輸出是否有仿冒、濫用或有害誤用
- **設計知識來源：** 濫用分類語料庫、冒充案例、政策規則手冊
- **設計自評標準：** 策略命中率、濫用風險召回、被阻止案例的低漏報
- **設計 surpass 訊號：** 比通用審核隊列更早發現誤用風險
- **設計工具：** 安全分類器、濫用分類資料庫、審核 API
- **設計架構：** 用於信任和安全政策執行的憲法人工智慧
- **設計接受 critique 來源：** 合規代理、DeepfakeDetectionAgent、SafetyRedTeamAgent
- **設計可評論對象：** 有害的濫用途徑、冒充媒介、政策差距

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.trustsafety.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比通用審核隊列更早發現誤用風險
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.trustsafety.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：用於信任和安全政策執行的憲法人工智慧

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.trustsafety` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent, DeepfakeDetectionAgent, SafetyRedTeamAgent`；comments_on=`Harmful misuse pathways, impersonation vectors, policy gaps`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.trustsafety` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.trustsafety` 成熟度 11.0 且 11 個「是」

### `video.crm` — CRMAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 92 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.crm.v1`／`video.rubric.crm.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 9 檔 · provenance=True
- **設計責任：** 透過 CRM 系統提供針對受眾或基於觸發器的活動
- **設計知識來源：** CRM 自動化流程、生命週期行銷手冊、受眾細分規則
- **設計自評標準：** 受眾羣體正確性、交付準備、觸發準確性
- **設計 surpass 訊號：** 執行分段到交付流程比手動操作更快
- **設計工具：** HubSpot/Salesforce 式 CRM API、細分工具
- **設計架構：** 透過觸發器和受眾模式做出反應
- **設計接受 critique 來源：** 個人化工程師代理、範本設計代理、分析代理
- **設計可評論對象：** 錯誤的分段、中斷的觸發時間、不完整的 CRM 有效負載

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.crm.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：執行分段到交付流程比手動操作更快
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.crm.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：透過觸發器和受眾模式做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.crm` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`PersonalizationEngineerAgent, TemplateDesignAgent, AnalystAgent`；comments_on=`Wrong segmentation, broken trigger timing, incomplete CRM payloads`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.crm` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.crm` 成熟度 11.0 且 11 個「是」

### `video.legal` — LegalAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 93 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.legal.v1`／`video.rubric.legal.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 對新穎或高風險的出版問題進行最終的法律審查
- **設計知識來源：** 媒體法參考、清關工作流程、誹謗/智慧財產權/隱私權案件
- **設計自評標準：** 問題識別召回、簽核完整性、升級質量
- **設計 surpass 訊號：** 減少與分散的法律審查相關的後期法律意外
- **設計工具：** 法律備忘錄系統、權利追蹤器、許可資料庫
- **設計架構：** 人環升級+憲法審查
- **設計接受 critique 來源：** 合規代理（法律）、記者代理、ProducerAgent / EP、MPAAgent
- **設計可評論對象：** 法律風險新、權利不明確、索賠高風險未解決

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.legal.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：減少與分散的法律審查相關的後期法律意外
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.legal.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：人環升級+憲法審查

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.legal` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComplianceAgent (Legal), JournalistAgent, ProducerAgent / EP, MPAAgent`；comments_on=`Novel legal risks, unclear rights, unresolved high-risk claims`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.legal` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.legal` 成熟度 11.0 且 11 個「是」

### `video.festivalstrategist` — FestivalStrategistAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 94 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.festivalstrategist.v1`／`video.rubric.festivalstrategist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 為節日和提交日曆定位項目
- **設計知識來源：** 影展提交指南、頒獎季策略、評選歷史
- **設計自評標準：** 適應節日的強度、包裝準備、時間安排
- **設計 surpass 訊號：** 與通用發布計劃相比，改進了提交目標
- **設計工具：** 節日日曆、提交清單、新聞資料袋追蹤器
- **設計架構：** 透過日曆和套件驗證進行 ReAct
- **設計接受 critique 來源：** ProducerAgent / EP、DirectorAgent、CriticAgent
- **設計可評論對象：** 定位薄弱、提交計畫不及時、包不完整

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.festivalstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與通用發布計劃相比，改進了提交目標
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.festivalstrategist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：透過日曆和套件驗證進行 ReAct

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.festivalstrategist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent / EP, DirectorAgent, CriticAgent`；comments_on=`Weak positioning, mistimed submission plans, incomplete packages`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.festivalstrategist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.festivalstrategist` 成熟度 11.0 且 11 個「是」

### `video.lms` — LMSAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 96 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.lms.v1`／`video.rubric.lms.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 13 檔 · provenance=True
- **設計責任：** 將學習內容打包並部署到 LMS 環境
- **設計知識來源：** SCORM/xAPI 標準、LMS 發布工作流程、完成追蹤模式
- **設計自評標準：** 套件有效性、追蹤完整性、部署成功率
- **設計 surpass 訊號：** 交付可發布的學習包比手動課程操作更快
- **設計工具：** LMS API、SCORM/xAPI 驗證器、課程打包工具
- **設計架構：** ReAct over LMS 部署架構
- **設計接受 critique 來源：** 教學設計代理、輔助功能代理、學習者模擬代理
- **設計可評論對象：** 包合規性、追蹤錯誤、學習目標不匹配

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.lms.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：交付可發布的學習包比手動課程操作更快
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.lms.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct over LMS 部署架構

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.lms` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`InstructionalDesignAgent, AccessibilityAgent, LearnerSimAgent`；comments_on=`Package compliance, tracking errors, learning-objective mismatch`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.lms` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.lms` 成熟度 11.0 且 11 個「是」

### `video.learnersim` — LearnerSimAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 97 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.learnersim.v1`／`video.rubric.learnersim.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 模擬學習者行為、困惑點和評估表現
- **設計知識來源：** 學習者建模資料集、完成分析、測驗結果模式
- **設計自評標準：** 摩擦點預測、完成精確度、模擬測驗真實性
- **設計 surpass 訊號：** 在現場學習者抱怨出現之前預測弱點
- **設計工具：** 學習者模擬模型、評估預測器、LMS 數據
- **設計架構：** 適合學習成果的觀眾模擬
- **設計接受 critique 來源：** 教學設計代理、LMSA代理、分析代理
- **設計可評論對象：** 內容混亂、評估薄弱、完成度低

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.learnersim.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在現場學習者抱怨出現之前預測弱點
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.learnersim.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：適合學習成果的觀眾模擬

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.learnersim` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`InstructionalDesignAgent, LMSAgent, AnalystAgent`；comments_on=`Confusing content, weak assessments, low-completion pathways`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.learnersim` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.learnersim` 成熟度 11.0 且 11 個「是」

### `video.continuity` — ContinuityAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 98 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.continuity.v1`／`video.rubric.continuity.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 保持角色、道具、服裝、環境和時間狀態的連續性
- **設計知識來源：** 連續性日誌、腳本主管實務、資產清單狀態跟蹤
- **設計自評標準：** 狀態漂移偵測、場景間一致性、明顯更新正確性
- **設計 surpass 訊號：** 在事後審查結束之前發現連續性中斷
- **設計工具：** 狀態清單、鏡頭比較工具、連續性資料庫
- **設計架構：** 工具使用/ReAct 與連續性清單執行
- **設計接受 critique 來源：** CostumeDesignAgent、MUAAgent、AIQAConsistencyAgent、CinematographerAgent (DoP)、GateKeeperAgent
- **設計可評論對象：** 角色狀態漂移、服裝與道具不符、時間邏輯錯誤

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.continuity.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：在事後審查結束之前發現連續性中斷
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.continuity.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用/ReAct 與連續性清單執行

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.continuity` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`CostumeDesignAgent, MUAAgent, AIQAConsistencyAgent, CinematographerAgent (DoP), GateKeeperAgent`；comments_on=`Character-state drift, wardrobe and prop mismatch, time logic errors`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.continuity` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.continuity` 成熟度 11.0 且 11 個「是」

### `video.lipsync` — LipSyncAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 99 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.lipsync.v1`／`video.rubric.lipsync.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 驗證和細化音素-視位對齊作為專用門
- **設計知識來源：** 口型同步研究、動畫計時參考、視位資料集
- **設計自評標準：** 同步誤差低於閾值、校正特異性、低誤報
- **設計 surpass 訊號：** 比一般 QC 審查更精確地發現同步漂移
- **設計工具：** 音位-視位對齊器、幀級同步工具
- **設計架構：** 圍繞同步驗證器輸出進行自我最佳化
- **設計接受 critique 來源：** VoiceCloneAgent / LipSyncSpecialist、AnimatorAgent、AIQAConsistencyAgent
- **設計可評論對象：** 口型不匹配、對話幀漂移、校正優先級

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.lipsync.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比一般 QC 審查更精確地發現同步漂移
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.lipsync.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：圍繞同步驗證器輸出進行自我最佳化

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.lipsync` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`VoiceCloneAgent / LipSyncSpecialist, AnimatorAgent, AIQAConsistencyAgent`；comments_on=`Mouth-shape mismatch, frame drift in dialogue, correction priority`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.lipsync` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.lipsync` 成熟度 11.0 且 11 個「是」

### `video.musicsupervisor` — MusicSupervisorAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 100 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.musicsupervisor.v1`／`video.rubric.musicsupervisor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 管理音樂配合、提示使用、權利意識和音軌包裝
- **設計知識來源：** 音樂監督筆記、提示放置參考、配樂發行練習
- **設計自評標準：** 提示的適用性、權利意識覆蓋範圍、原聲帶包的完整性
- **設計 surpass 訊號：** 比分散的交接更一致地協調音樂位置
- **設計工具：** 音樂資產追蹤器、提示表、音軌包工具
- **設計架構：** 對提示表和權限要求做出反應
- **設計接受 critique 來源：** ComposerAgent、TrailerEditorAgent、LabelA&RAgent、LegalAgent
- **設計可評論對象：** 提示濫用、音樂版權模糊、配樂銜接問題

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.musicsupervisor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比分散的交接更一致地協調音樂位置
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.musicsupervisor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：對提示表和權限要求做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.musicsupervisor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ComposerAgent, TrailerEditorAgent, LabelA&RAgent, LegalAgent`；comments_on=`Cue misuse, music-rights ambiguity, soundtrack cohesion issues`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.musicsupervisor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.musicsupervisor` 成熟度 11.0 且 11 個「是」

### `video.labela_r` — LabelA&RAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 101 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.labela_r.v1`／`video.rubric.labela_r.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 代表音樂特定工作流程的唱片公司與藝人方向
- **設計知識來源：** A&R 手冊、唱片公司發行說明、藝人簡介檔案
- **設計自評標準：** 適合藝術家的品質、發布定位、回饋週轉
- **設計 surpass 訊號：** 比分散的利害關係人線索更快協調音樂創意
- **設計工具：** 曲目系統、發行追蹤器、藝人簡介工具
- **設計架構：** 與音樂利害關係人的多主體辯論
- **設計接受 critique 來源：** MusicVideoDirectorAgent、MusicSupervisorAgent、LabelDigitalAgent
- **設計可評論對象：** 藝術家方向漂移、發行不匹配、包裝缺陷

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.labela_r.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比分散的利害關係人線索更快協調音樂創意
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.labela_r.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：與音樂利害關係人的多主體辯論

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.labela_r` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`MusicVideoDirectorAgent, MusicSupervisorAgent, LabelDigitalAgent`；comments_on=`Artist-direction drift, release mismatch, packaging weakness`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.labela_r` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.labela_r` 成熟度 11.0 且 11 個「是」

### `video.labeldigital` — LabelDigitalAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 102 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.labeldigital.v1`／`video.rubric.labeldigital.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 運行標籤端數位推廣、元數據和通路打包
- **設計知識來源：** 數位音樂發行操作、元資料模式、發行平臺要求
- **設計自評標準：** 元資料完整性、推出時間、通路準備狀況
- **設計 surpass 訊號：** 提供比臨時發布操作更乾淨的標籤端包
- **設計工具：** 數位發布系統、頻道儀錶板、元資料工具
- **設計架構：** 根據發布包要求做出反應
- **設計接受 critique 來源：** 音樂錄影帶導演代理、社羣媒體策略代理、行銷代理
- **設計可評論對象：** 元資料缺失、發佈時間問題、資產版本混亂

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.labeldigital.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：提供比臨時發布操作更乾淨的標籤端包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.labeldigital.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：根據發布包要求做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.labeldigital` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`MusicVideoDirectorAgent, SocialMediaStrategistAgent, MarketingAgent`；comments_on=`Missing metadata, release timing issues, asset-version confusion`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.labeldigital` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.labeldigital` 成熟度 11.0 且 11 個「是」

### `video.deepfakedetection` — DeepfakeDetectionAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 103 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.deepfakedetection.v1`／`video.rubric.deepfakedetection.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 檢測合成身份、聲音和來源欺騙風險
- **設計知識來源：** Deepfake 取證語料庫、合成媒體基準、身分風險研究
- **設計自評標準：** 法醫召回、假陰性控制、來源驗證準確性
- **設計 surpass 訊號：** 捕捉一般 QC 遺漏的欺騙性合成標記
- **設計工具：** 取證模型、臉部/語音異常偵測器、來源驗證器
- **設計架構：** 工具使用/ReAct 與取證評分
- **設計接受 critique 來源：** AvatarDesignAgent、VoiceCloneAgent、TrustSafetyAgent、SafetyRedTeamAgent
- **設計可評論對象：** 身分異常、來源漏洞、欺騙性合成模式

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.deepfakedetection.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：捕捉一般 QC 遺漏的欺騙性合成標記
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.deepfakedetection.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用/ReAct 與取證評分

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.deepfakedetection` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`AvatarDesignAgent, VoiceCloneAgent, TrustSafetyAgent, SafetyRedTeamAgent`；comments_on=`Identity anomalies, provenance holes, deceptive synthesis patterns`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.deepfakedetection` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.deepfakedetection` 成熟度 11.0 且 11 個「是」

### `video.comms` — CommsAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 104 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.comms.v1`／`video.rubric.comms.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 協調外部訊息傳遞、揭露和公眾回應態勢
- **設計知識來源：** 危機溝通指南、揭露標準、公關手冊
- **設計自評標準：** 訊息一致性、揭露完整性、升級品質
- **設計 surpass 訊號：** 比分散的利害關係人訊息傳遞產生更快的一致回應
- **設計工具：** 通訊行事曆、審核工作流程、回應模板
- **設計架構：** 使用審批鏈做出反應
- **設計接受 critique 來源：** 行銷代理、社羣代理、法律代理、品牌代理
- **設計可評論對象：** 揭露差距、外部訊息不一致、回應框架薄弱

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.comms.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比分散的利害關係人訊息傳遞產生更快的一致回應
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.comms.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：使用審批鏈做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.comms` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`MarketingAgent, CommunityAgent, LegalAgent, BrandAgent`；comments_on=`Disclosure gaps, inconsistent external messaging, weak response framing`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.comms` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.comms` 成熟度 11.0 且 11 個「是」

### `video.standardseditor` — StandardsEditorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 106 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.standardseditor.v1`／`video.rubric.standardseditor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 執行編輯標準、採購紀律和糾正政策
- **設計知識來源：** 新聞編輯室標準手冊、修正政策、歸屬標準
- **設計自評標準：** 標準符合率、歸因準確度、修正準備度
- **設計 surpass 訊號：** 比後期複製編輯更好地減少標準漂移
- **設計工具：** 編輯清單、歸屬驗證器、標準資料庫
- **設計架構：** 憲法人工智慧與編輯標準憲法
- **設計接受 critique 來源：** 記者代理、事實檢驗代理、糾正代理、法律代理
- **設計可評論對象：** 歸因薄弱、違反標準、糾正政策差距

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.standardseditor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比後期複製編輯更好地減少標準漂移
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.standardseditor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：憲法人工智慧與編輯標準憲法

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.standardseditor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`JournalistAgent, FactCheckerAgent, CorrectionsAgent, LegalAgent`；comments_on=`Weak attribution, standards violations, correction policy gaps`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.standardseditor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.standardseditor` 成熟度 11.0 且 11 個「是」

### `video.ethics` — EthicsAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 107 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.ethics.v1`／`video.rubric.ethics.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 10 檔 · provenance=True
- **設計責任：** 審查道德風險、揭露充分性、公平性和社會影響
- **設計知識來源：** 道德框架、合成媒體揭露指南、公平審計
- **設計自評標準：** 道德問題召回、緩解清晰度、升級精準度
- **設計 surpass 訊號：** Surface 比反應性倫理審查更早釋放風險
- **設計工具：** 道德審查範本、風險矩陣、揭露清單
- **設計架構：** 多主體辯論+違憲審查
- **設計接受 critique 來源：** StandardsEditorAgent、ComplianceAgent（法律）、TrustSafetyAgent、SafetyRedTeamAgent
- **設計可評論對象：** 揭露不充分、公平性擔憂、敏感內容風險

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.ethics.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：Surface 比反應性倫理審查更早釋放風險
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.ethics.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：多主體辯論+違憲審查

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.ethics` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`StandardsEditorAgent, ComplianceAgent (Legal), TrustSafetyAgent, SafetyRedTeamAgent`；comments_on=`Disclosure insufficiency, fairness concerns, sensitive-content risk`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.ethics` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.ethics` 成熟度 11.0 且 11 個「是」

### `video.channelmanager` — ChannelManagerAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 108 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.channelmanager.v1`／`video.rubric.channelmanager.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 管理片段或平臺頻道操作以確保節奏和元資料準備情況
- **設計知識來源：** 通路發布手冊、元資料標準、調度操作
- **設計自評標準：** 發布準備、節奏穩定性、元資料完整性
- **設計 surpass 訊號：** 改進手動渠道操作的發布紀律
- **設計工具：** CMS/頻道儀錶板、排程器工具、元資料驗證器
- **設計架構：** ReAct 發布操作手冊
- **設計接受 critique 來源：** 社羣媒體策略代理、SEOAgent、分析師代理、行銷代理
- **設計可評論對象：** 發布準備差距、元資料遺漏、進度延誤

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.channelmanager.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：改進手動渠道操作的發布紀律
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.channelmanager.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct 發布操作手冊

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.channelmanager` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SocialMediaStrategistAgent, SEOAgent, AnalystAgent, MarketingAgent`；comments_on=`Release readiness gaps, metadata omissions, schedule slippage`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.channelmanager` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.channelmanager` 成熟度 11.0 且 11 個「是」

### `video.corrections` — CorrectionsAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 109 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.corrections.v1`／`video.rubric.corrections.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 11 檔 · provenance=True
- **設計責任：** 協調出版後修復和更正披露
- **設計知識來源：** 更正工作流程、撤回和更新政策、版本跟蹤
- **設計自評標準：** 修正週轉、版本替換準確性、通知完整性
- **設計 surpass 訊號：** 比非結構化事件處理更快解決發布後問題
- **設計工具：** 版本控制系統、發布工具、校正追蹤器
- **設計架構：** ReAct 修正與取代工作流程
- **設計接受 critique 來源：** StandardsEditorAgent、FactCheckerAgent、ChannelManagerAgent
- **設計可評論對象：** 未封閉的更正循環、不完整的通知、過時的版本

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.corrections.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比非結構化事件處理更快解決發布後問題
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.corrections.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct 修正與取代工作流程

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.corrections` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`StandardsEditorAgent, FactCheckerAgent, ChannelManagerAgent`；comments_on=`Unclosed correction loops, incomplete notices, stale versions`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.corrections` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.corrections` 成熟度 11.0 且 11 個「是」

### `video.mpa` — MPAAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 110 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.mpa.v1`／`video.rubric.mpa.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 30 檔 · provenance=True
- **設計責任：** 為功能工作流程準備與評級相關的打包和發布準備輸入
- **設計知識來源：** 評等提交參考、內容建議、戲院包裝規則
- **設計自評標準：** 評級包完整性、諮詢清晰度、升級質量
- **設計 surpass 訊號：** 準備比手動準備更乾淨的功能發布分類包
- **設計工具：** 提交包裹、諮詢範本、分類清單
- **設計架構：** 具有結構化包裝支援的人機交互
- **設計接受 critique 來源：** ProducerAgent / EP、法律代理、道德代理
- **設計可評論對象：** 缺少建議、評級準備不完整、分類支援不明確

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.mpa.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：準備比手動準備更乾淨的功能發布分類包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.mpa.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：具有結構化包裝支援的人機交互

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.mpa` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent / EP, LegalAgent, EthicsAgent`；comments_on=`Missing advisories, incomplete rating prep, unclear classification support`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.mpa` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.mpa` 成熟度 11.0 且 11 個「是」

### `video.sales` — SalesAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 111 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.sales.v1`／`video.rubric.sales.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 8 檔 · provenance=True
- **設計責任：** 為分銷商和商店處理面向買家的銷售包裝
- **設計知識來源：** 權利窗口手冊、市場包範例、買家材料
- **設計自評標準：** 買方包裝完整性、權利明確性、適合市場的包裝
- **設計 surpass 訊號：** 比手動組裝更快生產可銷售的發布包
- **設計工具：** 權利系統、軟體包建構者、買家 CRM
- **設計架構：** 對買家套餐要求做出反應
- **設計接受 critique 來源：** 製片代理/EP、發行人代理、行銷代理
- **設計可評論對象：** 買家資訊缺失、定位薄弱、權利摘要不完整

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.sales.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：比手動組裝更快生產可銷售的發布包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.sales.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：對買家套餐要求做出反應

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.sales` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent / EP, DistributorAgent, MarketingAgent`；comments_on=`Missing buyer info, weak positioning, incomplete rights summaries`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.sales` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.sales` 成熟度 11.0 且 11 個「是」

### `video.distributor` — DistributorAgent （現況 6.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 112 · **優先帶：** P6
- **現況儲存格：** 是=3 部分=7 否=1
- **Prompt／Rubric 參照：** `video.prompt.distributor.v1`／`video.rubric.distributor.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 12 檔 · provenance=True
- **設計責任：** 管理向買家、平臺和地區的下游交付
- **設計知識來源：** 分銷規格、出口要求、包裹交接工作流程
- **設計自評標準：** 插座規格合規性、切換完整性、區域路由準確性
- **設計 surpass 訊號：** 減少相對於分散交付操作的交付規範不匹配
- **設計工具：** 交付管理系統、出口規格資料庫、包裝驗證器
- **設計架構：** 分佈規範矩陣上的 ReAct
- **設計接受 critique 來源：** SalesAgent、ArchiveMasterAgent、SoundMixerAgent、ColoristAgent
- **設計可評論對象：** 規格不符、出口包裝不完整、路線錯誤

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.distributor.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：減少相對於分散交付操作的交付規範不匹配
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.distributor.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：分佈規範矩陣上的 ReAct

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.distributor` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`SalesAgent, ArchiveMasterAgent, SoundMixerAgent, ColoristAgent`；comments_on=`Spec mismatches, incomplete outlet packages, routing errors`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.distributor` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.distributor` 成熟度 11.0 且 11 個「是」

### `video.awardsstrategist` — AwardsStrategistAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 113 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.awardsstrategist.v1`／`video.rubric.awardsstrategist.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 6 檔 · provenance=True
- **設計責任：** 計劃獎項提交和活動時間表
- **設計知識來源：** 獎項日曆、活動手冊、類別定位歷史
- **設計自評標準：** 提交準備情況、類別適合度、時間軸精度
- **設計 surpass 訊號：** 改進通用發布計畫的獎勵時間規則
- **設計工具：** 獎項日曆、活動追蹤器、提交清單
- **設計架構：** ReAct 優化獎勵時間表
- **設計接受 critique 來源：** ProducerAgent / EP、CriticAgent、MarketingAgent
- **設計可評論對象：** 活動時機不佳、類別契合度差、提交資產不完整

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 6 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.awardsstrategist.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：改進通用發布計畫的獎勵時間規則
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.awardsstrategist.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：ReAct 優化獎勵時間表

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.awardsstrategist` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`ProducerAgent / EP, CriticAgent, MarketingAgent`；comments_on=`Weak campaign timing, poor category fit, incomplete submission assets`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.awardsstrategist` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.awardsstrategist` 成熟度 11.0 且 11 個「是」

### `video.archivemaster` — ArchiveMasterAgent （現況 6.0/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 114 · **優先帶：** P6
- **現況儲存格：** 是=2 部分=8 否=1
- **Prompt／Rubric 參照：** `video.prompt.archivemaster.v1`／`video.rubric.archivemaster.v1`
- **現有工具：** `（無）` · live_media=False
- **現有來源：** 7 檔 · provenance=True
- **設計責任：** 製作檔案級母帶和保存包
- **設計知識來源：** 保存標準、校驗和工作流程、存檔元資料實踐
- **設計自評標準：** 校驗和完整性、保存元資料完整性、歸檔包有效性
- **設計 surpass 訊號：** 與後期僅匯出工作流程相比，提供更可靠的存檔包
- **設計工具：** 歸檔管理工具、校驗和實用程式、保存元資料系統
- **設計架構：** 工具使用/帶有保存驗證的 ReAct
- **設計接受 critique 來源：** DistributorAgent、ColoristAgent、SoundMixerAgent、GateKeeperAgent
- **設計可評論對象：** 不完整的保存包、存檔規範違規、元資料差距

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **部分** | **是** |
| Q4 自評方法與內容 | **部分** | **是** |
| Q5 超越人類（可量測） | **否** | **是** |
| Q6 工作執行路徑 | **部分** | **是** |
| Q7 Skills／plugins／harness | **部分** | **是** |
| Q8 自我改進機制 | **部分** | **是** |
| Q9 研究以改進 | **部分** | **是** |
| Q10 協作／指令收發 | **部分** | **是** |
| Q11 衝突解決與確認 | **部分** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯跑唯一性 CI。
- [ ] 若缺 does_not_own 清單則補上；user_guide.md 保持同步。
- [ ] 確認 runtime prompt 注入包含責任區塊。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。
- [ ] 建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。
- [ ] 將計畫登錄至 pack corpus index（含 next_review_at）。
- [ ] 計畫輸出連結至 MemoryAgent／RAG namespace id。
- [ ] 自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。

**Q3 來源可用／可取得**（現況 部分 → 是）

- [ ] 將包裝來源由 7 提升至 ≥8 份實質檔（摘錄＋目錄）。
- [ ] 將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。
- [ ] 每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。
- [ ] 每來源類別至少一份可用摘錄或合成授權 fixture。
- [ ] 更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。
- [ ] 在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。

**Q4 自評方法與內容**（現況 部分 → 是）

- [ ] 為 `video.rubric.archivemaster.v1` 撰寫 rubrics 內容（目前 files=0）。
- [ ] 依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。
- [ ] 定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。
- [ ] 定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。
- [ ] 在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。
- [ ] Host eval harness 載入 rubric_reference；缺檔 fail-closed。

**Q5 超越人類（可量測）**（現況 否 → 是）

- [ ] 為 surpass 訊號登錄量測協定：與後期僅匯出工作流程相比，提供更可靠的存檔包
- [ ] 將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。
- [ ] 在相同 golden task 上收集人類基線（N 次、凍結輸入）。
- [ ] 以鎖定之模型／工具版本跑 agent；保存 evidence bundle。
- [ ] 計算 delta；僅在預先登錄協定下達標纔可標「是」。
- [ ] 於 SPEC `## Human Baseline Results` 公佈報告路徑（或標為僅目標）。

**Q6 工作執行路徑**（現況 部分 → 是）

- [ ] 為 `video.prompt.archivemaster.v1` 撰寫 prompts 內容（目前 files=0）。
- [ ] 以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。
- [ ] 落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。
- [ ] 實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。
- [ ] 將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。
- [ ] 至少登錄一個 workflow DNA／graph（含 I／O 契約）。
- [ ] 整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。
- [ ] 實作架構模式：工具使用/帶有保存驗證的 ReAct

**Q7 Skills／plugins／harness**（現況 部分 → 是）

- [ ] 為 `video.archivemaster` 建立 per-agent skills harness 目錄。
- [ ] 建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。
- [ ] 經 skills/bindings.json 綁定所需 pack special_skills（若有）。
- [ ] 宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。
- [ ] 能力登錄項列出 skills hash＋版本。
- [ ] 煙霧測試：除非 production flags，host 無網路亦可載入 skill。

**Q8 自我改進機制**（現況 部分 → 是）

- [ ] 保留 max_refinement_count 並於 SPEC 記錄政策。
- [ ] Host 以 prompt_reference＋critique 輸入實作 refine 迴路。
- [ ] 改進候選持久化於 evidence/（含前後分數）。
- [ ] 晉升閘門：L2 分數提升且無 L1 迴歸。
- [ ] 排程定期改進工作（或操作者觸發）並寫 audit log。

**Q9 研究以改進**（現況 部分 → 是）

- [ ] 定義 research request schema（主題、來源類、上限成本、期限）。
- [ ] 協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。
- [ ] 研究輸出存於 sources/research/（含 provenance）。
- [ ] 對應 research → 蒸餾計畫更新 → golden eval 刷新。
- [ ] 新增可用 fixture 語料之離線 dry-run 研究路徑。

**Q10 協作／指令收發**（現況 部分 → 是）

- [ ] 編碼 accepts_from=`DistributorAgent, ColoristAgent, SoundMixerAgent, GateKeeperAgent`；comments_on=`Incomplete preservation bundles, archive-spec violations, metadata gaps`。
- [ ] 依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。
- [ ] 實作 CritiqueMessage＋InstructionMessage host APIs。
- [ ] 整合測試證明此 agent 至少一條 send 與一條 receive。
- [ ] 於 SPEC `## Collaboration Matrix` 記錄協作夥伴。
- [ ] Orchestrator／router 可以 id＋correlation 識別符定址 agent。

**Q11 衝突解決與確認**（現況 部分 → 是）

- [ ] 定義衝突政策：blocker／major／minor 與自動解決規則。
- [ ] 爭議接至 video.judge（或角色 judge）多代理辯論。
- [ ] 未決 blocker 需 HiTL 確認；記錄決策 evidence。
- [ ] 整合測試：注入衝突 critique，斷言解決或升級路徑。
- [ ] 在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。

#### 此 agent 出場閘門

- [ ] `video.archivemaster` 離線 golden run 通過 L1＋L2 門檻
- [ ] 協作 send／receive 測試全綠
- [ ] 衝突解決或 HiTL 升級測試全綠
- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）
- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass
- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `video.archivemaster` 成熟度 11.0 且 11 個「是」

---

## 7. Agent 實作優先序（佇列）

由上而下。主幹解鎖其餘。

| 序 | 帶 | Agent | 現況 | 為何優先 |
|---:|----|-------|------|----------|
| 1 | P0 | `video.orchestrator` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 2 | P0 | `video.planner` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 3 | P0 | `video.router` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 4 | P0 | `video.judge` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 5 | P0 | `video.gatekeeper` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 6 | P0 | `video.memory` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 7 | P0 | `video.critic` | 6.5 | 平臺主幹 — 編排、規劃、路由、裁決 |
| 8 | P1 | `video.ideation` | 6.5 | Meta 平臺能力 |
| 9 | P1 | `video.narrativearc` | 6.5 | Meta 平臺能力 |
| 10 | P1 | `video.styletransfer` | 6.5 | Meta 平臺能力 |
| 11 | P1 | `video.worldbuilding` | 6.5 | Meta 平臺能力 |
| 12 | P1 | `video.moodboard` | 6.5 | Meta 平臺能力 |
| 13 | P1 | `video.novelty` | 6.5 | Meta 平臺能力 |
| 14 | P1 | `video.emotionalarc` | 6.5 | Meta 平臺能力 |
| 15 | P1 | `video.webresearch` | 6.5 | Meta 平臺能力 |
| 16 | P1 | `video.archiveresearch` | 6.5 | Meta 平臺能力 |
| 17 | P1 | `video.trendintelligence` | 6.5 | Meta 平臺能力 |
| 18 | P1 | `video.competitorintelligence` | 6.5 | Meta 平臺能力 |
| 19 | P1 | `video.citation` | 6.5 | Meta 平臺能力 |
| 20 | P1 | `video.interviewsynthesis` | 6.5 | Meta 平臺能力 |
| 21 | P1 | `video.benchmarkresearch` | 6.5 | Meta 平臺能力 |
| 22 | P1 | `video.promptoptimizer` | 6.5 | Meta 平臺能力 |
| 23 | P1 | `video.costoptimizer` | 6.5 | Meta 平臺能力 |
| 24 | P1 | `video.latencyoptimizer` | 6.5 | Meta 平臺能力 |
| 25 | P1 | `video.retentionoptimizer` | 6.5 | Meta 平臺能力 |
| 26 | P1 | `video.roasoptimizer` | 6.5 | Meta 平臺能力 |
| 27 | P1 | `video.accessibilityoptimizer` | 6.5 | Meta 平臺能力 |
| 28 | P1 | `video.evaluationharness` | 6.5 | Meta 平臺能力 |
| 29 | P1 | `video.safetyredteam` | 6.5 | Meta 平臺能力 |
| 30 | P2 | `video.director` | 6.5 | Above-the-line 創作權威 |
| 31 | P2 | `video.producer` | 6.5 | Above-the-line 創作權威 |
| 32 | P2 | `video.screenwriter` | 6.5 | Above-the-line 創作權威 |
| 33 | P2 | `video.showrunner` | 6.5 | Above-the-line 創作權威 |
| 34 | P2 | `video.casting` | 6.5 | Above-the-line 創作權威 |
| 35 | P3 | `video.editor` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 36 | P3 | `video.animator_2d` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 37 | P3 | `video.motiongraphics` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 38 | P3 | `video.sounddesign` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 39 | P3 | `video.voiceover` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 40 | P3 | `video.creativedirector` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 41 | P3 | `video.audiobooknarrator` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 42 | P3 | `video.promptengineer` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 43 | P3 | `video.voiceclone` | 6.5 | 已有 live 媒體工具 — 補齊 harness／evals |
| 44 | P3 | `video.archiveproducer` | 6.0 | 已有 live 媒體工具 — 補齊 harness／evals |
| 45 | P4 | `video.cinematographer` | 6.5 | 核心工藝製作路徑 |
| 46 | P4 | `video.cameraoperator` | 6.5 | 核心工藝製作路徑 |
| 47 | P4 | `video.dronepilot` | 6.5 | 核心工藝製作路徑 |
| 48 | P4 | `video.colorist` | 6.5 | 核心工藝製作路徑 |
| 49 | P4 | `video.vfxsupervisor` | 6.5 | 核心工藝製作路徑 |
| 50 | P4 | `video.storyboard` | 6.5 | 核心工藝製作路徑 |
| 51 | P4 | `video.conceptartist` | 6.5 | 核心工藝製作路徑 |
| 52 | P4 | `video.productiondesign` | 6.5 | 核心工藝製作路徑 |
| 53 | P4 | `video.costumedesign` | 6.5 | 核心工藝製作路徑 |
| 54 | P4 | `video.mua_makeup` | 6.5 | 核心工藝製作路徑 |
| 55 | P4 | `video.composer` | 6.5 | 核心工藝製作路徑 |
| 56 | P4 | `video.soundmixer` | 6.5 | 核心工藝製作路徑 |
| 57 | P5 | `video.choreography` | 6.5 | 專門工藝／AI 時代 |
| 58 | P5 | `video.musicvideodirector` | 6.0 | 專門工藝／AI 時代 |
| 59 | P5 | `video.comedywriter` | 6.5 | 專門工藝／AI 時代 |
| 60 | P5 | `video.talent` | 6.5 | 專門工藝／AI 時代 |
| 61 | P5 | `video.ugccreator` | 6.0 | 專門工藝／AI 時代 |
| 62 | P5 | `video.socialmediastrategist` | 6.5 | 專門工藝／AI 時代 |
| 63 | P5 | `video.copywriter` | 6.5 | 專門工藝／AI 時代 |
| 64 | P5 | `video.performancemarketer` | 6.5 | 專門工藝／AI 時代 |
| 65 | P5 | `video.avatardesign` | 6.5 | 專門工藝／AI 時代 |
| 66 | P5 | `video.aiqaconsistency` | 6.5 | 專門工藝／AI 時代 |
| 67 | P5 | `video.personalizationengineer` | 6.5 | 專門工藝／AI 時代 |
| 68 | P5 | `video.trailereditor` | 6.5 | 專門工藝／AI 時代 |
| 69 | P5 | `video.sportsanalyst` | 6.5 | 專門工藝／AI 時代 |
| 70 | P6 | `video.instructionaldesign` | 6.5 | 支援與長尾 |
| 71 | P6 | `video.sme` | 6.5 | 支援與長尾 |
| 72 | P6 | `video.factchecker` | 6.5 | 支援與長尾 |
| 73 | P6 | `video.medicalillustrator` | 6.5 | 支援與長尾 |
| 74 | P6 | `video.journalist` | 6.5 | 支援與長尾 |
| 75 | P6 | `video.compliance` | 6.5 | 支援與長尾 |
| 76 | P6 | `video.finance` | 6.5 | 支援與長尾 |
| 77 | P6 | `video.foodstylist` | 6.5 | 支援與長尾 |
| 78 | P6 | `video.travelcine` | 6.5 | 支援與長尾 |
| 79 | P6 | `video.childrensauthor` | 6.5 | 支援與長尾 |
| 80 | P6 | `video.signlanguageinterpreter` | 6.5 | 支援與長尾 |
| 81 | P6 | `video.localizationqa` | 6.5 | 支援與長尾 |
| 82 | P6 | `video.realestatephoto` | 6.0 | 支援與長尾 |
| 83 | P6 | `video.analyst` | 6.5 | 支援與長尾 |
| 84 | P6 | `video.audiencesim` | 6.5 | 支援與長尾 |
| 85 | P6 | `video.accessibility` | 6.5 | 支援與長尾 |
| 86 | P6 | `video.brand` | 6.5 | 支援與長尾 |
| 87 | P6 | `video.brandstrategist` | 6.5 | 支援與長尾 |
| 88 | P6 | `video.marketing` | 6.5 | 支援與長尾 |
| 89 | P6 | `video.seo` | 6.5 | 支援與長尾 |
| 90 | P6 | `video.community` | 6.5 | 支援與長尾 |
| 91 | P6 | `video.templatedesign` | 6.5 | 支援與長尾 |
| 92 | P6 | `video.ux` | 6.0 | 支援與長尾 |
| 93 | P6 | `video.trustsafety` | 6.5 | 支援與長尾 |
| 94 | P6 | `video.crm` | 6.5 | 支援與長尾 |
| 95 | P6 | `video.legal` | 6.5 | 支援與長尾 |
| 96 | P6 | `video.festivalstrategist` | 6.0 | 支援與長尾 |
| 97 | P6 | `video.lms` | 6.5 | 支援與長尾 |
| 98 | P6 | `video.learnersim` | 6.5 | 支援與長尾 |
| 99 | P6 | `video.continuity` | 6.5 | 支援與長尾 |
| 100 | P6 | `video.lipsync` | 6.5 | 支援與長尾 |
| 101 | P6 | `video.musicsupervisor` | 6.0 | 支援與長尾 |
| 102 | P6 | `video.labela_r` | 6.0 | 支援與長尾 |
| 103 | P6 | `video.labeldigital` | 6.0 | 支援與長尾 |
| 104 | P6 | `video.deepfakedetection` | 6.5 | 支援與長尾 |
| 105 | P6 | `video.comms` | 6.5 | 支援與長尾 |
| 106 | P6 | `video.standardseditor` | 6.5 | 支援與長尾 |
| 107 | P6 | `video.ethics` | 6.5 | 支援與長尾 |
| 108 | P6 | `video.channelmanager` | 6.0 | 支援與長尾 |
| 109 | P6 | `video.corrections` | 6.5 | 支援與長尾 |
| 110 | P6 | `video.mpa` | 6.5 | 支援與長尾 |
| 111 | P6 | `video.sales` | 6.5 | 支援與長尾 |
| 112 | P6 | `video.distributor` | 6.5 | 支援與長尾 |
| 113 | P6 | `video.awardsstrategist` | 6.0 | 支援與長尾 |
| 114 | P6 | `video.archivemaster` | 6.0 | 支援與長尾 |

---

## 8. 估算模型（規劃用）

| 工作項 | 單位 | 數量 | 備註 |
|--------|------|-----:|------|
| Prompt 檔 | agent | 114 | 工廠＋人工工藝審閱 |
| Rubric 檔 | agent | 114 | 工廠＋工藝 owner 簽核 |
| 來源目錄＋取得計畫 | agent | 114 | 法務可能序列化 |
| Skills harness | agent | 114 | 薄封裝可接受 |
| Golden eval | agent | 114 | 先用 fixtures |
| Mock tool adapters | 工具類 | ~30–50 | 跨 agents 共享 |
| 協作邊測試 | agent | 114 | 由矩陣產生 |
| 人類基線 | agent | 114 | 成本高；按組批次 |
| Surpass 量測 | agent | 114 | 基線之後 |

**Q5 實務分期：** 不要讓 surpass 卡住 Phase 1–4。及早立案基線協定；執行路徑可用後再做人體評估。滿分仍要求 Q5「是」— 請為人類評估排程，或將「是」定義為「量測協定完成且達標」（絕無資料不得宣稱）。

---

## 9. 治理閘門（防止假滿分）

1. **無路徑不可「是」：** 稽覈腳本須檢查檔案存在＋測試名稱，而非只看 SPEC 關鍵字（升級 auditor）。
2. **無 evidence hash 不得在 UI 顯示 surpass。**
3. **工具 fail-closed：** 缺 adapter ⇒ mock 或錯誤，永不靜默成功。
4. **HiTL 確認僅用 action refs**（product façade 紀律）。
5. **PR 清單** 須含受影響 agents 的 capability audit 差分。

---

## 10. 重新產生

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v1.py
python scripts/business/render_agent_capability_status_v1_hk.py
python scripts/business/render_agent_improvement_plan_v1.py
python scripts/business/render_agent_improvement_plan_v1_hk.py
```

以重跑稽覈追蹤進度：成熟度平均應由 **6.45** 朝 **11.0** 上升。

本繁中版結構與行動清單為繁體中文撰寫；`agents.md` 設計原文欄位經 en→zh-TW 機器翻譯，並以 OpenCC s2t 正規化。

