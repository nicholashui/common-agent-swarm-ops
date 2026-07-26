/**
 * Stored login screen copy (ui_01). Not hardcoded in LoginScreen.
 */

export type LoginLocale = "en" | "zh-Hant";

export interface LoginCopy {
  readonly productName: string;
  readonly tagline: string;
  readonly badge: string;
  readonly titleLine1: string;
  readonly titleLine2: string;
  readonly subtitle: string;
  readonly email: string;
  readonly emailPlaceholder: string;
  readonly password: string;
  readonly passwordPlaceholder: string;
  readonly showPassword: string;
  readonly hidePassword: string;
  readonly rememberDevice: string;
  readonly forgotPassword: string;
  readonly signIn: string;
  readonly signingIn: string;
  readonly orContinue: string;
  readonly keycloak: string;
  readonly google: string;
  readonly github: string;
  readonly demoTitle: string;
  readonly demoBody: string;
  readonly preparingDemo: string;
  readonly docs: string;
  readonly githubLink: string;
  readonly status: string;
  readonly language: string;
  readonly footerMeta: string;
  readonly emailRequired: string;
  readonly passwordRequired: string;
  readonly invalidCredentials: string;
  readonly networkError: string;
  readonly ssoUnavailable: string;
  readonly resetTitle: string;
  readonly resetEmailLabel: string;
  readonly resetRequest: string;
  readonly resetTokenLabel: string;
  readonly resetNewPassword: string;
  readonly resetConfirm: string;
  readonly resetClose: string;
  readonly localHints: string;
}

export interface LoginLandingView {
  readonly defaultLocale: LoginLocale;
  readonly localeStorageKey: string;
  readonly copyByLocale: Readonly<Record<LoginLocale, LoginCopy>>;
}

export const LOCAL_LOGIN_LANDING: LoginLandingView = {
  defaultLocale: "en",
  localeStorageKey: "casops:login-locale",
  copyByLocale: {
    en: {
      productName: "common-agent-swarm-ops",
      tagline: "Reusable agent swarms · Collective improvement · Production ops",
      badge: "v2.0 · Common Registry Live",
      titleLine1: "Sign in to orchestrate",
      titleLine2: "reusable agent swarms",
      subtitle: "Access Common Registry & live ops",
      email: "Email",
      emailPlaceholder: "you@company.com",
      password: "Password",
      passwordPlaceholder: "••••••••••••",
      showPassword: "Show password",
      hidePassword: "Hide password",
      rememberDevice: "Remember this device",
      forgotPassword: "Forgot password?",
      signIn: "Sign in",
      signingIn: "Signing in...",
      orContinue: "or continue with",
      keycloak: "Keycloak (Self-hosted)",
      google: "Google",
      github: "GitHub",
      demoTitle: "Try Demo Workspace →",
      demoBody: "Explore Common Agents, Patterns & live ops — no setup",
      preparingDemo: "Preparing Common Registry & sample swarms...",
      docs: "Docs",
      githubLink: "GitHub",
      status: "Status",
      language: "Language",
      footerMeta: "Demo available · No credit card · build 2026.07 · CSP-secured",
      emailRequired: "Enter an email address.",
      passwordRequired: "Enter a password.",
      invalidCredentials: "Invalid email or password.",
      networkError: "Could not reach session entry. Retry shortly.",
      ssoUnavailable: "Enterprise SSO is not configured in this environment.",
      resetTitle: "Reset password",
      resetEmailLabel: "Account email",
      resetRequest: "Send reset instructions",
      resetTokenLabel: "Reset token",
      resetNewPassword: "New password",
      resetConfirm: "Update password",
      resetClose: "Close",
      localHints: "Local users: demo@local / demo · ops@local / ops",
    },
    "zh-Hant": {
      productName: "common-agent-swarm-ops",
      tagline: "可重用代理群 · 集體改進 · 生產營運",
      badge: "v2.0 · Common Registry 線上",
      titleLine1: "登入以編排",
      titleLine2: "可重用代理群",
      subtitle: "存取 Common Registry 與即時營運",
      email: "電子郵件",
      emailPlaceholder: "you@company.com",
      password: "密碼",
      passwordPlaceholder: "••••••••••••",
      showPassword: "顯示密碼",
      hidePassword: "隱藏密碼",
      rememberDevice: "記住此裝置",
      forgotPassword: "忘記密碼？",
      signIn: "登入",
      signingIn: "登入中...",
      orContinue: "或以其他方式繼續",
      keycloak: "Keycloak（自架）",
      google: "Google",
      github: "GitHub",
      demoTitle: "試用示範工作區 →",
      demoBody: "探索 Common Agents、Patterns 與即時營運 — 無需設定",
      preparingDemo: "正在準備 Common Registry 與示範 swarm...",
      docs: "文件",
      githubLink: "GitHub",
      status: "狀態",
      language: "語言",
      footerMeta: "提供示範 · 無需信用卡 · build 2026.07 · CSP 保護",
      emailRequired: "請輸入電子郵件。",
      passwordRequired: "請輸入密碼。",
      invalidCredentials: "電子郵件或密碼不正確。",
      networkError: "無法連線工作階段入口，請稍後再試。",
      ssoUnavailable: "此環境尚未設定企業 SSO。",
      resetTitle: "重設密碼",
      resetEmailLabel: "帳號電子郵件",
      resetRequest: "送出重設指示",
      resetTokenLabel: "重設權杖",
      resetNewPassword: "新密碼",
      resetConfirm: "更新密碼",
      resetClose: "關閉",
      localHints: "本機帳號：demo@local / demo · ops@local / ops",
    },
  },
};
