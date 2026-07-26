"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type CollaborationLandingView,
  type CollaborationSharedItem,
} from "../lib/projections/collaboration-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function CollaborationHome({
  view }: Readonly<{ view: CollaborationLandingView }>): JSX.Element {
  const labels = view.labels;
  const [tab, setTab] = useState(view.tabs[0] ?? "Shared with me");
  const [query, setQuery] = useState("");
  const [shareOpen, setShareOpen] = useState(true);
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [peopleQuery, setPeopleQuery] = useState("");

  const announce = (message: string): void => setStatusMessage(message);

  const items = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.sharedItems;
    return view.sharedItems.filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.detail.toLowerCase().includes(q) ||
        item.owner.toLowerCase().includes(q),
    );
  }, [query, view.sharedItems]);

  return (
    <section aria-label={L(labels, "collaboration_and_sharing_hub")} className="collab-home">
      <header className="collab-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <div className="collab-home__header-actions">
          <label className="collab-home__search">
            <span className="visually-hidden">{L(labels, "search_shared_items")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={query}
            />
          </label>
          <button
            className="collab-home__action collab-home__action--primary"
            onClick={() => {
              setShareOpen(true);
              announce(
                "Share requires an authorized sharing action with server-controlled permissions.",
              );
            }}
            type="button"
          >
            Share…
          </button>
        </div>
      </header>

      {statusMessage ? (
        <p aria-live="polite" className="collab-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div
        aria-label={L(labels, "share_lists")}
        className="collab-home__tabs"
        role="tablist"
      >
        {view.tabs.map((entry) => (
          <button
            aria-selected={tab === entry}
            className={
              tab === entry
                ? "collab-home__tab collab-home__tab--active"
                : "collab-home__tab"
            }
            key={entry}
            onClick={() => setTab(entry)}
            role="tab"
            type="button"
          >
            {entry}
          </button>
        ))}
      </div>

      <div className="collab-home__body">
        <div className="collab-home__main">
          <section aria-labelledby="shared-heading">
            <h2 className="visually-hidden" id="shared-heading">
              {tab}
            </h2>
            <ul className="collab-home__items">
              {items.map((item) => (
                <SharedItemRow
                  key={item.id}
                  item={item}
                  onAnnounce={announce}
                />
              ))}
            </ul>
            {items.length === 0 ? (
              <p className="collab-home__muted">{L(labels, "no_shared_items_match_the_search")}</p>
            ) : null}
          </section>

          {shareOpen ? (
            <section
              aria-label={L(labels, "share_modal")}
              className="collab-home__share-modal"
            >
              <div className="collab-home__section-head">
                <h2>{view.shareModal.title}</h2>
                <button
                  className="collab-home__linkish"
                  onClick={() => setShareOpen(false)}
                  type="button"
                >
                  Close
                </button>
              </div>
              <label className="collab-home__search collab-home__search--wide">
                <span className="visually-hidden">{L(labels, "add_people_or_teams")}</span>
                <input
                  onChange={(event) => setPeopleQuery(event.target.value)}
                  placeholder={L(labels, "add_people_or_teams_2")}
                  value={peopleQuery}
                />
              </label>
              <ul className="collab-home__members">
                {view.shareModal.members.map((member) => (
                  <li key={member.id}>
                    <span className="collab-home__avatar" aria-hidden="true">
                      {member.initials}
                    </span>
                    <div>
                      <strong>{member.name}</strong>
                      <span>{member.role}</span>
                    </div>
                  </li>
                ))}
              </ul>
              <div className="collab-home__link-box">
                <p>{L(labels, "link_sharing")}</p>
                <code>{view.shareModal.link}</code>
                <button
                  className="collab-home__action"
                  onClick={() =>
                    announce(
                      "Copy link is local-preview. Access is controlled server-side and can be revoked anytime.",
                    )
                  }
                  type="button"
                >
                  Copy link
                </button>
              </div>
              <p className="collab-home__muted">{view.shareModal.note}</p>
              <div className="collab-home__perm-toggles" role="group" aria-label={L(labels, "permission_levels")}>
                {["View", "Comment", "Edit"].map((level) => (
                  <label key={level}>
                    <input defaultChecked={level !== "Edit"} type="checkbox" />
                    {level}
                  </label>
                ))}
              </div>
            </section>
          ) : null}

          <section
            aria-labelledby="contribute-heading"
            className="collab-home__panel"
          >
            <h2 id="contribute-heading">{L(labels, "contribute_back_to_commons")}</h2>
            <p className="collab-home__muted">
              Turn your custom agents &amp; verified improvements into shared
              commons.
            </p>
            <ul className="collab-home__contrib-list">
              {view.contributions.map((item) => (
                <li key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.detail}</p>
                  </div>
                  <button
                    className="collab-home__action collab-home__action--primary"
                    onClick={() =>
                      announce(
                        `${item.cta} requires eval + review before merge. Provenance & attribution preserved.`,
                      )
                    }
                    type="button"
                  >
                    {item.cta}
                  </button>
                </li>
              ))}
            </ul>
            <p className="collab-home__muted">
              Proposals go through eval + review before merge. Provenance &amp;
              attribution preserved.
            </p>
            <p className="collab-home__impact">
              Your ecosystem impact: {view.impact}
            </p>
          </section>
        </div>

        <aside className="collab-home__sidebar">
          <section className="collab-home__panel" aria-labelledby="coedit-heading">
            <h2 id="coedit-heading">{L(labels, "live_co_editing")}</h2>
            <p className="collab-home__muted">
              Real-time collaboration on swarm canvases (presence only in this
              preview — CRDT/Yjs deferred).
            </p>
            <ul className="collab-home__sessions">
              {view.sessions.map((session) => (
                <li key={session.id}>
                  <strong>{session.title}</strong>
                  <div className="collab-home__presence">
                    {session.editors.map((editor) => (
                      <span className="collab-home__avatar" key={editor}>
                        {editor}
                      </span>
                    ))}
                    <span className="collab-home__muted">{session.presence}</span>
                  </div>
                  {session.canJoin ? (
                    <Link
                      className="collab-home__action collab-home__action--primary"
                      href="/canvas"
                    >
                      Join session
                    </Link>
                  ) : (
                    <button
                      className="collab-home__action"
                      onClick={() =>
                        announce(
                          "Open canvas in read-only presence mode when authorized.",
                        )
                      }
                      type="button"
                    >
                      Open canvas
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </section>

          <section className="collab-home__panel" aria-labelledby="team-heading">
            <h2 id="team-heading">{L(labels, "team_activity")}</h2>
            <ul className="collab-home__activity">
              {view.teamActivity.map((item) => (
                <li key={item.id}>
                  <span className="collab-home__avatar" aria-hidden="true">
                    {item.initials}
                  </span>
                  <div>
                    <p>{item.text}</p>
                    <small>{item.time}</small>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section className="collab-home__panel" aria-labelledby="queue-heading">
            <h2 id="queue-heading">{L(labels, "proposal_review_workflows")}</h2>
            <ul className="collab-home__queue">
              {view.proposalQueue.map((item) => (
                <li key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <span>
                      Assigned: {item.assignee} · {item.status}
                    </span>
                  </div>
                  <Link className="collab-home__linkish" href="/evaluations">
                    Open
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          <p className="collab-home__critique" role="note">
            {view.critiqueNote}
          </p>
        </aside>
      </div>

      <p className="collab-home__footer">{view.footerNote}</p>
    </section>
  );
}

function SharedItemRow({
  item,
  onAnnounce,
}: Readonly<{
  item: CollaborationSharedItem;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <li className="collab-home__item">
      <div className="collab-home__item-main">
        <span className={`collab-home__kind collab-home__kind--${item.kind}`}>
          {item.kind}
        </span>
        <div>
          <strong>{item.title}</strong>
          <p>{item.detail}</p>
          <small>
            {item.owner} · {item.scope}
          </small>
        </div>
      </div>
      <div className="collab-home__item-actions">
        {item.actions.map((action) => {
          if (action === "Open") {
            return (
              <Link
                className="collab-home__action collab-home__action--primary"
                href={item.kind === "agent" ? "/registry/agents/local-preview" : "/canvas"}
                key={action}
              >
                {action}
              </Link>
            );
          }
          if (action === "Add" || action === "Propose") {
            return (
              <button
                className="collab-home__action"
                key={action}
                onClick={() =>
                  onAnnounce(
                    `${action} requires an authorized registry or proposal action.`,
                  )
                }
                type="button"
              >
                {action}
              </button>
            );
          }
          return (
            <button
              className="collab-home__action"
              key={action}
              onClick={() =>
                onAnnounce(
                  `${action} requires an authorized workspace action.`,
                )
              }
              type="button"
            >
              {action}
            </button>
          );
        })}
      </div>
    </li>
  );
}
