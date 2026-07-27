"use client";

/**
 * @duty ProfileHome — operator profile projection (ui_13)
 * @role Display/edit profile fields via projection; mutations only through onAction.
 * @controls Section nav, profile fields, save intents when authorized.
 * @must Not store secrets; prefer host-authorized profile updates.
 * @mustnot Invent identity or privilege claims client-side.
 * @redesign docs/frontend_redesign/ui_13_profile.md
 */
import React, { useState } from "react";
import Link from "next/link";

import {
  type ProfileLandingView,
  type ProfileSectionId,
} from "../lib/projections/profile-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function ProfileHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: ProfileLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [section, setSection] = useState<ProfileSectionId>(view.defaultSectionId);
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [tokenRevealOnce, setTokenRevealOnce] = useState<string | undefined>();

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  return (
    <section aria-label={L(labels, "user_profile_and_preferences")} className="profile-home">
      <header className="profile-home__header">
        <div className="profile-home__identity">
          <span aria-hidden="true" className="profile-home__avatar">
            {view.initials}
          </span>
          <div>
            <p className="eyebrow">{view.eyebrow}</p>
            <h1>{view.displayName}</h1>
            <div className="profile-home__badges-row">
              <span className="profile-home__pill profile-home__pill--violet">
                {view.badge}
              </span>
              <span className="profile-home__pill">
                {view.roleLabel} · {view.workspaceLabel}
              </span>
            </div>
            <p className="profile-home__rank">{view.rankLabel}</p>
          </div>
        </div>
      </header>

      {feedback ? (
        <p aria-live="polite" className="profile-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div
        aria-label={L(labels, "profile_sections")}
        className="profile-home__tabs"
        role="tablist"
      >
        {view.sections.map((entry) => (
          <button
            aria-selected={section === entry.id}
            className={
              section === entry.id
                ? "profile-home__tab profile-home__tab--active"
                : "profile-home__tab"
            }
            key={entry.id}
            onClick={() => setSection(entry.id)}
            role="tab"
            type="button"
          >
            {entry.label}
          </button>
        ))}
      </div>

      {section === "overview" || section === "usage" ? (
        <OverviewSection view={view} onAnnounce={announce}  labels={labels} />
      ) : null}
      {section === "account" ? (
        <AccountSection view={view} onAnnounce={announce}  labels={labels} />
      ) : null}
      {section === "security" ? (
        <SecuritySection view={view} onAnnounce={announce}  labels={labels} />
      ) : null}
      {section === "preferences" ? (
        <PreferencesSection view={view} onAnnounce={announce}  labels={labels} />
      ) : null}
      {section === "tokens" ? (
        <TokensSection
          view={view}
          labels={labels}
          tokenRevealOnce={tokenRevealOnce}
          onCreate={() => {
            setTokenRevealOnce("casops_pat_•••••••••••••••• (shown once)");
            announce(
              "Create token requires an authorized token service. Value is shown once and never stored in the browser.",
            );
          }}
          onRevoke={() =>
            announce(L(labels, "revoke_requires_confirmation_and_an_authorized_t"))
          }
        />
      ) : null}

      <p className="profile-home__safety" role="note">
        {view.safetyNote}
      </p>
      <p className="profile-home__footer">{view.footerNote}</p>
    </section>
  );
}

function OverviewSection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="profile-home__overview">
      <div className="profile-home__impact" aria-label={L(labels, "personal_impact")}>
        {view.impact.map((card) => (
          <article key={card.id}>
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.detail}</span>
          </article>
        ))}
      </div>

      <div className="profile-home__split">
        <section aria-labelledby="activity-heading" className="profile-home__panel">
          <h2 id="activity-heading">{L(labels, "contribution_activity")}</h2>
          <p className="profile-home__muted">
            Proposals, merges, verifications over the last year
          </p>
          <div className="profile-home__heatmap" aria-hidden="true">
            {Array.from({ length: 52 }, (_, week) => (
              <span key={week} style={{ opacity: 0.25 + ((week * 7) % 5) * 0.15 }} />
            ))}
          </div>
          <div className="profile-home__heatmap-legend">
            <span>{L(labels, "less")}</span>
            <span>{L(labels, "more")}</span>
          </div>
          <p className="profile-home__activity-summary">{view.activitySummary}</p>
        </section>

        <section aria-labelledby="badges-heading" className="profile-home__panel">
          <h2 id="badges-heading">{L(labels, "badges_recognition")}</h2>
          <ul className="profile-home__badge-list">
            {view.badges.map((badge) => (
              <li key={badge}>{badge}</li>
            ))}
          </ul>
          <h3>{L(labels, "reputation_breakdown")}</h3>
          <dl className="profile-home__reputation">
            {view.reputation.map((row) => (
              <div key={row.label}>
                <dt>{row.label}</dt>
                <dd>{row.value}</dd>
              </div>
            ))}
          </dl>
          <p className="profile-home__muted">
            Reputation reflects server-attributed provenance — not self-declared.
          </p>
        </section>
      </div>

      <section aria-labelledby="contributions-heading" className="profile-home__panel">
        <div className="profile-home__section-head">
          <h2 id="contributions-heading">{L(labels, "my_contributions")}</h2>
          <button
            className="profile-home__action"
            onClick={() =>
              onAnnounce(
                "Export contribution history requires an authorized export action.",
              )
            }
            type="button"
          >
            Export contribution history (CSV)
          </button>
        </div>
        <p className="profile-home__muted">
          Filter by type · status · impact
        </p>
        <div className="profile-home__table-wrap">
          <table className="profile-home__table">
            <thead>
              <tr>
                <th scope="col">{L(labels, "common")}</th>
                <th scope="col">{L(labels, "type")}</th>
                <th scope="col">{L(labels, "status")}</th>
                <th scope="col">{L(labels, "impact")}</th>
              </tr>
            </thead>
            <tbody>
              {view.contributions.map((row) => (
                <tr key={row.id}>
                  <td>
                    <strong>{row.common}</strong>
                  </td>
                  <td>{row.type}</td>
                  <td>{row.status}</td>
                  <td>{row.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="profile-home__usage-links">
          {view.usageLinks.map((link) => (
            <Link className="profile-home__linkish" href={link.href} key={link.href}>
              {link.label}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function AccountSection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label={L(labels, "account")}>
      <h2>{L(labels, "account")}</h2>
      <dl className="profile-home__prefs">
        <div>
          <dt>{L(labels, "display_name")}</dt>
          <dd>{view.displayName}</dd>
        </div>
        <div>
          <dt>{L(labels, "handle")}</dt>
          <dd>{view.handle}</dd>
        </div>
        <div>
          <dt>{L(labels, "role_server_derived")}</dt>
          <dd>{view.roleLabel}</dd>
        </div>
        <div>
          <dt>{L(labels, "workspace_scope_server_derived")}</dt>
          <dd>{view.workspaceLabel}</dd>
        </div>
      </dl>
      <h3>{L(labels, "connected_sso_providers")}</h3>
      <ul className="profile-home__sso">
        {view.ssoProviders.map((provider) => (
          <li key={provider.id}>
            <strong>{provider.label}</strong>
            <span>{provider.status}</span>
          </li>
        ))}
      </ul>
      <button
        className="profile-home__action profile-home__action--primary"
        onClick={() =>
          onAnnounce("Account changes require an authorized profile action.")
        }
        type="button"
      >
        Save changes
      </button>
    </section>
  );
}

function SecuritySection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label={L(labels, "security")}>
      <h2>{L(labels, "security")}</h2>
      <p className="profile-home__muted">
        Credentials and automation secrets are never displayed or managed as
        plaintext on this page. SSO and session controls use server-side flows.
      </p>
      <ul className="profile-home__sso">
        {view.ssoProviders.map((provider) => (
          <li key={provider.id}>
            <strong>{provider.label}</strong>
            <span>{provider.status}</span>
            <button
              className="profile-home__linkish"
              onClick={() =>
                onAnnounce(
                  "SSO link/unlink requires an authorized identity action.",
                )
              }
              type="button"
            >
              Manage
            </button>
          </li>
        ))}
      </ul>
      <button
        className="profile-home__action"
        onClick={() =>
          onAnnounce("Sign out other sessions requires an authorized session action.")
        }
        type="button"
      >
        Sign out other sessions
      </button>
    </section>
  );
}

function PreferencesSection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label={L(labels, "personal_settings_2")}>
      <h2>{L(labels, "personal_settings")}</h2>
      <dl className="profile-home__prefs">
        {view.preferences.map((item) => (
          <div key={item.id}>
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
          </div>
        ))}
      </dl>
      <button
        className="profile-home__action profile-home__action--primary"
        onClick={() =>
          onAnnounce("Save preferences requires an authorized profile action.")
        }
        type="button"
      >
        Save changes
      </button>
    </section>
  );
}

function TokensSection({
  view,
  tokenRevealOnce,
  onCreate,
  onRevoke,
  labels,
}: Readonly<{
  view: ProfileLandingView;
  tokenRevealOnce?: string;
  onCreate: () => void;
  onRevoke: () => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label={L(labels, "api_tokens")}>
      <div className="profile-home__section-head">
        <h2>{L(labels, "api_token_manager")}</h2>
        <button
          className="profile-home__action profile-home__action--primary"
          onClick={onCreate}
          type="button"
        >
          Create token
        </button>
      </div>
      <p className="profile-home__muted">
        Scopes align with backend permissions. Token values are shown once at
        creation and never re-rendered from storage.
      </p>
      {tokenRevealOnce ? (
        <p className="profile-home__token-once" role="status">
          Copy now: {tokenRevealOnce}
        </p>
      ) : null}
      <div className="profile-home__table-wrap">
        <table className="profile-home__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "name")}</th>
              <th scope="col">{L(labels, "scopes")}</th>
              <th scope="col">{L(labels, "last_used")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "actions")}</th>
            </tr>
          </thead>
          <tbody>
            {view.tokens.map((token) => (
              <tr key={token.id}>
                <td>
                  <strong>{token.name}</strong>
                </td>
                <td>{token.scopes}</td>
                <td>{token.lastUsed}</td>
                <td>{token.status}</td>
                <td>
                  <button
                    className="profile-home__linkish"
                    onClick={onRevoke}
                    type="button"
                  >
                    Revoke
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
