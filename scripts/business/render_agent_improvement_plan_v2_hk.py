#!/usr/bin/env python3
"""Render agent_improvement_plan_v2_hk.md (Traditional Chinese).

Mirrors agent_improvement_plan_v2.md; technical IDs/paths/commands stay English.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_COMPLETION = _ROOT / "agent_improvement_plan_completion_v1.json"
_OUT = _ROOT / "agent_improvement_plan_v2_hk.md"

CATEGORY_ORDER = [
    "1-ATL",
    "2-Cam",
    "3-Edit",
    "4-Snd",
    "5-Perf",
    "6-Dist",
    "7-Edu",
    "8-AI",
    "9-Meta",
    "10-Sup",
]

CATEGORY_LABELS = {
    "1-ATL": "Above-the-Line（製片主創）",
    "2-Cam": "Camera & Lighting（攝影燈光）",
    "3-Edit": "Editorial & Color / Design（剪接調光設計）",
    "4-Snd": "Sound & Music（聲音音樂）",
    "5-Perf": "Performance & Choreography（表演編舞）",
    "6-Dist": "Distribution & Marketing（發行行銷）",
    "7-Edu": "Education & Domain-Expert（教育與領域專家）",
    "8-AI": "AI-Era Specialists（AI 時代專才）",
    "9-Meta": "Specialist Meta-Agents（元代理／平台）",
    "10-Sup": "Workflow Support（流程支援）",
}

STATUS_ZH = {"yes": "是", "partial": "部分", "no": "否"}

Q_META = [
    (
        "q1_responsibility",
        "Q1 SPEC 中的責任界定",
        "身分與 owns／does_not_own 精確、唯一，並在 runtime 注入。",
        [
            "每次 SPEC 編輯維持 ## Responsibility 唯一性 CI。",
            "保持 agent_spec.does_not_own 與 prompt System 區段對齊。",
            "user_guide.md 開頭句與 Responsibility 同步。",
            "L1 loader 檢查必須持續要求 prompt 含 Responsibility 區塊。",
        ],
    ),
    (
        "q2_knowledge_distill_plan",
        "Q2 專業知識蒸餾計畫",
        "有書面持續蒸餾計畫：負責人、節奏、晉升標準。",
        [
            "每季檢視 sources/DISTILLATION_PLAN.json 的 next_review_at 與 owner。",
            "蒸餾輸出連結 memory_namespace pack.video.<agent_id>。",
            "對變更過的 agents 在 CI 做 distill schema dry-run。",
        ],
    ),
    (
        "q3_sources_available",
        "Q3 來源可用／可取得",
        "已授權或允許之來源＋可重跑 ACQUIRE SOP。",
        [
            "盤點 SOURCE_CATALOG.json；盡量把 license_class 從 unknown_review_required 推進。",
            "新增語料類別後更新 ACQUIRE.md 步驟。",
            "摘錄變更時更新 PROVENANCE.json hash。",
            "法務核准前優先使用 fixture-only 離線 grounding。",
        ],
    ),
    (
        "q4_self_eval",
        "Q4 自評方法與內容",
        "可執行 L1＋L2 rubric＋可選 L3 preference 與門檻。",
        [
            "保持 rubrics/<rubric_reference>.json 的 pass_threshold ≥ 85。",
            "agents.md Self-Quality Criteria 變更時重推維度。",
            "確保 golden.json 仍要求 l1_passed＋artifact。",
            "rubric 編輯後重跑 pack golden。",
        ],
    ),
    (
        "q5_surpass_human",
        "Q5 超越人類（可量測）",
        "非合成人類基線＋agent 量測＋gate.met=true。",
        [
            "確認 human_baseline_protocol.json 存在且指標對齊 agents.md surpass 訊號。",
            "真實場次前清除任何 synthetic human trials。",
            "在凍結 golden 輸入上收集 ≥5 次真實人類 trials。",
            "確保 agent_measurement 有 ≥5 次離線（或鎖定版本）trials。",
            "執行 evaluate_gate；YES 僅當 gate.met && !synthetic。",
            "發布 human_baseline_evidence.json；之後才允許 UI 使用超越人類用語。",
            "若 not_met：改進 prompt/rubric/tools，重測 agent，任務變更時重評人類。",
        ],
    ),
    (
        "q6_execution",
        "Q6 工作執行路徑",
        "Host 路徑：prompt＋rubric＋skill＋golden/runner 證據。",
        [
            "保持 prompts/<prompt_reference>.md 完整（System/Developer/Task/Output）。",
            "驗證 PackAgentLoader.load(agent_id) 離線成功。",
            "以 PackGoldenRunner 保持 golden.json 全綠。",
            "無 env 閘門時對 network=true/production=true fail-closed。",
            "可選：將設計 Tool Access 對應 mock adapters 並附測試。",
        ],
    ),
    (
        "q7_skills_plugins",
        "Q7 Skills／plugins／harness",
        "每 agent skills harness 可被 host 載入。",
        [
            "維持 skills/SKILL.md＋integration.json＋bindings.json。",
            "使用時驗證 special_skills 綁定路徑。",
            "煙霧：host 無網路可載入 skill。",
        ],
    ),
    (
        "q8_self_improve",
        "Q8 自我改進機制",
        "critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。",
        [
            "保持 max_refinement_count 政策文件化。",
            "變更 runner 時以 force_l2_fail_once 路徑做測試。",
            "改進後重跑 golden＋baseline agent_measurement。",
            "可選：以 evidence bundle 持久晉升新 prompt/rubric 版本。",
        ],
    ),
    (
        "q9_research_for_improve",
        "Q9 研究以改進",
        "可請求／消費研究包進入蒸餾與 evals。",
        [
            "以 SOURCE_CATALOG＋ACQUIRE 做研究進場。",
            "需要外部刷新時接研究型 meta-agents（先離線 fixtures）。",
            "研究輸出放入 sources/research/ 並含 provenance。",
            "僅在協議變更控制下刷新 golden 門檻。",
        ],
    ),
    (
        "q10_collab_instructions",
        "Q10 協作／指令收發",
        "型別化收發，含 edge allowlist＋ack。",
        [
            "保持 critique_edges 對齊 agents.md Accepts／Comments。",
            "至少一條 partner edge 在整合測試證明 send＋receive（spine）。",
            "所有 critique／handoff 帶 correlation_id。",
        ],
    ),
    (
        "q11_conflict_resolve",
        "Q11 衝突解決與確認",
        "嚴重度路由；可自解則自解；否則 Judge／HiTL 確認。",
        [
            "保持 blocker → requires_hitl 確認路徑。",
            "未決爭議在 outputs allowlist 時導向 video.judge。",
            "產品層確認僅用 action refs（不虛構權限）。",
            "edge 矩陣變更後重測。",
        ],
    ),
]


def short(s: str, n: int = 160) -> str:
    t = " ".join((s or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def priority_rank(agent: dict) -> int:
    aid = agent.get("agent_id") or ""
    cat = agent.get("va_category") or ""
    if aid in {
        "video.orchestrator",
        "video.planner",
        "video.router",
        "video.judge",
        "video.gatekeeper",
        "video.critic",
        "video.memory",
    }:
        return 0
    if cat == "9-Meta":
        return 1
    if cat == "1-ATL":
        return 2
    if agent.get("live_media_tools"):
        return 3
    if cat in {"3-Edit", "4-Snd", "2-Cam"}:
        return 4
    if cat in {"8-AI", "6-Dist", "5-Perf"}:
        return 5
    return 6


def remaining_actions(agent: dict) -> list[tuple[str, str, str, list[str]]]:
    out: list[tuple[str, str, str, list[str]]] = []
    va = agent.get("va_table") or {}
    aid = agent["agent_id"]
    for qid, title, _done, base in Q_META:
        st = agent["questions"][qid]["status"]
        if st == "yes":
            actions = [f"維持「是」：{base[0]}", *base[1:3]]
        else:
            actions = list(base)

        if qid == "q5_surpass_human":
            sig = va.get("surpass_human_signal") or "相對人類基線的工藝分數"
            actions = [
                f"主要缺口：關閉 `{aid}` 的 Q5 — 設計訊號：{short(sig, 140)}",
                (
                    f"協議路徑：business/video/evals/agents/{aid}/human_baseline_protocol.json"
                    f"（status={agent.get('baseline_status')}，"
                    f"gate_met={agent.get('baseline_gate_met')}，"
                    f"synthetic={agent.get('baseline_gate_synthetic')}）"
                ),
                f"若有 synthetic 人類：`python scripts/business/record_human_baseline.py --clear-synthetic --agents {aid}`",
                f"評分簡報（若有）：business/video/evals/rater_sessions/{aid}/RATER_BRIEF.md",
                (
                    f"互動場次：`python scripts/business/record_human_baseline.py --session "
                    f"--agent {aid} --rater <真實id> --evaluate`"
                ),
                "或 CSV：匯出範本 → 填 ≥5 分 → `record_human_baseline.py --import-csv ... --evaluate`",
                (
                    f"prompt 變更後重測 agent：`scaffold_human_baselines_v1.py --agent {aid} "
                    "--measure-agent --evaluate-gate`"
                ),
                "Q5 滿分僅當 gate.met=true 且 synthetic=false 且 evidence 檔已寫入。",
                "若 gate not_met：改進 prompt/rubric，重跑離線量測，任務變更時重評人類。",
            ]

        if qid == "q6_execution" and st == "yes":
            tools = agent.get("allowed_tools") or []
            if not tools or tools == ["media.stub"]:
                actions.append("可選強化：以角色 mock adapters＋單元測試取代純 media.stub。")
            if agent.get("live_media_tools"):
                actions.append("強化：live 媒體維持 env 閘門；離線 golden 必須在無網路下仍綠。")

        if qid == "q3_sources_available" and agent.get("source_file_count", 0) < 8:
            actions.insert(
                0,
                f"在授權允許下，將包裝來源檔由 {agent.get('source_file_count')} 擴向 ≥8 份摘錄。",
            )

        out.append((qid, title, st, actions))
    return out


def main() -> int:
    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    completion: dict = {}
    if _COMPLETION.is_file():
        try:
            completion = json.loads(_COMPLETION.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            completion = {}

    agents = data["agents"]
    n = len(agents)
    g = data["global_summary"]
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_ORDER}
    for ag in agents:
        by_cat.setdefault(ag["va_category"], []).append(ag)

    yes_c = g["status_counts"]["yes"]
    part_c = g["status_counts"]["partial"]
    no_c = g["status_counts"]["no"]
    total_c = yes_c + part_c + no_c
    weighted_pct = 100.0 * (yes_c + 0.5 * part_c) / max(total_c, 1)
    strict_pct = 100.0 * yes_c / max(total_c, 1)
    plan_pct = (completion.get("complete_percent") or {}).get("plan_composite", weighted_pct)
    auto_pct = (completion.get("complete_percent") or {}).get("automatable_q_except_q5", 100.0)

    q5_partial = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "partial")
    q5_yes = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "yes")
    q5_no = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "no")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    a = lines.append

    a("# Agent 改進計畫 v2 — 邁向滿分（11/11 是）")
    a("")
    a(f"**產生時間：** {now}  ")
    a("**依據：** `agent_capability_status_v2.md`＋`business/video/AGENT_CAPABILITY_AUDIT.json`  ")
    a(
        "**前一版計畫：** `agent_improvement_plan_v1.md`／`agent_improvement_plan_v1_hk.md`／"
        "`agent_improvement_plan_v2.md`  "
    )
    a("**設計權威：** `va-agent-swarm/study/agents.md`  ")
    a(f"**範圍：** {n} 個非 specials 的 video pack agents  ")
    a("**目標：** 每個 agent 達到 **滿分** = 十一項問題皆為「是」（成熟度 **11.0/11**）。")
    a("")
    a(
        "> **v2 論點：** v1 的可自動化 Wave A–D **已完成**。剩餘滿分工作幾乎全是 "
        "**Q5 可量測人類基線**（真實評分者，非 synthetic），外加對已綠項目的維護／強化。"
    )
    a("")
    a("---")
    a("")
    a("## 0. 相對滿分的計分板（完成度 %）")
    a("")
    a("| 指標 | 現況 | 滿分目標 |")
    a("|------|----:|-----------------:|")
    a(f"| 平均成熟度 0–11 | **{g['avg_maturity']}** | **11.0** |")
    a(f"| **加權儲存格完成度** | **{weighted_pct:.2f}%** | **100%** |")
    a(f"| 嚴格僅「是」 | **{strict_pct:.2f}%** | **100%** |")
    a(f"| 是／部分／否 | {yes_c}／{part_c}／{no_c} | {n * 11}／0／0 |")
    a(f"| 計畫綜合完成度（追蹤器） | **{plan_pct}%** | **100%** |")
    a(f"| 可自動化（除 Q5） | **{auto_pct}%** | **100%**（已達） |")
    a(f"| Q5 已「是」的 agents | **{q5_yes}/{n}** | **{n}/{n}** |")
    a("")
    a(
        f"**完成度總覽：** 加權 **{weighted_pct:.2f}%** · 嚴格 YES **{strict_pct:.2f}%** · "
        f"可自動化 **{auto_pct}%** · 計畫綜合 **{plan_pct}%**。"
    )
    a(
        f"**缺口：** 仍非「是」的儲存格 {part_c + no_c} — 其中 **{q5_partial}** 為 Q5 部分、"
        f"**{q5_no}** 為 Q5 否。關閉 Q5 即可 **{g['avg_maturity']} → 11.0**（其餘 Q 維持「是」）。"
    )
    a("")
    a("---")
    a("")
    a("## 1. v1 已完成項目（勿重建）")
    a("")
    a("| 工作流 | 證據 | 狀態 |")
    a("|--------|------|------|")
    a("| P0 產物工廠 | prompts/rubrics/skills/catalogs/goldens ×114 | **完成** |")
    a("| P1 執行 runtime | `backend/app/video/pack_runtime/` | **完成** |")
    a("| P2 評估／基線套件 | rubrics＋human_baseline_protocol ×114 | **完成（協議）** |")
    a("| P3 Critique bus | CritiqueBus edges、ack、HiTL | **完成** |")
    a("| P4 蒸餾／改進腳手架 | DISTILLATION_PLAN＋ACQUIRE＋refine | **完成** |")
    a("| Q1–Q4、Q6–Q11 全艦隊「是」 | capability audit v2 | **完成** |")
    a("| Q5 真實人類 MET | gate.met && !synthetic | **未完成** |")
    a("")
    a("---")
    a("")
    a("## 2. 滿分 Definition of Done（v2）")
    a("")
    a("| Q | 標題 | 僅在下列情況可標「是」 | 主要證據 |")
    a("|---|------|------------------------|----------|")
    for _qid, title, done, _ in Q_META:
        a(f"| {title.split()[0]} | {title} | {done} | 見每 agent 清單 |")
    a("")
    a("### 計分規則")
    a("")
    a("- **單 agent 滿分：** 11 個「是」（無「部分」、無「否」）。")
    a(f"- **全艦隊滿分：** {n}/{n} agents 達 11.0，且 UI 無合成 surpass 宣稱。")
    a(
        "- **Q5 特別規則：** `gate.met=true` 且 `gate.synthetic=false` 且有 "
        "`human_baseline_evidence.json`。"
    )
    a("")
    a("---")
    a("")
    a("## 3. 剩餘缺口（Q5）的研究型路徑")
    a("")
    a("| 來源 | v2 用法 |")
    a("|------|---------|")
    a("| `agents.md` Surpass-Human Signal | 指標推斷（勝率、TTD、成本、κ、工藝分） |")
    a("| LLM-as-Judge／pairwise arena | L2 rubrics＋可選 pairwise 閘門 |")
    a("| 人類評估協議（凍結任務、盲測） | human_baseline_protocol 程序 |")
    a("| Anthropic Agent Skills | 每 agent harness 已可載入 |")
    a("| 離線 pack_runtime | 可重現 agent_measurement |")
    a("| Fail-closed 產品規則 | 無證據不可 surpass UI |")
    a("")
    a("### 建議評估科學（每 agent）")
    a("")
    a("1. **凍結輸入** — 僅用 golden.json（或版本化雙生）。")
    a("2. **人類 trials n≥5** — 盡量獨立評分者；記錄 rater_id。")
    a("3. **Agent trials n≥5** — 鎖定 runner/prompt/rubric 版本。")
    a("4. **預先登錄指標** — 來自 agents.md（開評後不改）。")
    a("5. **閘門** — higher：agent≥human；lower：agent<human；pairwise：rate≥threshold。")
    a("6. **發布證據** — 僅 met && !synthetic 可宣稱。")
    a("")
    a("---")
    a("")
    a("## 4. 共享工作流 v2")
    a("")
    a("### W0 — 守護已綠（持續）")
    a("")
    a("| ID | 行動 | 完成條件 |")
    a("|----|------|----------|")
    a("| W0.1 | CI：pack golden spine 7/7 | pytest＋run_pack_agent_golden --spine |")
    a("| W0.2 | CI：Q1–4、6–11 無迴歸 | audit JSON 閘門 |")
    a("| W0.3 | 禁止合成 surpass 宣稱 | claim_allowed_in_ui |")
    a("")
    a("### W1 — 人類基線營運（主要）")
    a("")
    a("| ID | 行動 | 完成條件 |")
    a("|----|------|----------|")
    a("| W1.1 | 保持協議最新 ×114 | scaffold 可重跑 |")
    a("| W1.2 | 真實場次前清 synthetic | synthetic_any=false |")
    a("| W1.3 | 評分場次包 rater_sessions | spine+ATL 簡報 |")
    a("| W1.4 | 記錄真實 trials n≥5 | CLI/CSV/session |")
    a("| W1.5 | evaluate_gate met 非合成 | gate.met |")
    a("| W1.6 | baseline_status 儀表板 | claimable 上升 |")
    a("| W1.7 | 重跑 audit＋完成度 | 成熟度 → 11 |")
    a("")
    a("### W2 — 可選強化")
    a("")
    a("| ID | 行動 |")
    a("|----|------|")
    a("| W2.1 | 角色 mock adapters（超越 media.stub） |")
    a("| W2.2 | 授權語料取得 |")
    a("| W2.3 | 持久 prompt/rubric 晉升管線 |")
    a("| W2.4 | HiTL 產品 UI action-refs |")
    a("")
    a("---")
    a("")
    a("## 5. 分階段邁向全艦隊滿分")
    a("")
    a("| 階段 | 主題 | 出場條件 |")
    a("|------|------|----------|")
    a("| V2-P0 | 守護已綠 | spine golden＋測試綠 |")
    a("| V2-P1 | Spine 人類基線 | 7 agents Q5 是 |")
    a("| V2-P2 | ATL 人類基線 | ＋5 agents Q5 是 |")
    a("| V2-P3 | 核心工藝 Cam/Edit/Snd | 分組 MET |")
    a("| V2-P4 | 長尾 | 114 Q5 是 |")
    a("| V2-P5 | 滿分凍結 | **11.0 × 114** |")
    a("")
    a("```")
    a("baseline_status → 清 synthetic → 評 spine 人類 → gate")
    a("  → ATL → 工藝組 → 長尾 → audit → 完成度 100%")
    a("```")
    a("")
    a("---")
    a("")
    a("## 6. 通用清單 v2（每個 agent）")
    a("")
    a("```text")
    a("[ ] V2-U1  SPEC 編輯後 Q1–Q4 仍「是」")
    a("[ ] V2-U2  PackAgentLoader 可載入 prompt+rubric+skill")
    a("[ ] V2-U3  golden 離線通過")
    a("[ ] V2-U4  critique_edges 有效")
    a("[ ] V2-U5  DISTILLATION_PLAN + SOURCE_CATALOG + ACQUIRE")
    a("[ ] V2-U6  human_baseline_protocol 存在")
    a("[ ] V2-U7  agent_measurement n≥5")
    a("[ ] V2-U8  真實人類 n≥5（synthetic=false）")
    a("[ ] V2-U9  gate.met=true && !synthetic")
    a("[ ] V2-U10 claim_allowed_in_ui true")
    a("[ ] V2-U11 audit 成熟度 11.0／11 是")
    a("```")
    a("")
    a("---")
    a("")
    a("## 7. 按問題的艦隊級行動")
    a("")
    for qid, title, done, actions in Q_META:
        y = sum(1 for x in agents if x["questions"][qid]["status"] == "yes")
        p = sum(1 for x in agents if x["questions"][qid]["status"] == "partial")
        no = sum(1 for x in agents if x["questions"][qid]["status"] == "no")
        a(f"### {title}")
        a("")
        a(f"- **「是」的定義：** {done}")
        a(f"- **現況：** 是={y}，部分={p}，否={no}")
        a(f"- **達滿分仍需工作：** {p + no}")
        a(
            "- **模式：** "
            + ("維持（全艦隊已是）" if y == n else "關閉缺口（主要交付）")
        )
        a("- **標準行動：**")
        for act in actions:
            a(f"  - [ ] {act}")
        a("")

    a("---")
    a("")
    a("## 8. 分組計畫（v2）")
    a("")
    for cat in CATEGORY_ORDER:
        group_agents = by_cat.get(cat) or []
        if not group_agents:
            continue
        avg = round(
            sum(x["score"]["maturity_0_to_11"] for x in group_agents) / len(group_agents),
            2,
        )
        need_q5 = sum(
            1 for x in group_agents if x["questions"]["q5_surpass_human"]["status"] != "yes"
        )
        a(
            f"### {cat} — {CATEGORY_LABELS.get(cat, cat)} "
            f"（{len(group_agents)} agents，平均 {avg}，Q5 剩餘 {need_q5}）"
        )
        a("")
        a("**分組里程碑：**")
        a(f"- [ ] 全部 {len(group_agents)} 通過 V2-U1…U5")
        a(f"- [ ] 全部 {len(group_agents)} 真實人類基線 V2-U8…U10")
        a(f"- [ ] 稽核：組內每 agent **11.0**")
        a("")
        a("| Agent | 現況 | 距 11 | 帶 | 達滿分前幾項 |")
        a("|-------|------|------:|----|--------------|")
        for ag in sorted(
            group_agents,
            key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"]),
        ):
            gap = round(11.0 - ag["score"]["maturity_0_to_11"], 2)
            first: list[str] = []
            for _qid, title, st, acts in remaining_actions(ag):
                if st != "yes" and acts:
                    first.append(f"{title.split()[0]}: {acts[0]}")
                if len(first) >= 3:
                    break
            if not first:
                first = ["全部 Q 已是 — 維持＋重驗 golden/baseline"]
            cells = "<br>".join(f"{i+1}. {short(x, 100)}" for i, x in enumerate(first))
            a(
                f"| `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {gap} | "
                f"P{priority_rank(ag)} | {cells} |"
            )
        a("")

    a("---")
    a("")
    a("## 9. 各 Agent 滿分行動清單")
    a("")
    a("每節列出維持或達到 **11/11 是** 的全部行動。「主要缺口」為今日達滿分所必需。")
    a("")

    ordered = sorted(
        agents, key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"])
    )
    for ag in ordered:
        va = ag.get("va_table") or {}
        aid = ag["agent_id"]
        a(
            f"### `{aid}` — {ag.get('va_name') or aid} "
            f"（現況 {ag['score']['maturity_0_to_11']}/11 → 目標 11.0）"
        )
        a("")
        a(
            f"- **類別：** `{ag.get('va_category')}` · **VA#：** {ag.get('va_id')} · "
            f"**優先帶：** P{priority_rank(ag)}"
        )
        a(
            f"- **儲存格：** 是={ag['score']['yes']} 部分={ag['score']['partial']} "
            f"否={ag['score']['no']}"
        )
        a(
            f"- **Prompt／rubric：** `{ag.get('prompt_reference')}`／`{ag.get('rubric_reference')}` "
            f"（檔案 {ag.get('prompt_file_count')}/{ag.get('rubric_file_count')}）"
        )
        a(
            f"- **Harness：** skill={ag.get('has_skill_harness')} golden={ag.get('has_golden_eval')} "
            f"baseline={ag.get('has_baseline_protocol')} status=`{ag.get('baseline_status')}` "
            f"gate_met={ag.get('baseline_gate_met')} synthetic={ag.get('baseline_gate_synthetic')}"
        )
        tools = ", ".join(ag.get("allowed_tools") or []) or "（無）"
        a(f"- **工具：** `{tools}` · live_media={ag.get('live_media_tools')}")
        if va:
            a(f"- **設計 surpass 訊號：** {short(va.get('surpass_human_signal', ''), 160)}")
            a(f"- **設計自評標準：** {short(va.get('self_quality_criteria', ''), 140)}")
            a(f"- **設計架構：** {short(va.get('architecture_pattern', ''), 120)}")
        a("")
        a("#### 邁向滿分狀態")
        a("")
        a("| 問題 | 現況 | 目標 |")
        a("|------|------|------|")
        for qid, title, _d, _acts in Q_META:
            st = STATUS_ZH.get(ag["questions"][qid]["status"], "?")
            a(f"| {title} | **{st}** | **是** |")
        a("")
        a("#### 行動清單（全部完成）")
        a("")
        for qid, title, st, acts in remaining_actions(ag):
            a(f"**{title}**（現況 {STATUS_ZH.get(st, st)} → 是）")
            a("")
            for act in acts:
                a(f"- [ ] {act}")
            a("")
        a("#### 此 agent 出場閘門")
        a("")
        a(f"- [ ] `{aid}` 離線 golden 仍通過")
        a("- [ ] PackAgentLoader 可載入 prompt＋rubric＋skill")
        a("- [ ] 真實人類 n≥5，synthetic=false")
        a("- [ ] evaluate_gate → met=true")
        a("- [ ] human_baseline_evidence.json 的 claim_allowed_in_ui 為 true")
        a(f"- [ ] audit 中 `{aid}` 成熟度 **11.0** 且 11 個「是」")
        a("")

    a("---")
    a("")
    a("## 10. 實作佇列（優先序）")
    a("")
    a("| 序 | 帶 | Agent | 現況 | 為何 |")
    a("|---:|----|-------|------|------|")
    why = {
        0: "主幹 — 先評人類；解鎖協作信任",
        1: "其餘 Meta",
        2: "ATL 創作權威",
        3: "Live 媒體 agents — 基線需謹慎",
        4: "核心工藝製作",
        5: "專門工藝／AI 時代",
        6: "支援與長尾",
    }
    for i, ag in enumerate(ordered, start=1):
        a(
            f"| {i} | P{priority_rank(ag)} | `{ag['agent_id']}` | "
            f"{ag['score']['maturity_0_to_11']} | {why[priority_rank(ag)]} |"
        )
    a("")
    a("---")
    a("")
    a("## 11. 操作者指令")
    a("")
    a("```bash")
    a("python scripts/business/baseline_status.py")
    a("python scripts/business/prepare_rater_sessions_v1.py")
    a("python scripts/business/record_human_baseline.py --clear-synthetic --agents \\")
    a("  video.orchestrator video.planner video.router video.judge \\")
    a("  video.gatekeeper video.critic video.memory")
    a("python scripts/business/record_human_baseline.py --session \\")
    a("  --agent video.orchestrator --rater alice --evaluate")
    a("python scripts/business/run_pack_agent_golden.py --spine")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("python scripts/business/report_improvement_plan_completion.py")
    a("python scripts/business/render_agent_improvement_plan_v2.py")
    a("python scripts/business/render_agent_improvement_plan_v2_hk.py")
    a("```")
    a("")
    a("---")
    a("")
    a("## 12. 剩餘估算")
    a("")
    a("| 工作項 | 單位 | 數量 | 備註 |")
    a("|--------|------|-----:|------|")
    a("| 真實人類 trial 組 | agent | 114 | 各 ≥5；主要成本 |")
    a("| 閘門評估 | agent | 114 | trials 後自動化 |")
    a("| 重測 agent 離線 | agent | 視需要 | prompt 變更後 |")
    a("| 可選 tool mocks | 工具類 | ~20–40 | Q5 YES 非必須 |")
    a("")
    a("**時程提示：** Spine（7）→ ATL（5）→ 每週約 10 個工藝 agents。")
    a("")
    a("---")
    a("")
    a("## 13. 治理（防止假滿分）")
    a("")
    a("1. **無證據不可 Q5「是」** — audit 讀 gate.met && !synthetic。")
    a("2. **record_human_baseline.py 拒絕真實場次使用 --synthetic**。")
    a("3. **任何 prompt/rubric 變更後 golden 必須仍綠。**")
    a("4. **產品 UI 的 HiTL 確認僅用 action refs。**")
    a("5. **完成度報告須顯示 claimable surpass 數量**，而非只數協議檔。")
    a("")
    a("---")
    a("")
    a("## 14. 重新產生")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("python scripts/business/render_agent_improvement_plan_v2.py")
    a("python scripts/business/render_agent_improvement_plan_v2_hk.py")
    a("python scripts/business/report_improvement_plan_completion.py")
    a("```")
    a("")
    a(
        f"追蹤進度：成熟度 **{g['avg_maturity']} → 11.0**，"
        f"加權 **{weighted_pct:.2f}% → 100%**，"
        f"Q5 是 **{q5_yes} → {n}**。"
    )
    a("")
    a("本檔為繁體中文版 `agent_improvement_plan_v2.md`；技術 ID／路徑／指令保留原文。")
    a("")

    text = "\n".join(lines) + "\n"
    try:
        from opencc import OpenCC

        text = OpenCC("s2t").convert(text)
    except Exception as exc:  # noqa: BLE001
        print(f"OpenCC skipped: {exc}")

    _OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}")
    print(
        f"COMPLETE% weighted={weighted_pct:.2f} plan={plan_pct} "
        f"auto_ex_q5={auto_pct} strict={strict_pct:.2f} "
        f"q5_yes={q5_yes}/{n} remaining_q5={q5_partial + q5_no}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
