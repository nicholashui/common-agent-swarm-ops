"use client";

import React, { useEffect, useId, useState, type FormEvent } from "react";
import Link from "next/link";

import type {
  LoginLandingView,
  LoginLocale,
} from "../lib/projections/login-landing";

function readLocalePreference(
  storageKey: string,
  fallback: LoginLocale,
): LoginLocale {
  if (typeof window === "undefined") return fallback;
  try {
    const value = window.sessionStorage.getItem(storageKey);
    return value === "zh-Hant" ? "zh-Hant" : "en";
  } catch {
    return fallback;
  }
}

function writeLocalePreference(storageKey: string, locale: LoginLocale): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(storageKey, locale);
  } catch {
    // Preference is best-effort only; never store credentials.
  }
}

function ProductMark(): JSX.Element {
  return (
    <span aria-hidden="true" className="login-product-mark">
      <svg fill="none" viewBox="0 0 34 34">
        <circle cx="17" cy="11" r="2.4" />
        <circle cx="10" cy="23" r="2.4" />
        <circle cx="24" cy="23" r="2.4" />
        <path d="m17 13.4-6 7.6m6-7.6 6 7.6M11.6 23h10.8" />
      </svg>
    </span>
  );
}

/**
 * Public identity-only session entry (ui_01_login).
 * Copy and messages come from stored login parameters (`view`), not hardcoded
 * module constants. Posts credentials only to same-origin session entry routes.
 */
