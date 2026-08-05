/**
 * Structure map layout inspired by common-agent-structure.svg
 * (not an SVG embed — product panels using common-style tokens).
 */
import React from "react";
import Link from "next/link";

export type AgentStructureMapModel = {
  readonly agentId: string;
  readonly agentName: string;
  readonly role: string;
  readonly category: string;
  readonly versionLabel: string;
  readonly folderPath: string;
  readonly promptReference: string;
  readonly rubricReference: string;
  readonly tools: readonly string[];
  readonly networkAccess: boolean;
  readonly productionActivationRequested: boolean;
  readonly critiqueIn: readonly string[];
  readonly critiqueOut: readonly string[];
  readonly hasSpec: boolean;
  readonly hasSources: boolean;
  readonly architecture: string;
};

function Panel({
  kicker,
  title,
  children,
  tone = "default",
}: Readonly<{
  kicker: string;
  title: string;
  children: React.ReactNode;
  tone?: "default" | "indigo" | "violet" | "emerald" | "amber";
}>): JSX.Element {
  return (
    <section className={`agent-structure__panel agent-structure__panel--${tone}`}>
      <header className="agent-structure__panel-head">
        <p className="agent-structure__kicker">{kicker}</p>
        <h3 className="agent-structure__panel-title">{title}</h3>
      </header>
      <div className="agent-structure__panel-body">{children}</div>
    </section>
  );
}

function ChipList({
  items,
  empty,
  linkAgents = false,
}: Readonly<{
  items: readonly string[];
  empty: string;
  linkAgents?: boolean;
}>): JSX.Element {
  if (items.length === 0) {
    return <p className="agent-structure__empty">{empty}</p>;
  }
  return (
    <ul className="agent-structure__chips">
      {items.map((item) => (
        <li key={item}>
          {linkAgents && item.startsWith("video.") ? (
            <Link
              className="agent-structure__chip agent-structure__chip--link"
              href={`/registry/agents/${encodeURIComponent(item)}`}
            >
              {item}
            </Link>
          ) : (
            <span className="agent-structure__chip">{item}</span>
          )}
        </li>
      ))}
    </ul>
  );
}

