"use client";

/**
 * Shared Agent-Workflow-style diagram (phases · agents · gates).
 * Used by Compose ACC and Canvas orchestration board.
 */
import React from "react";

import type { ComposerWorkflowGraph } from "../../lib/projections/composer-workflow";

export function WorkflowDiagramPanel({
  graph,
  emptyHint,
  className,
}: Readonly<{
  graph: ComposerWorkflowGraph;
  emptyHint?: string;
  className?: string;
}>): JSX.Element {
  const phases = graph.nodes.filter((n) => n.kind === "phase");
  const agents = graph.nodes.filter((n) => n.kind !== "phase");

  return (
    <div
      aria-label="Workflow graph"
      className={className ?? "workflow-diagram"}
    >
      <ul className="workflow-diagram__legend">
        <li className="workflow-diagram__legend-item workflow-diagram__legend-item--phase">
          Phase
        </li>
        <li className="workflow-diagram__legend-item workflow-diagram__legend-item--agent">
          Agent
        </li>
        <li className="workflow-diagram__legend-item workflow-diagram__legend-item--gate">
          Critic / verify
        </li>
        <li className="workflow-diagram__legend-item workflow-diagram__legend-item--edge">
          handoff
        </li>
        <li className="workflow-diagram__legend-item workflow-diagram__legend-item--refine">
          refine cycle
        </li>
      </ul>

      <div className="workflow-diagram__stats">
        <span>
          {graph.agentCount + graph.gateCount} nodes · {graph.phaseCount} phases
          · {graph.gateCount} gate
        </span>
      </div>

      <div className="workflow-diagram__canvas">
        <div className="workflow-diagram__phases">
          {phases.map((phase) => (
            <div className="workflow-diagram__phase" key={phase.id}>
              {phase.title}
            </div>
          ))}
        </div>
        <div className="workflow-diagram__nodes">
          {agents.length === 0 ? (
            <p className="workflow-diagram__empty">
              {emptyHint ??
                "No workflow agents yet. Materialize from Compose or load a swarm draft."}
            </p>
          ) : (
            agents.map((node, index) => (
              <React.Fragment key={node.id}>
                {index > 0 ? (
                  <span
                    aria-hidden="true"
                    className={
                      node.kind === "gate"
                        ? "workflow-diagram__arrow workflow-diagram__arrow--gate"
                        : "workflow-diagram__arrow"
                    }
                  >
                    →
                  </span>
                ) : null}
                <article
                  className={
                    node.kind === "gate"
                      ? "workflow-diagram__node workflow-diagram__node--gate"
                      : "workflow-diagram__node"
                  }
                >
                  {node.kind === "gate" ? (
                    <span className="workflow-diagram__badge">GATE</span>
                  ) : (
                    <span className="workflow-diagram__badge workflow-diagram__badge--agent">
                      agent
                    </span>
                  )}
                  <strong>{node.title}</strong>
                  <span title={node.subtitle}>{node.subtitle}</span>
                </article>
              </React.Fragment>
            ))
          )}
        </div>
        {graph.edges.some((e) => e.style === "refine") ? (
          <p className="workflow-diagram__refine">
            refine ≤3 · verify cycle (Agent Workflow style)
          </p>
        ) : null}
      </div>
    </div>
  );
}
