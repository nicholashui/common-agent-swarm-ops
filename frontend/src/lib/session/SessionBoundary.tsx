"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import type { ServerSessionSignal } from "./server-session";
import {
  SessionTransitionCoordinator,
  type AbortableSseSubscription,
  type CommandIntentPresentationStore,
  type ProjectionStateStore,
  type SessionSafeCache,
  type StreamRegistration,
} from "./session-runtime";

interface SessionBoundaryContextValue {
  readonly coordinator: SessionTransitionCoordinator;
}

const SessionBoundaryContext = createContext<SessionBoundaryContextValue | null>(null);

export function SessionBoundary({ signal, children }: Readonly<{ signal: ServerSessionSignal; children: ReactNode }>): JSX.Element {
  const coordinatorRef = useRef<SessionTransitionCoordinator | null>(null);
  if (coordinatorRef.current === null) coordinatorRef.current = new SessionTransitionCoordinator();
  const coordinator = coordinatorRef.current;
  const previousVersionRef = useRef(signal.version);
  const [renderedVersion, setRenderedVersion] = useState(signal.version);
  const isTransitioning = renderedVersion !== signal.version;

  useEffect((): void => {
    if (previousVersionRef.current === signal.version) return;
    previousVersionRef.current = signal.version;
    coordinator.beginSessionTransition();
    coordinator.authorizeNextProjection();
    setRenderedVersion(signal.version);
  }, [coordinator, signal.version]);

  if (isTransitioning || !coordinator.canRenderAuthorizedProjection()) {
    return <div aria-busy="true" role="status">Refreshing authorized session…</div>;
  }
  return <SessionBoundaryContext.Provider value={{ coordinator }}>{children}</SessionBoundaryContext.Provider>;
}

function useCoordinator(): SessionTransitionCoordinator {
  const context = useContext(SessionBoundaryContext);
  if (context === null) throw new Error("Session-bound state must render inside SessionBoundary.");
  return context.coordinator;
}

export function useSessionProjectionState(store: ProjectionStateStore): void {
  const coordinator = useCoordinator();
  useEffect((): (() => void) => coordinator.registerProjectionState(store), [coordinator, store]);
}

export function useSessionSafeCache(cache: SessionSafeCache): void {
  const coordinator = useCoordinator();
  useEffect((): (() => void) => coordinator.registerCache(cache), [cache, coordinator]);
}

export function useCommandIntentPresentation(store: CommandIntentPresentationStore): void {
  const coordinator = useCoordinator();
  useEffect((): (() => void) => coordinator.registerCommandIntentPresentation(store), [coordinator, store]);
}

export function useSessionSseSubscription(subscription: AbortableSseSubscription): StreamRegistration | null {
  const coordinator = useCoordinator();
  const [registration, setRegistration] = useState<StreamRegistration | null>(null);
  useEffect((): (() => void) => {
    const nextRegistration = coordinator.registerSseSubscription(subscription);
    setRegistration(nextRegistration);
    return (): void => {
      nextRegistration.unregister();
      setRegistration(null);
    };
  }, [coordinator, subscription]);
  return registration;
}
