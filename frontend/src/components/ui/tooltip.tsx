"use client";

/**
 * Shadcn-style tooltip primitives (no Radix dependency).
 * Default delay is 0ms for near-instant open — matches dense ops UI.
 * API mirrors https://ui.shadcn.com/docs/components/base/tooltip
 */
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type FocusEvent,
  type MouseEvent,
  type ReactElement,
  type ReactNode,
  type Ref,
} from "react";
import { createPortal } from "react-dom";

type TooltipProviderValue = {
  readonly delayDuration: number;
  readonly skipDelayDuration: number;
  isWithinSkipWindow: () => boolean;
  markClosed: () => void;
};

const TooltipProviderContext = createContext<TooltipProviderValue | null>(null);

export function TooltipProvider({
  children,
  delayDuration = 0,
  skipDelayDuration = 300,
}: {
  readonly children: ReactNode;
  /** ms before open; 0 = instant (default). */
  readonly delayDuration?: number;
  /** After a close, re-open within this window ignores delay. */
  readonly skipDelayDuration?: number;
}): JSX.Element {
  const lastCloseRef = useRef(0);
  const value = useMemo<TooltipProviderValue>(
    () => ({
      delayDuration,
      skipDelayDuration,
      isWithinSkipWindow: () =>
        Date.now() - lastCloseRef.current < skipDelayDuration,
      markClosed: () => {
        lastCloseRef.current = Date.now();
      },
    }),
    [delayDuration, skipDelayDuration],
  );
  return (
    <TooltipProviderContext.Provider value={value}>
      {children}
    </TooltipProviderContext.Provider>
  );
}

type TooltipRootValue = {
  readonly open: boolean;
  readonly contentId: string;
  readonly triggerRef: React.MutableRefObject<HTMLElement | null>;
  scheduleOpen: () => void;
  scheduleClose: () => void;
};

const TooltipRootContext = createContext<TooltipRootValue | null>(null);

function useTooltipRoot(): TooltipRootValue {
  const ctx = useContext(TooltipRootContext);
  if (!ctx) {
    throw new Error("Tooltip components must be used within <Tooltip>");
  }
  return ctx;
}

export function Tooltip({
  children,
  delayDuration,
  defaultOpen = false,
  open: controlledOpen,
  onOpenChange,
}: {
  readonly children: ReactNode;
  readonly delayDuration?: number;
  readonly defaultOpen?: boolean;
  readonly open?: boolean;
  readonly onOpenChange?: (open: boolean) => void;
}): JSX.Element {
  const provider = useContext(TooltipProviderContext);
  const [uncontrolledOpen, setUncontrolledOpen] = useState(defaultOpen);
  const open = controlledOpen ?? uncontrolledOpen;
  const contentId = useId();
  const triggerRef = useRef<HTMLElement | null>(null);
  const openTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const delay = delayDuration ?? provider?.delayDuration ?? 0;

  const clearOpenTimer = useCallback(() => {
    if (openTimerRef.current !== null) {
      clearTimeout(openTimerRef.current);
      openTimerRef.current = null;
    }
  }, []);

  const setOpen = useCallback(
    (next: boolean) => {
      onOpenChange?.(next);
      if (controlledOpen === undefined) {
        setUncontrolledOpen(next);
      }
      if (!next) {
        provider?.markClosed();
      }
    },
    [controlledOpen, onOpenChange, provider],
  );

  const scheduleOpen = useCallback(() => {
    clearOpenTimer();
    const ms = provider?.isWithinSkipWindow() ? 0 : delay;
    if (ms <= 0) {
      setOpen(true);
      return;
    }
    openTimerRef.current = setTimeout(() => {
      openTimerRef.current = null;
      setOpen(true);
    }, ms);
  }, [clearOpenTimer, delay, provider, setOpen]);

  const scheduleClose = useCallback(() => {
    clearOpenTimer();
    setOpen(false);
  }, [clearOpenTimer, setOpen]);

  useEffect(() => () => clearOpenTimer(), [clearOpenTimer]);

  const root = useMemo<TooltipRootValue>(
    () => ({
      open,
      contentId,
      triggerRef,
      scheduleOpen,
      scheduleClose,
    }),
    [open, contentId, scheduleOpen, scheduleClose],
  );

  return (
    <TooltipRootContext.Provider value={root}>
      {children}
    </TooltipRootContext.Provider>
  );
}

function assignRef<T>(ref: Ref<T> | undefined, value: T): void {
  if (typeof ref === "function") {
    ref(value);
    return;
  }
  if (ref && typeof ref === "object") {
    (ref as { current: T }).current = value;
  }
}

