/**
 * Host Agentic RAG client (offline plan/retrieve/reflect foundation).
 */

function unwrapData<T>(payload: unknown): T {
  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    "meta" in payload
  ) {
    return (payload as { data: T }).data;
  }
  return payload as T;
}

async function parseError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const errBody = (await response.json()) as {
      error?: { message?: string };
      detail?: { message?: string };
    };
    return errBody.error?.message ?? errBody.detail?.message ?? fallback;
  } catch {
    return fallback;
  }
}

export type RagFail = { readonly ok: false; readonly message: string };

export async function queryAgenticRag(
  query: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly maxIterations?: number;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly answer: string;
      readonly confidence: number;
      readonly citationCount: number;
      readonly patterns: readonly string[];
      readonly reflectionTriggered: boolean;
      readonly escalateToHitl: boolean;
    }
  | RagFail
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/rag/query", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        query,
        max_iterations: options.maxIterations ?? 3,
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      run?: {
        final_answer?: string;
        confidence?: number;
        citations?: unknown[];
        patterns_used?: string[];
        reflection_triggered?: boolean;
        escalate_to_hitl?: boolean;
      };
    }>(await response.json());
    const run = data.run ?? {};
    return {
      ok: true,
      answer: run.final_answer ?? "",
      confidence: run.confidence ?? 0,
      citationCount: (run.citations ?? []).length,
      patterns: run.patterns_used ?? [],
      reflectionTriggered: Boolean(run.reflection_triggered),
      escalateToHitl: Boolean(run.escalate_to_hitl),
    };
  } catch {
    return { ok: false, message: "Network error calling agentic RAG query." };
  }
}

export async function fetchRagPolicy(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly liveWeb: boolean;
      readonly chroma: boolean;
      readonly lightrag: boolean;
      readonly patterns: readonly string[];
    }
  | RagFail
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/rag/policy", {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      activation_policy?: {
        live_web?: boolean;
        chroma?: boolean;
        lightrag?: boolean;
      };
      patterns?: string[];
    }>(await response.json());
    return {
      ok: true,
      liveWeb: data.activation_policy?.live_web ?? false,
      chroma: data.activation_policy?.chroma ?? false,
      lightrag: data.activation_policy?.lightrag ?? false,
      patterns: data.patterns ?? [],
    };
  } catch {
    return { ok: false, message: "Network error calling RAG policy." };
  }
}

export async function ingestRagDocument(
  title: string,
  content: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly sourceRef?: string;
  } = {},
): Promise<{ readonly ok: true; readonly docId: string } | RagFail> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/rag/ingest", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        title,
        content,
        source_ref: options.sourceRef ?? "",
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{ ok?: boolean; doc_id?: string }>(await response.json());
    return { ok: true, docId: data.doc_id ?? "" };
  } catch {
    return { ok: false, message: "Network error calling RAG ingest." };
  }
}
