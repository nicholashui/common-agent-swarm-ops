#!/usr/bin/env python3
"""Render agent_capability_status_v1_hk.md (Traditional Chinese / Hong Kong).

Structural prose and assessments are authored in zh-Hant. Free-text design fields
from agents.md (responsibility, knowledge sources, etc.) are translated en→zh-TW
via deep_translator with an on-disk cache.
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
_OUT = _ROOT / "agent_capability_status_v1_hk.md"
_CACHE = _ROOT / "business" / "video" / ".translate_cache_capability_hk.json"

Q_ORDER = [
    ("q1_responsibility", "1) SPEC.md 中的責任（Responsibility）是否清楚界定"),
    ("q2_knowledge_distill_plan", "2) 是否有專業知識蒸餾計畫"),
    ("q3_sources_available", "3) 是否有蒸餾來源／是否知道如何取得來源"),
    ("q4_self_eval", "4) 是否已收集自評方法與相關內容"),
    ("q5_surpass_human", "5) 現行實作是否已超越人類"),
    ("q6_execution", "6) 如何執行工作"),
    ("q7_skills_plugins", "7) 是否有專屬 skills／plugins／harness"),
    ("q8_self_improve", "8) 是否有自我改進機制"),
    ("q9_research_for_improve", "9) 是否知道如何蒐集／研究資訊以自我改進"),
    ("q10_collab_instructions", "10) 是否能接收／發送指令與其他 agent 協作"),
    ("q11_conflict_resolve", "11) 是否能自行解決衝突並確認"),
]

STATUS_ICON = {"yes": "是", "partial": "部分", "no": "否"}

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

GROUP_PRIORITY = {
    "1-ATL": "具體化導演／製片／編劇 prompts 與 rubrics；綠燈 HiTL；媒體工具須有同意權閘門。",
    "2-Cam": "相機路徑 tool adapters＋安全憲章測試（尤其無人機）；美學評分 harness。",
    "3-Edit": "剪接／調光之 Resolve／FFmpeg 橋接；Murch／12 原則等可執行 rubrics。",
    "4-Snd": "ElevenLabs／響度（LUFS）工具路徑；以 LUFS 驗證作 L1；混音交付 schema。",
    "5-Perf": "肖像／同意權政策閘門；編舞／節奏 rubrics；未同意不啟用 voice clone。",
    "6-Dist": "品牌／合規驗證器；平台規格清單；行銷指標 evals。",
    "7-Edu": "事實查核＋SME HiTL；在地化／無障礙 rubrics 優先。",
    "8-AI": "prompt／avatar／voice-clone 最接近 live——擴張前先加 red-team 與 deepfake 閘門。",
    "9-Meta": "先完成 orchestrator／planner／router／judge 執行主幹；先建 critique bus 再擴 craft。",
    "10-Sup": "支援型 agents 需明確 SLA 與資料契約；多數工具仍僅設計文字。",
}

_PROTECT = re.compile(
    r"(`[^`]+`"
    r"|business/[A-Za-z0-9_./-]+"
    r"|video\.[A-Za-z0-9_.-]+"
    r"|specials\.[A-Za-z0-9_.-]+"
    r"|[A-Za-z0-9_./-]+\.(?:md|json|py|ts|tsx|svg)"
    r"|https?://\S+"
    r"|CASOPS_[A-Z0-9_]+"
    r")"
)


def short_note(note: str, limit: int = 260) -> str:
    n = " ".join((note or "").split())
    return n if len(n) <= limit else n[: limit - 1] + "…"


def status_cell(s: str) -> str:
    return STATUS_ICON.get(s, s.upper())


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
        self._errors = 0

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

    def translate(self, text: str, *, max_len: int = 900) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        latin = sum(1 for c in text if "a" <= c.lower() <= "z")
        if latin < max(6, len(text) * 0.12):
            return text

        # Prefer short form used in report
        if len(text) > max_len:
            text = text[: max_len - 1] + "…"

        key = self._key(text)
        if key in self.cache:
            return self.cache[key]

        holders: list[str] = []

        def _hold(m: re.Match[str]) -> str:
            holders.append(m.group(0))
            return f"[[T{len(holders) - 1}]]"

        protected = _PROTECT.sub(_hold, text)
        translated = protected
        for attempt in range(4):
            try:
                translated = self._get_client().translate(protected)
                self._calls += 1
                break
            except Exception as exc:  # noqa: BLE001
                self._errors += 1
                print(f"  translate retry {attempt + 1}: {exc}", flush=True)
                time.sleep(1.2 * (attempt + 1))
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
            time.sleep(0.25)
        else:
            time.sleep(0.05)
        return translated


def assessment_zh(agent: dict, qid: str) -> str:
    """Chinese assessment from structured fields (no MT of English notes)."""
    st = agent["questions"][qid]["status"]
    va = agent.get("va_table") or {}
    tools = agent.get("allowed_tools") or []
    edges = agent.get("critique_edges") or {}

    if qid == "q1_responsibility":
        if st == "yes":
            return (
                f"SPEC 已有 `## Responsibility`（約 {agent.get('responsibility_chars', 0)} 字元），"
                "責任邊界在 pack 層面清楚。"
            )
        if st == "partial":
            return "有責任標題但內容偏薄；應對齊 agents.md 並補「不擁有」邊界。"
        return "缺少 `## Responsibility` 標題。"

    if qid == "q2_knowledge_distill_plan":
        if st == "yes":
            return "agents.md／SPEC 已規劃知識蒸餾；需把持續蒸餾管線產品化。"
        return "未見清楚的知識蒸餾計畫。"

    if qid == "q3_sources_available":
        n = agent.get("source_file_count", 0)
        prov = agent.get("has_provenance")
        if st == "yes":
            return f"本地來源檔約 {n} 個，PROVENANCE={prov}；仍須核對授權與可重跑取得程序。"
        return f"來源不足或不完整（files={n}，PROVENANCE={prov}）；需補 SOURCE_CATALOG 與 ACQUIRE 程序。"

    if qid == "q4_self_eval":
        return (
            f"設計層有自評標準與 `rubric_reference`=`{agent.get('rubric_reference') or '—'}`，"
            f"但可執行 rubric 檔數={agent.get('rubric_file_count', 0)}。"
            "需落地 rubrics／並接入 eval harness。"
        )

    if qid == "q5_surpass_human":
        sig = (va.get("surpass_human_signal") or "（agents.md 目標訊號）").strip()
        return (
            "實作層面尚未以受控評估證明超越人類。設計目標僅供參考："
            f"{short_note(sig, 120)}。必須先有人類基線與 evidence bundle。"
        )

    if qid == "q6_execution":
        return (
            f"以 host 編排／graph 為主；`prompt_reference`=`{agent.get('prompt_reference') or '—'}` "
            f"（prompt 檔數={agent.get('prompt_file_count', 0)}）；"
            f"provider=`{agent.get('provider')}`；tools=`{tools or ['（無／stub）']}`。"
            "預設非自主 coding-plan agent；需落地 prompt＋工具／mock 測試。"
        )

    if qid == "q7_skills_plugins":
        return (
            "主要依賴 pack 級 `special_skills/` 與 host adapters；"
            "每 agent 私有 skill／plugin harness 尚未完備。"
        )

    if qid == "q8_self_improve":
        return (
            f"SPEC 描述持續學習；`max_refinement_count`={agent.get('max_refinement_count')}。"
            "閉環 refine→re-eval→promote／reject 尚未完整產品化。"
        )

    if qid == "q9_research_for_improve":
        return (
            "有來源清單與研究型設計路徑，但「研究→蒸餾→eval→晉升」自動化未完成；"
            "需接 research meta agents 與 fixture 離線路徑。"
        )

    if qid == "q10_collab_instructions":
        return (
            f"critique_edges={json.dumps(edges, ensure_ascii=False)}；"
            "handoff／critique 設計存在，runtime 多代理指令匯流排僅部分實作。"
            "需補全 Accepts／Comments 矩陣與端到端測試。"
        )

    if qid == "q11_conflict_resolve":
        return (
            "SPEC／共通結構描述 爭議→Judge→HiTL。"
            "每 agent 的自主衝突解決＋確認尚未完整驗證；需 severity 路由與 action ref 確認。"
        )

    return agent["questions"][qid].get("notes") or ""


def suggestions_zh(agent: dict) -> list[str]:
    out: list[str] = []
    if agent["questions"]["q1_responsibility"]["status"] != "yes":
        out.append(
            "重寫 `## Responsibility` 為單一操作者面向段落，並加上可量測的 owns／does-not-own 邊界，對齊 agents.md。"
        )
    if agent.get("prompt_file_count", 0) == 0:
        out.append(
            f"在 `prompts/` 落地可執行 prompt，實作 `{agent.get('prompt_reference') or 'prompt_reference'}`"
            "（system＋task＋output schema）。"
        )
    if agent.get("rubric_file_count", 0) == 0:
        out.append(
            f"依 VA Self-Quality Criteria 在 `rubrics/` 落地 rubric，並接到 host eval harness："
            f"`{agent.get('rubric_reference') or 'rubric_reference'}`。"
        )
    if agent.get("source_file_count", 0) < 5:
        out.append(
            "擴充 `sources/`：授權摘錄＋取得 SOP（URL、授權、刷新節奏），並寫入 MAPPING.md。"
        )
    out.append(
        "以可量測 benchmark（盲測／CSAT／rubric）取代「超越人類」口號；通過閘門前不得宣稱 surpass。"
    )
    tools = agent.get("allowed_tools") or []
    if not tools or tools == ["media.stub"]:
        out.append(
            "定義最小權限 tool allowlist 與 host adapter 測試；無憑證時 fail-closed。"
        )
    out.append(
        "實作閉環改進：critique → refine ≤N → judge → promote／reject，並保存 evidence bundle。"
    )
    out.append(
        "在 host graphs 端到端實作 typed CritiqueMessage＋handoff；發布 agents.md 的 accepts_from／comments_on 矩陣。"
    )
    out.append(
        "新增衝突政策：嚴重度路由（blocker／major／minor）、JudgeAgent 辯論、未決 blocker 的 HiTL 確認。"
    )
    if not agent.get("has_user_guide"):
        out.append("維持 `docs/user_guide.md` 與 SPEC 責任及操作 runbook 對齊。")
    return out


def collect_design_strings(data: dict) -> list[str]:
    seen: set[str] = set()
    uniq: list[str] = []
    keys = (
        "responsibility",
        "knowledge_distillation_source",
        "self_quality_criteria",
        "surpass_human_signal",
        "accepts_critique_from",
        "comments_on",
        "tool_access",
        "architecture_pattern",
    )
    for ag in data["agents"]:
        for s in [ag.get("responsibility_excerpt") or ""]:
            s = short_note(s.strip(), 400)
            if s and s not in seen:
                seen.add(s)
                uniq.append(s)
        va = ag.get("va_table") or {}
        for k in keys:
            s = short_note((va.get(k) or "").strip(), 220)
            if s and s not in seen:
                seen.add(s)
                uniq.append(s)
    return uniq


def main() -> int:
    if not _AUDIT.is_file():
        print(f"Missing {_AUDIT}", file=sys.stderr)
        return 1

    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    tr = Translator(_CACHE)
    strings = collect_design_strings(data)
    print(f"Design strings to translate: {len(strings)} (cache={len(tr.cache)})", flush=True)

    for i, s in enumerate(strings, start=1):
        tr.translate(s)
        if i % 50 == 0 or i == len(strings):
            print(
                f"  {i}/{len(strings)} calls={tr._calls} errors={tr._errors} cache={len(tr.cache)}",
                flush=True,
            )
            tr.save()
    tr.save()

    def T(s: str, limit: int = 220) -> str:
        s = short_note(s or "", limit)
        return short_note(tr.translate(s), limit)

    g = data["global_summary"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    a = lines.append

    a("# Agent 能力狀態報告 v1（繁體中文）")
    a("")
    a(f"**產生時間：** {now}  ")
    a(f"**設計權威來源：** `{data['agents_md_source']}`（`va-agent-swarm/study/agents.md`）  ")
    a(
        f"**實作 Pack：** `{data['pack_root']}`（非 specials 之 video agents；共 **{data['agent_count']}** 個）  "
    )
    a(f"**已對應 VA 表格列數：** {data['va_table_row_count']}  ")
    a(f"**稽核產物：** `business/video/AGENT_CAPABILITY_AUDIT.json`  ")
    a("**英文原文報告：** `agent_capability_status_v1.md`")
    a("")
    a(
        "> **誠實準則：** `agents.md` 的設計主張描述的是「目標級」專業多代理製片系統。"
        "本報告評分的是 **common host pack 實際存在的內容**（SPEC、sources、tools、prompts、rubrics、graphs）"
        "相對於這些主張的落差。**設計文字 ≠ 生產能力。**"
    )
    a("")
    a("---")
    a("")
    a("## 0. 全艦隊執行摘要（十一問）")
    a("")
    a("| # | 問題 | 全艦隊結論 | 證據摘要 |")
    a("|---|------|------------|----------|")
    a(
        f"| 1 | SPEC 中的責任界定 | **大致為「是」** | {g['agents_responsibility_strong']}/{data['agent_count']} 個 agent 具有完整 `## Responsibility` |"
    )
    a(
        "| 2 | 專業知識蒸餾計畫 | **部分** | 每個 VA 列皆有 Knowledge Distillation Source；SPEC 嵌入共通結構；持續蒸餾迴路尚未自動化 |"
    )
    a(
        "| 3 | 來源存在／可知如何取得 | **部分** | 常見 `sources/`＋PROVENANCE／MAPPING；授權線上語料未完整取得 |"
    )
    a(
        f"| 4 | 自評方法與內容 | **部分（設計偏重）** | agents.md 自評標準＋SPEC 品質閘門存在；**{g['agents_with_rubric_files']}/{data['agent_count']}** 個 agent 有非空 `rubrics/` 檔 |"
    )
    a(
        f"| 5 | 是否已超越人類 | **否** | **0** 個 agent 在 host 上有通過驗證的人類超越量測。設計中的 surpass 訊號僅屬目標 |"
    )
    a(
        f"| 6 | 如何執行工作 | **部分 — host 編排** | Graph／DNA＋adapters；**{g['agents_with_live_media_tools']}** 個有 live 媒體工具；**{g['agents_with_prompt_files']}** 個有已落地 prompt 檔；預設非自主 coding-plan agent |"
    )
    a(
        "| 7 | Skills／plugins／harness | **部分（共享 pack skills）** | 存在 `special_skills/` 與 host adapters；每 agent 私有 skill 安裝 harness 大多缺失 |"
    )
    a(
        "| 8 | 自我改進機制 | **部分** | SPEC 持續學習＋`max_refinement_count`；閉環 RLAIF／晉升未完整產品化 |"
    )
    a(
        "| 9 | 研究以改進之路徑 | **部分** | 來源清單＋研究型 meta agents 已設計；research→eval→promote 未完成 |"
    )
    a(
        "| 10 | 協作／指令收發 | **部分** | `critique_edges`＋handoff 設計＋workflow DNA；完整 runtime critique bus 未齊 |"
    )
    a(
        "| 11 | 衝突解決與確認 | **部分** | 設計：爭議 → Judge → HiTL；自主解決＋確認未在每 agent 驗證 |"
    )
    a("")
    a(f"**平均成熟度（0–11）：** **{g['avg_maturity']}**  ")
    a(
        f"**儲存格計數（114×11）：** 是={g['status_counts']['yes']}，部分={g['status_counts']['partial']}，否={g['status_counts']['no']}"
    )
    a("")
    a("### 全艦隊關鍵缺口（重新思考／改進）")
    a("")
    a(
        "1. **Prompt 尚未落地** — 每 agent 有 `prompt_reference`，但 **0** 個有非空 `prompts/` 內容。沒有真實 prompt，角色忠實執行不可能。"
    )
    a(
        "2. **Rubric 尚未落地** — 有 `rubric_reference`，但 **0** 個有非空 `rubrics/`。L2 工藝評分無法執行。"
    )
    a(
        "3. **「超越人類」在量測前屬設計虛構** — 不可把 agents.md「盲測勝率 ≥55%…」當成現況能力。"
    )
    a(
        "4. **工具多為 stub** — 僅少數媒體子集有 live adapter allowlist；多數工藝工具（Resolve／Nuke／Sheets／FAA…）仍是設計文字。"
    )
    a(
        "5. **協作與衝突以 schema 為主** — edges 與 SPEC 文字存在；端到端 CritiqueMessage bus＋Judge＋HiTL 確認需完成。"
    )
    a(
        "6. **自我改進有文件、無閉環** — 有 refinement 預算但無持久 promote／reject 證據則不完整。"
    )
    a("")
    a("---")
    a("")
    a("## 1. `agents.md` 要求什麼（VA 設計契約）")
    a("")
    a("每個 agent 在 `va-agent-swarm/study/agents.md` 以八欄定義：")
    a("")
    a("| 欄位 | 對應問題 | 意義 |")
    a("|------|----------|------|")
    a("| Responsibility | Q1 | 單一工藝所有權邊界 |")
    a("| Knowledge Distillation Source | Q2–Q3、Q9 | 專業知識從何而來 |")
    a("| Self-Quality Criteria | Q4 | 如何自評輸出 |")
    a("| Surpass-Human Signal | Q5 | 目標人類對等／超越指標（理想） |")
    a("| Accepts Critique From / Comments On | Q10–Q11 | 同儕 critique 拓樸 |")
    a("| Tool Access | Q6–Q7 | 外部工具／生成器／DCC 橋 |")
    a("| Architecture Pattern | Q6、Q8 | Self-Refine、ReAct、Debate、Agentic Graph 等 |")
    a("")
    a(
        "第 **§11 Common Structure** 另要求 *每一個* agent：Identity、Responsibility、Knowledge source、Tool access、Architecture pattern、Memory、Constitution／Rubric、L1 Spec／L2 Rubric／L3 Preference 閘門、Critique inbox、Continuous learning、Handoff contracts、HiTL escalation。"
    )
    a("")
    a(
        "**含義：** 若項目只存在於 `agents.md` 而未成為可執行 pack 產物（`SPEC`＋`prompts/`＋`rubrics/`＋tools＋eval fixtures＋host graph 配線），狀態為 **部分** 或 **否**，不是「是」。"
    )
    a("")
    a("---")
    a("")
    a("## 2. 跨切面深度回答（Q1–Q11）")
    a("")
    a("### Q1 — 如何確保每個 agent 知道責任（且在 SPEC.md 界定清楚）")
    a("")
    a(
        "**現況：** 強。Pack SPECs 對 114 個 agent 皆有 `## Responsibility`（常由 VA 表＋共通結構蒸餾）。`agent_spec.json` 亦存 `role`、`va_name`、`va_id`、`va_category`。"
    )
    a("")
    a("**建議控制系統：**")
    a("")
    a(
        "1. **單一真相鏈：** `agents.md` 列 → `agent_spec.json.role` → `SPEC.md ## Responsibility` → `docs/user_guide.md` 開頭（必須一致）。"
    )
    a(
        "2. **機器閘門：** CI 檢查每個 agent Responsibility 長度、含 owns 語意、不與其他 agent 前 40 token 雷同。"
    )
    a("3. **操作者測試：** Registry 詳情只顯示來自 SPEC 的責任；缺失則卡片生成失敗。")
    a("4. **執行期身分注入：** Host system prompt 在工具前必須先放入責任邊界＋不擁有清單。")
    a("")
    a("### Q2 — 是否有蒸餾專業知識的計畫？")
    a("")
    a("**現況：部分 — 設計有、管線未完整。**")
    a("")
    a("- VA 表列出每 agent 的 Knowledge Distillation Sources。")
    a("- SPEC 共通結構含持續學習／蒸餾語言。")
    a("- Pack 有 `corpus/study/`、每 agent `sources/` 摘錄、共享 `special_skills/`。")
    a("- 缺：授權持續蒸餾工作、刷新 SLA、新來源進場品質閘門。")
    a("")
    a("### Q3 — 來源是否存在，或知道如何取得？")
    a("")
    a("**現況：部分。**")
    a("")
    a("- 本地：`sources/PROVENANCE.json`、`MAPPING.md`、`excerpts/`、有時 `generic/` SPEC 副本。")
    a("- 已知做法：agents.md＋mapping 說明 *要取什麼*；不保證合法取得、API 存取或語料最新。")
    a("- 缺口：許多列舉來源（MasterClass、DGA、WGA 等）**未**完整離線授權於 pack。")
    a("")
    a("### Q4 — 是否已收集自評方法？")
    a("")
    a("**現況：部分（標準已設計；產物空白）。**")
    a("")
    a("- 設計：Self-Quality Criteria 欄＋三層閘門（Spec→Rubric→Preference）。")
    a("- Pack：`rubric_reference` ID＋少數 pack 級 evals。")
    a("- 缺口：**零** 個 per-agent 非空 `rubrics/` → 無法執行 L2 工藝評分。")
    a("")
    a("### Q5 — 是否已超越人類？")
    a("")
    a("**答案：全部 agent 皆為「否」。**")
    a("")
    a(
        "設計訊號（例如「相對 DGA 剪接盲測勝率 ≥55%」）是 **目標**，不是 host 量測結果。本 repo 沒有受控評估證據包證明任何 agent 已超越人類。"
    )
    a("")
    a("### Q6 — 如何執行工作？")
    a("")
    a("| 層級 | 今日存在 | 不存在 |")
    a("|------|----------|--------|")
    a("| Host 編排 | Workflow DNA／graphs、product APIs、registry | 與 agents.md 每工具完整對等的 CrewAI／LangGraph |")
    a("| LLM 呼叫 | host model policy；啟用 env 時之媒體供應商 | 磁碟上每 agent 硬化 system prompts |")
    a("| 工具 | 部分 `media.*` adapters | 多數 DCC MCP、Sheets、FAA 等 |")
    a("| Coding plan agents | special skills／specials 設計 | 每 video agent 自主 coding agent |")
    a("| 確定性路徑 | 無 production flags 時 fail-closed | 永遠開啟的 live 生成 |")
    a("")
    a(
        "**今日預設執行路徑：** Host 經 roster／workflow map 選 agent → 跑 graph node → 可能呼叫 allowlist 工具或本地確定性路徑 → 記錄 evidence。"
        "**不是**「每個 agent 獨立跑 coding plan」。"
    )
    a("")
    a("### Q7 — 是否有 skills／plugins／harness？")
    a("")
    a(
        "**部分。** 共享 pack skills 在 `business/video/special_skills/`，specials 在 `business/specials/agents/`。"
        "個別 video agents 通常 **沒有** 私有 plugin 樹；繼承 host＋pack harness。"
    )
    a("")
    a("### Q8 — 是否有自我改進機制？")
    a("")
    a(
        "**部分。** SPEC 描述持續學習；有 `max_refinement_count`。缺：會寫入新 prompt／rubric 版本並附 eval 證明的控制器。"
    )
    a("")
    a("### Q9 — 是否知道如何蒐集／研究以改進？")
    a("")
    a(
        "**部分。** 研究／meta agents 在設計上編碼了 *如何做*。對每個 craft agent，「研究 → 蒸餾 → eval → 晉升」未完成。"
    )
    a("")
    a("### Q10 — 協作時如何收發指令？")
    a("")
    a("**部分。**")
    a("")
    a("- 設計：Accepts／Comments 矩陣；CritiqueMessage；handoffs。")
    a("- Pack：`critique_edges`；workflow DNA；orchestrator／planner entry。")
    a("- 缺口：通用 runtime bus＋每對 agent 的投遞／ack 保證。")
    a("")
    a("### Q11 — 是否能自行解決衝突並確認？")
    a("")
    a(
        "**部分。** 設計路徑：blocker／major／minor → Self-Refine → 多代理辯論／JudgeAgent → 未決則 HiTL。"
        "Host 仍須把嚴重度路由與人類確認閘門做成所有 pack 的一等 API。"
    )
    a("")
    a("---")
    a("")
    a("## 3. 分組狀態")
    a("")
    a(
        "| 分組 | 標籤 | Agents | 平均成熟度（0–11） | 相對最強 | 相對最弱 | 分組優先行動 |"
    )
    a("|------|------|--------|-------------------|----------|----------|--------------|")

    for cat, group in data["groups"].items():
        agents = group["agents"]
        dim_scores = {qk: 0.0 for qk, _ in Q_ORDER}
        for ag in agents:
            for qk, _ in Q_ORDER:
                st = ag["questions"][qk]["status"]
                dim_scores[qk] += 1.0 if st == "yes" else 0.5 if st == "partial" else 0.0
        best = max(dim_scores, key=dim_scores.get)
        worst = min(dim_scores, key=dim_scores.get)
        best_l = dict(Q_ORDER)[best]
        worst_l = dict(Q_ORDER)[worst]
        a(
            f"| `{cat}` | {CATEGORY_LABELS.get(cat, group.get('label', cat))} | {group['count']} | **{group['avg_maturity']}** | {best_l} | {worst_l} | {GROUP_PRIORITY.get(cat, '落地 prompts／rubrics；證明一條 golden eval。')} |"
        )

    a("")
    a("---")
    a("")
    a("## 4. 各 Agent 詳細狀態（按分組）")
    a("")
    a("圖例：**是**＝pack 層面已可用 · **部分**＝已設計或不完整 · **否**＝缺失／未達成。")
    a("")

    total = data["agent_count"]
    done = 0
    for cat, group in data["groups"].items():
        a(
            f"### {cat} — {CATEGORY_LABELS.get(cat, group.get('label', cat))}（{group['count']} agents，平均成熟度 {group['avg_maturity']}）"
        )
        a("")
        a("#### 分組綜合")
        a("")
        for qk, ql in Q_ORDER:
            counts = {"yes": 0, "partial": 0, "no": 0}
            for ag in group["agents"]:
                counts[ag["questions"][qk]["status"]] += 1
            mode = max(counts, key=counts.get)
            a(
                f"- **{ql}：** 主調 **{status_cell(mode)}**（是={counts['yes']}，部分={counts['partial']}，否={counts['no']}）"
            )
        a("")
        a("#### Agents")
        a("")

        for ag in sorted(
            group["agents"],
            key=lambda x: (x.get("va_id") is None, x.get("va_id") or 9999, x["agent_id"]),
        ):
            done += 1
            if done % 20 == 0:
                print(f"  rendering agent {done}/{total}", flush=True)
            va = ag.get("va_table") or {}
            a(
                f"##### `{ag['agent_id']}` — {ag.get('va_name') or ag.get('role') or ag['agent_id']}"
            )
            a("")
            a(
                f"- **VA id／類別：** {ag.get('va_id')}／`{ag.get('va_category')}`  "
            )
            a(
                f"- **狀態／供應商／網路：** `{ag.get('status')}`／`{ag.get('provider')}`／network={ag.get('network_access')}  "
            )
            a(
                f"- **工具：** `{', '.join(ag.get('allowed_tools') or []) or '（無）'}`  "
            )
            a(
                f"- **Prompt 參照／檔案數：** `{ag.get('prompt_reference') or '—'}`／files={ag.get('prompt_file_count')}  "
            )
            a(
                f"- **Rubric 參照／檔案數：** `{ag.get('rubric_reference') or '—'}`／files={ag.get('rubric_file_count')}  "
            )
            a(
                f"- **來源／溯源：** files={ag.get('source_file_count')} · PROVENANCE={ag.get('has_provenance')} · MAPPING={ag.get('has_mapping')}  "
            )
            a(
                f"- **Critique edges：** `{json.dumps(ag.get('critique_edges') or {}, ensure_ascii=False)}`  "
            )
            a(
                f"- **成熟度：** {ag['score']['maturity_0_to_11']}/11（是={ag['score']['yes']} 部分={ag['score']['partial']} 否={ag['score']['no']}）  "
            )
            a(
                f"- **SPEC 責任摘錄：** {T(ag.get('responsibility_excerpt') or '（缺失）', 280)}"
            )
            if va:
                a("")
                a("**來自 `agents.md` 設計列：**")
                a("")
                a(f"- 責任：{T(va.get('responsibility', ''), 200)}")
                a(f"- 知識蒸餾來源：{T(va.get('knowledge_distillation_source', ''), 200)}")
                a(f"- 自評標準：{T(va.get('self_quality_criteria', ''), 200)}")
                a(f"- 超越人類訊號（理想）：{T(va.get('surpass_human_signal', ''), 180)}")
                a(f"- 接受 critique 來源：{T(va.get('accepts_critique_from', ''), 160)}")
                a(f"- 可評論對象：{T(va.get('comments_on', ''), 160)}")
                a(f"- 工具存取（設計）：{T(va.get('tool_access', ''), 180)}")
                a(f"- 架構模式（設計）：{T(va.get('architecture_pattern', ''), 160)}")

            a("")
            a("| 問題 | 狀態 | 評估 |")
            a("|------|------|------|")
            for qk, ql in Q_ORDER:
                a(
                    f"| {ql} | **{status_cell(ag['questions'][qk]['status'])}** | {assessment_zh(ag, qk)} |"
                )

            a("")
            a("**缺口與改進建議：**")
            a("")
            for s in suggestions_zh(ag):
                a(f"- {s}")
            a("")
            a("**重新思考／提高標準：**")
            a("")
            a(
                f"1. 為 `{ag['agent_id']}` 凍結一條 **golden task**（輸入 brief → 期望 artifact schema → 依 agents.md 的 L1／L2 門檻）。"
            )
            a(
                "2. 入庫 **prompt v1＋rubric v1**，並附確定性單元測試（schema＋fixture），而非只有 SPEC 散文。"
            )
            a(
                "3. 端到端證明 **一條協作邊**（發送 critique → 接收 → 精煉或升級）並留下 evidence ID。"
            )
            a(
                "4. 在同一 golden task 上記錄 **人類基線**；沒有 delta 前絕不宣稱超越。"
            )
            a("")

    a("---")
    a("")
    a("## 5. 實作路線圖（全艦隊）")
    a("")
    a("### Wave A — 讓責任與評估成真（2–3 週）")
    a("")
    a("1. 由 agents.md 欄位＋架構模式，為 114 agents 產生 `prompts/*.md`＋`rubrics/*.json`。")
    a("2. CI 閘門：禁止空的 prompts／rubrics 目錄。")
    a("3. 主幹 agents 的 golden evals：orchestrator、planner、director、editor、critic、judge。")
    a("")
    a("### Wave B — 協作與衝突匯流排（2–4 週）")
    a("")
    a("1. 以 host API 實作 CritiqueMessage schema（含 severity）。")
    a("2. 將 `critique_edges` 配線為可強制路由。")
    a("3. JudgeAgent 多代理辯論＋blocker 的 HiTL 確認。")
    a("")
    a("### Wave C — 工具與知識合法性（持續）")
    a("")
    a("1. 優先解鎖工藝價值的 tool adapters（媒體已開始；其次 editor／color／sound）。")
    a("2. 來源取得 SOP：授權、刷新、隔離、hash 鎖定。")
    a("3. 按類別蒸餾工作，從 9-Meta 研究 agents 開始。")
    a("")
    a("### Wave D — 可量測品質（持續）")
    a("")
    a("1. 對前 20 個營收關鍵 agents 擷取人類基線。")
    a("2. 發布儀表板：L1 通過率、L2 rubric、相對人類偏好勝率。")
    a("3. 然後才重訪每 agent 的「超越人類」主張。")
    a("")
    a("---")
    a("")
    a("## 6. 特別說明")
    a("")
    a(
        "- **Specials pack**（`business/specials`）刻意不在本報告的 video roster 表內；視為共享平台 skills，不是 video 工藝組織節點。"
    )
    a(
        "- 媒體 **production activation** 受 env 閘門（`CASOPS_VIDEO_PRODUCTION_ENABLED`＋憑證）。Fail-closed 正確；這不等於工藝就緒。"
    )
    a("- **Org Chart UI** 視覺化層級；並不執行 agents。")
    a(
        "- 本繁中版：結構與評估為繁體中文撰寫；`agents.md` 設計原文欄位經 en→zh-TW 機器翻譯（可於 `business/video/.translate_cache_capability_hk.json` 覆核）。"
    )
    a("")
    a("---")
    a("")
    a("## 7. 重新產生")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v1.py")
    a("python scripts/business/render_agent_capability_status_v1_hk.py")
    a("```")
    a("")
    a("輸出：")
    a("")
    a("- `business/video/AGENT_CAPABILITY_AUDIT.json`")
    a("- `agent_capability_status_v1.md`（英文）")
    a("- `agent_capability_status_v1_hk.md`（本檔，繁體中文）")
    a("")

    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tr.save()
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
