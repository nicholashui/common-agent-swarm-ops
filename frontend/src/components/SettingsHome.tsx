"use client";

/**
 * @duty SettingsHome — workspace settings projection (ui_08)
 * @role Present preference sections; persist only local or host-authorized prefs.
 * @controls Section nav, preference fields, save intents via onAction.
 * @must Never store credentials or production activation toggles.
 * @mustnot Enable live media/production from client prefs alone.
 * @redesign docs/frontend_redesign/ui_08_settings.md
 */
import React, { useMemo, useState } from "react";

import {
  type SettingsLandingView,
  type SettingsSectionId,
} from "../lib/projections/settings-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function SettingsHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: SettingsLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [section, setSection] = useState<SettingsSectionId>("providers");
  const [query, setQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [policyDraft, setPolicyDraft] = useState<ReadonlyMap<string, boolean>>(
    () => new Map(view.policies.map((policy) => [policy.id, policy.enabled])),
  );

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const navItems = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.nav;
    return view.nav.filter((item) => item.label.toLowerCase().includes(q));
  }, [query, view.nav]);

  const activeLabel =
    view.nav.find((item) => item.id === section)?.label ?? "Settings";

  return (
    <section aria-label={L(labels, "global_settings")} className="settings-home">
      <header className="settings-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <label className="settings-home__search">
          <span className="visually-hidden">{L(labels, "search_across_settings")}</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={query}
          />
        </label>
      </header>

      {feedback ? (
        <p aria-live="polite" className="settings-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="settings-home__body">
        <nav aria-label={L(labels, "settings_sections")} className="settings-home__nav">
          {navItems.map((item) => (
            <button
              aria-current={section === item.id ? "page" : undefined}
              className={
                section === item.id
                  ? "settings-home__nav-item settings-home__nav-item--active"
                  : "settings-home__nav-item"
              }
              key={item.id}
              onClick={() => setSection(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="settings-home__content">
          <h2 className="settings-home__section-title">{activeLabel}</h2>

          {section === "providers" ? (
            <ProvidersSection view={view} onAnnounce={announce} />
          ) : null}
          {section === "secrets" ? (
            <SecretsSection view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {section === "integrations" ? (
            <IntegrationsSection view={view} onAnnounce={announce} />
          ) : null}
          {section === "policies" ? (
            <PoliciesSection
              view={view}
              policyDraft={policyDraft}
              onToggle={(id, enabled) => {
                setPolicyDraft((current) => {
                  const next = new Map(current);
                  next.set(id, enabled);
                  return next;
                });
                announce(
                  "Policy changes require confirmation and an authorized settings action.",
                );
              }}
              onAnnounce={announce}
            />
          ) : null}
          {section === "defaults" ? (
            <DefaultsSection view={view} onAnnounce={announce} />
          ) : null}
          {section === "ui" ? <UiSection view={view} onAnnounce={announce} /> : null}
          {section === "workspaces" ? (
            <WorkspacesSection view={view} onAnnounce={announce}  labels={labels} />
          ) : null}

          <p className="settings-home__va" role="note">
            {view.vaNote}
          </p>
        </div>
      </div>

      <p className="settings-home__footer">{view.footerNote}</p>
    </section>
  );
}

function ProvidersSection({
  view,
  onAnnounce,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <p className="settings-home__intro">
        Configure providers, fetch models, test connections. Secrets stay
        server-side.
      </p>
      <ul className="settings-home__cards">
        {view.providers.map((provider) => (
          <li className="settings-home__card" key={provider.id}>
            <div className="settings-home__card-top">
              <span aria-hidden="true" className="settings-home__provider-icon">
                {provider.icon}
              </span>
              <div>
                <strong>{provider.name}</strong>
                <span
                  className={`settings-home__health settings-home__health--${provider.status}`}
                >
                  {provider.statusLabel}
                </span>
              </div>
            </div>
            <p>{provider.models}</p>
            <div className="settings-home__actions">
              <button
                className="settings-home__action settings-home__action--primary"
                onClick={() =>
                  onAnnounce(
                    "Test connection requires an authorized settings action.",
                  )
                }
                type="button"
              >
                Test connection
              </button>
              <button
                className="settings-home__action"
                onClick={() =>
                  onAnnounce(
                    "Fetch models requires an authorized settings action.",
                  )
                }
                type="button"
              >
                Fetch models
              </button>
            </div>
          </li>
        ))}
      </ul>
      <button
        className="settings-home__action"
        onClick={() =>
          onAnnounce("Add provider requires an authorized settings action.")
        }
        type="button"
      >
        + Add provider
      </button>
    </div>
  );
}

function SecretsSection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <p className="settings-home__intro">{view.secretsNote}</p>
      <div className="settings-home__table-wrap">
        <table className="settings-home__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "name")}</th>
              <th scope="col">{L(labels, "scope")}</th>
              <th scope="col">{L(labels, "last_rotated")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "actions")}</th>
            </tr>
          </thead>
          <tbody>
            {view.secrets.map((secret) => (
              <tr key={secret.id}>
                <td>
                  <strong>{secret.name}</strong>
                </td>
                <td>{secret.scope}</td>
                <td>{secret.lastRotated}</td>
                <td>{secret.status}</td>
                <td>
                  <button
                    className="settings-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Reveal requires an authorized audited reveal action. Values are never stored client-side.",
                      )
                    }
                    type="button"
                  >
                    Reveal
                  </button>
                  <button
                    className="settings-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Rotate requires an authorized secrets action.",
                      )
                    }
                    type="button"
                  >
                    Rotate
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        className="settings-home__action settings-home__action--primary"
        onClick={() =>
          onAnnounce(
            "Add secret requires an authorized secrets action. Value is never shown after save.",
          )
        }
        type="button"
      >
        + Add secret
      </button>
      <p className="settings-home__muted">
        No secret values are present in this local preview projection.
      </p>
    </div>
  );
}

function IntegrationsSection({
  view,
  onAnnounce,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <ul className="settings-home__cards">
      {view.integrations.map((item) => (
        <li className="settings-home__card" key={item.id}>
          <div className="settings-home__card-top">
            <strong>{item.name}</strong>
            <span
              className={`settings-home__health settings-home__health--${item.health}`}
            >
              {item.healthLabel}
            </span>
          </div>
          <p>{item.detail}</p>
          <button
            className="settings-home__action"
            onClick={() =>
              onAnnounce(
                "Configure integration requires an authorized settings action.",
              )
            }
            type="button"
          >
            Configure
          </button>
        </li>
      ))}
    </ul>
  );
}

function PoliciesSection({
  view,
  policyDraft,
  onToggle,
  onAnnounce,
}: Readonly<{
  view: SettingsLandingView;
  policyDraft: ReadonlyMap<string, boolean>;
  onToggle: (id: string, enabled: boolean) => void;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <div className="settings-home__impact" role="status">
        <span aria-hidden="true">!</span>
        <div>
          <strong>{view.policyImpact.title}</strong>
          <p>{view.policyImpact.body}</p>
          <p className="settings-home__muted">{view.policyImpact.affectedLabel}</p>
          <div className="settings-home__actions">
            <button
              className="settings-home__action settings-home__action--primary"
              onClick={() => {
                const enabled = [...policyDraft.entries()]
                  .filter(([, on]) => on)
                  .map(([id]) => id);
                onAnnounce(
                  `Applied ${enabled.length} enabled policy flag(s) to session draft for all swarms: ${enabled.join(", ") || "none"}.`,
                );
              }}
              type="button"
            >
              Apply to all my swarms
            </button>
            <button
              className="settings-home__action"
              onClick={() => {
                const enabled = [...policyDraft.entries()]
                  .filter(([, on]) => on)
                  .map(([id]) => id);
                onAnnounce(
                  `Applied ${enabled.length} policy flag(s) to selected swarms in session draft.`,
                );
              }}
              type="button"
            >
              Apply only to selected
            </button>
          </div>
        </div>
      </div>

      <ul className="settings-home__policies">
        {view.policies.map((policy) => {
          const enabled = policyDraft.get(policy.id) ?? policy.enabled;
          return (
            <li key={policy.id}>
              <div>
                <strong>{policy.label}</strong>
                <p>{policy.description}</p>
                <span className="settings-home__muted">{policy.impactLabel}</span>
              </div>
              <label className="settings-home__switch">
                <span className="visually-hidden">
                  Toggle {policy.label}
                </span>
                <input
                  checked={enabled}
                  onChange={(event) => onToggle(policy.id, event.target.checked)}
                  type="checkbox"
                />
              </label>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function DefaultsSection({
  view,
  onAnnounce,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <ul className="settings-home__defaults">
        {view.defaults.map((item) => (
          <li key={item.id}>
            <strong>{item.label}</strong>
            <span>{item.value}</span>
            <small>{item.note}</small>
          </li>
        ))}
      </ul>
      <button
        className="settings-home__action settings-home__action--primary"
        onClick={() =>
          onAnnounce(
            `Saved ${view.defaults.length} default setting(s) to session draft.`,
          )
        }
        type="button"
      >
        Save defaults
      </button>
    </div>
  );
}

function UiSection({
  view,
  onAnnounce,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <ul className="settings-home__defaults">
        {view.uiPrefs.map((item) => (
          <li key={item.id}>
            <strong>{item.label}</strong>
            <span>{item.value}</span>
          </li>
        ))}
      </ul>
      <button
        className="settings-home__action settings-home__action--primary"
        onClick={() =>
          onAnnounce(
            `Saved ${view.uiPrefs.length} UI preference(s) to session draft.`,
          )
        }
        type="button"
      >
        Save preferences
      </button>
    </div>
  );
}

function WorkspacesSection({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: SettingsLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="settings-home__section">
      <h3 className="settings-home__subsection">{L(labels, "workspaces_access_control")}</h3>
      <div className="settings-home__table-wrap">
        <table className="settings-home__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "member")}</th>
              <th scope="col">{L(labels, "role")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "actions")}</th>
            </tr>
          </thead>
          <tbody>
            {view.members.map((member) => (
              <tr key={member.id}>
                <td>
                  <span className="settings-home__avatar" aria-hidden="true">
                    {member.initials}
                  </span>
                  <strong>{member.name}</strong>
                </td>
                <td>{member.role}</td>
                <td>{member.status}</td>
                <td>
                  <button
                    className="settings-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Role changes require an authorized access-control action.",
                      )
                    }
                    type="button"
                  >
                    Edit role
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        className="settings-home__action settings-home__action--primary"
        onClick={() =>
          onAnnounce(
            "Invite member requires an authorized workspace invite action (e.g. Keycloak-linked).",
          )
        }
        type="button"
      >
        + Invite member
      </button>
    </div>
  );
}
