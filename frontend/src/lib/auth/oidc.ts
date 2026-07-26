import { createSessionClaims, type SessionClaims } from "./local-auth";

export type OidcProvider = "keycloak" | "google" | "github";

export interface OidcProviderConfig {
  readonly provider: OidcProvider;
  readonly clientId: string;
  readonly clientSecret: string | null;
  readonly redirectUri: string;
  readonly authorizationEndpoint: string;
  readonly tokenEndpoint: string;
  readonly userInfoEndpoint: string | null;
  readonly scope: string;
}

export interface OidcIdentity {
  readonly email: string;
  readonly workspaceLabel: string;
  readonly subject: string;
  readonly provider: OidcProvider;
}

export type FetchLike = (
  input: string,
  init?: {
    readonly method?: string;
    readonly headers?: Record<string, string>;
    readonly body?: string;
  },
) => Promise<{
  readonly ok: boolean;
  readonly status: number;
  json(): Promise<unknown>;
  text(): Promise<string>;
}>;

export function isOidcProvider(value: string | null | undefined): value is OidcProvider {
  return value === "keycloak" || value === "google" || value === "github";
}

export function defaultOidcRedirectUri(
  origin: string,
  provider: OidcProvider,
): string {
  const base = origin.replace(/\/$/, "");
  return `${base}/api/auth/oidc/callback?provider=${provider}`;
}

export function resolveOidcProviderConfig(
  provider: OidcProvider,
  origin: string,
  env: NodeJS.ProcessEnv = process.env,
): OidcProviderConfig | null {
  if (provider === "keycloak") {
    const issuer = env.CASOPS_OIDC_ISSUER?.replace(/\/$/, "");
    const clientId = env.CASOPS_OIDC_CLIENT_ID?.trim();
    if (!issuer || !clientId) return null;
    const redirectUri =
      env.CASOPS_OIDC_REDIRECT_URI?.trim() ||
      defaultOidcRedirectUri(origin, provider);
    return {
      provider,
      clientId,
      clientSecret: env.CASOPS_OIDC_CLIENT_SECRET?.trim() || null,
      redirectUri,
      authorizationEndpoint: `${issuer}/protocol/openid-connect/auth`,
      tokenEndpoint: `${issuer}/protocol/openid-connect/token`,
      userInfoEndpoint: `${issuer}/protocol/openid-connect/userinfo`,
      scope: "openid profile email",
    };
  }

  if (provider === "google") {
    const clientId = env.CASOPS_GOOGLE_CLIENT_ID?.trim();
    if (!clientId) return null;
    const redirectUri =
      env.CASOPS_GOOGLE_REDIRECT_URI?.trim() ||
      defaultOidcRedirectUri(origin, provider);
    return {
      provider,
      clientId,
      clientSecret: env.CASOPS_GOOGLE_CLIENT_SECRET?.trim() || null,
      redirectUri,
      authorizationEndpoint: "https://accounts.google.com/o/oauth2/v2/auth",
      tokenEndpoint: "https://oauth2.googleapis.com/token",
      userInfoEndpoint: "https://openidconnect.googleapis.com/v1/userinfo",
      scope: "openid email profile",
    };
  }

  const clientId = env.CASOPS_GITHUB_CLIENT_ID?.trim();
  if (!clientId) return null;
  const redirectUri =
    env.CASOPS_GITHUB_REDIRECT_URI?.trim() ||
    defaultOidcRedirectUri(origin, provider);
  return {
    provider,
    clientId,
    clientSecret: env.CASOPS_GITHUB_CLIENT_SECRET?.trim() || null,
    redirectUri,
    authorizationEndpoint: "https://github.com/login/oauth/authorize",
    tokenEndpoint: "https://github.com/login/oauth/access_token",
    userInfoEndpoint: "https://api.github.com/user",
    scope: "read:user user:email",
  };
}

export function buildOidcAuthorizationUrl(
  config: OidcProviderConfig,
  state: string,
): string {
  const url = new URL(config.authorizationEndpoint);
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", config.scope);
  url.searchParams.set("state", state);
  if (config.provider === "google") {
    url.searchParams.set("access_type", "online");
    url.searchParams.set("include_granted_scopes", "true");
  }
  return url.toString();
}

export function encodeOidcStateCookie(
  provider: OidcProvider,
  state: string,
): string {
  return `${provider}.${state}`;
}

