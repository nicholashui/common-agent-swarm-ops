"use client";

/**
 * @duty AccessibleDialog — accessible modal host
 * @role Focus trap, restore focus, labelled dialog for proposals/approvals/confirmations.
 * @controls Close (IconControl); primary actions supplied by parent with authorized handlers only.
 * @must Trap focus while open; restore invoker focus on close; Escape closes.
 * @mustnot Invent host mutations inside the dialog chrome.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2; ui_07 proposal modal
 */
import React, { useEffect, useId, useRef, type KeyboardEvent, type ReactNode } from "react";

import { IconControl } from "./IconControl";

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

export interface AccessibleDialogProps {
  readonly open: boolean;
  readonly title: string;
  readonly children: ReactNode;
  readonly onClose: () => void;
}

function getFocusableElements(dialog: HTMLElement): HTMLElement[] {
  return Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
    (element): boolean => !element.hasAttribute("disabled"),
  );
}

export interface DialogFocusableElement {
  focus(): void;
}

export interface FocusRestorationDocument<TElement> {
  contains(element: TElement): boolean;
}

/** Selects the next focus target while retaining focus inside a dialog. */
export function nextDialogFocusTarget<TElement extends DialogFocusableElement>(
  focusableElements: readonly TElement[],
  activeElement: TElement | null,
  shiftKey: boolean,
  heading: TElement,
): TElement {
  if (focusableElements.length === 0) return heading;

  const activeIndex = activeElement === null ? -1 : focusableElements.indexOf(activeElement);
  if (shiftKey) return focusableElements[activeIndex <= 0 ? focusableElements.length - 1 : activeIndex - 1]!;
  return focusableElements[activeIndex === -1 || activeIndex === focusableElements.length - 1 ? 0 : activeIndex + 1]!;
}

/** Restores the invoking control only while it remains in the active document. */
export function restoreDialogInvokerFocus<TElement extends DialogFocusableElement>(
  invoker: TElement | null,
  documentLike: FocusRestorationDocument<TElement>,
): void {
  if (invoker !== null && documentLike.contains(invoker)) invoker.focus();
}

/**
 * A controlled modal dialog that focuses its heading, traps keyboard focus, and
 * restores focus to the invoking control after close.
 */
export function AccessibleDialog({ open, title, children, onClose }: AccessibleDialogProps): JSX.Element | null {
  const dialogRef = useRef<HTMLElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const headingId = useId();

  useEffect((): (() => void) | undefined => {
    if (!open) return undefined;

    const invoker = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    headingRef.current?.focus();

    return (): void => {
      restoreDialogInvokerFocus<HTMLElement>(invoker, document);
    };
  }, [open]);

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>): void => {
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
      return;
    }

    if (event.key !== "Tab") return;

    const dialog = dialogRef.current;
    const heading = headingRef.current;
    if (dialog === null || heading === null) return;

    const focusableElements = getFocusableElements(dialog);
    const activeElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    event.preventDefault();
    nextDialogFocusTarget(focusableElements, activeElement, event.shiftKey, heading).focus();
  };

  if (!open) return null;

  return <div className="accessible-dialog-backdrop">
    <section
      aria-labelledby={headingId}
      aria-modal="true"
      className="accessible-dialog"
      onKeyDown={handleKeyDown}
      ref={dialogRef}
      role="dialog"
    >
      <header className="accessible-dialog__header">
        <h2 id={headingId} ref={headingRef} tabIndex={-1}>{title}</h2>
        <IconControl kind="close" onClick={onClose}>×</IconControl>
      </header>
      <div className="accessible-dialog__content">{children}</div>
    </section>
  </div>;
}
