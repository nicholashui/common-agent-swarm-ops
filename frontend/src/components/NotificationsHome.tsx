"use client";

/**
 * @duty NotificationsHome — notifications projection (ui_12)
 * @role List notifications; mark-read is session/local or host-authorized only.
 * @controls List filters, mark read, open deep links in-app.
 * @must Not invent notification authority or privileged payloads.
 * @mustnot Auto-open external untrusted destinations.
 * @redesign docs/frontend_redesign/ui_12_notifications.md
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type NotificationItem,
  type NotificationsLandingView,
} from "../lib/projections/notifications-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { cycleOption } from "../lib/ui/local-controls";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

const GROUP_BY_OPTIONS = [
  "Group by: time",
  "Group by: kind",
  "Group by: priority",
  "Group by: none",
] as const;

export function NotificationsHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: NotificationsLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [filter, setFilter] = useState(view.filters[0] ?? "All (7)");
  const [query, setQuery] = useState("");
  const [readIds, setReadIds] = useState<ReadonlySet<string>>(() => new Set());
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [groupBy, setGroupBy] = useState<string>(GROUP_BY_OPTIONS[0]);
  const [notifyAbout, setNotifyAbout] = useState(
    () => new Map(view.notifyAbout.map((item) => [item.id, item.enabled])),
  );
  const [channels, setChannels] = useState(
    () => new Map(view.channels.map((item) => [item.id, item.enabled])),
  );

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const items = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = view.items.filter((item) => {
      if (filter.startsWith("Proposals") && item.kind !== "proposal") return false;
      if (filter.startsWith("Rollouts") && item.kind !== "rollout" && item.kind !== "common") {
        return false;
      }
      if (filter.startsWith("Gates") && item.kind !== "gate") return false;
      if (filter.startsWith("Anomalies") && item.kind !== "anomaly") return false;
      if (q.length === 0) return true;
      return (
        item.title.toLowerCase().includes(q) ||
        item.body.toLowerCase().includes(q) ||
        item.meta.toLowerCase().includes(q)
      );
    });
    if (groupBy.includes("kind")) {
      return [...filtered].sort((a, b) => a.kind.localeCompare(b.kind));
    }
    if (groupBy.includes("priority")) {
      return [...filtered].sort((a, b) => {
        const score = (item: NotificationItem): number =>
          item.group === "today-high" ? 0 : item.unread ? 1 : 2;
        return score(a) - score(b);
      });
    }
    return filtered;
  }, [filter, groupBy, query, view.items]);

  const highPriority = items.filter((item) => item.group === "today-high");
  const earlier = items.filter((item) => item.group === "earlier");
  const flatGroups =
    groupBy.includes("none") || groupBy.includes("kind") || groupBy.includes("priority");

  const unreadCount = view.items.filter(
    (item) => item.unread && !readIds.has(item.id),
  ).length;

  const markAllRead = (): void => {
    const ids = view.items.map((item) => item.id);
    setReadIds(new Set(ids));
    if (onAction) {
      void onAction({ kind: "local.mark_read", ids });
      return;
    }
    announce(`Marked ${ids.length} notification(s) as read.`);
  };

  const markRead = (id: string): void => {
    setReadIds((current) => new Set(current).add(id));
    if (onAction) {
      void onAction({ kind: "local.mark_read", ids: [id] });
      return;
    }
    announce(`Notification ${id} marked read.`);
  };

  const savePreferences = (): void => {
    const enabledNotify = [...notifyAbout.entries()]
      .filter(([, enabled]) => enabled)
      .map(([id]) => id);
    const enabledChannels = [...channels.entries()]
      .filter(([, enabled]) => enabled)
      .map(([id]) => id);
    const summary = `Preferences saved locally: notify=${enabledNotify.join(",") || "none"}; channels=${enabledChannels.join(",") || "none"}.`;
    if (onAction) {
      void onAction({
        kind: "local.save_prefs",
        screen: "notifications",
        summary,
      });
      return;
    }
    announce(summary);
  };

  return (
    <section aria-label={L(labels, "notifications_center")} className="notifications-home">
      <header className="notifications-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>
            {view.title}
            <span className="notifications-home__badge" aria-label={`${unreadCount} unread`}>
              {unreadCount}
            </span>
          </h1>
          <p className="lede">{view.description}</p>
        </div>
        <div className="notifications-home__header-actions">
          <label className="notifications-home__search">
            <span className="visually-hidden">{L(labels, "search_notifications")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={L(labels, "search_notifications_2")}
              value={query}
            />
          </label>
          <button
            className="notifications-home__action"
            onClick={markAllRead}
            type="button"
          >
            Mark all read
          </button>
          <button
            aria-label={`${groupBy}. Click to cycle grouping.`}
            className="notifications-home__action"
            onClick={() => {
              const next = cycleOption([...GROUP_BY_OPTIONS], groupBy);
              setGroupBy(next);
              announce(`${next} (local presentation).`);
            }}
            type="button"
          >
            {groupBy} ▾
          </button>
        </div>
      </header>

      <div
        aria-label={L(labels, "notification_filters")}
        className="notifications-home__filters"
        role="group"
      >
        {view.filters.map((entry) => (
          <button
            aria-pressed={filter === entry}
            className={
              filter === entry
                ? "notifications-home__filter notifications-home__filter--active"
                : "notifications-home__filter"
            }
            key={entry}
            onClick={() => setFilter(entry)}
            type="button"
          >
            {entry}
          </button>
        ))}
      </div>

      {feedback ? (
        <p aria-live="polite" className="notifications-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="notifications-home__body">
        <div className="notifications-home__main">
          {flatGroups ? (
            <section aria-labelledby="flat-list-heading">
              <h2 className="notifications-home__section-label" id="flat-list-heading">
                {groupBy}
              </h2>
              <ul className="notifications-home__list">
                {items.map((item) => (
                  <NotificationCard
                    key={item.id}
                    item={item}
                    isRead={readIds.has(item.id) || !item.unread}
                    onMarkRead={markRead}
                    onAnnounce={announce}
                    labels={labels}
                  />
                ))}
              </ul>
            </section>
          ) : null}

          {!flatGroups && highPriority.length > 0 ? (
            <section aria-labelledby="high-priority-heading">
              <h2 className="notifications-home__section-label" id="high-priority-heading">
                Today · High priority
              </h2>
              <ul className="notifications-home__list">
                {highPriority.map((item) => (
                  <NotificationCard
                    key={item.id}
                    item={item}
                    isRead={readIds.has(item.id) || !item.unread}
                    onMarkRead={markRead}
                    onAnnounce={announce}
                   labels={labels} />
                ))}
              </ul>
            </section>
          ) : null}

          {!flatGroups && earlier.length > 0 ? (
            <section aria-labelledby="earlier-heading">
              <h2 className="notifications-home__section-label" id="earlier-heading">
                Earlier today
              </h2>
              <ul className="notifications-home__list">
                {earlier.map((item) => (
                  <NotificationCard
                    key={item.id}
                    item={item}
                    isRead={readIds.has(item.id) || !item.unread}
                    onMarkRead={markRead}
                    onAnnounce={announce}
                   labels={labels} />
                ))}
              </ul>
            </section>
          ) : null}

          {items.length === 0 ? (
            <div className="notifications-home__empty panel">
              <p>{L(labels, "no_notifications_match_the_current_filters")}</p>
            </div>
          ) : null}
        </div>

        <aside aria-label={L(labels, "notification_preferences")} className="notifications-home__prefs">
          <h2>{L(labels, "preferences")}</h2>
          <h3>{L(labels, "notify_me_about")}</h3>
          <ul className="notifications-home__pref-list">
            {view.notifyAbout.map((item) => (
              <li key={item.id}>
                <label>
                  <input
                    checked={notifyAbout.get(item.id) ?? item.enabled}
                    onChange={(event) => {
                      setNotifyAbout((current) => {
                        const next = new Map(current);
                        next.set(item.id, event.target.checked);
                        return next;
                      });
                    }}
                    type="checkbox"
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>

          <h3>{L(labels, "delivery_channels")}</h3>
          <ul className="notifications-home__pref-list">
            {view.channels.map((item) => (
              <li key={item.id}>
                <label>
                  <input
                    checked={channels.get(item.id) ?? item.enabled}
                    onChange={(event) => {
                      setChannels((current) => {
                        const next = new Map(current);
                        next.set(item.id, event.target.checked);
                        return next;
                      });
                    }}
                    type="checkbox"
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>

          <div className="notifications-home__quiet">
            <h3>{L(labels, "quiet_hours_digest")}</h3>
            <p>{view.quietHours}</p>
          </div>

          <button
            className="notifications-home__action notifications-home__action--primary"
            onClick={savePreferences}
            type="button"
          >
            Save preferences
          </button>

          <button
            className="notifications-home__action"
            onClick={() => announce("Snoozed notification type for 24 hours (local).")}
            type="button"
          >
            Snooze type 24h
          </button>

          <p className="notifications-home__safety" role="note">
            {view.safetyNote}
          </p>
        </aside>
      </div>

      <p className="notifications-home__footer">{view.footerNote}</p>
    </section>
  );
}

function NotificationCard({
  item,
  isRead,
  onMarkRead,
  onAnnounce,
  labels,
}: Readonly<{
  item: NotificationItem;
  isRead: boolean;
  onMarkRead: (id: string) => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <li>
      <article
        className={
          isRead
            ? `notifications-home__card notifications-home__card--${item.priority} notifications-home__card--read`
            : `notifications-home__card notifications-home__card--${item.priority}`
        }
      >
        <div className="notifications-home__card-top">
          <span className={`notifications-home__kind notifications-home__kind--${item.kind}`}>
            {item.kind}
          </span>
          {!isRead ? (
            <span className="notifications-home__unread">{L(labels, "unread")}</span>
          ) : null}
        </div>
        <h3>{item.title}</h3>
        <p>{item.body}</p>
        {item.gateDetail ? (
          <p className="notifications-home__gate">{item.gateDetail}</p>
        ) : null}
        <p className="notifications-home__meta">{item.meta}</p>
        <div className="notifications-home__actions">
          {item.actions.map((action) => {
            if (action.href) {
              return (
                <Link
                  className={
                    action.primary
                      ? "notifications-home__action notifications-home__action--primary"
                      : "notifications-home__action"
                  }
                  href={action.href}
                  key={action.id}
                  onClick={() => onMarkRead(item.id)}
                >
                  {action.label}
                </Link>
              );
            }
            return (
              <button
                className={
                  action.primary
                    ? "notifications-home__action notifications-home__action--primary"
                    : "notifications-home__action"
                }
                key={action.id}
                onClick={() => {
                  onMarkRead(item.id);
                  onAnnounce(
                    `${action.label} requires an authorized server command — payloads never embed approval ops or secrets.`,
                  );
                }}
                type="button"
              >
                {action.label}
              </button>
            );
          })}
        </div>
      </article>
    </li>
  );
}
