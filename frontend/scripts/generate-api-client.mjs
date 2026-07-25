import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const GENERATOR_VERSION = "1.0.0";
const HTTP_METHODS = new Set(["delete", "get", "head", "options", "patch", "post", "put"]);
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = resolve(SCRIPT_DIR, "..");
const DEFAULT_INPUT = resolve(FRONTEND_ROOT, "../backend/build/contracts/openapi.json");
const DEFAULT_OUTPUT = resolve(FRONTEND_ROOT, "src/lib/api/generated/index.ts");

const argumentsByName = new Map(process.argv.slice(2).map((argument, index, all) => [argument, all[index + 1]]));
const inputPath = resolve(argumentsByName.get("--input") ?? DEFAULT_INPUT);
const outputPath = resolve(argumentsByName.get("--output") ?? DEFAULT_OUTPUT);
const document = JSON.parse(await readFile(inputPath, "utf8"));
const paths = document.paths;
if (typeof document.openapi !== "string" || typeof paths !== "object" || paths === null) throw new Error("The OpenAPI document is invalid.");

const quote = (value) => JSON.stringify(value);
const pascal = (value) => value.replace(/[^a-zA-Z0-9]+(.)/g, (_, character) => character.toUpperCase()).replace(/^[a-z]/, (character) => character.toUpperCase());
const referenceName = (reference) => reference.split("/").at(-1);
const typeFor = (schema = {}) => {
  if (typeof schema.$ref === "string") return referenceName(schema.$ref);
  const variants = schema.anyOf ?? schema.oneOf ?? schema.allOf;
  if (Array.isArray(variants)) return variants.map(typeFor).join(" | ");
  if (Array.isArray(schema.enum)) return schema.enum.map((item) => JSON.stringify(item)).join(" | ");
  if (schema.type === "array") return `readonly (${typeFor(schema.items)})[]`;
  if (schema.type === "string") return "string";
  if (schema.type === "number" || schema.type === "integer") return "number";
  if (schema.type === "boolean") return "boolean";
  if (schema.type === "null") return "null";
  if (schema.type === "object" || schema.properties) {
    const required = new Set(schema.required ?? []);
    return `Readonly<{ ${Object.entries(schema.properties ?? {}).map(([name, value]) => `readonly ${quote(name)}${required.has(name) ? "" : "?"}: ${typeFor(value)}`).join("; ")} }>`;
  }
  return "unknown";
};
const schemas = document.components?.schemas ?? {};
const schemaLines = Object.entries(schemas).map(([name, schema]) => {
  if (schema.type !== "object" && !schema.properties) return `export type ${name} = ${typeFor(schema)};`;
  const required = new Set(schema.required ?? []);
  const properties = Object.entries(schema.properties ?? {}).map(([propertyName, propertySchema]) => `  readonly ${quote(propertyName)}${required.has(propertyName) ? "" : "?"}: ${typeFor(propertySchema)};`);
  return `export interface ${name} {\n${properties.join("\n")}\n}`;
});