export function AgentStructureMap({
  model,
}: Readonly<{ model: AgentStructureMapModel }>): JSX.Element {
  const toolsPreview = model.tools.slice(0, 8);
  const toolsMore = Math.max(0, model.tools.length - toolsPreview.length);

  return (
    <div
      className="agent-structure"
      aria-label="Common agent structure map"
    >
      <header className="agent-structure__banner">
        <div>
          <p className="agent-structure__banner-kicker">
            Common AI agent structure
          </p>
          <p className="agent-structure__banner-lede">
            Same professional control model for every craft, research,
            orchestration, and support agent — governed execution, measurable
            quality, auditable outputs.
          </p>
        </div>
        <span className="ds-status ds-status--queued agent-structure__banner-badge">
          <span className="ds-status__dot" aria-hidden="true" />
          Common to all agents
        </span>
      </header>

      {/* ORCHESTRATION LAYER — context of the swarm, not this agent alone */}
      <section
        className="agent-structure__orch"
        aria-label="Orchestration layer"
      >
        <p className="agent-structure__layer-label">Orchestration layer</p>
        <div className="agent-structure__orch-row">
          {(
            [
              ["Orchestrator", "state · retries · fan-out", "video.orchestrator"],
              ["Planner", "scope & task graph", "video.planner"],
              ["Router", "agent & model selection", "video.router"],
              ["Gatekeeper", "phase & release", "video.gatekeeper"],
              ["Memory", "shared context", "video.memory"],
            ] as const
          ).map(([label, detail, id]) => (
            <Link
              key={id}
              className={
                id === model.agentId
                  ? "agent-structure__orch-card agent-structure__orch-card--self"
                  : "agent-structure__orch-card"
              }
              href={`/registry/agents/${encodeURIComponent(id)}`}
            >
              <strong>{label}</strong>
              <span>{detail}</span>
              {id === model.agentId ? (
                <em className="agent-structure__you">this agent</em>
              ) : null}
            </Link>
          ))}
        </div>
      </section>

      <p className="agent-structure__core-label">
        Common agent core · <strong>{model.agentName}</strong>
        {model.category ? ` · ${model.category}` : ""}
      </p>

      <div className="agent-structure__grid">
        <Panel kicker="Entry" title="Input package" tone="amber">
          <p>
            Structured brief, phase ticket, and artifact handoff. Missing
            required fields block execution before tool use.
          </p>
          <ChipList
            empty="No input contract listed"
            items={[
              "artifact_id · version · parent_assets",
              "technical_spec · channels",
              "rights · continuity · qc_status",
            ]}
          />
        </Panel>

        <Panel kicker="Grounding" title="Knowledge and memory" tone="indigo">
          <p>
            Licensed corpora, validated references, episodic memory, and
            correction history. Retrieval must be traceable.
          </p>
          <dl className="agent-structure__kv">
            <div>
              <dt>Prompt</dt>
              <dd>
                <code>{model.promptReference || "—"}</code>
              </dd>
            </div>
            <div>
              <dt>Sources</dt>
              <dd>{model.hasSources ? "pack sources present" : "no sources flag"}</dd>
            </div>
            <div>
              <dt>Folder</dt>
              <dd>
                <code>{model.folderPath || "—"}</code>
              </dd>
            </div>
          </dl>
        </Panel>

        <Panel kicker="Surface" title="Tool and policy" tone="violet">
          <p>
            Tools, providers, validators, and role constitutions define what
            this agent may do and how it is scored.
          </p>
          <dl className="agent-structure__kv">
            <div>
              <dt>Provider</dt>
              <dd>{model.networkAccess ? "network allowed" : "offline / local"}</dd>
            </div>
            <div>
              <dt>Rubric</dt>
              <dd>
                <code>{model.rubricReference || "—"}</code>
              </dd>
            </div>
            <div>
              <dt>Activation</dt>
              <dd>
                {model.productionActivationRequested
                  ? "requested (host gate)"
                  : "fail-closed · non-active"}
              </dd>
            </div>
          </dl>
          <ChipList
            empty="No tools listed"
            items={
              toolsMore > 0
                ? [...toolsPreview, `+${toolsMore} more`]
                : toolsPreview
            }
          />
        </Panel>
      </div>

      {/* Execution loop — Plan → Act → Self-Review */}
      <section
        className="agent-structure__loop"
        aria-label="Agent contract and execution loop"
      >
        <header className="agent-structure__loop-head">
          <p className="agent-structure__kicker">Contract &amp; execution loop</p>
          <h3 className="agent-structure__panel-title">
            Identity · Plan · Act · Self-review
          </h3>
          <p className="agent-structure__loop-meta">
            <code>{model.agentId}</code>
            {model.role ? ` · ${model.role}` : ""}
            {model.architecture ? ` · ${model.architecture}` : ""}
          </p>
        </header>
        <ol className="agent-structure__phases">
          <li className="agent-structure__phase">
            <span className="agent-structure__phase-n">1</span>
            <div>
              <strong>Plan</strong>
              <p>Parse the brief and select an execution path.</p>
            </div>
          </li>
          <li className="agent-structure__phase-arrow" aria-hidden="true">
            →
          </li>
          <li className="agent-structure__phase">
            <span className="agent-structure__phase-n">2</span>
            <div>
              <strong>Act</strong>
              <p>Call tools, models, and validators (stub / gated).</p>
            </div>
          </li>
          <li className="agent-structure__phase-arrow" aria-hidden="true">
            →
          </li>
          <li className="agent-structure__phase">
            <span className="agent-structure__phase-n">3</span>
            <div>
              <strong>Self-review</strong>
              <p>Score against rubric and evidence (L1 / L2).</p>
            </div>
          </li>
        </ol>
        <p className="agent-structure__loop-note">
          Bounded revision loop · max retries · escalate on unresolved failure
        </p>
      </section>

      <div className="agent-structure__grid agent-structure__grid--bottom">
        <Panel kicker="Quality" title="Critique · L1 · L2" tone="emerald">
          <p>
            CritiqueMessage · decision_log · evidence_refs · revision_notes.
            Three-layer quality gate.
          </p>
          <div className="agent-structure__gates">
            <span className="agent-structure__gate">
              <strong>L1 Spec</strong>
              <span>
                {model.hasSpec ? "SPEC schema present" : "SPEC missing"}
              </span>
            </span>
            <span className="agent-structure__gate">
              <strong>L2 Rubric</strong>
              <span>
                {model.rubricReference ? "rubric bound" : "no rubric ref"}
              </span>
            </span>
          </div>
          <p className="agent-structure__subhead">Critique in</p>
          <ChipList
            empty="No critique inputs"
            items={model.critiqueIn}
            linkAgents
          />
          <p className="agent-structure__subhead">Critique out</p>
          <ChipList
            empty="No critique outputs"
            items={model.critiqueOut}
            linkAgents
          />
        </Panel>

        <Panel kicker="Safety" title="Provenance and safety" tone="amber">
          <p>
            Disclosure flags, rights checks, and abuse screening. Outputs carry
            machine-readable metadata for downstream handoff.
          </p>
          <ChipList
            empty="—"
            items={[
              model.versionLabel || "version —",
              model.productionActivationRequested
                ? "activation requested"
                : "production fail-closed",
              model.networkAccess ? "network on" : "network off",
            ]}
          />
        </Panel>

        <Panel kicker="Ops" title="Observability" tone="default">
          <p>
            Structured logs, state transitions, lineage, and replay context.
            Browser is non-authority.
          </p>
          <ChipList
            empty="—"
            items={[
              "decision_log",
              "evidence_refs",
              "handoff ArtifactHandoffV1",
            ]}
          />
        </Panel>
      </div>
    </div>
  );
}

export function parseCritiqueCompat(raw: string): {
  readonly inputs: readonly string[];
  readonly outputs: readonly string[];
} {
  if (!raw || !raw.trim()) return { inputs: [], outputs: [] };
  try {
    const parsed = JSON.parse(raw) as {
      inputs?: unknown;
      outputs?: unknown;
    };
    const inputs = Array.isArray(parsed.inputs)
      ? parsed.inputs.map(String)
      : [];
    const outputs = Array.isArray(parsed.outputs)
      ? parsed.outputs.map(String)
      : [];
    return { inputs, outputs };
  } catch {
    return { inputs: [], outputs: [] };
  }
}
