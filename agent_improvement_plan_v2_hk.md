# Agent 改進計畫 v2 — 邁向滿分（11/11 是）

**產生時間：** 2026-07-30T14:45:36Z  
**依據：** `agent_capability_status_v2.md`＋`business/video/AGENT_CAPABILITY_AUDIT.json`  
**前一版計畫：** `agent_improvement_plan_v1.md`／`agent_improvement_plan_v1_hk.md`／`agent_improvement_plan_v2.md`  
**設計權威：** `va-agent-swarm/study/agents.md`  
**範圍：** 114 個非 specials 的 video pack agents  
**目標：** 每個 agent 達到 **滿分** = 十一項問題皆為「是」（成熟度 **11.0/11**）。

> **v2 論點：** v1 的可自動化 Wave A–D **已完成**。剩餘滿分工作幾乎全是 **Q5 可量測人類基線**（真實評分者，非 synthetic），外加對已綠項目的維護／強化。

---

## 0. 相對滿分的計分板（完成度 %）

| 指標 | 現況 | 滿分目標 |
|------|----:|-----------------:|
| 平均成熟度 0–11 | **10.5** | **11.0** |
| **加權儲存格完成度** | **95.45%** | **100%** |
| 嚴格僅「是」 | **90.91%** | **100%** |
| 是／部分／否 | 1140／114／0 | 1254／0／0 |
| 計畫綜合完成度（追蹤器） | **95.71%** | **100%** |
| 可自動化（除 Q5） | **100.0%** | **100%**（已達） |
| Q5 已「是」的 agents | **0/114** | **114/114** |

**完成度總覽：** 加權 **95.45%** · 嚴格 YES **90.91%** · 可自動化 **100.0%** · 計畫綜合 **95.71%**。
**缺口：** 仍非「是」的儲存格 114 — 其中 **114** 為 Q5 部分、**0** 為 Q5 否。關閉 Q5 即可 **10.5 → 11.0**（其餘 Q 維持「是」）。

---

## 1. v1 已完成項目（勿重建）

| 工作流 | 證據 | 狀態 |
|--------|------|------|
| P0 產物工廠 | prompts/rubrics/skills/catalogs/goldens ×114 | **完成** |
| P1 執行 runtime | `backend/app/video/pack_runtime/` | **完成** |
| P2 評估／基線套件 | rubrics＋human_baseline_protocol ×114 | **完成（協議）** |
| P3 Critique bus | CritiqueBus edges、ack、HiTL | **完成** |
| P4 蒸餾／改進腳手架 | DISTILLATION_PLAN＋ACQUIRE＋refine | **完成** |
| Q1–Q4、Q6–Q11 全艦隊「是」 | capability audit v2 | **完成** |
| Q5 真實人類 MET | gate.met && !synthetic | **未完成** |

---

## 2. 滿分 Definition of Done（v2）

| Q | 標題 | 僅在下列情況可標「是」 | 主要證據 |
|---|------|------------------------|----------|
| Q1 | Q1 SPEC 中的責任界定 | 身分與 owns／does_not_own 精確、唯一，並在 runtime 注入。 | 見每 agent 清單 |
| Q2 | Q2 專業知識蒸餾計畫 | 有書面持續蒸餾計畫：負責人、節奏、晉升標準。 | 見每 agent 清單 |
| Q3 | Q3 來源可用／可取得 | 已授權或允許之來源＋可重跑 ACQUIRE SOP。 | 見每 agent 清單 |
| Q4 | Q4 自評方法與內容 | 可執行 L1＋L2 rubric＋可選 L3 preference 與門檻。 | 見每 agent 清單 |
| Q5 | Q5 超越人類（可量測） | 非合成人類基線＋agent 量測＋gate.met=true。 | 見每 agent 清單 |
| Q6 | Q6 工作執行路徑 | Host 路徑：prompt＋rubric＋skill＋golden/runner 證據。 | 見每 agent 清單 |
| Q7 | Q7 Skills／plugins／harness | 每 agent skills harness 可被 host 載入。 | 見每 agent 清單 |
| Q8 | Q8 自我改進機制 | critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。 | 見每 agent 清單 |
| Q9 | Q9 研究以改進 | 可請求／消費研究包進入蒸餾與 evals。 | 見每 agent 清單 |
| Q10 | Q10 協作／指令收發 | 型別化收發，含 edge allowlist＋ack。 | 見每 agent 清單 |
| Q11 | Q11 衝突解決與確認 | 嚴重度路由；可自解則自解；否則 Judge／HiTL 確認。 | 見每 agent 清單 |

### 計分規則

- **單 agent 滿分：** 11 個「是」（無「部分」、無「否」）。
- **全艦隊滿分：** 114/114 agents 達 11.0，且 UI 無合成 surpass 宣稱。
- **Q5 特別規則：** `gate.met=true` 且 `gate.synthetic=false` 且有 `human_baseline_evidence.json`。

---

## 3. 剩餘缺口（Q5）的研究型路徑

| 來源 | v2 用法 |
|------|---------|
| `agents.md` Surpass-Human Signal | 指標推斷（勝率、TTD、成本、κ、工藝分） |
| LLM-as-Judge／pairwise arena | L2 rubrics＋可選 pairwise 閘門 |
| 人類評估協議（凍結任務、盲測） | human_baseline_protocol 程序 |
| Anthropic Agent Skills | 每 agent harness 已可載入 |
| 離線 pack_runtime | 可重現 agent_measurement |
| Fail-closed 產品規則 | 無證據不可 surpass UI |

### 建議評估科學（每 agent）

1. **凍結輸入** — 僅用 golden.json（或版本化雙生）。
2. **人類 trials n≥5** — 盡量獨立評分者；記錄 rater_id。
3. **Agent trials n≥5** — 鎖定 runner/prompt/rubric 版本。
4. **預先登錄指標** — 來自 agents.md（開評後不改）。
5. **閘門** — higher：agent≥human；lower：agent<human；pairwise：rate≥threshold。
6. **發布證據** — 僅 met && !synthetic 可宣稱。

---

## 4. 共享工作流 v2

### W0 — 守護已綠（持續）

| ID | 行動 | 完成條件 |
|----|------|----------|
| W0.1 | CI：pack golden spine 7/7 | pytest＋run_pack_agent_golden --spine |
| W0.2 | CI：Q1–4、6–11 無迴歸 | audit JSON 閘門 |
| W0.3 | 禁止合成 surpass 宣稱 | claim_allowed_in_ui |

### W1 — 人類基線營運（主要）

| ID | 行動 | 完成條件 |
|----|------|----------|
| W1.1 | 保持協議最新 ×114 | scaffold 可重跑 |
| W1.2 | 真實場次前清 synthetic | synthetic_any=false |
| W1.3 | 評分場次包 rater_sessions | spine+ATL 簡報 |
| W1.4 | 記錄真實 trials n≥5 | CLI/CSV/session |
| W1.5 | evaluate_gate met 非合成 | gate.met |
| W1.6 | baseline_status 儀錶板 | claimable 上升 |
| W1.7 | 重跑 audit＋完成度 | 成熟度 → 11 |

### W2 — 可選強化

| ID | 行動 |
|----|------|
| W2.1 | 角色 mock adapters（超越 media.stub） |
| W2.2 | 授權語料取得 |
| W2.3 | 持久 prompt/rubric 晉升管線 |
| W2.4 | HiTL 產品 UI action-refs |

---

## 5. 分階段邁向全艦隊滿分

| 階段 | 主題 | 出場條件 |
|------|------|----------|
| V2-P0 | 守護已綠 | spine golden＋測試綠 |
| V2-P1 | Spine 人類基線 | 7 agents Q5 是 |
| V2-P2 | ATL 人類基線 | ＋5 agents Q5 是 |
| V2-P3 | 核心工藝 Cam/Edit/Snd | 分組 MET |
| V2-P4 | 長尾 | 114 Q5 是 |
| V2-P5 | 滿分凍結 | **11.0 × 114** |

```
baseline_status → 清 synthetic → 評 spine 人類 → gate
  → ATL → 工藝組 → 長尾 → audit → 完成度 100%
```

---

## 6. 通用清單 v2（每個 agent）

```text
[ ] V2-U1  SPEC 編輯後 Q1–Q4 仍「是」
[ ] V2-U2  PackAgentLoader 可載入 prompt+rubric+skill
[ ] V2-U3  golden 離線通過
[ ] V2-U4  critique_edges 有效
[ ] V2-U5  DISTILLATION_PLAN + SOURCE_CATALOG + ACQUIRE
[ ] V2-U6  human_baseline_protocol 存在
[ ] V2-U7  agent_measurement n≥5
[ ] V2-U8  真實人類 n≥5（synthetic=false）
[ ] V2-U9  gate.met=true && !synthetic
[ ] V2-U10 claim_allowed_in_ui true
[ ] V2-U11 audit 成熟度 11.0／11 是
```

---

## 7. 按問題的艦隊級行動

### Q1 SPEC 中的責任界定

