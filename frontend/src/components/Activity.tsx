"use client";

import { useState } from "react";
import Link from "next/link";

import { RECENT_RUNS, type RunStatus } from "../lib/demo-data";
import { PageHeader, StatusBadge, VersionPill } from "./design";

const activity = [...RECENT_RUNS, { name: "Content release pipeline", pattern: "Map-reduce + consensus", status: "error" as const, duration: "8m 16s", cost: "$0.82", commons: "7 linked" }];

export function Activity(): JSX.Element {
  const [view, setView] = useState<"board" | "table">("board");
  const [status, setStatus] = useState<RunStatus | "all">("all");
  const visible = activity.filter((item) => status === "all" || item.status === status);
  return <><PageHeader eyebrow="ACTIVITY & OPS INTELLIGENCE" title="Trace every outcome to its common version." description="Find fleet bottlenecks, compare versions, and safely replay what needs attention." actions={<button className="button button--secondary" type="button">Live updates <span className="live-dot" /> On</button>} /><section className="activity-filters"><label className="search-input"><span>⌕</span><input placeholder="Search swarm, run ID, common agent, or error" aria-label="Search activity" /></label><select aria-label="Date range" defaultValue="7"><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="today">Today</option></select><select aria-label="Run status" value={status} onChange={(event) => setStatus(event.target.value as RunStatus | "all")}><option value="all">All statuses</option><option value="running">Running</option><option value="success">Success</option><option value="paused">Paused</option><option value="error">Error</option></select><button className="filter-button" type="button">Outdated commons only</button></section><div className="activity-header"><div className="view-toggle"><button type="button" className={view === "board" ? "active" : ""} onClick={() => setView("board")}>Board</button><button type="button" className={view === "table" ? "active" : ""} onClick={() => setView("table")}>Table</button></div><span>{visible.length} runs in this view</span></div>{view === "board" ? <section className="activity-board">{["Data & analysis", "Synthesis & verification"].map((group, groupIndex) => <article className="board-column" key={group}><header><div><VersionPill version={groupIndex === 0 ? "1.4" : "2.0"} label="Pattern" /><h2>{group}</h2></div><span>{groupIndex === 0 ? "94% success" : "91% success"}</span></header>{visible.filter((_, index) => index % 2 === groupIndex).map((run) => <RunCard key={run.name} {...run} />)}</article>)}</section> : <section className="panel"><div className="run-table" role="table" aria-label="Activity table"><div className="run-table__head" role="row"><span>SWARM</span><span>PATTERN</span><span>COMMONS</span><span>STATUS</span><span>METRICS</span></div>{visible.map((run) => <div className="run-table__row" role="row" key={run.name}><Link href="/canvas">{run.name}</Link><span>{run.pattern}</span><span>{run.commons}</span><StatusBadge status={run.status} /><span>{run.duration} · {run.cost}</span></div>)}</div></section>}<section className="insight-strip"><span>✦</span><p><strong>Rollout opportunity:</strong> Research Verifier v1.8 has a 12% higher pass rate than v1.6 across similar swarms.</p><button className="button button--ghost" type="button">Review impact →</button></section></>;
}

function RunCard({ name, pattern, status, duration, cost, commons }: { readonly name: string; readonly pattern: string; readonly status: RunStatus; readonly duration: string; readonly cost: string; readonly commons: string }): JSX.Element {
  return <article className="execution-card"><div><StatusBadge status={status} /><time>Today, 10:42</time></div><h3>{name}</h3><p>{pattern}</p><VersionPill version="1.8" /><footer><span>{commons}</span><span>{duration} · {cost}</span></footer><Link href="/canvas">View canvas →</Link></article>;
}
