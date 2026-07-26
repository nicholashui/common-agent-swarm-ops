import assert from "node:assert/strict";
import test from "node:test";

import {
  buildOidcAuthorizationUrl,
  defaultOidcRedirectUri,
  encodeOidcStateCookie,
  exchangeOidcAuthorizationCode,
  fetchOidcIdentity,
  loginErrorRedirect,
  parseOidcStateCookie,
  resolveOidcProviderConfig,
  sessionClaimsFromOidcIdentity,
  type FetchLike,
  type OidcProviderConfig,
} from "./oidc";

function envWith(values: Record<string, string | undefined>): NodeJS.ProcessEnv {
  return { ...process.env, ...values };
}

test("resolves provider configs and default callback URIs", () => {
  assert.equal(
    resolveOidcProviderConfig("keycloak", "http://127.0.0.1:3000", envWith({})),
    null,
  );

  const keycloak = resolveOidcProviderConfig(
    "keycloak",
    "http://127.0.0.1:3000",
    envWith({
      CASOPS_OIDC_ISSUER: "https://auth.example/realms/casops",
      CASOPS_OIDC_CLIENT_ID: "casops-web",
      CASOPS_OIDC_CLIENT_SECRET: "secret",
    }),
  );
  assert.ok(keycloak);
  assert.equal(
    keycloak.redirectUri,
    "http://127.0.0.1:3000/api/auth/oidc/callback?provider=keycloak",
  );
  assert.match(
    buildOidcAuthorizationUrl(keycloak, "state-abc"),
    /client_id=casops-web/,
  );
  assert.equal(
    defaultOidcRedirectUri("http://127.0.0.1:3000/", "google"),
    "http://127.0.0.1:3000/api/auth/oidc/callback?provider=google",
  );
});

test("parses and validates OIDC state cookies", () => {
  assert.deepEqual(parseOidcStateCookie(encodeOidcStateCookie("github", "xyz")), {
    provider: "github",
    state: "xyz",
  });
  assert.equal(parseOidcStateCookie("not-a-provider.xyz"), null);
  assert.equal(parseOidcStateCookie("keycloak."), null);
});

test("exchanges authorization codes and maps identity through injectible fetch", async () => {
  const config: OidcProviderConfig = {
    provider: "keycloak",
    clientId: "casops-web",
    clientSecret: "secret",
    redirectUri: "http://127.0.0.1:3000/api/auth/oidc/callback?provider=keycloak",
    authorizationEndpoint: "https://auth.example/auth",
    tokenEndpoint: "https://auth.example/token",
    userInfoEndpoint: "https://auth.example/userinfo",
    scope: "openid email profile",
  };

  const missingSecret = await exchangeOidcAuthorizationCode(
    { ...config, clientSecret: null },
    "code-1",
  );
  assert.equal(missingSecret.ok, false);

  const fetchImpl: FetchLike = async (input, init) => {
    if (input === config.tokenEndpoint) {
      assert.equal(init?.method, "POST");
      return {
        ok: true,
        status: 200,
        json: async () => ({
          access_token: "access-1",
          id_token: Buffer.from(
            JSON.stringify({ alg: "none" }),
          ).toString("base64url") +
            "." +
            Buffer.from(
              JSON.stringify({ email: "sso@example.com", sub: "user-1" }),
            ).toString("base64url") +
            ".sig",
        }),
        text: async () => "",
      };
    }
    if (input === config.userInfoEndpoint) {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          email: "sso@example.com",
          sub: "user-1",
          name: "SSO Operator",
        }),
        text: async () => "",
      };
    }
    throw new Error(`unexpected fetch ${input}`);
  };

  const tokens = await exchangeOidcAuthorizationCode(config, "code-1", fetchImpl);
  assert.equal(tokens.ok, true);
  if (!tokens.ok) throw new Error("expected token success");

  const identity = await fetchOidcIdentity(
    config,
    tokens.accessToken,
    tokens.idToken,
    fetchImpl,
  );
  assert.equal(identity.ok, true);
  if (!identity.ok) throw new Error("expected identity success");
  assert.equal(identity.identity.email, "sso@example.com");
  assert.match(identity.identity.workspaceLabel, /SSO Operator/);

  const claims = sessionClaimsFromOidcIdentity(identity.identity);
  assert.equal(claims.mode, "user");
  assert.equal(claims.email, "sso@example.com");
  assert.match(
    loginErrorRedirect("http://127.0.0.1:3000", "bad state"),
    /error=bad(\+|%20)state/,
  );
});
