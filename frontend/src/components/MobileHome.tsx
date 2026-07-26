"use client";

import React, { useState } from "react";
import Link from "next/link";

import {
  type MobileLandingView,
  type MobileTabId,
} from "../lib/projections/mobile-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function MobileHome({
  view }: Readonly<{ view: MobileLandingView }>): JSX.Element {
  const labels = view.labels;
  const [tab, setTab] = useState<MobileTabId>("home");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [sheet, setSheet] = useState<string | undefined>();
  const [registryQuery, setRegistryQuery] = useState("");

  const announce = (message: string): void => setStatusMessage(message);

  return (
    <section aria-label={L(labels, "mobile_companion")} className="mobile-home">
      <p className="mobile-home__intro lede">
        Mobile / PWA companion views for on-the-go monitoring, approvals, and
        quick actions. Desktop canvas editing is intentionally out of scope
        here.
      </p>

      <div className="mobile-home__device" aria-label={L(labels, "phone_preview")}>
        <header className="mobile-home__status-bar">
          <span>{view.timeLabel}</span>
          <span className="mobile-home__brand">{view.brand}</span>
          <span aria-hidden="true">●●●</span>
        </header>

        <div className="mobile-home__app-header">
          <div>
            <p className="mobile-home__workspace">{view.workspaceLabel}</p>
            <p className="mobile-home__live" role="status">
              {view.liveSummary}
            </p>
          </div>
          <Link
            aria-label={L(labels, "notifications_3_unread")}
            className="mobile-home__bell"
            href="/notifications"
          >
            3
          </Link>
          <Link
            aria-label={L(labels, "profile")}
            className="mobile-home__avatar"
            href="/profile"
          >
            NH
          </Link>
        </div>

        {statusMessage ? (
          <p aria-live="polite" className="mobile-home__status" role="status">
            {statusMessage}
          </p>
        ) : null}

        <div className="mobile-home__screen">
          {tab === "home" ? (
            <HomeTab
              view={view}
              onAnnounce={announce}
              onOpenSheet={setSheet}
             labels={labels} />
          ) : null}
          {tab === "activity" ? (
            <ActivityTab view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {tab === "registry" ? (
            <RegistryTab
              view={view}
              query={registryQuery}
              onQuery={setRegistryQuery}
              onAnnounce={announce}
             labels={labels} />
          ) : null}
          {tab === "more" ? (
            <MoreTab view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {tab === "compose" ? (
            <div className="mobile-home__panel">
              <p>{L(labels, "compose_opens_the_full_composer_for_guided_creat")}</p>
              <Link
                className="mobile-home__btn mobile-home__btn--primary"
                href="/composer"
              >
                Open Compose
              </Link>
            </div>
          ) : null}
        </div>

        {sheet ? (
          <div
            aria-label={L(labels, "action_sheet")}
            className="mobile-home__sheet"
            role="dialog"
          >
            <p>{sheet}</p>
            <button
              className="mobile-home__btn"
              onClick={() => setSheet(undefined)}
              type="button"
            >
              Close
            </button>
          </div>
        ) : null}

        <nav aria-label={L(labels, "mobile_bottom_navigation")} className="mobile-home__nav">
          {view.tabs.map((entry) => {
            if (entry.href && entry.id === "compose") {
              return (
                <Link
                  className="mobile-home__nav-item"
                  href={entry.href}
                  key={entry.id}
                >
                  {entry.label}
                </Link>
              );
            }
            return (
              <button
                aria-current={tab === entry.id ? "page" : undefined}
                className={
                  tab === entry.id
                    ? "mobile-home__nav-item mobile-home__nav-item--active"
                    : "mobile-home__nav-item"
                }
                key={entry.id}
                onClick={() => setTab(entry.id)}
                type="button"
              >
                {entry.label}
              </button>
            );
          })}
        </nav>
      </div>

      <p className="mobile-home__safety" role="note">
        {view.safetyNote}
      </p>
      <p className="mobile-home__footer">{view.footerNote}</p>
    </section>
  );
}

function HomeTab({
  view,
  onAnnounce,
  onOpenSheet,
  labels,
}: Readonly<{
  view: MobileLandingView;
  onAnnounce: (message: string) => void;
  onOpenSheet: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="mobile-home__stack">
      <div className="mobile-home__stats">
        {view.stats.map((stat) => (
          <article key={stat.id}>
            <p>{stat.label}</p>
            <strong>{stat.value}</strong>
          </article>
        ))}
      </div>

      <section aria-labelledby="mobile-swarms-heading">
        <div className="mobile-home__section-head">
          <h2 id="mobile-swarms-heading">{L(labels, "your_swarms")}</h2>
          <Link className="mobile-home__linkish" href="/activity">
            See all →
          </Link>
        </div>
        <ul className="mobile-home__cards">
          {view.runningSwarms.map((swarm) => (
            <li key={swarm.id}>
              <article className="mobile-home__card">
                <div className="mobile-home__card-top">
                  <strong>{swarm.name}</strong>
                  <span
                    className={`mobile-home__pill mobile-home__pill--${swarm.statusTone}`}
                  >
                    {swarm.status}
                  </span>
                </div>
                <p>{swarm.pattern}</p>
                <p className="mobile-home__meta">{swarm.meta}</p>
                {swarm.blockedReason ? (
                  <p className="mobile-home__blocked">
                    Blocked: {swarm.blockedReason}
                  </p>
                ) : null}
                <Link className="mobile-home__btn" href={swarm.canvasHref}>
                  Canvas
                </Link>
              </article>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="mobile-notes-heading">
        <h2 id="mobile-notes-heading">{L(labels, "notifications")}</h2>
        <ul className="mobile-home__cards">
          {view.notifications.map((item) => (
            <li key={item.id}>
              <article
                className={
                  item.highRisk
                    ? "mobile-home__card mobile-home__card--risk"
                    : "mobile-home__card"
                }
              >
                <div className="mobile-home__card-top">
                  <strong>{item.title}</strong>
                  <span className="mobile-home__meta">{item.meta}</span>
                </div>
                <p>{item.body}</p>
                <div className="mobile-home__actions">
                  {item.actions.map((action) =>
                    action.href ? (
                      <Link
                        className={
                          action.primary
                            ? "mobile-home__btn mobile-home__btn--primary"
                            : "mobile-home__btn"
                        }
                        href={action.href}
                        key={action.id}
                      >
                        {action.label}
                      </Link>
                    ) : (
                      <button
                        className={
                          action.primary
                            ? "mobile-home__btn mobile-home__btn--primary"
                            : "mobile-home__btn"
                        }
                        key={action.id}
                        onClick={() => {
                          onOpenSheet(
                            `${action.label} requires an authorized server command with evidence view (same as desktop).`,
                          );
                          onAnnounce(
                            `${action.label} uses server-issued IDs — payloads never embed approval ops or secrets.`,
                          );
                        }}
                        type="button"
                      >
                        {action.label}
                      </button>
                    ),
                  )}
                </div>
              </article>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="mobile-quick-heading">
        <h2 id="mobile-quick-heading">{L(labels, "quick_actions")}</h2>
        <div className="mobile-home__actions">
          <Link
            className="mobile-home__btn mobile-home__btn--primary"
            href="/registry"
          >
            Browse Commons
          </Link>
          <Link className="mobile-home__btn" href="/composer">
            Compose Swarm
          </Link>
        </div>
      </section>
    </div>
  );
}

function ActivityTab({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: MobileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="mobile-home__stack">
      <div className="mobile-home__section-head">
        <h2>{L(labels, "activity_feed")}</h2>
        <button
          className="mobile-home__linkish"
          onClick={() =>
            onAnnounce(
              "Pull-to-refresh is local-preview chrome until live activity projections connect.",
            )
          }
          type="button"
        >
          Refresh
        </button>
      </div>
      <ul className="mobile-home__cards">
        {view.activity.map((item) => (
          <li key={item.id}>
            <article className="mobile-home__card">
              <div className="mobile-home__card-top">
                <strong>{item.title}</strong>
                <span className="mobile-home__pill">{item.status}</span>
              </div>
              <p>{item.version}</p>
              <p className="mobile-home__meta">{item.meta}</p>
              <p className="mobile-home__meta">{item.lifecycle}</p>
              <div className="mobile-home__actions">
                <button
                  className="mobile-home__btn"
                  onClick={() =>
                    onAnnounce(
                      "Replay with latest requires server-determined eligibility and preserves immutable provenance.",
                    )
                  }
                  type="button"
                >
                  Replay with latest
                </button>
                <button
                  className="mobile-home__btn"
                  onClick={() =>
                    onAnnounce(
                      "Update commons requires an authorized bulk version action.",
                    )
                  }
                  type="button"
                >
                  Update commons
                </button>
              </div>
            </article>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RegistryTab({
  view,
  query,
  onQuery,
  onAnnounce,
  labels,
}: Readonly<{
  view: MobileLandingView;
  query: string;
  onQuery: (value: string) => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  const hits = view.registryHits.filter((hit) => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return true;
    return (
      hit.name.toLowerCase().includes(q) ||
      hit.version.toLowerCase().includes(q)
    );
  });

  return (
    <div className="mobile-home__stack">
      <h2>{L(labels, "registry_quick_search")}</h2>
      <label className="mobile-home__search">
        <span className="visually-hidden">{L(labels, "search_commons")}</span>
        <input
          onChange={(event) => onQuery(event.target.value)}
          placeholder={L(labels, "search_commons_2")}
          value={query}
        />
      </label>
      <ul className="mobile-home__cards">
        {hits.map((hit) => (
          <li key={hit.id}>
            <article className="mobile-home__card">
              <strong>{hit.name}</strong>
              <p>{hit.version}</p>
              <p className="mobile-home__meta">{hit.metric}</p>
              <div className="mobile-home__actions">
                <button
                  className="mobile-home__btn"
                  onClick={() =>
                    onAnnounce("Favorite is local-preview only until prefs connect.")
                  }
                  type="button"
                >
                  Favorite
                </button>
                <button
                  className="mobile-home__btn"
                  onClick={() =>
                    onAnnounce(
                      "Propose improvement requires an authorized proposal action.",
                    )
                  }
                  type="button"
                >
                  Propose
                </button>
                <Link
                  className="mobile-home__btn mobile-home__btn--primary"
                  href={`/registry/agents/${hit.id}`}
                >
                  Detail
                </Link>
              </div>
            </article>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MoreTab({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: MobileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="mobile-home__stack">
      <h2>{L(labels, "more")}</h2>
      <ul className="mobile-home__more-links">
        <li>
          <Link href="/profile">{L(labels, "profile")}</Link>
        </li>
        <li>
          <Link href="/notifications">{L(labels, "notifications")}</Link>
        </li>
        <li>
          <Link href="/operations">{L(labels, "monitoring")}</Link>
        </li>
        <li>
          <Link href="/settings">{L(labels, "settings")}</Link>
        </li>
        <li>
          <Link href="/onboarding">{L(labels, "help_onboarding")}</Link>
        </li>
      </ul>
      <div className="mobile-home__panel">
        <h3>{L(labels, "pwa")}</h3>
        <p className="mobile-home__meta">{view.offlineNote}</p>
        <button
          className="mobile-home__btn"
          onClick={() =>
            onAnnounce(
              "Push permission flow is reserved for service worker setup — not enabled in local preview.",
            )
          }
          type="button"
        >
          Enable push notifications
        </button>
      </div>
    </div>
  );
}