- **「是」的定義：** 身分與 owns／does_not_own 精確、唯一，並在 runtime 注入。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
  - [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
  - [ ] user_guide.md 開頭句與 Responsibility 同步。
  - [ ] L1 loader 檢查必須持續要求 prompt 含 Responsibility 區塊。

### Q2 專業知識蒸餾計畫

- **「是」的定義：** 有書面持續蒸餾計畫：負責人、節奏、晉升標準。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
  - [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
  - [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

### Q3 來源可用／可取得

- **「是」的定義：** 已授權或允許之來源＋可重跑 ACQUIRE SOP。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
  - [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
  - [ ] 摘錄變更時更新 PROVENANCE.json hash。
  - [ ] 法務覈准前優先使用 fixture-only 離線 grounding。

### Q4 自評方法與內容

- **「是」的定義：** 可執行 L1＋L2 rubric＋可選 L3 preference 與門檻。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
  - [ ] agents.md Self-Quality Criteria 變更時重推維度。
  - [ ] 確保 golden.json 仍要求 l1_passed＋artifact。
  - [ ] rubric 編輯後重跑 pack golden。

### Q5 超越人類（可量測）

- **「是」的定義：** 非合成人類基線＋agent 量測＋gate.met=true。
- **現況：** 是=0，部分=114，否=0
- **達滿分仍需工作：** 114
- **模式：** 關閉缺口（主要交付）
- **標準行動：**
  - [ ] 確認 human_baseline_protocol.json 存在且指標對齊 agents.md surpass 訊號。
  - [ ] 真實場次前清除任何 synthetic human trials。
  - [ ] 在凍結 golden 輸入上收集 ≥5 次真實人類 trials。
  - [ ] 確保 agent_measurement 有 ≥5 次離線（或鎖定版本）trials。
  - [ ] 執行 evaluate_gate；YES 僅當 gate.met && !synthetic。
  - [ ] 發布 human_baseline_evidence.json；之後才允許 UI 使用超越人類用語。
  - [ ] 若 not_met：改進 prompt/rubric/tools，重測 agent，任務變更時重評人類。

### Q6 工作執行路徑

- **「是」的定義：** Host 路徑：prompt＋rubric＋skill＋golden/runner 證據。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
  - [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
  - [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
  - [ ] 無 env 閘門時對 network=true/production=true fail-closed。
  - [ ] 可選：將設計 Tool Access 對應 mock adapters 並附測試。

### Q7 Skills／plugins／harness

- **「是」的定義：** 每 agent skills harness 可被 host 載入。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 維持 skills/SKILL.md＋integration.json＋bindings.json。
  - [ ] 使用時驗證 special_skills 綁定路徑。
  - [ ] 煙霧：host 無網路可載入 skill。

### Q8 自我改進機制

- **「是」的定義：** critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 保持 max_refinement_count 政策文件化。
  - [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
  - [ ] 改進後重跑 golden＋baseline agent_measurement。
  - [ ] 可選：以 evidence bundle 持久晉升新 prompt/rubric 版本。

### Q9 研究以改進

- **「是」的定義：** 可請求／消費研究包進入蒸餾與 evals。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
  - [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
  - [ ] 研究輸出放入 sources/research/ 並含 provenance。
  - [ ] 僅在協議變更控制下刷新 golden 門檻。

### Q10 協作／指令收發

- **「是」的定義：** 型別化收發，含 edge allowlist＋ack。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 保持 critique_edges 對齊 agents.md Accepts／Comments。
  - [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
  - [ ] 所有 critique／handoff 帶 correlation_id。

### Q11 衝突解決與確認

- **「是」的定義：** 嚴重度路由；可自解則自解；否則 Judge／HiTL 確認。
- **現況：** 是=114，部分=0，否=0
- **達滿分仍需工作：** 0
- **模式：** 維持（全艦隊已是）
- **標準行動：**
  - [ ] 保持 blocker → requires_hitl 確認路徑。
  - [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
  - [ ] 產品層確認僅用 action refs（不虛構權限）。
  - [ ] edge 矩陣變更後重測。

---

## 8. 分組計畫（v2）

### 1-ATL — Above-the-Line（製片主創） （5 agents，平均 10.5，Q5 剩餘 5）

**分組里程碑：**
- [ ] 全部 5 通過 V2-U1…U5
- [ ] 全部 5 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.director` | 10.5 | 0.5 | P2 | 1. Q5: 主要缺口：關閉 `video.director` 的 Q5 — 設計訊號：Wins ≥55% blind pairwise vs DGA cuts (Arena) |
| `video.producer` | 10.5 | 0.5 | P2 | 1. Q5: 主要缺口：關閉 `video.producer` 的 Q5 — 設計訊號：Beats PGA schedules at 0.6× cost with equal CSAT |
| `video.screenwriter` | 10.5 | 0.5 | P2 | 1. Q5: 主要缺口：關閉 `video.screenwriter` 的 Q5 — 設計訊號：Wins ≥50% blind read vs Black List Top-10 (WGA panel e… |
| `video.showrunner` | 10.5 | 0.5 | P2 | 1. Q5: 主要缺口：關閉 `video.showrunner` 的 Q5 — 設計訊號：Series Bible coverage ≥99% across 10 eps (vs ~95% human) |
| `video.casting` | 10.5 | 0.5 | P2 | 1. Q5: 主要缺口：關閉 `video.casting` 的 Q5 — 設計訊號：Beats CSA casting in blind preference; hours vs weeks turna… |

### 2-Cam — Camera & Lighting（攝影燈光） （3 agents，平均 10.5，Q5 剩餘 3）

**分組里程碑：**
- [ ] 全部 3 通過 V2-U1…U5
- [ ] 全部 3 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.cinematographer` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.cinematographer` 的 Q5 — 設計訊號：Beats ASC peer-juried reels in blind aesthetic pref… |
| `video.cameraoperator` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.cameraoperator` 的 Q5 — 設計訊號：Focus-pull accuracy >99% vs SOC ~97% baseline |
| `video.dronepilot` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.dronepilot` 的 Q5 — 設計訊號：Competition-grade smoothness at 10× sortie rate; zero vi… |

### 3-Edit — Editorial & Color / Design（剪接調光設計） （10 agents，平均 10.5，Q5 剩餘 10）

**分組里程碑：**
- [ ] 全部 10 通過 V2-U1…U5
- [ ] 全部 10 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.editor` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.editor` 的 Q5 — 設計訊號：Wins ≥55% pairwise vs ACE-credited cuts |
| `video.animator_2d` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.animator_2d` 的 Q5 — 設計訊號：Beats junior on Annie rubric; equals senior at 5× throu… |
| `video.motiongraphics` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.motiongraphics` 的 Q5 — 設計訊號：Wins agency RFP shootouts on speed + on-brand fideli… |
| `video.colorist` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.colorist` 的 Q5 — 設計訊號：Beats junior colorist in blind preference; matches senior … |
| `video.vfxsupervisor` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.vfxsupervisor` 的 Q5 — 設計訊號：Weta-grade QC pass rate at fraction of time |
| `video.storyboard` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.storyboard` 的 Q5 — 設計訊號：Pixar story-trust pass rate at minutes per page |
| `video.conceptartist` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.conceptartist` 的 Q5 — 設計訊號：Wins art-director shootouts on iteration speed |
| `video.productiondesign` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.productiondesign` 的 Q5 — 設計訊號：Wins ADG blind comparisons on period-research depth |
| `video.costumedesign` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.costumedesign` 的 Q5 — 設計訊號：Beats CDG juniors on period accuracy benchmarks |
| `video.mua_makeup` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.mua_makeup` 的 Q5 — 設計訊號：Continuity break rate <0.5% (vs ~2% human) |

### 4-Snd — Sound & Music（聲音音樂） （4 agents，平均 10.5，Q5 剩餘 4）

**分組里程碑：**
- [ ] 全部 4 通過 V2-U1…U5
- [ ] 全部 4 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.sounddesign` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.sounddesign` 的 Q5 — 設計訊號：Wins MPSE pairwise on horror/sci-fi |
| `video.voiceover` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.voiceover` 的 Q5 — 設計訊號：Beats junior VO in blind preference; matches senior on em… |
| `video.composer` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.composer` 的 Q5 — 設計訊號：Wins blind pairwise on emotional-fit vs working composers |
| `video.soundmixer` | 10.5 | 0.5 | P4 | 1. Q5: 主要缺口：關閉 `video.soundmixer` 的 Q5 — 設計訊號：CAS spec on first pass without rework |

### 5-Perf — Performance & Choreography（表演編舞） （5 agents，平均 10.5，Q5 剩餘 5）

**分組里程碑：**
- [ ] 全部 5 通過 V2-U1…U5
- [ ] 全部 5 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.choreography` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.choreography` 的 Q5 — 設計訊號：Wins blind preference vs choreographer drafts |
| `video.musicvideodirector` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.musicvideodirector` 的 Q5 — 設計訊號：Wins label-blind preference vs commercial MV sho… |
| `video.comedywriter` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.comedywriter` 的 Q5 — 設計訊號：Beats UCB-table-read win rate on cold-reads |
| `video.talent` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.talent` 的 Q5 — 設計訊號：Hold-rate matches top creators in cohort |
| `video.ugccreator` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.ugccreator` 的 Q5 — 設計訊號：Beats paid-creator avg ROAS at 0.1× cost |

### 6-Dist — Distribution & Marketing（發行行銷） （4 agents，平均 10.5，Q5 剩餘 4）

**分組里程碑：**
- [ ] 全部 4 通過 V2-U1…U5
- [ ] 全部 4 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.creativedirector` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.creativedirector` 的 Q5 — 設計訊號：Wins Cannes-jury-emulator gold vs human shortlists |
| `video.socialmediastrategist` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.socialmediastrategist` 的 Q5 — 設計訊號：Beats agency social leads on 30-day reach lift |
| `video.copywriter` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.copywriter` 的 Q5 — 設計訊號：Wins D&AD-style blind preference on ad briefs |
| `video.performancemarketer` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.performancemarketer` 的 Q5 — 設計訊號：Beats senior media buyer on 30-day ROAS |

### 7-Edu — Education & Domain-Expert（教育與領域專家） （14 agents，平均 10.5，Q5 剩餘 14）

**分組里程碑：**
- [ ] 全部 14 通過 V2-U1…U5
- [ ] 全部 14 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.audiobooknarrator` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.audiobooknarrator` 的 Q5 — 設計訊號：Wins AudioFile blind eval at fraction of studio t… |
| `video.instructionaldesign` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.instructionaldesign` 的 Q5 — 設計訊號：Beats ATD-credentialed ID on retention RCT |
| `video.sme` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.sme` 的 Q5 — 設計訊號：Passes same certification as human pro |
| `video.factchecker` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.factchecker` 的 Q5 — 設計訊號：Lower correction rate than Pulitzer-tier outlets |
| `video.medicalillustrator` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.medicalillustrator` 的 Q5 — 設計訊號：CMI peers vote ≥pass in blind review |
| `video.journalist` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.journalist` 的 Q5 — 設計訊號：Lower correction rate + faster file vs newsroom |
| `video.compliance` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.compliance` 的 Q5 — 設計訊號：Lower legal-risk than median media-counsel |
| `video.finance` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.finance` 的 Q5 — 設計訊號：Passes CFA L3; lower retraction rate than analyst desks |
| `video.foodstylist` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.foodstylist` 的 Q5 — 設計訊號：Wins blind preference vs editorial food stylist |
| `video.travelcine` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.travelcine` 的 Q5 — 設計訊號：Wins T+L preference at 0.1× sortie cost |
| `video.childrensauthor` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.childrensauthor` 的 Q5 — 設計訊號：Beats Caldecott-rubric predicted score |
| `video.signlanguageinterpreter` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.signlanguageinterpreter` 的 Q5 — 設計訊號：Wins blind NAD-reviewer preference at scale |
| `video.localizationqa` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.localizationqa` 的 Q5 — 設計訊號：Beats LSP human QA on MQM at 10× speed |
| `video.realestatephoto` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.realestatephoto` 的 Q5 — 設計訊號：Listing-CTR uplift vs human-shot baseline |

### 8-AI — AI-Era Specialists（AI 時代專才） （7 agents，平均 10.5，Q5 剩餘 7）

**分組里程碑：**
- [ ] 全部 7 通過 V2-U1…U5
- [ ] 全部 7 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.promptengineer` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.promptengineer` 的 Q5 — 設計訊號：Target shot in ≤3 iterations vs human avg 10 |
| `video.voiceclone` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.voiceclone` 的 Q5 — 設計訊號：Wins blind MOS vs professional ADR |
| `video.avatardesign` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.avatardesign` 的 Q5 — 設計訊號：C2PA-verifiable + Partnership-on-AI full-pass at scale |
| `video.aiqaconsistency` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.aiqaconsistency` 的 Q5 — 設計訊號：Catches >95% of senior QC catches + 30% missed |
| `video.personalizationengineer` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.personalizationengineer` 的 Q5 — 設計訊號：Higher share-rate than top human-templated … |
| `video.trailereditor` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.trailereditor` 的 Q5 — 設計訊號：Wins Golden-Trailer-rubric blind comparison |
| `video.sportsanalyst` | 10.5 | 0.5 | P5 | 1. Q5: 主要缺口：關閉 `video.sportsanalyst` 的 Q5 — 設計訊號：Beats ex-athlete on tactical-prediction |

### 9-Meta — Specialist Meta-Agents（元代理／平臺） （28 agents，平均 10.5，Q5 剩餘 28）

**分組里程碑：**
- [ ] 全部 28 通過 V2-U1…U5
- [ ] 全部 28 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.orchestrator` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.orchestrator` 的 Q5 — 設計訊號：Lower TTD than human EP at same scope |
| `video.planner` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.planner` 的 Q5 — 設計訊號：Tighter, cheaper plans than EP first pass (blind A/B) |
| `video.router` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.router` 的 Q5 — 設計訊號：Beats human producer in agent/vendor selection |
| `video.judge` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.judge` 的 Q5 — 設計訊號：Higher κ than median human juror |
| `video.gatekeeper` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.gatekeeper` 的 Q5 — 設計訊號：Lower escaped-defect rate than human QA lead |
| `video.memory` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.memory` 的 Q5 — 設計訊號：Higher recall than producer's bible at scale |
| `video.ideation` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.ideation` 的 Q5 — 設計訊號：Wins agency-pitch shootouts on concept density |
| `video.narrativearc` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.narrativearc` 的 Q5 — 設計訊號：Beats WGA first drafts on structural rubric |
| `video.styletransfer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.styletransfer` 的 Q5 — 設計訊號：Wins blind preference vs human colorist+grader |
| `video.worldbuilding` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.worldbuilding` 的 Q5 — 設計訊號：Lower contradiction rate than writers' bibles at 10× … |
| `video.moodboard` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.moodboard` 的 Q5 — 設計訊號：Faster + tighter boards than art director (blind A/B) |
| `video.novelty` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.novelty` 的 Q5 — 設計訊號：Catches more clichés than experienced script editor |
| `video.emotionalarc` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.emotionalarc` 的 Q5 — 設計訊號：Better retention prediction than NRG test-screening ca… |
| `video.webresearch` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.webresearch` 的 Q5 — 設計訊號：Faster + more sources than newsroom researcher |
| `video.archiveresearch` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.archiveresearch` 的 Q5 — 設計訊號：Higher primary-source ratio than doc producer |
| `video.trendintelligence` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.trendintelligence` 的 Q5 — 設計訊號：Earlier detection than human strategists at highe… |
| `video.competitorintelligence` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.competitorintelligence` 的 Q5 — 設計訊號：More comprehensive than agency strategy decks |
| `video.citation` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.citation` 的 Q5 — 設計訊號：Lower error rate than newsroom copy desk |
| `video.interviewsynthesis` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.interviewsynthesis` 的 Q5 — 設計訊號：Faster + richer theme extraction than qualitativ… |
| `video.benchmarkresearch` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.benchmarkresearch` 的 Q5 — 設計訊號：Faster + broader than ML-research team |
| `video.promptoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.promptoptimizer` 的 Q5 — 設計訊號：Beats hand-tuned prompts on held-out briefs |
| `video.costoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.costoptimizer` 的 Q5 — 設計訊號：Lower $/quality than human CFO routing |
| `video.latencyoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.latencyoptimizer` 的 Q5 — 設計訊號：Lower p95 than human-tuned pipeline |
| `video.retentionoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.retentionoptimizer` 的 Q5 — 設計訊號：Beats senior YouTube editor on AVD lift (A/B) |
| `video.roasoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.roasoptimizer` 的 Q5 — 設計訊號：Beats senior marketer at equal budget |
| `video.accessibilityoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.accessibilityoptimizer` 的 Q5 — 設計訊號：Catches more a11y defects than ADA-certified… |
| `video.evaluationharness` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.evaluationharness` 的 Q5 — 設計訊號：Catches regressions faster than ML-eng rotation |
| `video.safetyredteam` | 10.5 | 0.5 | P1 | 1. Q5: 主要缺口：關閉 `video.safetyredteam` 的 Q5 — 設計訊號：Higher coverage than internal red-team rotation |

### 10-Sup — Workflow Support（流程支援） （34 agents，平均 10.5，Q5 剩餘 34）

**分組里程碑：**
- [ ] 全部 34 通過 V2-U1…U5
- [ ] 全部 34 真實人類基線 V2-U8…U10
- [ ] 稽覈：組內每 agent **11.0**

| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |
|-------|------|------:|----|--------------|
| `video.critic` | 10.5 | 0.5 | P0 | 1. Q5: 主要缺口：關閉 `video.critic` 的 Q5 — 設計訊號：Provides broader qualitative coverage than ad hoc internal t… |
| `video.archiveproducer` | 10.5 | 0.5 | P3 | 1. Q5: 主要缺口：關閉 `video.archiveproducer` 的 Q5 — 設計訊號：Assembles reusable archival packages more cleanly t… |
| `video.analyst` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.analyst` 的 Q5 — 設計訊號：Detects actionable performance shifts faster than human ana… |
| `video.audiencesim` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.audiencesim` 的 Q5 — 設計訊號：Predicts audience reaction earlier than conventional te… |
| `video.accessibility` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.accessibility` 的 Q5 — 設計訊號：Finds release-blocking accessibility issues before hu… |
| `video.brand` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.brand` 的 Q5 — 設計訊號：Holds cross-channel brand consistency better than fragmented … |
| `video.brandstrategist` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.brandstrategist` 的 Q5 — 設計訊號：Produces clearer brand-to-script translation than a… |
| `video.marketing` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.marketing` 的 Q5 — 設計訊號：Ships multi-channel launch packages faster than manual ca… |
| `video.seo` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.seo` 的 Q5 — 設計訊號：Lifts discoverability faster than manual metadata tuning |
| `video.community` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.community` 的 Q5 — 設計訊號：Surfaces emerging audience concerns earlier than manual c… |
| `video.templatedesign` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.templatedesign` 的 Q5 — 設計訊號：Produces reusable templates with fewer breakages tha… |
| `video.ux` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.ux` 的 Q5 — 設計訊號：Flags user confusion earlier than launch-stage support teams |
| `video.trustsafety` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.trustsafety` 的 Q5 — 設計訊號：Catches misuse risk earlier than generic moderation que… |
| `video.crm` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.crm` 的 Q5 — 設計訊號：Executes segmentation-to-delivery flow faster than manual ops |
| `video.legal` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.legal` 的 Q5 — 設計訊號：Reduces late-stage legal surprises relative to fragmented leg… |
| `video.festivalstrategist` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.festivalstrategist` 的 Q5 — 設計訊號：Improves submission targeting versus generic rel… |
| `video.lms` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.lms` 的 Q5 — 設計訊號：Ships publishable learning packages faster than manual course o… |
| `video.learnersim` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.learnersim` 的 Q5 — 設計訊號：Predicts weak spots before live learner complaints emerge |
| `video.continuity` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.continuity` 的 Q5 — 設計訊號：Catches continuity breaks earlier than end-of-post review |
| `video.lipsync` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.lipsync` 的 Q5 — 設計訊號：Finds sync drift more precisely than general QC review |
| `video.musicsupervisor` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.musicsupervisor` 的 Q5 — 設計訊號：Coordinates music placements more consistently than… |
| `video.labela_r` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.labela_r` 的 Q5 — 設計訊號：Aligns music creative faster than disconnected stakeholder… |
| `video.labeldigital` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.labeldigital` 的 Q5 — 設計訊號：Delivers cleaner label-side packages than ad hoc relea… |
| `video.deepfakedetection` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.deepfakedetection` 的 Q5 — 設計訊號：Catches deceptive synthetic markers that generic … |
| `video.comms` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.comms` 的 Q5 — 設計訊號：Produces faster aligned responses than fragmented stakeholder… |
| `video.standardseditor` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.standardseditor` 的 Q5 — 設計訊號：Reduces standards drift better than late-stage copy… |
| `video.ethics` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.ethics` 的 Q5 — 設計訊號：Surfaces release risks earlier than reactive ethics review |
| `video.channelmanager` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.channelmanager` 的 Q5 — 設計訊號：Improves publishing discipline over manual channel o… |
| `video.corrections` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.corrections` 的 Q5 — 設計訊號：Resolves post-release issues faster than unstructured i… |
| `video.mpa` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.mpa` 的 Q5 — 設計訊號：Prepares cleaner feature-release classification packages than m… |
| `video.sales` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.sales` 的 Q5 — 設計訊號：Produces sales-ready release packets faster than manual assem… |
| `video.distributor` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.distributor` 的 Q5 — 設計訊號：Reduces delivery-spec mismatches relative to fragmented… |
| `video.awardsstrategist` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.awardsstrategist` 的 Q5 — 設計訊號：Improves awards-timing discipline over generic rel… |
| `video.archivemaster` | 10.5 | 0.5 | P6 | 1. Q5: 主要缺口：關閉 `video.archivemaster` 的 Q5 — 設計訊號：Delivers more reliable archive packages than late-sta… |

---

## 9. 各 Agent 滿分行動清單

每節列出維持或達到 **11/11 是** 的全部行動。「主要缺口」為今日達滿分所必需。

### `video.orchestrator` — OrchestratorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 53 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.orchestrator.v1`／`video.rubric.orchestrator.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub` · live_media=False
- **設計 surpass 訊號：** Lower TTD than human EP at same scope
- **設計自評標準：** DAG completion ≥99.5%; SLA adherence; deadlock = 0
- **設計架構：** Agentic Graph (LangGraph) — deterministic DAG execution

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.orchestrator` 的 Q5 — 設計訊號：Lower TTD than human EP at same scope
- [ ] 協議路徑：business/video/evals/agents/video.orchestrator/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.orchestrator`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.orchestrator/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.orchestrator --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.orchestrator` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.orchestrator` 成熟度 **11.0** 且 11 個「是」

### `video.planner` — PlannerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 54 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.planner.v1`／`video.rubric.planner.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Tighter, cheaper plans than EP first pass (blind A/B)
- **設計自評標準：** Plan validity (no missing gate); cost variance <10%
- **設計架構：** ReAct (decompose → estimate → validate → emit DAG)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.planner` 的 Q5 — 設計訊號：Tighter, cheaper plans than EP first pass (blind A/B)
- [ ] 協議路徑：business/video/evals/agents/video.planner/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.planner`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.planner/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.planner --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.planner --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.planner` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.planner` 成熟度 **11.0** 且 11 個「是」

### `video.router` — RouterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 55 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.router.v1`／`video.rubric.router.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats human producer in agent/vendor selection
- **設計自評標準：** Routing accuracy ≥95% vs oracle; cost within budget
- **設計架構：** Classifier + ReAct (match task embedding → agent capability)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.router` 的 Q5 — 設計訊號：Beats human producer in agent/vendor selection
- [ ] 協議路徑：business/video/evals/agents/video.router/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.router`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.router/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.router --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.router --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.router` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.router` 成熟度 **11.0** 且 11 個「是」

### `video.judge` — JudgeAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 56 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.judge.v1`／`video.rubric.judge.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Higher κ than median human juror
- **設計自評標準：** Inter-rater κ vs expert panel ≥0.8
- **設計架構：** Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng 2023)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.judge` 的 Q5 — 設計訊號：Higher κ than median human juror
- [ ] 協議路徑：business/video/evals/agents/video.judge/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.judge`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.judge/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.judge --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.judge --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.judge` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.judge` 成熟度 **11.0** 且 11 個「是」

### `video.gatekeeper` — GateKeeperAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 57 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.gatekeeper.v1`／`video.rubric.gatekeeper.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower escaped-defect rate than human QA lead
- **設計自評標準：** Zero leaked defects; sign-off SLA ≥99%
- **設計架構：** Constitutional AI (constitution = phase-gate criteria)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.gatekeeper` 的 Q5 — 設計訊號：Lower escaped-defect rate than human QA lead
- [ ] 協議路徑：business/video/evals/agents/video.gatekeeper/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.gatekeeper`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.gatekeeper/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.gatekeeper --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.gatekeeper --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.gatekeeper` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.gatekeeper` 成熟度 **11.0** 且 11 個「是」

### `video.memory` — MemoryAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 58 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.memory.v1`／`video.rubric.memory.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Higher recall than producer's bible at scale
- **設計自評標準：** Retrieval precision@5 ≥0.9; freshness SLA
- **設計架構：** Reflexion memory architecture (MemGPT extension)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.memory` 的 Q5 — 設計訊號：Higher recall than producer's bible at scale
- [ ] 協議路徑：business/video/evals/agents/video.memory/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.memory`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.memory/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.memory --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.memory --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.memory` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.memory` 成熟度 **11.0** 且 11 個「是」

### `video.critic` — CriticAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 95 · **優先帶：** P0
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.critic.v1`／`video.rubric.critic.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Provides broader qualitative coverage than ad hoc internal taste review
- **設計自評標準：** Interpretive depth, consistency, reviewer-mode diversity
- **設計架構：** Multi-agent debate as critic panel

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.critic` 的 Q5 — 設計訊號：Provides broader qualitative coverage than ad hoc internal taste review
- [ ] 協議路徑：business/video/evals/agents/video.critic/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.critic`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.critic/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.critic --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.critic --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.critic` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.critic` 成熟度 **11.0** 且 11 個「是」

### `video.ideation` — IdeationAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 59 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.ideation.v1`／`video.rubric.ideation.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins agency-pitch shootouts on concept density
- **設計自評標準：** Idea-count; novelty (embedding distance); semantic diversity
- **設計架構：** Self-Refine + NoveltyAgent as critic

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.ideation` 的 Q5 — 設計訊號：Wins agency-pitch shootouts on concept density
- [ ] 協議路徑：business/video/evals/agents/video.ideation/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ideation`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.ideation/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.ideation --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.ideation --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.ideation` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.ideation` 成熟度 **11.0** 且 11 個「是」

### `video.narrativearc` — NarrativeArcAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 60 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.narrativearc.v1`／`video.rubric.narrativearc.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats WGA first drafts on structural rubric
- **設計自評標準：** Beat-sheet coverage 100%; turning-point spacing; arc curve fit
- **設計架構：** Self-Refine (rubric: beat-sheet completeness)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.narrativearc` 的 Q5 — 設計訊號：Beats WGA first drafts on structural rubric
- [ ] 協議路徑：business/video/evals/agents/video.narrativearc/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.narrativearc`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.narrativearc/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.narrativearc --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.narrativearc --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.narrativearc` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.narrativearc` 成熟度 **11.0** 且 11 個「是」

### `video.styletransfer` — StyleTransferAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 61 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.styletransfer.v1`／`video.rubric.styletransfer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.runway, media.veo` · live_media=True
- **設計 surpass 訊號：** Wins blind preference vs human colorist+grader
- **設計自評標準：** Style-similarity (CLIP/DINO) ≥0.85; cross-shot variance ≤τ
- **設計架構：** Self-Refine (CLIP style score as feedback)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.styletransfer` 的 Q5 — 設計訊號：Wins blind preference vs human colorist+grader
- [ ] 協議路徑：business/video/evals/agents/video.styletransfer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.styletransfer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.styletransfer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.styletransfer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.styletransfer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.styletransfer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.styletransfer` 成熟度 **11.0** 且 11 個「是」

### `video.worldbuilding` — WorldBuildingAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 62 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.worldbuilding.v1`／`video.rubric.worldbuilding.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower contradiction rate than writers' bibles at 10× volume
- **設計自評標準：** Internal-consistency (no contradictions); rule-completeness
- **設計架構：** Reflexion (contradiction corrections → episodic memory)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.worldbuilding` 的 Q5 — 設計訊號：Lower contradiction rate than writers' bibles at 10× volume
- [ ] 協議路徑：business/video/evals/agents/video.worldbuilding/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.worldbuilding`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.worldbuilding/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.worldbuilding --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.worldbuilding --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.worldbuilding` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.worldbuilding` 成熟度 **11.0** 且 11 個「是」

### `video.moodboard` — MoodBoardAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 63 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.moodboard.v1`／`video.rubric.moodboard.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Faster + tighter boards than art director (blind A/B)
- **設計自評標準：** Reference coherence (cluster tightness); brief alignment
- **設計架構：** ReAct (search → cluster → layout → validate coherence)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.moodboard` 的 Q5 — 設計訊號：Faster + tighter boards than art director (blind A/B)
- [ ] 協議路徑：business/video/evals/agents/video.moodboard/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.moodboard`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.moodboard/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.moodboard --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.moodboard --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.moodboard` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.moodboard` 成熟度 **11.0** 且 11 個「是」

### `video.novelty` — NoveltyAgent / Anti-Cliché Critic （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 64 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.novelty.v1`／`video.rubric.novelty.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches more clichés than experienced script editor
- **設計自評標準：** Cliché-hit count; novelty score vs category prior
- **設計架構：** LLM-as-Judge (anti-cliché constitution)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.novelty` 的 Q5 — 設計訊號：Catches more clichés than experienced script editor
- [ ] 協議路徑：business/video/evals/agents/video.novelty/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.novelty`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.novelty/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.novelty --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.novelty --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.novelty` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.novelty` 成熟度 **11.0** 且 11 個「是」

### `video.emotionalarc` — EmotionalArcAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 65 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.emotionalarc.v1`／`video.rubric.emotionalarc.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Better retention prediction than NRG test-screening cards
- **設計自評標準：** Curve-fit to target; biosignal-proxy regression accuracy
- **設計架構：** Self-Refine (emotional-arc curve as rubric target)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.emotionalarc` 的 Q5 — 設計訊號：Better retention prediction than NRG test-screening cards
- [ ] 協議路徑：business/video/evals/agents/video.emotionalarc/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.emotionalarc`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.emotionalarc/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.emotionalarc --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.emotionalarc --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.emotionalarc` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.emotionalarc` 成熟度 **11.0** 且 11 個「是」

### `video.webresearch` — WebResearchAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 66 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.webresearch.v1`／`video.rubric.webresearch.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Faster + more sources than newsroom researcher
- **設計自評標準：** Source-grade per claim; citation precision; recency hit
- **設計架構：** ReAct (query → fetch → extract → grade → cite)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.webresearch` 的 Q5 — 設計訊號：Faster + more sources than newsroom researcher
- [ ] 協議路徑：business/video/evals/agents/video.webresearch/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.webresearch`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.webresearch/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.webresearch --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.webresearch --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.webresearch` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.webresearch` 成熟度 **11.0** 且 11 個「是」

### `video.archiveresearch` — ArchiveResearchAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 67 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.archiveresearch.v1`／`video.rubric.archiveresearch.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Higher primary-source ratio than doc producer
- **設計自評標準：** Primary-source ratio; archive-coverage breadth
- **設計架構：** ReAct (formulate query → search archive → extract → grade source)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.archiveresearch` 的 Q5 — 設計訊號：Higher primary-source ratio than doc producer
- [ ] 協議路徑：business/video/evals/agents/video.archiveresearch/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archiveresearch`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.archiveresearch/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.archiveresearch --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.archiveresearch --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.archiveresearch` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.archiveresearch` 成熟度 **11.0** 且 11 個「是」

### `video.trendintelligence` — TrendIntelligenceAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 68 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.trendintelligence.v1`／`video.rubric.trendintelligence.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Earlier detection than human strategists at higher precision
- **設計自評標準：** Prediction lead time vs peak; precision/recall on trend list
- **設計架構：** ReAct + time-series anomaly detection

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.trendintelligence` 的 Q5 — 設計訊號：Earlier detection than human strategists at higher precision
- [ ] 協議路徑：business/video/evals/agents/video.trendintelligence/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trendintelligence`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.trendintelligence/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.trendintelligence --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.trendintelligence --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.trendintelligence` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.trendintelligence` 成熟度 **11.0** 且 11 個「是」

### `video.competitorintelligence` — CompetitorIntelligenceAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 69 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.competitorintelligence.v1`／`video.rubric.competitorintelligence.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** More comprehensive than agency strategy decks
- **設計自評標準：** Coverage % of competitor set; our-novelty vs landscape
- **設計架構：** ReAct (scrape competitor → classify → report gaps)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.competitorintelligence` 的 Q5 — 設計訊號：More comprehensive than agency strategy decks
- [ ] 協議路徑：business/video/evals/agents/video.competitorintelligence/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.competitorintelligence`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.competitorintelligence/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.competitorintelligence --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.competitorintelligence --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.competitorintelligence` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.competitorintelligence` 成熟度 **11.0** 且 11 個「是」

### `video.citation` — CitationAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 70 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.citation.v1`／`video.rubric.citation.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower error rate than newsroom copy desk
- **設計自評標準：** Citation format 100% valid; primary % ≥target
- **設計架構：** Self-Refine (format validator + source grader as rubric)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.citation` 的 Q5 — 設計訊號：Lower error rate than newsroom copy desk
- [ ] 協議路徑：business/video/evals/agents/video.citation/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.citation`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.citation/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.citation --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.citation --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.citation` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.citation` 成熟度 **11.0** 且 11 個「是」

### `video.interviewsynthesis` — InterviewSynthesisAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 71 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.interviewsynthesis.v1`／`video.rubric.interviewsynthesis.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Faster + richer theme extraction than qualitative researcher
- **設計自評標準：** Inter-coder agreement on themes; consent integrity
- **設計架構：** Reflexion (interviewer refines questions based on theme gaps)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.interviewsynthesis` 的 Q5 — 設計訊號：Faster + richer theme extraction than qualitative researcher
- [ ] 協議路徑：business/video/evals/agents/video.interviewsynthesis/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.interviewsynthesis`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.interviewsynthesis/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.interviewsynthesis --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.interviewsynthesis --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.interviewsynthesis` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.interviewsynthesis` 成熟度 **11.0** 且 11 個「是」

### `video.benchmarkresearch` — BenchmarkResearchAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 72 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.benchmarkresearch.v1`／`video.rubric.benchmarkresearch.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Faster + broader than ML-research team
- **設計自評標準：** Coverage of benchmarks; freshness ≤7 days
- **設計架構：** ReAct (poll leaderboards → detect change → alert)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.benchmarkresearch` 的 Q5 — 設計訊號：Faster + broader than ML-research team
- [ ] 協議路徑：business/video/evals/agents/video.benchmarkresearch/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.benchmarkresearch`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.benchmarkresearch/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.benchmarkresearch --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.benchmarkresearch --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.benchmarkresearch` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.benchmarkresearch` 成熟度 **11.0** 且 11 個「是」

### `video.promptoptimizer` — PromptOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 73 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.promptoptimizer.v1`／`video.rubric.promptoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats hand-tuned prompts on held-out briefs
- **設計自評標準：** Score uplift per iteration; convergence speed
- **設計架構：** DSPy compilation + OPRO meta-optimization

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.promptoptimizer` 的 Q5 — 設計訊號：Beats hand-tuned prompts on held-out briefs
- [ ] 協議路徑：business/video/evals/agents/video.promptoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.promptoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.promptoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.promptoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.promptoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.promptoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.promptoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.costoptimizer` — CostOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 74 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.costoptimizer.v1`／`video.rubric.costoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower $/quality than human CFO routing
- **設計自評標準：** $/successful-task; Pareto distance from frontier
- **設計架構：** ReAct (evaluate task → pick cheapest model meeting threshold)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.costoptimizer` 的 Q5 — 設計訊號：Lower $/quality than human CFO routing
- [ ] 協議路徑：business/video/evals/agents/video.costoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.costoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.costoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.costoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.costoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.costoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.costoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.latencyoptimizer` — LatencyOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 75 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.latencyoptimizer.v1`／`video.rubric.latencyoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower p95 than human-tuned pipeline
- **設計自評標準：** p50/p95 latency; throughput/GPU-hour
- **設計架構：** Tool-use profiling + automated pipeline restructuring

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.latencyoptimizer` 的 Q5 — 設計訊號：Lower p95 than human-tuned pipeline
- [ ] 協議路徑：business/video/evals/agents/video.latencyoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.latencyoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.latencyoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.latencyoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.latencyoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.latencyoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.latencyoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.retentionoptimizer` — RetentionOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 76 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.retentionoptimizer.v1`／`video.rubric.retentionoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats senior YouTube editor on AVD lift (A/B)
- **設計自評標準：** Predicted retention vs actual; AVD lift over control
- **設計架構：** RLAIF (reward = retention uplift from real analytics)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.retentionoptimizer` 的 Q5 — 設計訊號：Beats senior YouTube editor on AVD lift (A/B)
- [ ] 協議路徑：business/video/evals/agents/video.retentionoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.retentionoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.retentionoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.retentionoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.retentionoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.retentionoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.retentionoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.roasoptimizer` — ROASOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 77 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.roasoptimizer.v1`／`video.rubric.roasoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats senior marketer at equal budget
- **設計自評標準：** ROAS uplift vs control; significance ≥95%
- **設計架構：** RLAIF (reward = real ROAS from ad platform feedback)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.roasoptimizer` 的 Q5 — 設計訊號：Beats senior marketer at equal budget
- [ ] 協議路徑：business/video/evals/agents/video.roasoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.roasoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.roasoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.roasoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.roasoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.roasoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.roasoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 78 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.accessibilityoptimizer.v1`／`video.rubric.accessibilityoptimizer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches more a11y defects than ADA-certified auditor
- **設計自評標準：** Conformance 100% AA, ≥90% AAA; caption WER ≤2%
- **設計架構：** Constitutional AI (constitution = WCAG 2.2 success criteria)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.accessibilityoptimizer` 的 Q5 — 設計訊號：Catches more a11y defects than ADA-certified auditor
- [ ] 協議路徑：business/video/evals/agents/video.accessibilityoptimizer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.accessibilityoptimizer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.accessibilityoptimizer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.accessibilityoptimizer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.accessibilityoptimizer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.accessibilityoptimizer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.accessibilityoptimizer` 成熟度 **11.0** 且 11 個「是」

### `video.evaluationharness` — EvaluationHarnessAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 79 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.evaluationharness.v1`／`video.rubric.evaluationharness.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches regressions faster than ML-eng rotation
- **設計自評標準：** Regression precision/recall; alert latency <1h
- **設計架構：** Tool-use / ReAct (run benchmark → compare → alert if regressed)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.evaluationharness` 的 Q5 — 設計訊號：Catches regressions faster than ML-eng rotation
- [ ] 協議路徑：business/video/evals/agents/video.evaluationharness/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.evaluationharness`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.evaluationharness/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.evaluationharness --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.evaluationharness --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.evaluationharness` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.evaluationharness` 成熟度 **11.0** 且 11 個「是」

### `video.safetyredteam` — SafetyRedTeamAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `9-Meta` · **VA#：** 80 · **優先帶：** P1
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.safetyredteam.v1`／`video.rubric.safetyredteam.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Higher coverage than internal red-team rotation
- **設計自評標準：** Attack-success kept ≤1%; taxonomy coverage
- **設計架構：** Multi-agent debate (red-team vs defender) + adversarial search

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.safetyredteam` 的 Q5 — 設計訊號：Higher coverage than internal red-team rotation
- [ ] 協議路徑：business/video/evals/agents/video.safetyredteam/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.safetyredteam`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.safetyredteam/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.safetyredteam --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.safetyredteam --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.safetyredteam` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.safetyredteam` 成熟度 **11.0** 且 11 個「是」

### `video.director` — DirectorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 1 · **優先帶：** P2
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.director.v1`／`video.rubric.director.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins ≥55% blind pairwise vs DGA cuts (Arena)
- **設計自評標準：** Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior
- **設計架構：** Self-Refine + LLM-as-Judge (rubric: genre priors)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.director` 的 Q5 — 設計訊號：Wins ≥55% blind pairwise vs DGA cuts (Arena)
- [ ] 協議路徑：business/video/evals/agents/video.director/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.director`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.director/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.director --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.director --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.director` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.director` 成熟度 **11.0** 且 11 個「是」

### `video.producer` — ProducerAgent / EP （現況 10.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 2 · **優先帶：** P2
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.producer.v1`／`video.rubric.producer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats PGA schedules at 0.6× cost with equal CSAT
- **設計自評標準：** On-time delivery rate; budget variance <±5%; talent satisfaction (RLHF)
- **設計架構：** Agentic Graph (LangGraph DAG) + ReAct for tool calls

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.producer` 的 Q5 — 設計訊號：Beats PGA schedules at 0.6× cost with equal CSAT
- [ ] 協議路徑：business/video/evals/agents/video.producer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.producer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.producer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.producer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.producer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.producer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.producer` 成熟度 **11.0** 且 11 個「是」

### `video.screenwriter` — ScreenwriterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 3 · **優先帶：** P2
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.screenwriter.v1`／`video.rubric.screenwriter.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- **設計自評標準：** Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta
- **設計架構：** Reflexion (Shinn 2023) — verbal RL with episodic memory

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.screenwriter` 的 Q5 — 設計訊號：Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- [ ] 協議路徑：business/video/evals/agents/video.screenwriter/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.screenwriter`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.screenwriter/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.screenwriter --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.screenwriter --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.screenwriter` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.screenwriter` 成熟度 **11.0** 且 11 個「是」

### `video.showrunner` — ShowrunnerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 4 · **優先帶：** P2
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.showrunner.v1`／`video.rubric.showrunner.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- **設計自評標準：** Arc continuity score; character-thread completion; tonal variance within bounds
- **設計架構：** Multi-agent debate (Du 2023) + MemoryAgent retrieval

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.showrunner` 的 Q5 — 設計訊號：Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- [ ] 協議路徑：business/video/evals/agents/video.showrunner/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.showrunner`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.showrunner/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.showrunner --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.showrunner --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.showrunner` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.showrunner` 成熟度 **11.0** 且 11 個「是」

### `video.casting` — CastingAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `1-ATL` · **VA#：** 5 · **優先帶：** P2
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.casting.v1`／`video.rubric.casting.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats CSA casting in blind preference; hours vs weeks turnaround
- **設計自評標準：** Character-voice fit (audience preference); consent compliance 100%
- **設計架構：** LLM-as-Judge (pairwise preference on voice samples)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.casting` 的 Q5 — 設計訊號：Beats CSA casting in blind preference; hours vs weeks turnaround
- [ ] 協議路徑：business/video/evals/agents/video.casting/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.casting`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.casting/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.casting --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.casting --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.casting` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.casting` 成熟度 **11.0** 且 11 個「是」

### `video.editor` — EditorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 9 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.editor.v1`／`video.rubric.editor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.runway` · live_media=True
- **設計 surpass 訊號：** Wins ≥55% pairwise vs ACE-credited cuts
- **設計自評標準：** Pacing curve matches genre; Murch "Rule of Six" score; AVD ≥ target
- **設計架構：** Self-Refine (rubric: Murch Rule of Six)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.editor` 的 Q5 — 設計訊號：Wins ≥55% pairwise vs ACE-credited cuts
- [ ] 協議路徑：business/video/evals/agents/video.editor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.editor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.editor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.editor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.editor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.editor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.editor` 成熟度 **11.0** 且 11 個「是」

### `video.animator_2d` — AnimatorAgent (2D/3D) （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 12 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.animator_2d.v1`／`video.rubric.animator_2d.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.runway` · live_media=True
- **設計 surpass 訊號：** Beats junior on Annie rubric; equals senior at 5× throughput
- **設計自評標準：** 12-principles score; arc smoothness; lip-sync phoneme accuracy
- **設計架構：** Self-Refine (rubric: 12 principles checklist)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.animator_2d` 的 Q5 — 設計訊號：Beats junior on Annie rubric; equals senior at 5× throughput
- [ ] 協議路徑：business/video/evals/agents/video.animator_2d/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.animator_2d`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.animator_2d/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.animator_2d --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.animator_2d --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.animator_2d` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.animator_2d` 成熟度 **11.0** 且 11 個「是」

### `video.motiongraphics` — MotionGraphicsAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 13 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.motiongraphics.v1`／`video.rubric.motiongraphics.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.runway` · live_media=True
- **設計 surpass 訊號：** Wins agency RFP shootouts on speed + on-brand fidelity
- **設計自評標準：** Typographic hierarchy; brand compliance; readability at thumbnail
- **設計架構：** ReAct — reason about brand guidelines then render

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.motiongraphics` 的 Q5 — 設計訊號：Wins agency RFP shootouts on speed + on-brand fidelity
- [ ] 協議路徑：business/video/evals/agents/video.motiongraphics/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.motiongraphics`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.motiongraphics/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.motiongraphics --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.motiongraphics --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.motiongraphics` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.motiongraphics` 成熟度 **11.0** 且 11 個「是」

### `video.sounddesign` — SoundDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 19 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.sounddesign.v1`／`video.rubric.sounddesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.elevenlabs` · live_media=True
- **設計 surpass 訊號：** Wins MPSE pairwise on horror/sci-fi
- **設計自評標準：** Spectral diversity; sync ≤±1 frame; loudness -23 LUFS
- **設計架構：** ReAct (search SFX lib → validate sync → mix)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.sounddesign` 的 Q5 — 設計訊號：Wins MPSE pairwise on horror/sci-fi
- [ ] 協議路徑：business/video/evals/agents/video.sounddesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sounddesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.sounddesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.sounddesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.sounddesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.sounddesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.sounddesign` 成熟度 **11.0** 且 11 個「是」

### `video.voiceover` — VoiceOverAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 21 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.voiceover.v1`／`video.rubric.voiceover.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.elevenlabs` · live_media=True
- **設計 surpass 訊號：** Beats junior VO in blind preference; matches senior on emotion
- **設計自評標準：** Prosody match; pronunciation 100%; emotion tag match
- **設計架構：** LLM-as-Judge (MOS scoring rubric)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.voiceover` 的 Q5 — 設計訊號：Beats junior VO in blind preference; matches senior on emotion
- [ ] 協議路徑：business/video/evals/agents/video.voiceover/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.voiceover`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.voiceover/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.voiceover --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.voiceover --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.voiceover` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.voiceover` 成熟度 **11.0** 且 11 個「是」

### `video.creativedirector` — CreativeDirectorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 30 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.creativedirector.v1`／`video.rubric.creativedirector.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **設計 surpass 訊號：** Wins Cannes-jury-emulator gold vs human shortlists
- **設計自評標準：** Concept distinctiveness (embedding novelty); award-rubric predicted score
- **設計架構：** Multi-agent debate (panel of IdeationAgent + NoveltyAgent)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.creativedirector` 的 Q5 — 設計訊號：Wins Cannes-jury-emulator gold vs human shortlists
- [ ] 協議路徑：business/video/evals/agents/video.creativedirector/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.creativedirector`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.creativedirector/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.creativedirector --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.creativedirector --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.creativedirector` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.creativedirector` 成熟度 **11.0** 且 11 個「是」

### `video.audiobooknarrator` — AudiobookNarratorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 42 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.audiobooknarrator.v1`／`video.rubric.audiobooknarrator.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.elevenlabs` · live_media=True
- **設計 surpass 訊號：** Wins AudioFile blind eval at fraction of studio time
- **設計自評標準：** Vocal stamina (no drift 60min); character distinction (embedding distance)
- **設計架構：** Self-Refine (drift detection as feedback loop)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.audiobooknarrator` 的 Q5 — 設計訊號：Wins AudioFile blind eval at fraction of studio time
- [ ] 協議路徑：business/video/evals/agents/video.audiobooknarrator/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.audiobooknarrator`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.audiobooknarrator/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.audiobooknarrator --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.audiobooknarrator --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.audiobooknarrator` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.audiobooknarrator` 成熟度 **11.0** 且 11 個「是」

### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 46 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.promptengineer.v1`／`video.rubric.promptengineer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **設計 surpass 訊號：** Target shot in ≤3 iterations vs human avg 10
- **設計自評標準：** Prompt→output CLIP-T; iteration count to acceptance; seed reproducibility
- **設計架構：** DSPy / OPRO prompt optimization (Yang 2023)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.promptengineer` 的 Q5 — 設計訊號：Target shot in ≤3 iterations vs human avg 10
- [ ] 協議路徑：business/video/evals/agents/video.promptengineer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.promptengineer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.promptengineer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.promptengineer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.promptengineer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.promptengineer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.promptengineer` 成熟度 **11.0** 且 11 個「是」

### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 48 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.voiceclone.v1`／`video.rubric.voiceclone.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.elevenlabs` · live_media=True
- **設計 surpass 訊號：** Wins blind MOS vs professional ADR
- **設計自評標準：** Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified
- **設計架構：** Self-Refine + MOS scoring model as judge

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.voiceclone` 的 Q5 — 設計訊號：Wins blind MOS vs professional ADR
- [ ] 協議路徑：business/video/evals/agents/video.voiceclone/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.voiceclone`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.voiceclone/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.voiceclone --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.voiceclone --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.voiceclone` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.voiceclone` 成熟度 **11.0** 且 11 個「是」

### `video.archiveproducer` — ArchiveProducerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 105 · **優先帶：** P3
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.archiveproducer.v1`／`video.rubric.archiveproducer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **設計 surpass 訊號：** Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- **設計自評標準：** Source package completeness, rights coverage, provenance preservation
- **設計架構：** ReAct over archival manifests

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.archiveproducer` 的 Q5 — 設計訊號：Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- [ ] 協議路徑：business/video/evals/agents/video.archiveproducer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archiveproducer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.archiveproducer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.archiveproducer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.archiveproducer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.archiveproducer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.archiveproducer` 成熟度 **11.0** 且 11 個「是」

### `video.cinematographer` — CinematographerAgent (DoP) （現況 10.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 6 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.cinematographer.v1`／`video.rubric.cinematographer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats ASC peer-juried reels in blind aesthetic preference
- **設計自評標準：** Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency
- **設計架構：** Self-Refine + CLIP-based aesthetic scoring

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.cinematographer` 的 Q5 — 設計訊號：Beats ASC peer-juried reels in blind aesthetic preference
- [ ] 協議路徑：business/video/evals/agents/video.cinematographer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.cinematographer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.cinematographer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.cinematographer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.cinematographer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.cinematographer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.cinematographer` 成熟度 **11.0** 且 11 個「是」

### `video.cameraoperator` — CameraOperatorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 7 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.cameraoperator.v1`／`video.rubric.cameraoperator.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Focus-pull accuracy >99% vs SOC ~97% baseline
- **設計自評標準：** Frame steadiness, focus-hit %, action centering
- **設計架構：** ReAct (Yao 2022) — reason about framing then call renderer

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.cameraoperator` 的 Q5 — 設計訊號：Focus-pull accuracy >99% vs SOC ~97% baseline
- [ ] 協議路徑：business/video/evals/agents/video.cameraoperator/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.cameraoperator`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.cameraoperator/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.cameraoperator --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.cameraoperator --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.cameraoperator` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.cameraoperator` 成熟度 **11.0** 且 11 個「是」

### `video.dronepilot` — DronePilotAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `2-Cam` · **VA#：** 8 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.dronepilot.v1`／`video.rubric.dronepilot.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Competition-grade smoothness at 10× sortie rate; zero violations
- **設計自評標準：** Path smoothness; geofence compliance 100%; horizon stability
- **設計架構：** Constitutional AI (safety constitution: FAA rules as principles)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.dronepilot` 的 Q5 — 設計訊號：Competition-grade smoothness at 10× sortie rate; zero violations
- [ ] 協議路徑：business/video/evals/agents/video.dronepilot/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.dronepilot`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.dronepilot/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.dronepilot --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.dronepilot --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.dronepilot` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.dronepilot` 成熟度 **11.0** 且 11 個「是」

### `video.colorist` — ColoristAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 10 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.colorist.v1`／`video.rubric.colorist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats junior colorist in blind preference; matches senior within ΔE
- **設計自評標準：** ΔE drift <2; skin-tone IT8 alignment; mood vector match
- **設計架構：** Self-Refine + tool-use (colorimeter validation)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.colorist` 的 Q5 — 設計訊號：Beats junior colorist in blind preference; matches senior within ΔE
- [ ] 協議路徑：business/video/evals/agents/video.colorist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.colorist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.colorist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.colorist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.colorist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.colorist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.colorist` 成熟度 **11.0** 且 11 個「是」

### `video.vfxsupervisor` — VFXSupervisorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 11 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.vfxsupervisor.v1`／`video.rubric.vfxsupervisor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Weta-grade QC pass rate at fraction of time
- **設計自評標準：** Shot-completion %; comp-error pixel count; CLIP-T vs plate
- **設計架構：** Agentic Graph (fan-out per shot) + LLM-as-Judge (QC rubric)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.vfxsupervisor` 的 Q5 — 設計訊號：Weta-grade QC pass rate at fraction of time
- [ ] 協議路徑：business/video/evals/agents/video.vfxsupervisor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.vfxsupervisor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.vfxsupervisor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.vfxsupervisor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.vfxsupervisor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.vfxsupervisor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.vfxsupervisor` 成熟度 **11.0** 且 11 個「是」

### `video.storyboard` — StoryboardAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 14 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.storyboard.v1`／`video.rubric.storyboard.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Pixar story-trust pass rate at minutes per page
- **設計自評標準：** Shot-language fidelity; coverage completeness; staging clarity
- **設計架構：** Self-Refine (director feedback loop)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.storyboard` 的 Q5 — 設計訊號：Pixar story-trust pass rate at minutes per page
- [ ] 協議路徑：business/video/evals/agents/video.storyboard/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.storyboard`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.storyboard/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.storyboard --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.storyboard --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.storyboard` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.storyboard` 成熟度 **11.0** 且 11 個「是」

### `video.conceptartist` — ConceptArtistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 15 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.conceptartist.v1`／`video.rubric.conceptartist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins art-director shootouts on iteration speed
- **設計自評標準：** Style-bible adherence; silhouette readability; design coherence
- **設計架構：** Self-Refine + style-reference CLIP scoring

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.conceptartist` 的 Q5 — 設計訊號：Wins art-director shootouts on iteration speed
- [ ] 協議路徑：business/video/evals/agents/video.conceptartist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.conceptartist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.conceptartist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.conceptartist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.conceptartist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.conceptartist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.conceptartist` 成熟度 **11.0** 且 11 個「是」

### `video.productiondesign` — ProductionDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 16 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.productiondesign.v1`／`video.rubric.productiondesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins ADG blind comparisons on period-research depth
- **設計自評標準：** Period accuracy; palette coherence; build feasibility
- **設計架構：** Reflexion (stores period-research corrections in memory)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.productiondesign` 的 Q5 — 設計訊號：Wins ADG blind comparisons on period-research depth
- [ ] 協議路徑：business/video/evals/agents/video.productiondesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.productiondesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.productiondesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.productiondesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.productiondesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.productiondesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.productiondesign` 成熟度 **11.0** 且 11 個「是」

### `video.costumedesign` — CostumeDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 17 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.costumedesign.v1`／`video.rubric.costumedesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats CDG juniors on period accuracy benchmarks
- **設計自評標準：** Period/fashion accuracy; silhouette read; palette fit
- **設計架構：** Self-Refine (period-accuracy rubric)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.costumedesign` 的 Q5 — 設計訊號：Beats CDG juniors on period accuracy benchmarks
- [ ] 協議路徑：business/video/evals/agents/video.costumedesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.costumedesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.costumedesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.costumedesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.costumedesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.costumedesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.costumedesign` 成熟度 **11.0** 且 11 個「是」

### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX) （現況 10.5/11 → 目標 11.0）

- **類別：** `3-Edit` · **VA#：** 18 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.mua_makeup.v1`／`video.rubric.mua_makeup.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Continuity break rate <0.5% (vs ~2% human)
- **設計自評標準：** Continuity hash across takes; skin-tone realism (FID)
- **設計架構：** Constitutional AI (constitution: continuity rules)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.mua_makeup` 的 Q5 — 設計訊號：Continuity break rate <0.5% (vs ~2% human)
- [ ] 協議路徑：business/video/evals/agents/video.mua_makeup/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.mua_makeup`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.mua_makeup/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.mua_makeup --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.mua_makeup --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.mua_makeup` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.mua_makeup` 成熟度 **11.0** 且 11 個「是」

### `video.composer` — ComposerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 20 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.composer.v1`／`video.rubric.composer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins blind pairwise on emotional-fit vs working composers
- **設計自評標準：** Cue-to-emotion alignment (valence/arousal regression); thematic recurrence
- **設計架構：** Self-Refine + Emotional-Arc validation (biosignal proxy)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.composer` 的 Q5 — 設計訊號：Wins blind pairwise on emotional-fit vs working composers
- [ ] 協議路徑：business/video/evals/agents/video.composer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.composer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.composer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.composer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.composer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.composer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.composer` 成熟度 **11.0** 且 11 個「是」

### `video.soundmixer` — SoundMixerAgent (Re-recording) （現況 10.5/11 → 目標 11.0）

- **類別：** `4-Snd` · **VA#：** 22 · **優先帶：** P4
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.soundmixer.v1`／`video.rubric.soundmixer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** CAS spec on first pass without rework
- **設計自評標準：** LUFS target; STOI ≥0.85; spec-deliverable pass
- **設計架構：** Constitutional AI (constitution: broadcast-spec rules)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.soundmixer` 的 Q5 — 設計訊號：CAS spec on first pass without rework
- [ ] 協議路徑：business/video/evals/agents/video.soundmixer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.soundmixer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.soundmixer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.soundmixer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.soundmixer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.soundmixer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.soundmixer` 成熟度 **11.0** 且 11 個「是」

### `video.choreography` — ChoreographyAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 23 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.choreography.v1`／`video.rubric.choreography.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins blind preference vs choreographer drafts
- **設計自評標準：** Beat-sync accuracy; safety constraints; viral-pattern alignment
- **設計架構：** Self-Refine (rubric: beat-sync + safety)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.choreography` 的 Q5 — 設計訊號：Wins blind preference vs choreographer drafts
- [ ] 協議路徑：business/video/evals/agents/video.choreography/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.choreography`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.choreography/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.choreography --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.choreography --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.choreography` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.choreography` 成熟度 **11.0** 且 11 個「是」

### `video.musicvideodirector` — MusicVideoDirectorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 24 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.musicvideodirector.v1`／`video.rubric.musicvideodirector.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins label-blind preference vs commercial MV shortlist
- **設計自評標準：** Edit-rhythm sync; lookbook coherence; artist-brief fit
- **設計架構：** Multi-agent debate (with DirectorAgent + EditorAgent)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.musicvideodirector` 的 Q5 — 設計訊號：Wins label-blind preference vs commercial MV shortlist
- [ ] 協議路徑：business/video/evals/agents/video.musicvideodirector/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.musicvideodirector`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.musicvideodirector/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.musicvideodirector --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.musicvideodirector --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.musicvideodirector` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.musicvideodirector` 成熟度 **11.0** 且 11 個「是」

### `video.comedywriter` — ComedyWriterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 25 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.comedywriter.v1`／`video.rubric.comedywriter.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats UCB-table-read win rate on cold-reads
- **設計自評標準：** Joke-density; cold-open hook strength; predicted laughs/min
- **設計架構：** Reflexion (stores audience feedback in episodic memory)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.comedywriter` 的 Q5 — 設計訊號：Beats UCB-table-read win rate on cold-reads
- [ ] 協議路徑：business/video/evals/agents/video.comedywriter/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.comedywriter`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.comedywriter/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.comedywriter --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.comedywriter --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.comedywriter` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.comedywriter` 成熟度 **11.0** 且 11 個「是」

### `video.talent` — TalentAgent (On-camera) （現況 10.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 26 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.talent.v1`／`video.rubric.talent.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Hold-rate matches top creators in cohort
- **設計自評標準：** Emotion-target match; charisma score (audience proxy)
- **設計架構：** Self-Refine + emotion-regression validator

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.talent` 的 Q5 — 設計訊號：Hold-rate matches top creators in cohort
- [ ] 協議路徑：business/video/evals/agents/video.talent/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.talent`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.talent/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.talent --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.talent --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.talent` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.talent` 成熟度 **11.0** 且 11 個「是」

### `video.ugccreator` — UGCCreatorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `5-Perf` · **VA#：** 27 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.ugccreator.v1`／`video.rubric.ugccreator.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats paid-creator avg ROAS at 0.1× cost
- **設計自評標準：** Hook-rate ≥30%; "scripted" detector < threshold
- **設計架構：** RLAIF (reward from ROAS signal)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.ugccreator` 的 Q5 — 設計訊號：Beats paid-creator avg ROAS at 0.1× cost
- [ ] 協議路徑：business/video/evals/agents/video.ugccreator/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ugccreator`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.ugccreator/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.ugccreator --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.ugccreator --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.ugccreator` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.ugccreator` 成熟度 **11.0** 且 11 個「是」

### `video.socialmediastrategist` — SocialMediaStrategistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 28 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.socialmediastrategist.v1`／`video.rubric.socialmediastrategist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats agency social leads on 30-day reach lift
- **設計自評標準：** Predicted-vs-actual reach error; trend-timing latency <2h
- **設計架構：** ReAct (trend search → schedule → post)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.socialmediastrategist` 的 Q5 — 設計訊號：Beats agency social leads on 30-day reach lift
- [ ] 協議路徑：business/video/evals/agents/video.socialmediastrategist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.socialmediastrategist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.socialmediastrategist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.socialmediastrategist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.socialmediastrategist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.socialmediastrategist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.socialmediastrategist` 成熟度 **11.0** 且 11 個「是」

### `video.copywriter` — CopywriterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 29 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.copywriter.v1`／`video.rubric.copywriter.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins D&AD-style blind preference on ad briefs
- **設計自評標準：** Reading grade; hook-curiosity score; brand-voice cosine ≥0.85
- **設計架構：** Self-Refine (rubric: brand-voice similarity scorer)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.copywriter` 的 Q5 — 設計訊號：Wins D&AD-style blind preference on ad briefs
- [ ] 協議路徑：business/video/evals/agents/video.copywriter/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.copywriter`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.copywriter/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.copywriter --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.copywriter --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.copywriter` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.copywriter` 成熟度 **11.0** 且 11 個「是」

### `video.performancemarketer` — PerformanceMarketerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `6-Dist` · **VA#：** 31 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.performancemarketer.v1`／`video.rubric.performancemarketer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats senior media buyer on 30-day ROAS
- **設計自評標準：** ROAS uplift vs control; significance ≥95%
- **設計架構：** RLAIF (reward = ROAS uplift signal from ad platform)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.performancemarketer` 的 Q5 — 設計訊號：Beats senior media buyer on 30-day ROAS
- [ ] 協議路徑：business/video/evals/agents/video.performancemarketer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.performancemarketer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.performancemarketer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.performancemarketer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.performancemarketer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.performancemarketer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.performancemarketer` 成熟度 **11.0** 且 11 個「是」

### `video.avatardesign` — AvatarDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 47 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.avatardesign.v1`／`video.rubric.avatardesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** C2PA-verifiable + Partnership-on-AI full-pass at scale
- **設計自評標準：** Identity-hash consistency across shots; consent chain; C2PA signed
- **設計架構：** Constitutional AI (consent + identity constitution)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.avatardesign` 的 Q5 — 設計訊號：C2PA-verifiable + Partnership-on-AI full-pass at scale
- [ ] 協議路徑：business/video/evals/agents/video.avatardesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.avatardesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.avatardesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.avatardesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.avatardesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.avatardesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.avatardesign` 成熟度 **11.0** 且 11 個「是」

### `video.aiqaconsistency` — AIQAConsistencyAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 49 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.aiqaconsistency.v1`／`video.rubric.aiqaconsistency.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches >95% of senior QC catches + 30% missed
- **設計自評標準：** Per-frame artifact score; identity-hash drift; hand/finger pass
- **設計架構：** Tool-use / ReAct (run detectors → flag → report)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.aiqaconsistency` 的 Q5 — 設計訊號：Catches >95% of senior QC catches + 30% missed
- [ ] 協議路徑：business/video/evals/agents/video.aiqaconsistency/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.aiqaconsistency`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.aiqaconsistency/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.aiqaconsistency --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.aiqaconsistency --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.aiqaconsistency` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.aiqaconsistency` 成熟度 **11.0** 且 11 個「是」

### `video.personalizationengineer` — PersonalizationEngineerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 50 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.personalizationengineer.v1`／`video.rubric.personalizationengineer.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Higher share-rate than top human-templated campaigns
- **設計自評標準：** Render-success ≥99.5%; spot-check pass; privacy-audit pass
- **設計架構：** ReAct (assemble template → render → validate → deliver)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.personalizationengineer` 的 Q5 — 設計訊號：Higher share-rate than top human-templated campaigns
- [ ] 協議路徑：business/video/evals/agents/video.personalizationengineer/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.personalizationengineer`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.personalizationengineer/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.personalizationengineer --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.personalizationengineer --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.personalizationengineer` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.personalizationengineer` 成熟度 **11.0** 且 11 個「是」

### `video.trailereditor` — TrailerEditorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 51 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.trailereditor.v1`／`video.rubric.trailereditor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins Golden-Trailer-rubric blind comparison
- **設計自評標準：** Hook-rate at 3s; rising-action curve; music-sync precision
- **設計架構：** Self-Refine (retention-curve model as feedback)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.trailereditor` 的 Q5 — 設計訊號：Wins Golden-Trailer-rubric blind comparison
- [ ] 協議路徑：business/video/evals/agents/video.trailereditor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trailereditor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.trailereditor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.trailereditor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.trailereditor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.trailereditor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.trailereditor` 成熟度 **11.0** 且 11 個「是」

### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp （現況 10.5/11 → 目標 11.0）

- **類別：** `8-AI` · **VA#：** 52 · **優先帶：** P5
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.sportsanalyst.v1`／`video.rubric.sportsanalyst.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats ex-athlete on tactical-prediction
- **設計自評標準：** Play-call accuracy; on-screen clarity score
- **設計架構：** ReAct (fetch play data → annotate → render overlay)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.sportsanalyst` 的 Q5 — 設計訊號：Beats ex-athlete on tactical-prediction
- [ ] 協議路徑：business/video/evals/agents/video.sportsanalyst/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sportsanalyst`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.sportsanalyst/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.sportsanalyst --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.sportsanalyst --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.sportsanalyst` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.sportsanalyst` 成熟度 **11.0** 且 11 個「是」

### `video.instructionaldesign` — InstructionalDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 32 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.instructionaldesign.v1`／`video.rubric.instructionaldesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats ATD-credentialed ID on retention RCT
- **設計自評標準：** Bloom-level mapping; completion ≥70%; Kirkpatrick L2 quiz ≥80%
- **設計架構：** Self-Refine (rubric: Bloom/Kirkpatrick)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.instructionaldesign` 的 Q5 — 設計訊號：Beats ATD-credentialed ID on retention RCT
- [ ] 協議路徑：business/video/evals/agents/video.instructionaldesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.instructionaldesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.instructionaldesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.instructionaldesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.instructionaldesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.instructionaldesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.instructionaldesign` 成熟度 **11.0** 且 11 個「是」

### `video.sme` — SMEAgent (Subject-Matter Expert) （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 33 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.sme.v1`／`video.rubric.sme.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Passes same certification as human pro
- **設計自評標準：** Citation density; benchmark exam pass; hallucination ≤0.5%
- **設計架構：** Multi-agent debate + RAG retrieval

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.sme` 的 Q5 — 設計訊號：Passes same certification as human pro
- [ ] 協議路徑：business/video/evals/agents/video.sme/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sme`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.sme/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.sme --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.sme --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.sme` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.sme` 成熟度 **11.0** 且 11 個「是」

### `video.factchecker` — FactCheckerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 34 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.factchecker.v1`／`video.rubric.factchecker.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower correction rate than Pulitzer-tier outlets
- **設計自評標準：** Source-grade per claim (primary > secondary); cross-source ≥2
- **設計架構：** ReAct (extract claim → search → verify → grade)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.factchecker` 的 Q5 — 設計訊號：Lower correction rate than Pulitzer-tier outlets
- [ ] 協議路徑：business/video/evals/agents/video.factchecker/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.factchecker`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.factchecker/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.factchecker --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.factchecker --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.factchecker` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.factchecker` 成熟度 **11.0** 且 11 個「是」

### `video.medicalillustrator` — MedicalIllustratorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 35 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.medicalillustrator.v1`／`video.rubric.medicalillustrator.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** CMI peers vote ≥pass in blind review
- **設計自評標準：** Anatomical accuracy (detection model); AMI rubric
- **設計架構：** Self-Refine (rubric: AMI scoring criteria)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.medicalillustrator` 的 Q5 — 設計訊號：CMI peers vote ≥pass in blind review
- [ ] 協議路徑：business/video/evals/agents/video.medicalillustrator/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.medicalillustrator`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.medicalillustrator/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.medicalillustrator --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.medicalillustrator --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.medicalillustrator` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.medicalillustrator` 成熟度 **11.0** 且 11 個「是」

### `video.journalist` — JournalistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 36 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.journalist.v1`／`video.rubric.journalist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower correction rate + faster file vs newsroom
- **設計自評標準：** Source diversity; on-record ratio; ethical-checklist pass
- **設計架構：** Reflexion (ethical-checklist as verbal feedback)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.journalist` 的 Q5 — 設計訊號：Lower correction rate + faster file vs newsroom
- [ ] 協議路徑：business/video/evals/agents/video.journalist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.journalist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.journalist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.journalist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.journalist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.journalist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.journalist` 成熟度 **11.0** 且 11 個「是」

### `video.compliance` — ComplianceAgent (Legal) （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 37 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.compliance.v1`／`video.rubric.compliance.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lower legal-risk than median media-counsel
- **設計自評標準：** 100% rule-coverage; zero post-publish takedowns
- **設計架構：** Constitutional AI (constitution = compiled regulatory text)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.compliance` 的 Q5 — 設計訊號：Lower legal-risk than median media-counsel
- [ ] 協議路徑：business/video/evals/agents/video.compliance/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.compliance`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.compliance/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.compliance --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.compliance --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.compliance` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.compliance` 成熟度 **11.0** 且 11 個「是」

### `video.finance` — FinanceAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 38 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.finance.v1`／`video.rubric.finance.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Passes CFA L3; lower retraction rate than analyst desks
- **設計自評標準：** Numerical accuracy 100%; SEC compliance
- **設計架構：** ReAct (fetch data → validate → compose)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.finance` 的 Q5 — 設計訊號：Passes CFA L3; lower retraction rate than analyst desks
- [ ] 協議路徑：business/video/evals/agents/video.finance/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.finance`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.finance/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.finance --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.finance --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.finance` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.finance` 成熟度 **11.0** 且 11 個「是」

### `video.foodstylist` — FoodStylistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 39 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.foodstylist.v1`／`video.rubric.foodstylist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins blind preference vs editorial food stylist
- **設計自評標準：** Visual appetite-appeal (aesthetic regressor); recipe accuracy
- **設計架構：** Self-Refine (aesthetic regressor as rubric)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.foodstylist` 的 Q5 — 設計訊號：Wins blind preference vs editorial food stylist
- [ ] 協議路徑：business/video/evals/agents/video.foodstylist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.foodstylist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.foodstylist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.foodstylist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.foodstylist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.foodstylist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.foodstylist` 成熟度 **11.0** 且 11 個「是」

### `video.travelcine` — TravelCineAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 40 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.travelcine.v1`／`video.rubric.travelcine.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins T+L preference at 0.1× sortie cost
- **設計自評標準：** Establishing-shot diversity; location-mood match
- **設計架構：** Self-Refine + geofence safety validator

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.travelcine` 的 Q5 — 設計訊號：Wins T+L preference at 0.1× sortie cost
- [ ] 協議路徑：business/video/evals/agents/video.travelcine/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.travelcine`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.travelcine/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.travelcine --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.travelcine --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.travelcine` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.travelcine` 成熟度 **11.0** 且 11 個「是」

### `video.childrensauthor` — ChildrensAuthorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 41 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.childrensauthor.v1`／`video.rubric.childrensauthor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats Caldecott-rubric predicted score
- **設計自評標準：** Lexile band match; Common-Sense-Media safety pass; rhyme score
- **設計架構：** Constitutional AI (child-safety constitution)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.childrensauthor` 的 Q5 — 設計訊號：Beats Caldecott-rubric predicted score
- [ ] 協議路徑：business/video/evals/agents/video.childrensauthor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.childrensauthor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.childrensauthor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.childrensauthor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.childrensauthor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.childrensauthor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.childrensauthor` 成熟度 **11.0** 且 11 個「是」

### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 43 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.signlanguageinterpreter.v1`／`video.rubric.signlanguageinterpreter.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Wins blind NAD-reviewer preference at scale
- **設計自評標準：** Sign accuracy (Deaf-reviewer vote); facial-grammar markers
- **設計架構：** RLAIF (reward from Deaf-community review panel)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.signlanguageinterpreter` 的 Q5 — 設計訊號：Wins blind NAD-reviewer preference at scale
- [ ] 協議路徑：business/video/evals/agents/video.signlanguageinterpreter/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.signlanguageinterpreter`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.signlanguageinterpreter/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.signlanguageinterpreter --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.signlanguageinterpreter --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.signlanguageinterpreter` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.signlanguageinterpreter` 成熟度 **11.0** 且 11 個「是」

### `video.localizationqa` — LocalizationQAAgent (Linguist) （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 44 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.localizationqa.v1`／`video.rubric.localizationqa.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Beats LSP human QA on MQM at 10× speed
- **設計自評標準：** MQM error/1k words; cultural-flag count
- **設計架構：** Self-Refine (rubric: MQM scoring framework)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.localizationqa` 的 Q5 — 設計訊號：Beats LSP human QA on MQM at 10× speed
- [ ] 協議路徑：business/video/evals/agents/video.localizationqa/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.localizationqa`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.localizationqa/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.localizationqa --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.localizationqa --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.localizationqa` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.localizationqa` 成熟度 **11.0** 且 11 個「是」

### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan （現況 10.5/11 → 目標 11.0）

- **類別：** `7-Edu` · **VA#：** 45 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.realestatephoto.v1`／`video.rubric.realestatephoto.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Listing-CTR uplift vs human-shot baseline
- **設計自評標準：** Vertical-line straightness; HDR stack; coverage %
- **設計架構：** ReAct (assess space → generate views → validate geometry)

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.realestatephoto` 的 Q5 — 設計訊號：Listing-CTR uplift vs human-shot baseline
- [ ] 協議路徑：business/video/evals/agents/video.realestatephoto/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.realestatephoto`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.realestatephoto/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.realestatephoto --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.realestatephoto --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.realestatephoto` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.realestatephoto` 成熟度 **11.0** 且 11 個「是」

### `video.analyst` — AnalystAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 81 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.analyst.v1`／`video.rubric.analyst.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Detects actionable performance shifts faster than human analyst rotations
- **設計自評標準：** KPI completeness; forecast-vs-actual variance within tolerance; insight-to-action turnaround
- **設計架構：** ReAct over telemetry + regression analysis

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.analyst` 的 Q5 — 設計訊號：Detects actionable performance shifts faster than human analyst rotations
- [ ] 協議路徑：business/video/evals/agents/video.analyst/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.analyst`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.analyst/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.analyst --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.analyst --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.analyst` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.analyst` 成熟度 **11.0** 且 11 個「是」

### `video.audiencesim` — AudienceSimAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 82 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.audiencesim.v1`／`video.rubric.audiencesim.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Predicts audience reaction earlier than conventional test-screen cycles
- **設計自評標準：** Preference stability across cohorts; retention-prediction accuracy; disagreement logging
- **設計架構：** LLM-as-Judge + pairwise preference panel

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.audiencesim` 的 Q5 — 設計訊號：Predicts audience reaction earlier than conventional test-screen cycles
- [ ] 協議路徑：business/video/evals/agents/video.audiencesim/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.audiencesim`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.audiencesim/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.audiencesim --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.audiencesim --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.audiencesim` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.audiencesim` 成熟度 **11.0** 且 11 個「是」

### `video.accessibility` — AccessibilityAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 83 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.accessibility.v1`／`video.rubric.accessibility.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Finds release-blocking accessibility issues before human audits do
- **設計自評標準：** Caption accuracy, AD completeness, contrast compliance, release-readiness
- **設計架構：** Constitutional AI with accessibility constitution

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.accessibility` 的 Q5 — 設計訊號：Finds release-blocking accessibility issues before human audits do
- [ ] 協議路徑：business/video/evals/agents/video.accessibility/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.accessibility`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.accessibility/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.accessibility --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.accessibility --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.accessibility` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.accessibility` 成熟度 **11.0** 且 11 個「是」

### `video.brand` — BrandAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 84 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.brand.v1`／`video.rubric.brand.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Holds cross-channel brand consistency better than fragmented human review
- **設計自評標準：** Brand-voice similarity, policy adherence, low deviation across assets
- **設計架構：** Self-Refine against brand constitution

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.brand` 的 Q5 — 設計訊號：Holds cross-channel brand consistency better than fragmented human review
- [ ] 協議路徑：business/video/evals/agents/video.brand/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.brand`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.brand/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.brand --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.brand --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.brand` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.brand` 成熟度 **11.0** 且 11 個「是」

### `video.brandstrategist` — BrandStrategistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 85 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.brandstrategist.v1`／`video.rubric.brandstrategist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Produces clearer brand-to-script translation than ad hoc human handoffs
- **設計自評標準：** Strategy coherence, differentiation strength, audience-message clarity
- **設計架構：** Multi-agent debate with BrandAgent and CreativeDirectorAgent

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.brandstrategist` 的 Q5 — 設計訊號：Produces clearer brand-to-script translation than ad hoc human handoffs
- [ ] 協議路徑：business/video/evals/agents/video.brandstrategist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.brandstrategist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.brandstrategist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.brandstrategist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.brandstrategist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.brandstrategist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.brandstrategist` 成熟度 **11.0** 且 11 個「是」

### `video.marketing` — MarketingAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 86 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.marketing.v1`／`video.rubric.marketing.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Ships multi-channel launch packages faster than manual campaign ops
- **設計自評標準：** Metadata completeness, asset readiness, launch sequencing accuracy
- **設計架構：** ReAct over launch checklists and channel requirements

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.marketing` 的 Q5 — 設計訊號：Ships multi-channel launch packages faster than manual campaign ops
- [ ] 協議路徑：business/video/evals/agents/video.marketing/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.marketing`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.marketing/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.marketing --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.marketing --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.marketing` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.marketing` 成熟度 **11.0** 且 11 個「是」

### `video.seo` — SEOAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 87 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.seo.v1`／`video.rubric.seo.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Lifts discoverability faster than manual metadata tuning
- **設計自評標準：** Keyword fit, metadata completeness, search-intent match
- **設計架構：** ReAct with search-intent validation

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.seo` 的 Q5 — 設計訊號：Lifts discoverability faster than manual metadata tuning
- [ ] 協議路徑：business/video/evals/agents/video.seo/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.seo`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.seo/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.seo --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.seo --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.seo` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.seo` 成熟度 **11.0** 且 11 個「是」

### `video.community` — CommunityAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 88 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.community.v1`／`video.rubric.community.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Surfaces emerging audience concerns earlier than manual comment review
- **設計自評標準：** Response latency, issue clustering quality, sentiment tracking accuracy
- **設計架構：** Reflexion from post-launch audience feedback

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.community` 的 Q5 — 設計訊號：Surfaces emerging audience concerns earlier than manual comment review
- [ ] 協議路徑：business/video/evals/agents/video.community/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.community`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.community/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.community --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.community --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.community` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.community` 成熟度 **11.0** 且 11 個「是」

### `video.templatedesign` — TemplateDesignAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 89 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.templatedesign.v1`／`video.rubric.templatedesign.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Produces reusable templates with fewer breakages than manual design variants
- **設計自評標準：** Merge-field robustness, layout stability, render survivability
- **設計架構：** ReAct on template schemas and render constraints

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.templatedesign` 的 Q5 — 設計訊號：Produces reusable templates with fewer breakages than manual design variants
- [ ] 協議路徑：business/video/evals/agents/video.templatedesign/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.templatedesign`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.templatedesign/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.templatedesign --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.templatedesign --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.templatedesign` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.templatedesign` 成熟度 **11.0** 且 11 個「是」

### `video.ux` — UXAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 90 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.ux.v1`／`video.rubric.ux.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Flags user confusion earlier than launch-stage support teams
- **設計自評標準：** Readability, friction-point detection, user-flow clarity
- **設計架構：** LLM-as-Judge with UX rubric

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.ux` 的 Q5 — 設計訊號：Flags user confusion earlier than launch-stage support teams
- [ ] 協議路徑：business/video/evals/agents/video.ux/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ux`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.ux/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.ux --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.ux --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.ux` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.ux` 成熟度 **11.0** 且 11 個「是」

### `video.trustsafety` — TrustSafetyAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 91 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.trustsafety.v1`／`video.rubric.trustsafety.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches misuse risk earlier than generic moderation queues
- **設計自評標準：** Policy hit rate, abuse-risk recall, low false negatives on blocked cases
- **設計架構：** Constitutional AI for trust-and-safety policy enforcement

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.trustsafety` 的 Q5 — 設計訊號：Catches misuse risk earlier than generic moderation queues
- [ ] 協議路徑：business/video/evals/agents/video.trustsafety/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trustsafety`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.trustsafety/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.trustsafety --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.trustsafety --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.trustsafety` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.trustsafety` 成熟度 **11.0** 且 11 個「是」

### `video.crm` — CRMAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 92 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.crm.v1`／`video.rubric.crm.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Executes segmentation-to-delivery flow faster than manual ops
- **設計自評標準：** Audience-segment correctness, delivery readiness, trigger accuracy
- **設計架構：** ReAct over trigger and audience schemas

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.crm` 的 Q5 — 設計訊號：Executes segmentation-to-delivery flow faster than manual ops
- [ ] 協議路徑：business/video/evals/agents/video.crm/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.crm`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.crm/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.crm --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.crm --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.crm` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.crm` 成熟度 **11.0** 且 11 個「是」

### `video.legal` — LegalAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 93 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.legal.v1`／`video.rubric.legal.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Reduces late-stage legal surprises relative to fragmented legal review
- **設計自評標準：** Issue identification recall, sign-off completeness, escalation quality
- **設計架構：** Human-in-the-loop escalation + constitutional review

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.legal` 的 Q5 — 設計訊號：Reduces late-stage legal surprises relative to fragmented legal review
- [ ] 協議路徑：business/video/evals/agents/video.legal/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.legal`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.legal/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.legal --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.legal --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.legal` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.legal` 成熟度 **11.0** 且 11 個「是」

### `video.festivalstrategist` — FestivalStrategistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 94 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.festivalstrategist.v1`／`video.rubric.festivalstrategist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Improves submission targeting versus generic release planning
- **設計自評標準：** Fit-to-festival strength, package readiness, timing discipline
- **設計架構：** ReAct with calendar and package validation

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.festivalstrategist` 的 Q5 — 設計訊號：Improves submission targeting versus generic release planning
- [ ] 協議路徑：business/video/evals/agents/video.festivalstrategist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.festivalstrategist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.festivalstrategist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.festivalstrategist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.festivalstrategist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.festivalstrategist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.festivalstrategist` 成熟度 **11.0** 且 11 個「是」

### `video.lms` — LMSAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 96 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.lms.v1`／`video.rubric.lms.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Ships publishable learning packages faster than manual course ops
- **設計自評標準：** Package validity, tracking integrity, deploy success rate
- **設計架構：** ReAct over LMS deployment schema

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.lms` 的 Q5 — 設計訊號：Ships publishable learning packages faster than manual course ops
- [ ] 協議路徑：business/video/evals/agents/video.lms/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.lms`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.lms/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.lms --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.lms --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.lms` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.lms` 成熟度 **11.0** 且 11 個「是」

### `video.learnersim` — LearnerSimAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 97 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.learnersim.v1`／`video.rubric.learnersim.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Predicts weak spots before live learner complaints emerge
- **設計自評標準：** Friction-point prediction, completion accuracy, simulated quiz realism
- **設計架構：** Audience-style simulation adapted for learning outcomes

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.learnersim` 的 Q5 — 設計訊號：Predicts weak spots before live learner complaints emerge
- [ ] 協議路徑：business/video/evals/agents/video.learnersim/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.learnersim`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.learnersim/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.learnersim --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.learnersim --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.learnersim` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.learnersim` 成熟度 **11.0** 且 11 個「是」

### `video.continuity` — ContinuityAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 98 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.continuity.v1`／`video.rubric.continuity.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches continuity breaks earlier than end-of-post review
- **設計自評標準：** State-drift detection, scene-to-scene consistency, manifest update correctness
- **設計架構：** Tool-use / ReAct with continuity manifest enforcement

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.continuity` 的 Q5 — 設計訊號：Catches continuity breaks earlier than end-of-post review
- [ ] 協議路徑：business/video/evals/agents/video.continuity/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.continuity`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.continuity/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.continuity --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.continuity --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.continuity` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.continuity` 成熟度 **11.0** 且 11 個「是」

### `video.lipsync` — LipSyncAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 99 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.lipsync.v1`／`video.rubric.lipsync.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Finds sync drift more precisely than general QC review
- **設計自評標準：** Sync error below threshold, correction specificity, low false positives
- **設計架構：** Self-Refine around sync validator outputs

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.lipsync` 的 Q5 — 設計訊號：Finds sync drift more precisely than general QC review
- [ ] 協議路徑：business/video/evals/agents/video.lipsync/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.lipsync`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.lipsync/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.lipsync --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.lipsync --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.lipsync` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.lipsync` 成熟度 **11.0** 且 11 個「是」

### `video.musicsupervisor` — MusicSupervisorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 100 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.musicsupervisor.v1`／`video.rubric.musicsupervisor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Coordinates music placements more consistently than fragmented handoffs
- **設計自評標準：** Cue suitability, rights-awareness coverage, soundtrack-package completeness
- **設計架構：** ReAct over cue sheets and rights requirements

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.musicsupervisor` 的 Q5 — 設計訊號：Coordinates music placements more consistently than fragmented handoffs
- [ ] 協議路徑：business/video/evals/agents/video.musicsupervisor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.musicsupervisor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.musicsupervisor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.musicsupervisor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.musicsupervisor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.musicsupervisor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.musicsupervisor` 成熟度 **11.0** 且 11 個「是」

### `video.labela_r` — LabelA&RAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 101 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.labela_r.v1`／`video.rubric.labela_r.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Aligns music creative faster than disconnected stakeholder threads
- **設計自評標準：** Artist-fit quality, release positioning, feedback turnaround
- **設計架構：** Multi-agent debate with music stakeholders

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.labela_r` 的 Q5 — 設計訊號：Aligns music creative faster than disconnected stakeholder threads
- [ ] 協議路徑：business/video/evals/agents/video.labela_r/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.labela_r`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.labela_r/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.labela_r --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.labela_r --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.labela_r` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.labela_r` 成熟度 **11.0** 且 11 個「是」

### `video.labeldigital` — LabelDigitalAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 102 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.labeldigital.v1`／`video.rubric.labeldigital.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Delivers cleaner label-side packages than ad hoc release ops
- **設計自評標準：** Metadata completeness, rollout timing, channel readiness
- **設計架構：** ReAct on release package requirements

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.labeldigital` 的 Q5 — 設計訊號：Delivers cleaner label-side packages than ad hoc release ops
- [ ] 協議路徑：business/video/evals/agents/video.labeldigital/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.labeldigital`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.labeldigital/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.labeldigital --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.labeldigital --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.labeldigital` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.labeldigital` 成熟度 **11.0** 且 11 個「是」

### `video.deepfakedetection` — DeepfakeDetectionAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 103 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.deepfakedetection.v1`／`video.rubric.deepfakedetection.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Catches deceptive synthetic markers that generic QC misses
- **設計自評標準：** Forensic recall, false-negative control, provenance-validation accuracy
- **設計架構：** Tool-use / ReAct with forensic scoring

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.deepfakedetection` 的 Q5 — 設計訊號：Catches deceptive synthetic markers that generic QC misses
- [ ] 協議路徑：business/video/evals/agents/video.deepfakedetection/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.deepfakedetection`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.deepfakedetection/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.deepfakedetection --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.deepfakedetection --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.deepfakedetection` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.deepfakedetection` 成熟度 **11.0** 且 11 個「是」

### `video.comms` — CommsAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 104 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.comms.v1`／`video.rubric.comms.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Produces faster aligned responses than fragmented stakeholder messaging
- **設計自評標準：** Message consistency, disclosure completeness, escalation quality
- **設計架構：** ReAct with approval chains

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.comms` 的 Q5 — 設計訊號：Produces faster aligned responses than fragmented stakeholder messaging
- [ ] 協議路徑：business/video/evals/agents/video.comms/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.comms`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.comms/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.comms --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.comms --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.comms` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.comms` 成熟度 **11.0** 且 11 個「是」

### `video.standardseditor` — StandardsEditorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 106 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.standardseditor.v1`／`video.rubric.standardseditor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Reduces standards drift better than late-stage copy edits
- **設計自評標準：** Standards-compliance rate, attribution accuracy, corrections readiness
- **設計架構：** Constitutional AI with editorial standards constitution

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.standardseditor` 的 Q5 — 設計訊號：Reduces standards drift better than late-stage copy edits
- [ ] 協議路徑：business/video/evals/agents/video.standardseditor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.standardseditor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.standardseditor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.standardseditor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.standardseditor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.standardseditor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.standardseditor` 成熟度 **11.0** 且 11 個「是」

### `video.ethics` — EthicsAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 107 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.ethics.v1`／`video.rubric.ethics.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Surfaces release risks earlier than reactive ethics review
- **設計自評標準：** Ethical issue recall, mitigation clarity, escalation precision
- **設計架構：** Multi-agent debate + constitutional review

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.ethics` 的 Q5 — 設計訊號：Surfaces release risks earlier than reactive ethics review
- [ ] 協議路徑：business/video/evals/agents/video.ethics/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ethics`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.ethics/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.ethics --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.ethics --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.ethics` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.ethics` 成熟度 **11.0** 且 11 個「是」

### `video.channelmanager` — ChannelManagerAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 108 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.channelmanager.v1`／`video.rubric.channelmanager.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Improves publishing discipline over manual channel operations
- **設計自評標準：** Publishing readiness, cadence stability, metadata completeness
- **設計架構：** ReAct with publishing runbooks

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.channelmanager` 的 Q5 — 設計訊號：Improves publishing discipline over manual channel operations
- [ ] 協議路徑：business/video/evals/agents/video.channelmanager/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.channelmanager`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.channelmanager/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.channelmanager --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.channelmanager --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.channelmanager` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.channelmanager` 成熟度 **11.0** 且 11 個「是」

### `video.corrections` — CorrectionsAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 109 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.corrections.v1`／`video.rubric.corrections.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Resolves post-release issues faster than unstructured incident handling
- **設計自評標準：** Correction turnaround, version replacement accuracy, notice completeness
- **設計架構：** ReAct over correction and replacement workflows

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.corrections` 的 Q5 — 設計訊號：Resolves post-release issues faster than unstructured incident handling
- [ ] 協議路徑：business/video/evals/agents/video.corrections/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.corrections`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.corrections/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.corrections --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.corrections --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.corrections` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.corrections` 成熟度 **11.0** 且 11 個「是」

### `video.mpa` — MPAAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 110 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.mpa.v1`／`video.rubric.mpa.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Prepares cleaner feature-release classification packages than manual prep
- **設計自評標準：** Rating-package completeness, advisory clarity, escalation quality
- **設計架構：** Human-in-the-loop with structured packaging support

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.mpa` 的 Q5 — 設計訊號：Prepares cleaner feature-release classification packages than manual prep
- [ ] 協議路徑：business/video/evals/agents/video.mpa/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.mpa`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.mpa/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.mpa --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.mpa --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.mpa` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.mpa` 成熟度 **11.0** 且 11 個「是」

### `video.sales` — SalesAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 111 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.sales.v1`／`video.rubric.sales.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Produces sales-ready release packets faster than manual assembly
- **設計自評標準：** Buyer-package completeness, rights clarity, market-fit packaging
- **設計架構：** ReAct over buyer package requirements

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.sales` 的 Q5 — 設計訊號：Produces sales-ready release packets faster than manual assembly
- [ ] 協議路徑：business/video/evals/agents/video.sales/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sales`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.sales/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.sales --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.sales --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.sales` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.sales` 成熟度 **11.0** 且 11 個「是」

### `video.distributor` — DistributorAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 112 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.distributor.v1`／`video.rubric.distributor.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Reduces delivery-spec mismatches relative to fragmented delivery ops
- **設計自評標準：** Outlet-spec compliance, handoff completeness, territorial routing accuracy
- **設計架構：** ReAct over distribution specification matrices

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.distributor` 的 Q5 — 設計訊號：Reduces delivery-spec mismatches relative to fragmented delivery ops
- [ ] 協議路徑：business/video/evals/agents/video.distributor/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.distributor`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.distributor/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.distributor --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.distributor --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.distributor` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.distributor` 成熟度 **11.0** 且 11 個「是」

### `video.awardsstrategist` — AwardsStrategistAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 113 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.awardsstrategist.v1`／`video.rubric.awardsstrategist.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Improves awards-timing discipline over generic release planning
- **設計自評標準：** Submission readiness, category fit, timeline precision
- **設計架構：** ReAct with awards timeline optimization

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.awardsstrategist` 的 Q5 — 設計訊號：Improves awards-timing discipline over generic release planning
- [ ] 協議路徑：business/video/evals/agents/video.awardsstrategist/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.awardsstrategist`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.awardsstrategist/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.awardsstrategist --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.awardsstrategist --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.awardsstrategist` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.awardsstrategist` 成熟度 **11.0** 且 11 個「是」

### `video.archivemaster` — ArchiveMasterAgent （現況 10.5/11 → 目標 11.0）

- **類別：** `10-Sup` · **VA#：** 114 · **優先帶：** P6
- **儲存格：** 是=10 部分=1 否=0
- **Prompt／rubric：** `video.prompt.archivemaster.v1`／`video.rubric.archivemaster.v1` （檔案 1/1）
- **Harness：** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **工具：** `（無）` · live_media=False
- **設計 surpass 訊號：** Delivers more reliable archive packages than late-stage export-only workflows
- **設計自評標準：** Checksum integrity, preservation metadata completeness, archive package validity
- **設計架構：** Tool-use / ReAct with preservation validation

#### 邁向滿分狀態

| 問題 | 現況 | 目標 |
|------|------|------|
| Q1 SPEC 中的責任界定 | **是** | **是** |
| Q2 專業知識蒸餾計畫 | **是** | **是** |
| Q3 來源可用／可取得 | **是** | **是** |
| Q4 自評方法與內容 | **是** | **是** |
| Q5 超越人類（可量測） | **部分** | **是** |
| Q6 工作執行路徑 | **是** | **是** |
| Q7 Skills／plugins／harness | **是** | **是** |
| Q8 自我改進機制 | **是** | **是** |
| Q9 研究以改進 | **是** | **是** |
| Q10 協作／指令收發 | **是** | **是** |
| Q11 衝突解決與確認 | **是** | **是** |

#### 行動清單（全部完成）

**Q1 SPEC 中的責任界定**（現況 是 → 是）

- [ ] 維持「是」：每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。
- [ ] 保持 agent_spec.does_not_own 與 prompt System 區段對齊。
- [ ] user_guide.md 開頭句與 Responsibility 同步。

**Q2 專業知識蒸餾計畫**（現況 是 → 是）

- [ ] 維持「是」：每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。
- [ ] 蒸餾輸出連結 memory_namespace pack.video.<agent_id>。
- [ ] 對變更過的 agents 在 CI 做 distill schema dry-run。

**Q3 來源可用／可取得**（現況 是 → 是）

- [ ] 維持「是」：盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。
- [ ] 新增語料類別後更新 ACQUIRE.md 步驟。
- [ ] 摘錄變更時更新 PROVENANCE.json hash。

**Q4 自評方法與內容**（現況 是 → 是）

- [ ] 維持「是」：保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。
- [ ] agents.md Self-Quality Criteria 變更時重推維度。
- [ ] 確保 golden.json 仍要求 l1_passed＋artifact。

**Q5 超越人類（可量測）**（現況 部分 → 是）

- [ ] 主要缺口：關閉 `video.archivemaster` 的 Q5 — 設計訊號：Delivers more reliable archive packages than late-stage export-only workflows
- [ ] 協議路徑：business/video/evals/agents/video.archivemaster/human_baseline_protocol.json（status=measured，gate_met=False，synthetic=False）
- [ ] 若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archivemaster`
- [ ] 評分簡報（若有）：business/video/evals/rater_sessions/video.archivemaster/RATER_BRIEF.md
- [ ] 互動場次：`python scripts/business/record_human_baseline.py --session --agent video.archivemaster --rater <真實id> --evaluate`
- [ ] 或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent video.archivemaster --measure-agent --evaluate-gate`
- [ ] Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。
- [ ] 若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。

**Q6 工作執行路徑**（現況 是 → 是）

- [ ] 維持「是」：保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。
- [ ] 驗證 PackAgentLoader.load(agent_id) 離線成功。
- [ ] 以 PackGoldenRunner 保持 golden.json 全綠。
- [ ] 可選強化：以角色 mock adapters＋單元測試取代純 media.stub。

**Q7 Skills／plugins／harness**（現況 是 → 是）

- [ ] 維持「是」：維持 skills/SKILL.md＋integration.json＋bindings.json。
- [ ] 使用時驗證 special_skills 綁定路徑。
- [ ] 煙霧：host 無網路可載入 skill。

**Q8 自我改進機制**（現況 是 → 是）

- [ ] 維持「是」：保持 max_refinement_count 政策文件化。
- [ ] 變更 runner 時以 force_l2_fail_once 路徑做測試。
- [ ] 改進後重跑 golden＋baseline agent_measurement。

**Q9 研究以改進**（現況 是 → 是）

- [ ] 維持「是」：以 SOURCE_CATALOG＋ACQUIRE 做研究進場。
- [ ] 需要外部刷新時接研究型 meta-agents（先離線 fixtures）。
- [ ] 研究輸出放入 sources/research/ 並含 provenance。

**Q10 協作／指令收發**（現況 是 → 是）

- [ ] 維持「是」：保持 critique_edges 對齊 agents.md Accepts／Comments。
- [ ] 至少一條 partner edge 在整合測試證明 send＋receive（spine）。
- [ ] 所有 critique／handoff 帶 correlation_id。

**Q11 衝突解決與確認**（現況 是 → 是）

- [ ] 維持「是」：保持 blocker → requires_hitl 確認路徑。
- [ ] 未決爭議在 outputs allowlist 時導向 video.judge。
- [ ] 產品層確認僅用 action refs（不虛構權限）。

#### 此 agent 出場閘門

- [ ] `video.archivemaster` 離線 golden 仍通過
- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill
- [ ] 真實人類 n≥5，synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true
- [ ] audit 中 `video.archivemaster` 成熟度 **11.0** 且 11 個「是」

---

## 10. 實作佇列（優先序）

| 序 | 帶 | Agent | 現況 | 為何 |
|---:|----|-------|------|------|
| 1 | P0 | `video.orchestrator` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 2 | P0 | `video.planner` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 3 | P0 | `video.router` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 4 | P0 | `video.judge` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 5 | P0 | `video.gatekeeper` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 6 | P0 | `video.memory` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 7 | P0 | `video.critic` | 10.5 | 主幹 — 先評人類；解鎖協作信任 |
| 8 | P1 | `video.ideation` | 10.5 | 其餘 Meta |
| 9 | P1 | `video.narrativearc` | 10.5 | 其餘 Meta |
| 10 | P1 | `video.styletransfer` | 10.5 | 其餘 Meta |
| 11 | P1 | `video.worldbuilding` | 10.5 | 其餘 Meta |
| 12 | P1 | `video.moodboard` | 10.5 | 其餘 Meta |
| 13 | P1 | `video.novelty` | 10.5 | 其餘 Meta |
| 14 | P1 | `video.emotionalarc` | 10.5 | 其餘 Meta |
| 15 | P1 | `video.webresearch` | 10.5 | 其餘 Meta |
| 16 | P1 | `video.archiveresearch` | 10.5 | 其餘 Meta |
| 17 | P1 | `video.trendintelligence` | 10.5 | 其餘 Meta |
| 18 | P1 | `video.competitorintelligence` | 10.5 | 其餘 Meta |
| 19 | P1 | `video.citation` | 10.5 | 其餘 Meta |
| 20 | P1 | `video.interviewsynthesis` | 10.5 | 其餘 Meta |
| 21 | P1 | `video.benchmarkresearch` | 10.5 | 其餘 Meta |
| 22 | P1 | `video.promptoptimizer` | 10.5 | 其餘 Meta |
| 23 | P1 | `video.costoptimizer` | 10.5 | 其餘 Meta |
| 24 | P1 | `video.latencyoptimizer` | 10.5 | 其餘 Meta |
| 25 | P1 | `video.retentionoptimizer` | 10.5 | 其餘 Meta |
| 26 | P1 | `video.roasoptimizer` | 10.5 | 其餘 Meta |
| 27 | P1 | `video.accessibilityoptimizer` | 10.5 | 其餘 Meta |
| 28 | P1 | `video.evaluationharness` | 10.5 | 其餘 Meta |
| 29 | P1 | `video.safetyredteam` | 10.5 | 其餘 Meta |
| 30 | P2 | `video.director` | 10.5 | ATL 創作權威 |
| 31 | P2 | `video.producer` | 10.5 | ATL 創作權威 |
| 32 | P2 | `video.screenwriter` | 10.5 | ATL 創作權威 |
| 33 | P2 | `video.showrunner` | 10.5 | ATL 創作權威 |
| 34 | P2 | `video.casting` | 10.5 | ATL 創作權威 |
| 35 | P3 | `video.editor` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 36 | P3 | `video.animator_2d` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 37 | P3 | `video.motiongraphics` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 38 | P3 | `video.sounddesign` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 39 | P3 | `video.voiceover` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 40 | P3 | `video.creativedirector` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 41 | P3 | `video.audiobooknarrator` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 42 | P3 | `video.promptengineer` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 43 | P3 | `video.voiceclone` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 44 | P3 | `video.archiveproducer` | 10.5 | Live 媒體 agents — 基線需謹慎 |
| 45 | P4 | `video.cinematographer` | 10.5 | 核心工藝製作 |
| 46 | P4 | `video.cameraoperator` | 10.5 | 核心工藝製作 |
| 47 | P4 | `video.dronepilot` | 10.5 | 核心工藝製作 |
| 48 | P4 | `video.colorist` | 10.5 | 核心工藝製作 |
| 49 | P4 | `video.vfxsupervisor` | 10.5 | 核心工藝製作 |
| 50 | P4 | `video.storyboard` | 10.5 | 核心工藝製作 |
| 51 | P4 | `video.conceptartist` | 10.5 | 核心工藝製作 |
| 52 | P4 | `video.productiondesign` | 10.5 | 核心工藝製作 |
| 53 | P4 | `video.costumedesign` | 10.5 | 核心工藝製作 |
| 54 | P4 | `video.mua_makeup` | 10.5 | 核心工藝製作 |
| 55 | P4 | `video.composer` | 10.5 | 核心工藝製作 |
| 56 | P4 | `video.soundmixer` | 10.5 | 核心工藝製作 |
| 57 | P5 | `video.choreography` | 10.5 | 專門工藝／AI 時代 |
| 58 | P5 | `video.musicvideodirector` | 10.5 | 專門工藝／AI 時代 |
| 59 | P5 | `video.comedywriter` | 10.5 | 專門工藝／AI 時代 |
| 60 | P5 | `video.talent` | 10.5 | 專門工藝／AI 時代 |
| 61 | P5 | `video.ugccreator` | 10.5 | 專門工藝／AI 時代 |
| 62 | P5 | `video.socialmediastrategist` | 10.5 | 專門工藝／AI 時代 |
| 63 | P5 | `video.copywriter` | 10.5 | 專門工藝／AI 時代 |
| 64 | P5 | `video.performancemarketer` | 10.5 | 專門工藝／AI 時代 |
| 65 | P5 | `video.avatardesign` | 10.5 | 專門工藝／AI 時代 |
| 66 | P5 | `video.aiqaconsistency` | 10.5 | 專門工藝／AI 時代 |
| 67 | P5 | `video.personalizationengineer` | 10.5 | 專門工藝／AI 時代 |
| 68 | P5 | `video.trailereditor` | 10.5 | 專門工藝／AI 時代 |
| 69 | P5 | `video.sportsanalyst` | 10.5 | 專門工藝／AI 時代 |
| 70 | P6 | `video.instructionaldesign` | 10.5 | 支援與長尾 |
| 71 | P6 | `video.sme` | 10.5 | 支援與長尾 |
| 72 | P6 | `video.factchecker` | 10.5 | 支援與長尾 |
| 73 | P6 | `video.medicalillustrator` | 10.5 | 支援與長尾 |
| 74 | P6 | `video.journalist` | 10.5 | 支援與長尾 |
| 75 | P6 | `video.compliance` | 10.5 | 支援與長尾 |
| 76 | P6 | `video.finance` | 10.5 | 支援與長尾 |
| 77 | P6 | `video.foodstylist` | 10.5 | 支援與長尾 |
| 78 | P6 | `video.travelcine` | 10.5 | 支援與長尾 |
| 79 | P6 | `video.childrensauthor` | 10.5 | 支援與長尾 |
| 80 | P6 | `video.signlanguageinterpreter` | 10.5 | 支援與長尾 |
| 81 | P6 | `video.localizationqa` | 10.5 | 支援與長尾 |
| 82 | P6 | `video.realestatephoto` | 10.5 | 支援與長尾 |
| 83 | P6 | `video.analyst` | 10.5 | 支援與長尾 |
| 84 | P6 | `video.audiencesim` | 10.5 | 支援與長尾 |
| 85 | P6 | `video.accessibility` | 10.5 | 支援與長尾 |
| 86 | P6 | `video.brand` | 10.5 | 支援與長尾 |
| 87 | P6 | `video.brandstrategist` | 10.5 | 支援與長尾 |
| 88 | P6 | `video.marketing` | 10.5 | 支援與長尾 |
| 89 | P6 | `video.seo` | 10.5 | 支援與長尾 |
| 90 | P6 | `video.community` | 10.5 | 支援與長尾 |
| 91 | P6 | `video.templatedesign` | 10.5 | 支援與長尾 |
| 92 | P6 | `video.ux` | 10.5 | 支援與長尾 |
| 93 | P6 | `video.trustsafety` | 10.5 | 支援與長尾 |
| 94 | P6 | `video.crm` | 10.5 | 支援與長尾 |
| 95 | P6 | `video.legal` | 10.5 | 支援與長尾 |
| 96 | P6 | `video.festivalstrategist` | 10.5 | 支援與長尾 |
| 97 | P6 | `video.lms` | 10.5 | 支援與長尾 |
| 98 | P6 | `video.learnersim` | 10.5 | 支援與長尾 |
| 99 | P6 | `video.continuity` | 10.5 | 支援與長尾 |
| 100 | P6 | `video.lipsync` | 10.5 | 支援與長尾 |
| 101 | P6 | `video.musicsupervisor` | 10.5 | 支援與長尾 |
| 102 | P6 | `video.labela_r` | 10.5 | 支援與長尾 |
| 103 | P6 | `video.labeldigital` | 10.5 | 支援與長尾 |
| 104 | P6 | `video.deepfakedetection` | 10.5 | 支援與長尾 |
| 105 | P6 | `video.comms` | 10.5 | 支援與長尾 |
| 106 | P6 | `video.standardseditor` | 10.5 | 支援與長尾 |
| 107 | P6 | `video.ethics` | 10.5 | 支援與長尾 |
| 108 | P6 | `video.channelmanager` | 10.5 | 支援與長尾 |
| 109 | P6 | `video.corrections` | 10.5 | 支援與長尾 |
| 110 | P6 | `video.mpa` | 10.5 | 支援與長尾 |
| 111 | P6 | `video.sales` | 10.5 | 支援與長尾 |
| 112 | P6 | `video.distributor` | 10.5 | 支援與長尾 |
| 113 | P6 | `video.awardsstrategist` | 10.5 | 支援與長尾 |
| 114 | P6 | `video.archivemaster` | 10.5 | 支援與長尾 |

---

## 11. 操作者指令

```bash
python scripts/business/baseline_status.py
python scripts/business/prepare_rater_sessions_v1.py
python scripts/business/record_human_baseline.py --clear-synthetic --agents \
  video.orchestrator video.planner video.router video.judge \
  video.gatekeeper video.critic video.memory
python scripts/business/record_human_baseline.py --session \
  --agent video.orchestrator --rater alice --evaluate
python scripts/business/run_pack_agent_golden.py --spine
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v2.py
python scripts/business/report_improvement_plan_completion.py
python scripts/business/render_agent_improvement_plan_v2.py
python scripts/business/render_agent_improvement_plan_v2_hk.py
```

---

## 12. 剩餘估算

| 工作項 | 單位 | 數量 | 備註 |
|--------|------|-----:|------|
| 真實人類 trial 組 | agent | 114 | 各 ≥5；主要成本 |
| 閘門評估 | agent | 114 | trials 後自動化 |
| 重測 agent 離線 | agent | 視需要 | prompt 變更後 |
| 可選 tool mocks | 工具類 | ~20–40 | Q5 YES 非必須 |

**時程提示：** Spine（7）→ ATL（5）→ 每週約 10 個工藝 agents。

---

## 13. 治理（防止假滿分）

1. **無證據不可 Q5「是」** — audit 讀 gate.met && !synthetic。
2. **record_human_baseline.py 拒絕真實場次使用 --synthetic**。
3. **任何 prompt/rubric 變更後 golden 必須仍綠。**
4. **產品 UI 的 HiTL 確認僅用 action refs。**
5. **完成度報告須顯示 claimable surpass 數量**，而非只數協議檔。

---

## 14. 重新產生

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v2.py
python scripts/business/render_agent_improvement_plan_v2.py
python scripts/business/render_agent_improvement_plan_v2_hk.py
python scripts/business/report_improvement_plan_completion.py
```

追蹤進度：成熟度 **10.5 → 11.0**，加權 **95.45% → 100%**，Q5 是 **0 → 114**。

本檔為繁體中文版 `agent_improvement_plan_v2.md`；技術 ID／路徑／指令保留原文。