export function LoginScreen({
  view,
}: Readonly<{ view: LoginLandingView }>): JSX.Element {
  const emailId = useId();
  const passwordId = useId();
  const rememberId = useId();
  const alertId = useId();
  const resetEmailId = useId();
  const resetTokenId = useId();
  const resetPasswordId = useId();

  const [locale, setLocale] = useState<LoginLocale>(view.defaultLocale);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberDevice, setRememberDevice] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | undefined>();
  const [formInfo, setFormInfo] = useState<string | undefined>();
  const [resetOpen, setResetOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [resetMessage, setResetMessage] = useState<string | undefined>();
  const [resetBusy, setResetBusy] = useState(false);

  const copy = view.copyByLocale[locale];

  useEffect(() => {
    setLocale(readLocalePreference(view.localeStorageKey, view.defaultLocale));
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const error = params.get("error");
    if (error) {
      setFormError(error);
      const clean = new URL(window.location.href);
      clean.searchParams.delete("error");
      window.history.replaceState({}, "", clean.pathname + clean.search);
    }
  }, [view.defaultLocale, view.localeStorageKey]);

  const changeLocale = (next: LoginLocale): void => {
    setLocale(next);
    writeLocalePreference(view.localeStorageKey, next);
    setEmailError(undefined);
    setPasswordError(undefined);
    setFormError(undefined);
    setFormInfo(undefined);
  };

  const navigateAfterAuth = (redirectTo: string): void => {
    // Full navigation reloads server session cookies into App Router state.
    window.location.assign(redirectTo);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    const nextEmailError =
      email.trim().length === 0 ? copy.emailRequired : undefined;
    const nextPasswordError =
      password.length === 0 ? copy.passwordRequired : undefined;
    setEmailError(nextEmailError);
    setPasswordError(nextPasswordError);
    setFormError(undefined);
    setFormInfo(undefined);
    if (nextEmailError || nextPasswordError) return;

    setSubmitting(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email, password, rememberDevice }),
      });
      const payload = (await response.json()) as {
        ok?: boolean;
        error?: string;
        redirectTo?: string;
      };
      if (!response.ok || !payload.ok) {
        setFormError(payload.error ?? copy.invalidCredentials);
        setSubmitting(false);
        return;
      }
      navigateAfterAuth(payload.redirectTo ?? "/");
    } catch {
      setFormError(copy.networkError);
      setSubmitting(false);
    }
  };

  const startDemo = async (): Promise<void> => {
    setDemoLoading(true);
    setFormError(undefined);
    setFormInfo(copy.preparingDemo);
    try {
      const response = await fetch("/api/auth/demo", {
        method: "POST",
        credentials: "same-origin",
      });
      const payload = (await response.json()) as {
        ok?: boolean;
        error?: string;
        redirectTo?: string;
        message?: string;
      };
      if (!response.ok || !payload.ok) {
        setFormError(payload.error ?? copy.networkError);
        setDemoLoading(false);
        return;
      }
      setFormInfo(payload.message ?? copy.preparingDemo);
      navigateAfterAuth(payload.redirectTo ?? "/");
    } catch {
      setFormError(copy.networkError);
      setDemoLoading(false);
    }
  };

  const startSso = async (
    provider: "keycloak" | "google" | "github",
  ): Promise<void> => {
    setFormError(undefined);
    setFormInfo(undefined);
    try {
      const response = await fetch(
        `/api/auth/oidc/start?provider=${provider}`,
        { credentials: "same-origin" },
      );
      const payload = (await response.json()) as {
        ok?: boolean;
        error?: string;
        authorizationUrl?: string;
      };
      if (!response.ok || !payload.ok || !payload.authorizationUrl) {
        setFormError(payload.error ?? copy.ssoUnavailable);
        return;
      }
      window.location.assign(payload.authorizationUrl);
    } catch {
      setFormError(copy.networkError);
    }
  };

  const requestReset = async (): Promise<void> => {
    setResetBusy(true);
    setResetMessage(undefined);
    try {
      const response = await fetch("/api/auth/password-reset?action=request", {
        method: "POST",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: resetEmail || email }),
      });
      const payload = (await response.json()) as {
        ok?: boolean;
        message?: string;
        error?: string;
        devResetToken?: string;
      };
      if (!response.ok || !payload.ok) {
        setResetMessage(payload.error ?? copy.networkError);
        setResetBusy(false);
        return;
      }
      if (payload.devResetToken) {
        setResetToken(payload.devResetToken);
        setResetMessage(
          `${payload.message ?? ""} Local reset token issued for development.`,
        );
      } else {
        setResetMessage(payload.message);
      }
    } catch {
      setResetMessage(copy.networkError);
    }
    setResetBusy(false);
  };

  const confirmReset = async (): Promise<void> => {
    setResetBusy(true);
    setResetMessage(undefined);
    try {
      const response = await fetch("/api/auth/password-reset?action=confirm", {
        method: "POST",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ token: resetToken, password: resetPassword }),
      });
      const payload = (await response.json()) as {
        ok?: boolean;
        message?: string;
        error?: string;
      };
      if (!response.ok || !payload.ok) {
        setResetMessage(payload.error ?? copy.networkError);
        setResetBusy(false);
        return;
      }
      setResetMessage(payload.message);
      setPassword("");
      setResetPassword("");
    } catch {
      setResetMessage(copy.networkError);
    }
    setResetBusy(false);
  };

  const busy = submitting || demoLoading;

  return (
    <main className="login-page" lang={locale === "zh-Hant" ? "zh-Hant" : "en"}>
      <header className="login-topbar">
        <Link className="login-brand" href="/login">
          <ProductMark />
          <span className="login-brand-copy">
            <strong>{copy.productName}</strong>
            <small>{copy.tagline}</small>
          </span>
        </Link>
        <div aria-label={copy.language} className="login-language" role="group">
          <button
            aria-pressed={locale === "en"}
            className={
              locale === "en"
                ? "login-language__option login-language__option--active"
                : "login-language__option"
            }
            onClick={() => changeLocale("en")}
            type="button"
          >
            EN
          </button>
          <button
            aria-pressed={locale === "zh-Hant"}
            className={
              locale === "zh-Hant"
                ? "login-language__option login-language__option--active"
                : "login-language__option"
            }
            onClick={() => changeLocale("zh-Hant")}
            type="button"
          >
            繁體中文
          </button>
        </div>
      </header>

      <div className="login-stage">
        <section
          aria-describedby={formError || formInfo ? alertId : undefined}
          aria-labelledby="login-title"
          className="login-card"
        >
          <p className="login-badge">
            <span aria-hidden="true" className="login-badge-dot" />
            {copy.badge}
          </p>
          <h1 id="login-title" className="login-title">
            <span>{copy.titleLine1}</span>
            <span>{copy.titleLine2}</span>
          </h1>
          <p className="login-subtitle">{copy.subtitle}</p>
          <p className="login-local-hints">{copy.localHints}</p>

          {formError ? (
            <div className="login-alert" id={alertId} role="alert">
              {formError}
            </div>
          ) : null}
          {!formError && formInfo ? (
            <div className="login-alert login-alert--info" id={alertId} role="status">
              {formInfo}
            </div>
          ) : null}

          <form
            className="login-form"
            noValidate
            onSubmit={(event) => {
              void handleSubmit(event);
            }}
          >
            <div className="login-field">
              <label htmlFor={emailId}>{copy.email}</label>
              <input
                aria-invalid={emailError ? true : undefined}
                autoComplete="email"
                disabled={busy}
                id={emailId}
                name="email"
                onChange={(event) => {
                  setEmail(event.target.value);
                  if (emailError) setEmailError(undefined);
                }}
                placeholder={copy.emailPlaceholder}
                type="email"
                value={email}
              />
              {emailError ? (
                <p className="login-field-error" role="alert">
                  {emailError}
                </p>
              ) : null}
            </div>

            <div className="login-field">
              <label htmlFor={passwordId}>{copy.password}</label>
              <div className="login-password-row">
                <input
                  aria-invalid={passwordError ? true : undefined}
                  autoComplete="current-password"
                  disabled={busy}
                  id={passwordId}
                  name="password"
                  onChange={(event) => {
                    setPassword(event.target.value);
                    if (passwordError) setPasswordError(undefined);
                  }}
                  placeholder={copy.passwordPlaceholder}
                  type={showPassword ? "text" : "password"}
                  value={password}
                />
                <button
                  aria-label={
                    showPassword ? copy.hidePassword : copy.showPassword
                  }
                  className="login-password-toggle"
                  disabled={busy}
                  onClick={() => setShowPassword((current) => !current)}
                  type="button"
                >
                  <span aria-hidden="true">{showPassword ? "◉" : "◎"}</span>
                </button>
              </div>
              {passwordError ? (
                <p className="login-field-error" role="alert">
                  {passwordError}
                </p>
              ) : null}
            </div>

            <div className="login-form-row">
              <label className="login-check" htmlFor={rememberId}>
                <input
                  checked={rememberDevice}
                  disabled={busy}
                  id={rememberId}
                  name="remember"
                  onChange={(event) => setRememberDevice(event.target.checked)}
                  type="checkbox"
                />
                <span>{copy.rememberDevice}</span>
              </label>
              <button
                className="login-text-link"
                disabled={busy}
                onClick={() => {
                  setResetOpen(true);
                  setResetEmail(email);
                  setResetMessage(undefined);
                }}
                type="button"
              >
                {copy.forgotPassword}
              </button>
            </div>

            <button className="login-submit" disabled={busy} type="submit">
              {submitting ? (
                <>
                  <span aria-hidden="true" className="login-spinner" />
                  <span>{copy.signingIn}</span>
                </>
              ) : (
                copy.signIn
              )}
            </button>
          </form>

          <div className="login-divider" role="separator">
            <span>{copy.orContinue}</span>
          </div>

          <div className="login-sso">
            <button
              className="login-sso-primary"
              disabled={busy}
              onClick={() => {
                void startSso("keycloak");
              }}
              type="button"
            >
              {copy.keycloak}
            </button>
            <div className="login-sso-row">
              <button
                className="login-sso-secondary"
                disabled={busy}
                onClick={() => {
                  void startSso("google");
                }}
                type="button"
              >
                {copy.google}
              </button>
              <button
                className="login-sso-secondary"
                disabled={busy}
                onClick={() => {
                  void startSso("github");
                }}
                type="button"
              >
                {copy.github}
              </button>
            </div>
          </div>
        </section>

        <button
          className="login-demo"
          disabled={busy}
          onClick={() => {
            void startDemo();
          }}
          type="button"
        >
          <span aria-hidden="true" className="login-demo-icon">
            ▶
          </span>
          <span className="login-demo-copy">
            <strong>
              {demoLoading ? copy.preparingDemo : copy.demoTitle}
            </strong>
            <small>{copy.demoBody}</small>
          </span>
        </button>

        <footer className="login-footer">
          <nav aria-label="Login support links" className="login-footer-links">
            <a href="#docs">{copy.docs}</a>
            <a href="#github">{copy.githubLink}</a>
            <a href="#status">{copy.status}</a>
            <span>{copy.language}</span>
          </nav>
          <p className="login-footer-meta">{copy.footerMeta}</p>
        </footer>
      </div>

      {resetOpen ? (
        <div className="login-reset-backdrop" role="presentation">
          <div
            aria-labelledby="login-reset-title"
            aria-modal="true"
            className="login-reset-dialog"
            role="dialog"
          >
            <header className="login-reset-header">
              <h2 id="login-reset-title">{copy.resetTitle}</h2>
              <button
                className="login-text-link"
                onClick={() => setResetOpen(false)}
                type="button"
              >
                {copy.resetClose}
              </button>
            </header>
            <div className="login-reset-body">
              <div className="login-field">
                <label htmlFor={resetEmailId}>{copy.resetEmailLabel}</label>
                <input
                  disabled={resetBusy}
                  id={resetEmailId}
                  onChange={(event) => setResetEmail(event.target.value)}
                  type="email"
                  value={resetEmail}
                />
              </div>
              <button
                className="login-sso-primary"
                disabled={resetBusy}
                onClick={() => {
                  void requestReset();
                }}
                type="button"
              >
                {copy.resetRequest}
              </button>
              <div className="login-field">
                <label htmlFor={resetTokenId}>{copy.resetTokenLabel}</label>
                <input
                  disabled={resetBusy}
                  id={resetTokenId}
                  onChange={(event) => setResetToken(event.target.value)}
                  type="text"
                  value={resetToken}
                />
              </div>
              <div className="login-field">
                <label htmlFor={resetPasswordId}>{copy.resetNewPassword}</label>
                <input
                  disabled={resetBusy}
                  id={resetPasswordId}
                  onChange={(event) => setResetPassword(event.target.value)}
                  type="password"
                  value={resetPassword}
                />
              </div>
              <button
                className="login-submit"
                disabled={resetBusy}
                onClick={() => {
                  void confirmReset();
                }}
                type="button"
              >
                {copy.resetConfirm}
              </button>
              {resetMessage ? (
                <p className="login-reset-message" role="status">
                  {resetMessage}
                </p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}