export function TooltipTrigger({
  children,
  asChild = false,
  className,
  ...props
}: {
  readonly children: ReactNode;
  readonly asChild?: boolean;
  readonly className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>): JSX.Element {
  const ctx = useTooltipRoot();

  const onMouseEnter = (event: MouseEvent<HTMLElement>): void => {
    props.onMouseEnter?.(event as MouseEvent<HTMLButtonElement>);
    ctx.scheduleOpen();
  };
  const onMouseLeave = (event: MouseEvent<HTMLElement>): void => {
    props.onMouseLeave?.(event as MouseEvent<HTMLButtonElement>);
    ctx.scheduleClose();
  };
  const onFocus = (event: FocusEvent<HTMLElement>): void => {
    props.onFocus?.(event as FocusEvent<HTMLButtonElement>);
    ctx.scheduleOpen();
  };
  const onBlur = (event: FocusEvent<HTMLElement>): void => {
    props.onBlur?.(event as FocusEvent<HTMLButtonElement>);
    ctx.scheduleClose();
  };

  if (asChild && React.isValidElement(children)) {
    const child = children as ReactElement & {
      ref?: Ref<HTMLElement>;
      props?: {
        onMouseEnter?: (event: MouseEvent<HTMLElement>) => void;
        onMouseLeave?: (event: MouseEvent<HTMLElement>) => void;
        onFocus?: (event: FocusEvent<HTMLElement>) => void;
        onBlur?: (event: FocusEvent<HTMLElement>) => void;
      };
    };
    const childProps = child.props ?? {};
    return React.cloneElement(child, {
      ref: (node: HTMLElement | null) => {
        ctx.triggerRef.current = node;
        assignRef(child.ref, node);
      },
      "aria-describedby": ctx.open ? ctx.contentId : undefined,
      onMouseEnter: (event: MouseEvent<HTMLElement>) => {
        childProps.onMouseEnter?.(event);
        onMouseEnter(event);
      },
      onMouseLeave: (event: MouseEvent<HTMLElement>) => {
        childProps.onMouseLeave?.(event);
        onMouseLeave(event);
      },
      onFocus: (event: FocusEvent<HTMLElement>) => {
        childProps.onFocus?.(event);
        onFocus(event);
      },
      onBlur: (event: FocusEvent<HTMLElement>) => {
        childProps.onBlur?.(event);
        onBlur(event);
      },
    } as never);
  }

  return (
    <button
      type="button"
      className={className}
      ref={(node) => {
        ctx.triggerRef.current = node;
      }}
      aria-describedby={ctx.open ? ctx.contentId : undefined}
      {...props}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onFocus={onFocus}
      onBlur={onBlur}
    >
      {children}
    </button>
  );
}

export function TooltipContent({
  children,
  side = "top",
  sideOffset = 6,
  className,
}: {
  readonly children: ReactNode;
  readonly side?: "top" | "bottom" | "left" | "right";
  readonly sideOffset?: number;
  readonly className?: string;
}): JSX.Element | null {
  const ctx = useTooltipRoot();
  const [mounted, setMounted] = useState(false);
  const [style, setStyle] = useState<CSSProperties>({
    position: "fixed",
    top: -9999,
    left: -9999,
    visibility: "hidden",
  });

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!ctx.open) return;
    const el = ctx.triggerRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    let top = 0;
    let left = 0;
    let transform = "translate(-50%, 0)";
    switch (side) {
      case "top":
        top = r.top - sideOffset;
        left = r.left + r.width / 2;
        transform = "translate(-50%, -100%)";
        break;
      case "bottom":
        top = r.bottom + sideOffset;
        left = r.left + r.width / 2;
        transform = "translate(-50%, 0)";
        break;
      case "left":
        top = r.top + r.height / 2;
        left = r.left - sideOffset;
        transform = "translate(-100%, -50%)";
        break;
      case "right":
        top = r.top + r.height / 2;
        left = r.right + sideOffset;
        transform = "translate(0, -50%)";
        break;
    }
    setStyle({
      position: "fixed",
      top,
      left,
      transform,
      zIndex: 1000,
      visibility: "visible",
    });
  }, [ctx.open, side, sideOffset]);

  if (!ctx.open || !mounted || typeof document === "undefined") {
    return null;
  }

  return createPortal(
    <div
      id={ctx.contentId}
      role="tooltip"
      className={["ui-tooltip-content", className].filter(Boolean).join(" ")}
      data-side={side}
      style={style}
    >
      {children}
    </div>,
    document.body,
  );
}

/** Wrap any single child with a fast tooltip (replaces native title=). */
export function WithTooltip({
  content,
  children,
  side = "top",
  delayDuration = 0,
}: {
  readonly content: string;
  readonly children: ReactElement;
  readonly side?: "top" | "bottom" | "left" | "right";
  readonly delayDuration?: number;
}): JSX.Element {
  const trimmed = content.trim();
  if (!trimmed) return children;
  return (
    <Tooltip delayDuration={delayDuration}>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent side={side}>{trimmed}</TooltipContent>
    </Tooltip>
  );
}