export function parseOidcStateCookie(
  value: string | undefined | null,
): { readonly provider: OidcProvider; readonly state: string } | null {
  if (!value) return null;
  const separator = value.indexOf(".");
  if (separator <= 0) return null;
  const provider = value.slice(0, separator);
  const state = value.slice(separator + 1);
  if (!isOidcProvider(provider) || state.length === 0) return null;
  return { provider, state };
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function readString(record: Record<string, unknown>, key: string): string | null {
  const value = record[key];
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

export async function exchangeOidcAuthorizationCode(
  config: OidcProviderConfig,
  code: string,
  fetchImpl: FetchLike = fetch as FetchLike,
): Promise<
  | { readonly ok: true; readonly accessToken: string; readonly idToken: string | null }
  | { readonly ok: false; readonly error: string }
> {
  if (!config.clientSecret) {
    return {
      ok: false,
      error: `${config.provider} SSO requires a client secret for code exchange.`,
    };
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    client_id: config.clientId,
    client_secret: config.clientSecret,
    redirect_uri: config.redirectUri,
  });

  const headers: Record<string, string> = {
    "content-type": "application/x-www-form-urlencoded",
    accept: "application/json",
  };
  if (config.provider === "github") {
    headers.accept = "application/json";
  }

  let response: Awaited<ReturnType<FetchLike>>;
  try {
    response = await fetchImpl(config.tokenEndpoint, {
      method: "POST",
      headers,
      body: body.toString(),
    });
  } catch {
    return { ok: false, error: "Token endpoint is unreachable." };
  }

  if (!response.ok) {
    return {
      ok: false,
      error: `Token exchange failed (${response.status}).`,
    };
  }

  const payload = asRecord(await response.json());
  const accessToken = readString(payload, "access_token");
  if (!accessToken) {
    return { ok: false, error: "Token response did not include access_token." };
  }
  return {
    ok: true,
    accessToken,
    idToken: readString(payload, "id_token"),
  };
}

function emailFromIdToken(idToken: string | null): string | null {
  if (!idToken) return null;
  const parts = idToken.split(".");
  if (parts.length < 2 || !parts[1]) return null;
  try {
    const json = Buffer.from(parts[1], "base64url").toString("utf8");
    const payload = asRecord(JSON.parse(json) as unknown);
    return (
      readString(payload, "email") ??
      readString(payload, "preferred_username") ??
      null
    );
  } catch {
    return null;
  }
}

export async function fetchOidcIdentity(
  config: OidcProviderConfig,
  accessToken: string,
  idToken: string | null,
  fetchImpl: FetchLike = fetch as FetchLike,
): Promise<
  | { readonly ok: true; readonly identity: OidcIdentity }
  | { readonly ok: false; readonly error: string }
> {
  if (config.provider === "github") {
    return fetchGithubIdentity(config, accessToken, fetchImpl);
  }

  let email = emailFromIdToken(idToken);
  let subject = "oidc-user";
  let name: string | null = null;

  if (config.userInfoEndpoint) {
    try {
      const response = await fetchImpl(config.userInfoEndpoint, {
        method: "GET",
        headers: {
          authorization: `Bearer ${accessToken}`,
          accept: "application/json",
        },
      });
      if (response.ok) {
        const payload = asRecord(await response.json());
        email =
          email ??
          readString(payload, "email") ??
          readString(payload, "preferred_username");
        subject = readString(payload, "sub") ?? subject;
        name = readString(payload, "name") ?? readString(payload, "preferred_username");
      }
    } catch {
      // Fall through to id_token-derived identity.
    }
  }

  if (!email) {
    return {
      ok: false,
      error: "OIDC provider did not return an email claim.",
    };
  }

  return {
    ok: true,
    identity: {
      email: email.toLowerCase(),
      workspaceLabel: name ? `${name} workspace` : `${config.provider} workspace`,
      subject,
      provider: config.provider,
    },
  };
}

async function fetchGithubIdentity(
  config: OidcProviderConfig,
  accessToken: string,
  fetchImpl: FetchLike,
): Promise<
  | { readonly ok: true; readonly identity: OidcIdentity }
  | { readonly ok: false; readonly error: string }
> {
  try {
    const userResponse = await fetchImpl("https://api.github.com/user", {
      method: "GET",
      headers: {
        authorization: `Bearer ${accessToken}`,
        accept: "application/vnd.github+json",
        "user-agent": "casops-frontend",
      },
    });
    if (!userResponse.ok) {
      return { ok: false, error: "GitHub user profile request failed." };
    }
    const user = asRecord(await userResponse.json());
    let email = readString(user, "email");
    if (!email) {
      const emailsResponse = await fetchImpl("https://api.github.com/user/emails", {
        method: "GET",
        headers: {
          authorization: `Bearer ${accessToken}`,
          accept: "application/vnd.github+json",
          "user-agent": "casops-frontend",
        },
      });
      if (emailsResponse.ok) {
        const emails = (await emailsResponse.json()) as unknown;
        if (Array.isArray(emails)) {
          const preferred = emails.find((entry) => {
            const record = asRecord(entry);
            return record.primary === true && record.verified === true;
          });
          const fallback = emails.find((entry) => asRecord(entry).verified === true);
          email =
            readString(asRecord(preferred), "email") ??
            readString(asRecord(fallback), "email") ??
            readString(asRecord(emails[0]), "email");
        }
      }
    }
    if (!email) {
      const login = readString(user, "login");
      email = login ? `${login}@users.noreply.github.com` : null;
    }
    if (!email) {
      return { ok: false, error: "GitHub did not return an email address." };
    }
    const login = readString(user, "login") ?? "github";
    return {
      ok: true,
      identity: {
        email: email.toLowerCase(),
        workspaceLabel: `${login} workspace`,
        subject: String(user.id ?? login),
        provider: config.provider,
      },
    };
  } catch {
    return { ok: false, error: "GitHub identity lookup failed." };
  }
}

export function sessionClaimsFromOidcIdentity(
  identity: OidcIdentity,
  rememberDevice = true,
): SessionClaims {
  return createSessionClaims({
    mode: "user",
    email: identity.email,
    workspaceLabel: identity.workspaceLabel,
    rememberDevice,
  });
}

export function loginErrorRedirect(
  origin: string,
  message: string,
): string {
  const url = new URL("/login", origin);
  url.searchParams.set("error", message);
  return url.toString();
}
