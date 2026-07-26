"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  LOCAL_NOTIFICATIONS_LANDING,
  type NotificationItem,
  type NotificationsLandingView,
} from "../lib/projections/notifications-landing";

export function NotificationsHome({
  view = LOCAL_NOTIFICATIONS_LANDING,
}: Readonly<{ view?: NotificationsLandingView }>): JSX.Element {
  const [filter, setFilter] = useState(view.filters[0] ?? "All (7)");
  const [query, setQuery] = useState("");
  const [readIds, setReadIds] = useState<ReadonlySet<string>>(() => new Set());
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [notifyAbout, setNotifyAbout] = useState(
    () => new Map(view.notifyAbout.map((item) => [item.id, item.enabled])),
  );
  const [channels, setChannels] = useState(
    () => new Map(view.channels.map((item) => [item.id, item.enabled])),
  );

  const announce = (message: string): void => setStatusMessage(message);

  const items = useMemo(() => {
    const q = query.trim().toLowerCase();
    return view.items.filter((item) => {
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
  }, [filter, query, view.items]);

  const highPriority = items.filter((item) => item.group === "today-high");
  const earlier = items.filter((item) => item.group === "earlier");

  const unreadCount = view.items.filter(
    (item) => item.unread && !readIds.has(item.id),
  ).length;

  const markAllRead = (): void => {
    setReadIds(new Set(view.items.map((item) => item.id)));
    announce("Mark all read requires an authorized preference action when synced.");
  };

  const markRead = (id: string): void => {
    setReadIds((current) => new Set(current).add(id));
  };

  return (
    <section aria-label="Notifications center" className="notifications-home">
      <header className="notifications-home__header">
        <div>
          <p className="eyebrow">NOTIFICATIONS</p>
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
            <span className="visually-hidden">Search notifications</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search notifications…"
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
          <button className="notifications-home__action" type="button">
            Group by ▾
          </button>
        </div>
      </header>

      <div
        aria-label="Notification filters"
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

      {statusMessage ? (
        <p aria-live="polite" className="notifications-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="notifications-home__body">
        <div className="notifications-home__main">
          {highPriority.length > 0 ? (
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
                  />
                ))}
              </ul>
            </section>
          ) : null}

          {earlier.length > 0 ? (
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
                  />
                ))}
              </ul>
            </section>
          ) : null}

          {items.length === 0 ? (
            <div className="notifications-home__empty panel">
              <p>No notifications match the current filters.</p>
            </div>
          ) : null}
        </div>

        <aside aria-label="Notification preferences" className="notifications-home__prefs">
          <h2>Preferences</h2>
          <h3>Notify me about</h3>
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
                      announce(
                        "Preference changes require an authorized settings action when synced.",
                      );
                    }}
                    type="checkbox"
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>

          <h3>Delivery channels</h3>
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
                      announce(
                        "Channel preferences require an authorized settings action when synced.",
                      );
                    }}
                    type="checkbox"
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>

          <div className="notifications-home__quiet">
            <h3>Quiet hours &amp; digest</h3>
            <p>{view.quietHours}</p>
          </div>

          <button
            className="notifications-home__action"
            onClick={() =>
              announce("Snooze type 24h requires an authorized preference action.")
            }
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
}: Readonly<{
  item: NotificationItem;
  isRead: boolean;
  onMarkRead: (id: string) => void;
  onAnnounce: (message: string) => void;
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
            <span className="notifications-home__unread">Unread</span>
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
