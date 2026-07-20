"use client";

import { useState } from "react";
import Link from "next/link";

import { PATTERNS } from "../lib/demo-data";
import { VersionPill } from "./design";

const prompts = ["Daily market intelligence with verification", "YouTube cinematic pipeline with a quality loop", "DSE ICT adaptive tutor and assessment", "Parallel legacy code analysis"];
const DEFAULT_PATTERN = PATTERNS[0];

if (!DEFAULT_PATTERN) throw new Error("The composer requires a default common pattern.");

export function Composer(): JSX.Element {
  const [goal, setGoal] = useState("Build a daily market intelligence swarm with evidence verification and concise executive reporting.");
  const [selectedPattern, setSelectedPattern] = useState<(typeof PATTERNS)[number]>(DEFAULT_PATTERN);
  return <><header className="composer-header"><div><p className="eyebrow">NEW SWARM DRAFT</p><input aria-label="Swarm name" defaultValue="Market intelligence swarm" /></div><div className="button-row"><button className="button button--secondary" type="button">Save draft</button><Link className="button button--ghost" href="/">Close</Link></div></header><div className="composer-layout"><section className="composer-chat"><div className="architect-note"><span>✦</span><div><strong>Common Swarm Architect</strong><p>Recommends from the registry and prioritizes verification, parallelism, and efficient reuse.</p></div></div><div className="message message--user">{goal}</div><div className="message message--assistant"><p>I recommend <strong>{selectedPattern.name}</strong> because your source gathering and signal analysis can run independently before a final evidence check.</p><article className="recommendation"><div><VersionPill version={selectedPattern.version} label="Recommended pattern" /><h2>{selectedPattern.name}</h2><p>{selectedPattern.metrics}. Suggested linked agents: Market Sentinel v2.4, Research Verifier v1.8, and Content Director v3.1.</p></div><Link className="button button--primary" href="/canvas">Load into canvas <span>→</span></Link></article><p className="muted">Risk mitigation: require evidence on every material claim and pause before external actions.</p></div><div className="goal-chips">{prompts.map((prompt) => <button key={prompt} type="button" onClick={() => setGoal(prompt)}>{prompt}</button>)}</div><label className="composer-input"><textarea value={goal} onChange={(event) => setGoal(event.target.value)} aria-label="Describe your swarm goal" /><button className="button button--primary" type="button">Send <span>↑</span></button></label></section><aside className="pattern-browser"><div className="panel-heading"><div><p className="eyebrow">COMMON PATTERNS</p><h2>Pattern browser</h2></div><button className="icon-button" type="button" aria-label="Search patterns">⌕</button></div>{PATTERNS.map((pattern) => <button className={selectedPattern.id === pattern.id ? "pattern-option pattern-option--selected" : "pattern-option"} type="button" key={pattern.id} onClick={() => setSelectedPattern(pattern)}><div className="mini-graph mini-graph--compact" aria-hidden="true"><i /><i /><i /><b /><b /></div><div><VersionPill version={pattern.version} label="Pattern" /><strong>{pattern.name}</strong><span>{pattern.description}</span><em>{pattern.metrics}</em></div></button>)}</aside></div></>;
}