const operations = [];
for (const [path, pathItem] of Object.entries(paths)) {
  if (!path.startsWith("/api/v1/")) throw new Error(`Refusing to generate unversioned operation: ${path}`);
  for (const [method, operation] of Object.entries(pathItem)) {
    if (!HTTP_METHODS.has(method) || typeof operation !== "object" || operation === null) continue;
    if (typeof operation.operationId !== "string") throw new Error(`Missing operationId for ${method.toUpperCase()} ${path}`);
    const parameters = [...(pathItem.parameters ?? []), ...(operation.parameters ?? [])].filter((parameter) => parameter?.in === "path");
    const requestSchema = operation.requestBody?.content?.["application/json"]?.schema;
    const response = Object.entries(operation.responses ?? {}).find(([status]) => /^2\d\d$/.test(status))?.[1];
    const responseSchema = response?.content?.["application/json"]?.schema;
    operations.push({ id: operation.operationId, name: pascal(operation.operationId), method: method.toUpperCase(), path, parameters, requestSchema, responseSchema });
  }
}
operations.sort((left, right) => left.id.localeCompare(right.id));
const requestLines = operations.map((operation) => {
  const fields = operation.parameters.map((parameter) => `readonly ${quote(parameter.name)}: ${typeFor(parameter.schema)}`).join("; ");
  const body = operation.requestSchema ? `readonly body: ${typeFor(operation.requestSchema)};` : "readonly body?: never;";
  return `export interface ${operation.name}Request {\n  readonly path: Readonly<{ ${fields} }> ;\n  ${body}\n}`;
});
const responseLines = operations.map((operation) => `export type ${operation.name}Response = ${typeFor(operation.responseSchema)};`);
const requestMap = operations.map((operation) => `  readonly ${quote(operation.id)}: ${operation.name}Request;`).join("\n");
const responseMap = operations.map((operation) => `  readonly ${quote(operation.id)}: ${operation.name}Response;`).join("\n");
const definitionLines = operations.map((operation) => `  ${quote(operation.id)}: { method: ${quote(operation.method)}, path: ${quote(operation.path)}, pathParameters: [${operation.parameters.map((parameter) => quote(parameter.name)).join(", ")}] },`).join("\n");
const source = `/* eslint-disable */
// Generated by frontend/scripts/generate-api-client.mjs (v${GENERATOR_VERSION}). DO NOT EDIT.
// Source: backend/build/contracts/openapi.json (${document.openapi})

export const GENERATED_API_BASE_PATH = "/api/v1" as const;
export const GENERATED_OPENAPI_VERSION = ${quote(document.openapi)} as const;
export type GeneratedJsonScalar = string | number | boolean | null;
export type GeneratedJsonValue = GeneratedJsonScalar | readonly GeneratedJsonValue[] | GeneratedJsonObject;
export interface GeneratedJsonObject { readonly [key: string]: GeneratedJsonValue; }
export type GeneratedActionReference = GeneratedJsonObject;

export interface GeneratedPublicSuccess<TData> { readonly ok: true; readonly data: TData; readonly correlationId: string; }
export interface GeneratedPublicError { readonly ok: false; readonly code: string; readonly message: string; readonly retryable: boolean; readonly correlationId?: string; readonly retryAfterSeconds?: number; readonly actionReference?: GeneratedActionReference; }
export type GeneratedOperationResult<TData> = GeneratedPublicSuccess<TData> | GeneratedPublicError;

${schemaLines.join("\n\n")}

${requestLines.join("\n\n")}

${responseLines.join("\n")}

export interface GeneratedOperationRequests {
${requestMap}
}
export interface GeneratedOperationResponses {
${responseMap}
}
export type GeneratedOperationId = keyof GeneratedOperationRequests;
export type GeneratedOperationRequest<TId extends GeneratedOperationId> = GeneratedOperationRequests[TId];
export type GeneratedOperationResponse<TId extends GeneratedOperationId> = GeneratedOperationResponses[TId];
export type GeneratedOperationData<TId extends GeneratedOperationId> = GeneratedOperationResponse<TId> extends Readonly<{ readonly data: infer TData }> ? TData : never;
export interface GeneratedHttpRequest { readonly method: string; readonly path: string; readonly body?: unknown; }

const GENERATED_OPERATION_DEFINITIONS = {
${definitionLines}
} as const satisfies Record<GeneratedOperationId, { readonly method: string; readonly path: string; readonly pathParameters: readonly string[] }>;

export function buildGeneratedRequest<TId extends GeneratedOperationId>(operationId: TId, request: GeneratedOperationRequest<TId>): GeneratedHttpRequest {
  const definition = GENERATED_OPERATION_DEFINITIONS[operationId];
  let path: string = definition.path;
  for (const parameter of definition.pathParameters) {
    const value = (request.path as Readonly<Record<string, unknown>>)[parameter];
    if (typeof value !== "string" || value.length === 0) throw new Error("Generated path parameter is invalid.");
    path = path.replace(\`{\${parameter}}\`, encodeURIComponent(value));
  }
  if (!path.startsWith(\`\${GENERATED_API_BASE_PATH}/\`)) throw new Error("Generated operation is outside /api/v1.");
  return "body" in request && request.body !== undefined ? { method: definition.method, path, body: request.body } : { method: definition.method, path };
}

export interface GeneratedOperationExecutor {
  execute<TId extends GeneratedOperationId>(operationId: TId, request: GeneratedOperationRequest<TId>): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>>;
}
export function requestGeneratedOperation<TId extends GeneratedOperationId>(executor: GeneratedOperationExecutor, operationId: TId, request: GeneratedOperationRequest<TId>): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>>
{
  return executor.execute(operationId, request);
}
`;
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, source, "utf8");
