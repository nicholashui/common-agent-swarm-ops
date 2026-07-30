#!/usr/bin/env python3
"""Render agent_improvement_plan_v1_hk.md — Traditional Chinese full-mark action plan.

Structural prose is authored in zh-Hant. Free-text design fields from agents.md
are translated en→zh-TW (cache shared with capability HK report) then OpenCC s2t.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_OUT = _ROOT / "agent_improvement_plan_v1_hk.md"
_CACHE = _ROOT / "business" / "video" / ".translate_cache_capability_hk.json"

Q_META = [
    (
        "q1_responsibility",
        "Q1 SPEC 中的責任界定",
        "Agent 身分與所有權邊界精確、唯一，並在 runtime 注入。",
        [
            "將 SPEC.md `## Responsibility` 保持為單一權威段落（owns／does-not-own）。",
            "第一句同步至 agent_spec.json `role` 與 docs/user_guide.md 開頭。",
            "在 agent_spec.json 新增 `does_not_own: string[]` 以強制邊界。",
            "CI 閘門：責任長度、相對同儕前 40 token 唯一性、必要關鍵字。",
            "Host 在工具前將責任區塊注入為 system-prompt 第一段。",
        ],
    ),
    (
        "q2_knowledge_distill_plan",
        "Q2 專業知識蒸餾計畫",
        "有書面持續蒸餾計畫：負責人、節奏、晉升標準。",
        [
            "新增 SPEC 章節 `## Knowledge Distillation Plan`（來源、授權級別、刷新 SLA）。",
            "建立 sources/DISTILLATION_PLAN.json（inputs、extractors、chunk 政策、owner）。",
            "將計畫登錄至 pack corpus index（含 next_review_at）。",
            "計畫輸出連結至 MemoryAgent／RAG namespace id。",
            "自動化離線 dry-run 蒸餾工作（僅驗證計畫 schema）。",
        ],
    ),
    (
        "q3_sources_available",
        "Q3 來源可用／可取得",
        "已授權或允許之來源包＋可重跑的取得 SOP。",
        [
            "將 agents.md Knowledge Distillation Source 盤點為 sources/SOURCE_CATALOG.json。",
            "每來源記錄：授權、URL／路徑、取得方式、保留、hash、owner。",
            "每來源類別至少一份可用摘錄或合成授權 fixture。",
            "更新 PROVENANCE.json＋MAPPING.md；目錄空或缺授權計畫則 CI 失敗。",
            "在 sources/ACQUIRE.md 撰寫取得 runbook（手動或 API；密鑰不入 git）。",
        ],
    ),
    (
        "q4_self_eval",
        "Q4 自評方法與內容",
        "可執行 L1 schema＋L2 rubric＋L3 preference fixtures 與門檻。",
        [
            "依 agents.md Self-Quality Criteria 落地 rubrics/<rubric_reference>.json。",
            "定義 L1 驗證器（schema／codec／loudness／format）為機器檢查。",
            "定義 L2 LLM-as-Judge rubric 維度、權重，通過門檻 ≥85/100。",
            "在 business/video/evals/agents/<agent_id>/ 新增 golden eval fixture。",
            "Host eval harness 載入 rubric_reference；缺檔 fail-closed。",
        ],
    ),
    (
        "q5_surpass_human",
        "Q5 超越人類（可量測）",
        "受控評估顯示相對人類基線達到／超過 agents.md surpass 訊號。",
        [
            "將 agents.md Surpass-Human Signal 轉為可量測指標＋協定。",
            "在相同 golden task 上收集人類基線（N 次、凍結輸入）。",
            "以鎖定之模型／工具版本跑 agent；保存 evidence bundle。",
            "計算 delta；僅在預先登錄協定下達標才可標「是」。",
            "於 SPEC `## Human Baseline Results` 公布報告路徑（或標為僅目標）。",
        ],
    ),
    (
        "q6_execution",
        "Q6 工作執行路徑",
        "確定性 host 路徑：prompt＋tools＋graph node＋工藝任務 evidence。",
        [
            "落地 prompts/<prompt_reference>.md（system、developer、task、output schema）。",
            "實作 agents.md 架構模式（Self-Refine／ReAct／Debate／Graph）。",
            "將 Tool Access 欄對應 allowlist host adapters；stub 須聲明非 production。",
            "至少登錄一個 workflow DNA／graph（含 I／O 契約）。",
            "整合測試：離線（或 mock tools）呼叫 agent node 並斷言 artifact schema。",
        ],
    ),
    (
        "q7_skills_plugins",
        "Q7 Skills／plugins／harness",
        "角色綁定 skill pack＋host 可只為此 agent 載入的 harness 入口。",
        [
            "建立 business/video/agents/<id>/skills/（SKILL.md＋integration.json）。",
            "經 skills/bindings.json 綁定所需 pack special_skills（若有）。",
            "宣告 harness：runner 種類（graph-node｜tool-loop｜media-adapter）、入口、逾時。",
            "能力登錄項列出 skills hash＋版本。",
            "煙霧測試：除非 production flags，host 無網路亦可載入 skill。",
        ],
    ),
    (
        "q8_self_improve",
        "Q8 自我改進機制",
        "閉環：critique／失敗 → refine ≤N → 重評 → 附證據 promote／reject。",
        [
            "保留 max_refinement_count 並於 SPEC 記錄政策。",
            "Host 以 prompt_reference＋critique 輸入實作 refine 迴路。",
            "改進候選持久化於 evidence/（含前後分數）。",
            "晉升閘門：L2 分數提升且無 L1 迴歸。",
            "排程定期改進工作（或操作者觸發）並寫 audit log。",
        ],
    ),
    (
        "q9_research_for_improve",
        "Q9 研究以改進",
        "Agent 可請求／消費研究包，餵入蒸餾與 evals。",
        [
            "定義 research request schema（主題、來源類、上限成本、期限）。",
            "協作邊接到研究型 meta agents（webresearch／benchmark／trend 等）。",
            "研究輸出存於 sources/research/（含 provenance）。",
            "對應 research → 蒸餾計畫更新 → golden eval 刷新。",
            "新增可用 fixture 語料之離線 dry-run 研究路徑。",
        ],
    ),
    (
        "q10_collab_instructions",
        "Q10 協作／指令收發",
        "型別化收發指令與 critique，含 ack 與路由。",
        [
            "依 agents.md Accepts／Comments 欄擴充 critique_edges（完整矩陣）。",
            "實作 CritiqueMessage＋InstructionMessage host APIs。",
            "整合測試證明此 agent 至少一條 send 與一條 receive。",
            "於 SPEC `## Collaboration Matrix` 記錄協作夥伴。",
            "Orchestrator／router 可以 id＋correlation 識別符定址 agent。",
        ],
    ),
    (
        "q11_conflict_resolve",
        "Q11 衝突解決與確認",
        "嚴重度路由；可自動解決則自解，否則 Judge／HiTL 確認。",
        [
            "定義衝突政策：blocker／major／minor 與自動解決規則。",
            "爭議接至 video.judge（或角色 judge）多代理辯論。",
            "未決 blocker 需 HiTL 確認；記錄決策 evidence。",
            "整合測試：注入衝突 critique，斷言解決或升級路徑。",
            "在 activity／ops UI 呈現衝突狀態；確認僅用 action refs。",
        ],
    ),
]

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

GROUP_TOOL_PRIORITY = {
    "1-ATL": [
        "媒體生成（shot intent 預覽）",
        "時程／預算表 adapters（producer）",
        "劇本驗證器（Fountain／FDX）",
        "HiTL 綠燈 action refs",
    ],
    "2-Cam": [
        "相機路徑／ControlNet adapters",
        "ACES／色彩管線驗證器",
        "無人機 geofence 安全憲章測試",
    ],
    "3-Edit": [
        "FFmpeg／EDL 時間軸 adapters",
        "色度計／LUT 驗證器",
        "分鏡 panel schema",
        "Resolve／Nuke MCP 僅在核准後",
    ],
    "4-Snd": [
        "ElevenLabs／響度（LUFS）adapters",
        "分軌分離 mocks",
        "廣播交付 schema 檢查",
    ],
    "5-Perf": [
        "同意權／肖像閘門",
        "動作節奏 rubrics",
        "語音樣本偏好 judges（離線 fixtures）",
    ],
    "6-Dist": [
        "品牌指引檢查器",
        "平台包裝驗證器",
        "成效行銷指標 fixtures",
    ],
    "7-Edu": [
        "事實查核／引用驗證器",
        "WCAG／在地化檢查",
        "SME HiTL 確認路徑",
    ],
    "8-AI": [
        "prompt 優化 harness",
        "avatar／voice-clone adapters（含 red-team 閘門）",
        "deepfake／安全掃描器",
    ],
    "9-Meta": [
        "orchestrator graph runtime 完整度",
        "router 分類測試",
        "judge 辯論 harness",
        "memory retrieve APIs",
        "critique bus 作為平台主幹",
    ],
    "10-Sup": [
        "支援 SLA＋資料契約",
        "分析事件 schemas",
        "封存／發行包裝工具",
    ],
}

STATUS_ZH = {"yes": "是", "partial": "部分", "no": "否"}

_PROTECT = re.compile(
    r"(`[^`]+`"
    r"|business/[A-Za-z0-9_./-]+"
    r"|video\.[A-Za-z0-9_.-]+"
    r"|[A-Za-z0-9_./-]+\.(?:md|json|py|ts|tsx|svg)"
    r"|https?://\S+"
    r")"
)

BAND_WHY = {
    0: "平台主幹 — 編排、規劃、路由、裁決",
    1: "Meta 平台能力",
    2: "Above-the-line 創作權威",
    3: "已有 live 媒體工具 — 補齊 harness／evals",
    4: "核心工藝製作路徑",
    5: "專門工藝／AI 時代",
    6: "支援與長尾",
}


def short(s: str, n: int = 160) -> str:
    t = " ".join((s or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


class Translator:
    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        self.cache: dict[str, str] = {}
        if cache_path.is_file():
            try:
                self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.cache = {}
        self._client = None
        self._calls = 0

    def _get_client(self):
        if self._client is None:
            from deep_translator import GoogleTranslator

            self._client = GoogleTranslator(source="en", target="zh-TW")
        return self._client

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=0),
            encoding="utf-8",
        )

    def translate(self, text: str, *, max_len: int = 220) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        text = short(text, max_len)
        latin = sum(1 for c in text if "a" <= c.lower() <= "z")
        if latin < max(6, len(text) * 0.12):
            return text
        key = self._key(text)
        if key in self.cache:
            return self.cache[key]

        holders: list[str] = []

        def _hold(m: re.Match[str]) -> str:
            holders.append(m.group(0))
            return f"[[T{len(holders) - 1}]]"

        protected = _PROTECT.sub(_hold, text)
        translated = protected
        for attempt in range(3):
            try:
                translated = self._get_client().translate(protected)
                self._calls += 1
                break
            except Exception:
                time.sleep(1.0 * (attempt + 1))
                self._client = None
        else:
            translated = text

        for i, raw in enumerate(holders):
            for token in (f"[[T{i}]]", f"[T{i}]", f"T{i}"):
                if token in translated:
                    translated = translated.replace(token, raw)
                    break
        self.cache[key] = translated
        if self._calls % 40 == 0:
            self.save()
            time.sleep(0.2)
        else:
            time.sleep(0.04)
        return translated


def remaining_actions(agent: dict) -> list[tuple[str, str, list[str]]]:
    out: list[tuple[str, str, list[str]]] = []
    for qid, title, _done, base_actions in Q_META:
        st = agent["questions"][qid]["status"]
        actions = list(base_actions)
        if qid == "q1_responsibility" and st == "yes":
            actions = [
                "維持「是」：每次 SPEC 編輯跑唯一性 CI。",
                "若缺 does_not_own 清單則補上；user_guide.md 保持同步。",
                "確認 runtime prompt 注入包含責任區塊。",
            ]
        if qid == "q3_sources_available":
            if agent.get("source_file_count", 0) < 8:
                actions.insert(
                    0,
                    f"將包裝來源由 {agent.get('source_file_count')} 提升至 ≥8 份實質檔（摘錄＋目錄）。",
                )
            if not agent.get("has_provenance"):
                actions.insert(0, "建立 sources/PROVENANCE.json。")
            if not agent.get("has_mapping"):
                actions.insert(0, "建立 sources/MAPPING.md。")
        if qid == "q4_self_eval":
            actions.insert(
                0,
                f"為 `{agent.get('rubric_reference') or 'rubric_reference'}` 撰寫 rubrics 內容"
                f"（目前 files={agent.get('rubric_file_count')}）。",
            )
        if qid == "q5_surpass_human":
            va = agent.get("va_table") or {}
            sig = va.get("surpass_human_signal") or "（依工藝角色定義指標）"
            actions.insert(0, f"為 surpass 訊號登錄量測協定：{short(sig, 140)}")
        if qid == "q6_execution":
            actions.insert(
                0,
                f"為 `{agent.get('prompt_reference') or 'prompt_reference'}` 撰寫 prompts 內容"
                f"（目前 files={agent.get('prompt_file_count')}）。",
            )
            tools = agent.get("allowed_tools") or []
            if not tools or tools == ["media.stub"]:
                actions.insert(
                    1,
                    "以角色 allowlist 取代僅 stub 工具（或明確離線 mock adapters 並附測試）。",
                )
            elif agent.get("live_media_tools"):
                actions.insert(
                    1,
                    "live 媒體工具保持 fail-closed；新增無網路 mock-mode golden path 測試。",
                )
            arch = (agent.get("va_table") or {}).get("architecture_pattern") or ""
            if arch:
                actions.append(f"實作架構模式：{short(arch, 120)}")
        if qid == "q7_skills_plugins":
            actions.insert(
                0,
                f"為 `{agent['agent_id']}` 建立 per-agent skills harness 目錄。",
            )
        if qid == "q10_collab_instructions":
            va = agent.get("va_table") or {}
            actions.insert(
                0,
                f"編碼 accepts_from=`{short(va.get('accepts_critique_from', ''), 100)}`；"
                f"comments_on=`{short(va.get('comments_on', ''), 100)}`。",
            )
            edges = agent.get("critique_edges") or {}
            if not edges.get("inputs") and not edges.get("outputs"):
                actions.insert(0, "填寫 critique_edges.inputs／outputs（目前為空）。")
        if qid == "q11_conflict_resolve":
            if not agent.get("has_conflict_resolution_text"):
                actions.insert(
                    0,
                    "新增 SPEC 衝突政策章節（blocker／major／minor＋HiTL）。",
                )
        out.append((qid, title, actions))
    return out


def priority_rank(agent: dict) -> int:
    cat = agent.get("va_category") or ""
    aid = agent.get("agent_id") or ""
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


def main() -> int:
    if not _AUDIT.is_file():
        print(f"Missing {_AUDIT}", file=sys.stderr)
        return 1

    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    agents = data["agents"]
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_ORDER}
    for ag in agents:
        by_cat.setdefault(ag["va_category"], []).append(ag)

    tr = Translator(_CACHE)
    # Pre-translate design fields that appear in per-agent sections
    design_keys = (
        "responsibility",
        "knowledge_distillation_source",
        "self_quality_criteria",
        "surpass_human_signal",
        "accepts_critique_from",
        "comments_on",
        "tool_access",
        "architecture_pattern",
    )
    seen: set[str] = set()
    to_tr: list[str] = []
    for ag in agents:
        va = ag.get("va_table") or {}
        for k in design_keys:
            s = short(va.get(k) or "", 180)
            if s and s not in seen:
                seen.add(s)
                to_tr.append(s)
        # also architecture patterns used in actions
        arch = short(va.get("architecture_pattern") or "", 120)
        if arch and arch not in seen:
            seen.add(arch)
            to_tr.append(arch)
        sig = short(va.get("surpass_human_signal") or "", 140)
        if sig and sig not in seen:
            seen.add(sig)
            to_tr.append(sig)

    print(f"Design strings: {len(to_tr)} (cache={len(tr.cache)})", flush=True)
    for i, s in enumerate(to_tr, start=1):
        tr.translate(s)
        if i % 100 == 0 or i == len(to_tr):
            print(f"  {i}/{len(to_tr)} calls={tr._calls} cache={len(tr.cache)}", flush=True)
            tr.save()
    tr.save()

    def T(s: str, n: int = 180) -> str:
        return short(tr.translate(short(s or "", n)), n)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    a = lines.append
    g = data["global_summary"]

    a("# Agent 改進計畫 v1 — 邁向滿分（11/11 是）")
    a("")
    a(f"**產生時間：** {now}  ")
    a(
        "**依據：** `agent_capability_status_v1.md`／`agent_capability_status_v1_hk.md`＋"
        "`business/video/AGENT_CAPABILITY_AUDIT.json`  "
    )
    a("**設計權威：** `va-agent-swarm/study/agents.md`  ")
    a(f"**範圍：** {data['agent_count']} 個非 specials 的 video pack agents  ")
    a(
        "**目標：** 每個 agent 達到 **滿分** = 十一項能力問題皆為「是」（成熟度 **11.0/11**）。"
    )
    a("**英文原文：** `agent_improvement_plan_v1.md`")
    a("")
    a(
        "> 滿分採 **證據制**。agents.md 的理想文字不算。每個「是」需要產物、測試，"
        "且 Q5 需要可量測評估。"
    )
    a("")
    a("---")
    a("")
    a("## 0. 滿分（Definition of Done）")
    a("")
    a("| Q | 標題 | 僅在下列情況可標「是」 | 最低證據產物 |")
    a("|---|------|------------------------|--------------|")
    for qid, title, done, _actions in Q_META:
        qlabel = title.split()[0]
        a(f"| {qlabel} | {title} | {done} | 見平台工作流＋每 agent 清單 |")
    a("")
    a("### 計分規則")
    a("")
    a("- **單 agent 滿分：** 11 個「是」（無「部分」、無「否」）。")
    a(
        "- **全艦隊滿分：** 114／114 agents 滿分，且平台主幹（critique bus、eval harness、改進迴路）全綠。"
    )
    a(f"- **目前全艦隊平均成熟度：** {g['avg_maturity']} / 11")
    a(
        f"- **目前儲存格：** 是={g['status_counts']['yes']}，"
        f"部分={g['status_counts']['partial']}，"
        f"否={g['status_counts']['no']}"
    )
    a("")
    a("### 缺口估算（約略工作量）")
    a("")
    need = g["status_counts"]["partial"] + g["status_counts"]["no"]
    a(f"- 仍非「是」的儲存格：**{need}**／{data['agent_count'] * 11}")
    a(
        f"- 無 prompt 檔 agents：**{data['agent_count'] - g['agents_with_prompt_files']}**（必須歸零）"
    )
    a(
        f"- 無 rubric 檔 agents：**{data['agent_count'] - g['agents_with_rubric_files']}**（必須歸零）"
    )
    a(f"- 無量測人類超越 agents：**{data['agent_count']}**（皆需 Q5 協定）")
    a("")
    a("---")
    a("")
    a("## 1. 共享平台工作流（解鎖所有 agent 滿分）")
    a("")
    a("這些是 **全艦隊一次建置** 的系統。僅做 per-agent 工作無法讓 Q5–Q11 全「是」。")
    a("")
    a("### 工作流 P0 — 產物落地工廠")
    a("")
    a("| ID | 行動 | 輸出 | 完成條件 |")
    a("|----|------|------|----------|")
    a("| P0.1 | 由 agents.md＋SPEC 產生 prompt | `prompts/<prompt_reference>.md` × 114 | 缺／空則 CI 失敗 |")
    a("| P0.2 | 由 Self-Quality Criteria 產生 rubric | `rubrics/<rubric_reference>.json` × 114 | Host eval 可載入 |")
    a("| P0.3 | 來源目錄工廠 | `sources/SOURCE_CATALOG.json` × 114 | Schema 驗證通過 |")
    a("| P0.4 | Golden task 腳手架 | `evals/agents/<id>/golden.json` × 114 | 離線 dry-run 過 schema |")
    a("| P0.5 | Skills harness 腳手架 | `skills/SKILL.md`＋`integration.json` × 114 | Host 可載入 |")
    a("| P0.6 | 稽核重生閘門 | CI 重跑 capability audit | PR 附成熟度報告 |")
    a("")
    a("### 工作流 P1 — 執行 runtime")
    a("")
    a("| ID | 行動 | 輸出 | 完成條件 |")
    a("|----|------|------|----------|")
    a("| P1.1 | Agent runner 載入 prompt_reference | host 服務 | 每類別樣本單元測試 |")
    a("| P1.2 | Tool allowlist 登錄＋mock adapters | 設計工具 adapters | 離線 mock 路徑可用 |")
    a("| P1.3 | 每 agent graph node 綁定 | DNA／workflow 覆蓋圖 | 每 agent ≥1 可執行 graph 或 standby invoke API |")
    a("| P1.4 | Evidence writer | correlation id、artifacts、scores | 每次 run 產出 evidence bundle |")
    a("| P1.5 | Fail-closed production flags | env 閘門 | 無 keys＋flags 不呼叫 live provider |")
    a("")
    a("### 工作流 P2 — 評估與人類基線（Q4–Q5）")
    a("")
    a("| ID | 行動 | 輸出 | 完成條件 |")
    a("|----|------|------|----------|")
    a("| P2.1 | L1 驗證器庫 | 共享 schema／codec／loudness 檢查 | 跨 agents 可重用 |")
    a("| P2.2 | L2 judge harness | rubric runner | 分數寫入 evidence |")
    a("| P2.3 | L3 偏好／arena harness | pairwise 協定 | 用於 surpass 指標 |")
    a("| P2.4 | 人類基線擷取套件 | 操作協定＋表單 | 每 agent 存基線 |")
    a("| P2.5 | Surpass 儀表板 | 每 agent 指標對訊號 | 閘門綠才可「是」 |")
    a("")
    a("### 工作流 P3 — 協作與衝突匯流排（Q10–Q11）")
    a("")
    a("| ID | 行動 | 輸出 | 完成條件 |")
    a("|----|------|------|----------|")
    a("| P3.1 | CritiqueMessage＋InstructionMessage APIs | host 契約 | OpenAPI＋測試 |")
    a("| P3.2 | 由 agents.md 矩陣擴充 critique_edges | agent_spec × 114 | 矩陣完整度 CI |")
    a("| P3.3 | 投遞／ack 路由 | bus | 多代理整合測試 |")
    a("| P3.4 | Judge 辯論＋嚴重度政策 | judge 服務 | blocker 會升級 |")
    a("| P3.5 | HiTL 確認 actions | 僅 action refs | UI 確認路徑 |")
    a("")
    a("### 工作流 P4 — 蒸餾與自我改進（Q2–Q3、Q8–Q9）")
    a("")
    a("| ID | 行動 | 輸出 | 完成條件 |")
    a("|----|------|------|----------|")
    a("| P4.1 | 蒸餾計畫 schema＋jobs | 離線 job | 全艦隊 dry-run |")
    a("| P4.2 | 授權來源取得 SOP | legal／ops | 目錄合規 |")
    a("| P4.3 | Research request API | meta-agent 配線 | 離線 fixtures |")
    a("| P4.4 | Refine／promote 迴路 | 強制 max_refinement_count | 前後分數 |")
    a("| P4.5 | 每 agent Memory namespaces | memory 服務 | retrieve 測試 |")
    a("")
    a("---")
    a("")
    a("## 2. 分階段邁向全艦隊滿分")
    a("")
    a("| 階段 | 主題 | 目標成熟度 | 出場條件 |")
    a("|------|------|------------|----------|")
    a("| **Phase 0** | 誠實與閘門 | 僅報告 | CI 稽核；UI 無虛假 surpass |")
    a("| **Phase 1** | 產物（P0） | 平均 ~8.0 | 114 prompts＋114 rubrics＋catalogs |")
    a("| **Phase 2** | 主幹 runtime（P1＋P3 meta） | 9-Meta ~10+ | orchestrator／planner／judge／router 全路徑 |")
    a("| **Phase 3** | 工藝執行（P1 分組工具） | ATL／Cam／Edit／Snd ~10 | 每組樣本離線 golden 通過 |")
    a("| **Phase 4** | 全 agents 協作＋衝突 | Q10／Q11 全「是」 | 矩陣測試全綠 |")
    a("| **Phase 5** | 人類基線（P2） | Q5 可達成 | 前 40 再其餘 74 基線完成 |")
    a("| **Phase 6** | 滿分鎖定 | **11.0 × 114** | 稽核全「是」；evidence 索引完整 |")
    a("")
    a("### 建議順序（關鍵路徑）")
    a("")
    a("```")
    a("P0 工廠（prompts／rubrics／catalogs）")
    a("   -> P1 runner＋mock tools")
    a("      -> 9-Meta 主幹（orchestrator, planner, router, judge, critic, memory）")
    a("         -> P3 critique bus")
    a("            -> 工藝組 ATL -> Cam/Edit/Snd -> Perf/Dist/Edu/AI -> Sup")
    a("               -> P4 蒸餾／改進")
    a("                  -> P2 人類基線與 surpass 閘門")
    a("                     -> 滿分凍結")
    a("```")
    a("")
    a("---")
    a("")
    a("## 3. 通用清單（每個 agent 必須完成）")
    a("")
    a("可複製為每個 `video.*` agent 的票務範本：")
    a("")
    a("```text")
    a("[ ] U1  SPEC Responsibility 唯一＋does_not_own")
    a("[ ] U2  user_guide.md 與 Responsibility 同步")
    a("[ ] U3  Knowledge Distillation Plan 章節＋DISTILLATION_PLAN.json")
    a("[ ] U4  SOURCE_CATALOG.json＋PROVENANCE＋MAPPING＋ACQUIRE.md")
    a("[ ] U5  prompts/<prompt_reference>.md 完整")
    a("[ ] U6  rubrics/<rubric_reference>.json 完整（L2 ≥85）")
    a("[ ] U7  evals/agents/<id>/golden.json＋離線 mock 過 L1")
    a("[ ] U8  skills/SKILL.md＋integration.json＋harness 入口")
    a("[ ] U9  allowed_tools 已對應；mock adapters 已測")
    a("[ ] U10 Graph／workflow 綁定或 invoke API 綁定")
    a("[ ] U11 critique_edges 對齊 agents.md Accepts／Comments")
    a("[ ] U12 SPEC Collaboration Matrix 章節")
    a("[ ] U13 衝突政策章節＋Judge／HiTL 路徑測試")
    a("[ ] U14 Refine 迴路測試（失敗 → refine → 通過／升級）")
    a("[ ] U15 Research 請求路徑（fixture）更新 sources/research/")
    a("[ ] U16 已擷取人類基線，或明確「不宣稱」並立案協定")
    a("[ ] U17 Surpass 指標 run 已存；閘門綠才可「是」")
    a("[ ] U18 Capability audit 列顯示此 agent 11 個「是」")
    a("```")
    a("")
    a("---")
    a("")
    a("## 4. 按能力問題的艦隊級行動（彙總）")
    a("")
    for qid, title, done, actions in Q_META:
        yes = sum(1 for x in agents if x["questions"][qid]["status"] == "yes")
        partial = sum(1 for x in agents if x["questions"][qid]["status"] == "partial")
        no = sum(1 for x in agents if x["questions"][qid]["status"] == "no")
        a(f"### {title}")
        a("")
        a(f"- **「是」的定義：** {done}")
        a(f"- **現況：** 是={yes}，部分={partial}，否={no}")
        a(f"- **仍需工作的 agents：** {partial + no}（「部分」視為未完成）")
        a("- **達滿分標準行動：**")
        for act in actions:
            a(f"  - [ ] {act}")
        a("")

    a("---")
    a("")
    a("## 5. 分組改進計畫")
    a("")

    for cat in CATEGORY_ORDER:
        group_agents = by_cat.get(cat) or []
        if not group_agents:
            continue
        avg = round(
            sum(x["score"]["maturity_0_to_11"] for x in group_agents) / len(group_agents),
            2,
        )
        a(
            f"### {cat} — {CATEGORY_LABELS.get(cat, cat)}（{len(group_agents)} agents，平均 {avg}）"
        )
        a("")
        a("**分組工具／harness 優先：**")
        for t in GROUP_TOOL_PRIORITY.get(cat, []):
            a(f"- {t}")
        a("")
        a("**分組里程碑清單：**")
        a(f"- [ ] 全部 {len(group_agents)} agents 完成通用 U1–U10")
        a("- [ ] 分組 mock adapter pack 測試全綠")
        a("- [ ] 組內至少 1 條多代理路徑使用 critique bus")
        a("- [ ] 分組主幹 agents 人類基線完成")
        a("- [ ] 稽核：組內每 agent 成熟度 11.0")
        a("")
        a("| Agent | 現況 | 距 11 缺口 | 優先帶 | 前 5 項行動 |")
        a("|-------|------|-----------|--------|------------|")
        for ag in sorted(
            group_agents,
            key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"]),
        ):
            gap = round(11.0 - ag["score"]["maturity_0_to_11"], 2)
            rem = remaining_actions(ag)
            first_actions: list[str] = []
            for qid, title, acts in rem:
                st = ag["questions"][qid]["status"]
                if st != "yes" and acts:
                    first_actions.append(f"{title.split()[0]}: {acts[0]}")
                if len(first_actions) >= 5:
                    break
            if len(first_actions) < 5:
                for qid, title, acts in rem:
                    if acts and f"{title.split()[0]}:" not in " ".join(first_actions):
                        first_actions.append(f"{title.split()[0]}: {acts[0]}")
                    if len(first_actions) >= 5:
                        break
            band = priority_rank(ag)
            # Translate embedded English design snippets in specialized actions if any
            cells = []
            for i, x in enumerate(first_actions[:5]):
                # leave mostly Chinese; only translate pure-English tails
                cells.append(f"{i + 1}. {short(x, 90)}")
            a(
                f"| `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {gap} | P{band} | "
                + "<br>".join(cells)
                + " |"
            )
        a("")

    a("---")
    a("")
    a("## 6. 各 Agent 滿分行動清單")
    a("")
    a("每個 agent 章節列出達 **11/11 是** 所需 **全部行動**（按問題排序）。請勾完每一項。")
    a("")

    ordered = sorted(
        agents, key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"])
    )
    for idx, ag in enumerate(ordered, start=1):
        if idx % 20 == 0:
            print(f"  rendering agent {idx}/{len(ordered)}", flush=True)
        va = ag.get("va_table") or {}
        a(
            f"### `{ag['agent_id']}` — {ag.get('va_name') or ag['agent_id']} "
            f"（現況 {ag['score']['maturity_0_to_11']}/11 → 目標 11.0）"
        )
        a("")
        a(
            f"- **類別：** `{ag.get('va_category')}` · **VA#：** {ag.get('va_id')} · **優先帶：** P{priority_rank(ag)}"
        )
        a(
            f"- **現況儲存格：** 是={ag['score']['yes']} 部分={ag['score']['partial']} 否={ag['score']['no']}"
        )
        a(
            f"- **Prompt／Rubric 參照：** `{ag.get('prompt_reference')}`／`{ag.get('rubric_reference')}`"
        )
        a(
            f"- **現有工具：** `{', '.join(ag.get('allowed_tools') or []) or '（無）'}` · live_media={ag.get('live_media_tools')}"
        )
        a(
            f"- **現有來源：** {ag.get('source_file_count')} 檔 · provenance={ag.get('has_provenance')}"
        )
        if va:
            a(f"- **設計責任：** {T(va.get('responsibility', ''), 180)}")
            a(f"- **設計知識來源：** {T(va.get('knowledge_distillation_source', ''), 180)}")
            a(f"- **設計自評標準：** {T(va.get('self_quality_criteria', ''), 160)}")
            a(f"- **設計 surpass 訊號：** {T(va.get('surpass_human_signal', ''), 160)}")
            a(f"- **設計工具：** {T(va.get('tool_access', ''), 160)}")
            a(f"- **設計架構：** {T(va.get('architecture_pattern', ''), 140)}")
            a(f"- **設計接受 critique 來源：** {T(va.get('accepts_critique_from', ''), 140)}")
            a(f"- **設計可評論對象：** {T(va.get('comments_on', ''), 140)}")
        a("")
        a("#### 邁向滿分狀態")
        a("")
        a("| 問題 | 現況 | 目標 |")
        a("|------|------|------|")
        for qid, title, _d, _acts in Q_META:
            st = STATUS_ZH.get(ag["questions"][qid]["status"], ag["questions"][qid]["status"])
            a(f"| {title} | **{st}** | **是** |")
        a("")
        a("#### 行動清單（全部完成）")
        a("")
        for qid, title, acts in remaining_actions(ag):
            st = STATUS_ZH.get(ag["questions"][qid]["status"], "?")
            a(f"**{title}**（現況 {st} → 是）")
            a("")
            for act in acts:
                # Translate trailing English architecture snippets if present
                if act.startswith("實作架構模式："):
                    eng = act.split("：", 1)[-1]
                    act = f"實作架構模式：{T(eng, 120)}"
                elif "為 surpass 訊號登錄量測協定：" in act:
                    eng = act.split("：", 1)[-1]
                    act = f"為 surpass 訊號登錄量測協定：{T(eng, 140)}"
                a(f"- [ ] {act}")
            a("")
        a("#### 此 agent 出場閘門")
        a("")
        a(f"- [ ] `{ag['agent_id']}` 離線 golden run 通過 L1＋L2 門檻")
        a("- [ ] 協作 send／receive 測試全綠")
        a("- [ ] 衝突解決或 HiTL 升級測試全綠")
        a("- [ ] 改進迴路測試全綠（滿分不允許永久「不學習」）")
        a("- [ ] 人類基線套件已立案；僅在量測閘門綠時宣稱 surpass")
        a(
            f"- [ ] `AGENT_CAPABILITY_AUDIT.json` 中 `{ag['agent_id']}` 成熟度 11.0 且 11 個「是」"
        )
        a("")

    a("---")
    a("")
    a("## 7. Agent 實作優先序（佇列）")
    a("")
    a("由上而下。主幹解鎖其餘。")
    a("")
    a("| 序 | 帶 | Agent | 現況 | 為何優先 |")
    a("|---:|----|-------|------|----------|")
    for i, ag in enumerate(ordered, start=1):
        a(
            f"| {i} | P{priority_rank(ag)} | `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {BAND_WHY[priority_rank(ag)]} |"
        )
    a("")
    a("---")
    a("")
    a("## 8. 估算模型（規劃用）")
    a("")
    a("| 工作項 | 單位 | 數量 | 備註 |")
    a("|--------|------|-----:|------|")
    a("| Prompt 檔 | agent | 114 | 工廠＋人工工藝審閱 |")
    a("| Rubric 檔 | agent | 114 | 工廠＋工藝 owner 簽核 |")
    a("| 來源目錄＋取得計畫 | agent | 114 | 法務可能序列化 |")
    a("| Skills harness | agent | 114 | 薄封裝可接受 |")
    a("| Golden eval | agent | 114 | 先用 fixtures |")
    a("| Mock tool adapters | 工具類 | ~30–50 | 跨 agents 共享 |")
    a("| 協作邊測試 | agent | 114 | 由矩陣產生 |")
    a("| 人類基線 | agent | 114 | 成本高；按組批次 |")
    a("| Surpass 量測 | agent | 114 | 基線之後 |")
    a("")
    a(
        "**Q5 實務分期：** 不要讓 surpass 卡住 Phase 1–4。及早立案基線協定；執行路徑可用後再做人體評估。"
        "滿分仍要求 Q5「是」— 請為人類評估排程，或將「是」定義為「量測協定完成且達標」"
        "（絕無資料不得宣稱）。"
    )
    a("")
    a("---")
    a("")
    a("## 9. 治理閘門（防止假滿分）")
    a("")
    a("1. **無路徑不可「是」：** 稽核腳本須檢查檔案存在＋測試名稱，而非只看 SPEC 關鍵字（升級 auditor）。")
    a("2. **無 evidence hash 不得在 UI 顯示 surpass。**")
    a("3. **工具 fail-closed：** 缺 adapter ⇒ mock 或錯誤，永不靜默成功。")
    a("4. **HiTL 確認僅用 action refs**（product façade 紀律）。")
    a("5. **PR 清單** 須含受影響 agents 的 capability audit 差分。")
    a("")
    a("---")
    a("")
    a("## 10. 重新產生")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v1.py")
    a("python scripts/business/render_agent_capability_status_v1_hk.py")
    a("python scripts/business/render_agent_improvement_plan_v1.py")
    a("python scripts/business/render_agent_improvement_plan_v1_hk.py")
    a("```")
    a("")
    a(
        f"以重跑稽核追蹤進度：成熟度平均應由 **{g['avg_maturity']}** 朝 **11.0** 上升。"
    )
    a("")
    a(
        "本繁中版結構與行動清單為繁體中文撰寫；`agents.md` 設計原文欄位經 en→zh-TW 機器翻譯，"
        "並以 OpenCC s2t 正規化。"
    )
    a("")

    text = "\n".join(lines) + "\n"
    try:
        from opencc import OpenCC

        text = OpenCC("s2t").convert(text)
    except Exception as exc:  # noqa: BLE001
        print(f"OpenCC skipped: {exc}", flush=True)

    _OUT.write_text(text, encoding="utf-8")
    tr.save()
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
