"use client";

import React, { useState } from "react";
import Link from "next/link";

import {
  LOCAL_PROFILE_LANDING,
  type ProfileLandingView,
  type ProfileSectionId,
} from "../lib/projections/profile-landing";

const SECTIONS: readonly { readonly id: ProfileSectionId; readonly label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "account", label: "Account" },
  { id: "security", label: "Security" },
  { id: "usage", label: "Usage & Impact" },
  { id: "preferences", label: "Preferences" },
  { id: "tokens", label: "API Tokens" },
];

export function ProfileHome({
  view = LOCAL_PROFILE_LANDING,
}: Readonly<{ view?: ProfileLandingView }>): JSX.Element {
  const [section, setSection] = useState<ProfileSectionId>("overview");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [tokenRevealOnce, setTokenRevealOnce] = useState<string | undefined>();

  const announce = (message: string): void => setStatusMessage(message);

  return (
    <section aria-label="User profile and preferences" className="profile-home">
      <header className="profile-home__header">
        <div className="profile-home__identity">
          <span aria-hidden="true" className="profile-home__avatar">
            {view.initials}
          </span>
          <div>
            <p className="eyebrow">PROFILE &amp; CONTRIBUTIONS</p>
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

      {statusMessage ? (
        <p aria-live="polite" className="profile-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div
        aria-label="Profile sections"
        className="profile-home__tabs"
        role="tablist"
      >
        {SECTIONS.map((entry) => (
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
        <OverviewSection view={view} onAnnounce={announce} />
      ) : null}
      {section === "account" ? (
        <AccountSection view={view} onAnnounce={announce} />
      ) : null}
      {section === "security" ? (
        <SecuritySection view={view} onAnnounce={announce} />
      ) : null}
      {section === "preferences" ? (
        <PreferencesSection view={view} onAnnounce={announce} />
      ) : null}
      {section === "tokens" ? (
        <TokensSection
          view={view}
          tokenRevealOnce={tokenRevealOnce}
          onCreate={() => {
            setTokenRevealOnce("casops_pat_•••••••••••••••• (shown once)");
            announce(
              "Create token requires an authorized token service. Value is shown once and never stored in the browser.",
            );
          }}
          onRevoke={() =>
            announce("Revoke requires confirmation and an authorized token action.")
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
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="profile-home__overview">
      <div className="profile-home__impact" aria-label="Personal impact">
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
          <h2 id="activity-heading">Contribution Activity</h2>
          <p className="profile-home__muted">
            Proposals, merges, verifications over the last year
          </p>
          <div className="profile-home__heatmap" aria-hidden="true">
            {Array.from({ length: 52 }, (_, week) => (
              <span key={week} style={{ opacity: 0.25 + ((week * 7) % 5) * 0.15 }} />
            ))}
          </div>
          <div className="profile-home__heatmap-legend">
            <span>Less</span>
            <span>More</span>
          </div>
          <p className="profile-home__activity-summary">{view.activitySummary}</p>
        </section>

        <section aria-labelledby="badges-heading" className="profile-home__panel">
          <h2 id="badges-heading">Badges &amp; Recognition</h2>
          <ul className="profile-home__badge-list">
            {view.badges.map((badge) => (
              <li key={badge}>{badge}</li>
            ))}
          </ul>
          <h3>Reputation breakdown</h3>
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
          <h2 id="contributions-heading">My Contributions</h2>
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
                <th scope="col">Common</th>
                <th scope="col">Type</th>
                <th scope="col">Status</th>
                <th scope="col">Impact</th>
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
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label="Account">
      <h2>Account</h2>
      <dl className="profile-home__prefs">
        <div>
          <dt>Display name</dt>
          <dd>{view.displayName}</dd>
        </div>
        <div>
          <dt>Handle</dt>
          <dd>{view.handle}</dd>
        </div>
        <div>
          <dt>Role (server-derived)</dt>
          <dd>{view.roleLabel}</dd>
        </div>
        <div>
          <dt>Workspace scope (server-derived)</dt>
          <dd>{view.workspaceLabel}</dd>
        </div>
      </dl>
      <h3>Connected SSO providers</h3>
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
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label="Security">
      <h2>Security</h2>
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
}: Readonly<{
  view: ProfileLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label="Personal settings">
      <h2>Personal Settings</h2>
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
}: Readonly<{
  view: ProfileLandingView;
  tokenRevealOnce?: string;
  onCreate: () => void;
  onRevoke: () => void;
}>): JSX.Element {
  return (
    <section className="profile-home__panel" aria-label="API tokens">
      <div className="profile-home__section-head">
        <h2>API Token Manager</h2>
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
              <th scope="col">Name</th>
              <th scope="col">Scopes</th>
              <th scope="col">Last used</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
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
