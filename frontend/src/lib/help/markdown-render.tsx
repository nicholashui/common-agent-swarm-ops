/**
 * Safe-ish markdown → React rendering with relative asset resolution.
 * Lightweight GFM subset (no external markdown package) + KaTeX math.
 */

import React, { type ReactNode } from "react";

import { MathTex } from "./math-tex";

export function resolveMarkdownAssetUrl(
  asset: string,
  markdownPath: string,
): string {
  const src = asset.trim();
  if (!src) return src;
  if (/^(https?:|data:|blob:)/i.test(src)) return src;
  if (src.startsWith("/")) return src;

  const baseDir = markdownPath.includes("/")
    ? markdownPath.slice(0, markdownPath.lastIndexOf("/") + 1)
    : "/";
  try {
    // Resolve relative to markdown file location under same origin.
    const url = new URL(src, `https://local.invalid${baseDir}`);
    return url.pathname + url.search + url.hash;
  } catch {
    return src;
  }
}

/** Convert raw HTML &lt;img&gt; tags to markdown image syntax before parse. */
export function pretreatHtmlImages(markdown: string): string {
  return markdown.replace(
    /<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["'][^>]*\/?>/gi,
    (_full, src: string) => {
      const altMatch = _full.match(/\balt\s*=\s*["']([^"']*)["']/i);
      const alt = altMatch?.[1] ?? "";
      return `![${alt}](${src})`;
    },
  );
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

type InlineMathSegment =
  | { readonly kind: "math"; readonly tex: string }
  | { readonly kind: "text"; readonly text: string };

/**
 * Split inline text on \(…\) and $…$ (not $$). Math is extracted before other
 * markdown so backslashes and braces stay intact for KaTeX.
 */
export function splitInlineMath(text: string): InlineMathSegment[] {
  const segments: InlineMathSegment[] = [];
  // \( ... \)  or  $...$ (single-dollar, non-empty, no newlines)
  const pattern = /\\\(([\s\S]+?)\\\)|\$([^$\n]+?)\$/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      segments.push({ kind: "text", text: text.slice(last, match.index) });
    }
    const tex = (match[1] ?? match[2] ?? "").trim();
    if (tex) segments.push({ kind: "math", tex });
    last = match.index + match[0].length;
  }
  if (last < text.length) {
    segments.push({ kind: "text", text: text.slice(last) });
  }
  return segments.length > 0 ? segments : [{ kind: "text", text }];
}

function renderInlineBasic(
  text: string,
  markdownPath: string,
  keyPrefix: string,
): ReactNode[] {
  const nodes: ReactNode[] = [];
  // images, links, code, bold, italic — iterative scan
  const pattern =
    /(!\[([^\]]*)\]\(([^)]+)\))|(\[([^\]]+)\]\(([^)]+)\))|(`([^`]+)`)|(\*\*([^*]+)\*\*)|(\*([^*]+)\*)/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let i = 0;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }
    const k = `${keyPrefix}-${i++}`;
    if (match[1]) {
      const alt = match[2] ?? "";
      const src = resolveMarkdownAssetUrl(match[3] ?? "", markdownPath);
      nodes.push(
        <img alt={alt} className="help-md__img" key={k} src={src} />,
      );
    } else if (match[4]) {
      const label = match[5] ?? "";
      const href = match[6] ?? "";
      const safeHref =
        href.startsWith("/") || /^(https?:|mailto:)/i.test(href) ? href : "#";
      nodes.push(
        <a
          className="help-md__a"
          href={safeHref}
          key={k}
          rel={safeHref.startsWith("http") ? "noopener noreferrer" : undefined}
          target={safeHref.startsWith("http") ? "_blank" : undefined}
        >
          {label}
        </a>,
      );
    } else if (match[7]) {
      nodes.push(
        <code className="help-md__code" key={k}>
          {match[8]}
        </code>,
      );
    } else if (match[9]) {
      nodes.push(
        <strong key={k}>{match[10]}</strong>,
      );
    } else if (match[11]) {
      nodes.push(<em key={k}>{match[12]}</em>);
    }
    last = match.index + match[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function renderInline(
  text: string,
  markdownPath: string,
  keyPrefix: string,
): ReactNode[] {
  const nodes: ReactNode[] = [];
  let partIndex = 0;
  for (const segment of splitInlineMath(text)) {
    if (segment.kind === "math") {
      nodes.push(
        <MathTex
          key={`${keyPrefix}-math-${partIndex++}`}
          tex={segment.tex}
        />,
      );
    } else if (segment.text) {
      nodes.push(
        ...renderInlineBasic(
          segment.text,
          markdownPath,
          `${keyPrefix}-t${partIndex++}`,
        ),
      );
    }
  }
  return nodes;
}

function isDisplayMathOpen(line: string): boolean {
  const t = line.trim();
  return t === "\\[" || t === "$$";
}

function isDisplayMathClose(line: string, openMarker: string): boolean {
  const t = line.trim();
  if (openMarker === "$$") return t === "$$";
  return t === "\\]";
}

/** Single-line display: \[ ... \] or $$ ... $$ */
function singleLineDisplayMath(line: string): string | null {
  const bracket = /^\\\[(.+?)\\\]\s*$/.exec(line.trim());
  if (bracket) return (bracket[1] ?? "").trim();
  const dollars = /^\$\$(.+?)\$\$\s*$/.exec(line.trim());
  if (dollars) return (dollars[1] ?? "").trim();
  return null;
}

function parseTableRow(line: string): string[] {
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return trimmed.split("|").map((cell) => cell.trim());
}

function isTableSeparator(line: string): boolean {
  return /^\s*\|?[\s:-]+\|[\s|:-]*$/.test(line);
}

/** Bare design-doc sections like "11.1 Architecture Diagram" (no leading #). */
function bareSubsectionHeading(line: string): { level: number; text: string } | null {
  const m = /^(\d+\.\d+(?:\.\d+)*)\s+(\S.*)$/.exec(line.trim());
  if (!m) return null;
  const depth = (m[1] ?? "").split(".").length;
  const level = Math.min(Math.max(depth + 1, 2), 4);
  return { level, text: `${m[1]} ${m[2]}`.trim() };
}

/**
 * Bare top sections like "11. Common Structure of an AI Agent".
 * Procedure OL items usually end with . / ; or contain a mid-sentence ";".
 */
function bareTopSectionHeading(line: string): { level: number; text: string } | null {
  const m = /^(\d+)\.\s+([A-Z].{8,120})$/.exec(line.trim());
  if (!m) return null;
  const title = (m[2] ?? "").trim();
  if (title.endsWith(".") || title.endsWith(";") || title.endsWith(":") || title.includes(";")) {
    return null;
  }
  return { level: 2, text: `${m[1]}. ${title}` };
}

function startsTable(lines: string[], index: number): boolean {
  const line = lines[index] ?? "";
  return line.includes("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1] ?? "");
}

export function MarkdownDocument({
  markdown,
  markdownPath,
  className,
}: Readonly<{
  markdown: string;
  markdownPath: string;
  className?: string;
}>): JSX.Element {
  const source = pretreatHtmlImages(markdown);
  const lines = source.replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let blockIndex = 0;

  while (i < lines.length) {
    const line = lines[i] ?? "";

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    // fenced code (``` or ''' used in older dumps)
    const fenceOpen = /^(```|''')([^\s`]*)\s*$/.exec(line.trim());
    if (fenceOpen) {
      const marker = fenceOpen[1] ?? "```";
      const lang = fenceOpen[2] ?? "";
      const body: string[] = [];
      i += 1;
      while (i < lines.length) {
        const cur = (lines[i] ?? "").trim();
        if (cur === marker || cur === "```" || cur === "'''") break;
        body.push(lines[i] ?? "");
        i += 1;
      }
      if (i < lines.length) i += 1;
      blocks.push(
        <pre className="help-md__pre" key={`b${blockIndex++}`}>
          <code data-lang={lang || undefined}>{body.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    // heading
    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1]!.length;
      const content = heading[2] ?? "";
      const Tag = `h${level}` as keyof JSX.IntrinsicElements;
      blocks.push(
        <Tag className={`help-md__h help-md__h${level}`} key={`b${blockIndex++}`}>
          {renderInline(content, markdownPath, `h${blockIndex}`)}
        </Tag>,
      );
      i += 1;
      continue;
    }

    // bare numbered section titles (design-doc style without #)
    const bareSub = bareSubsectionHeading(line);
    const bareTop = bareSub ? null : bareTopSectionHeading(line);
    const bare = bareSub ?? bareTop;
    if (bare) {
      const Tag = `h${bare.level}` as keyof JSX.IntrinsicElements;
      blocks.push(
        <Tag className={`help-md__h help-md__h${bare.level}`} key={`b${blockIndex++}`}>
          {renderInline(bare.text, markdownPath, `h${blockIndex}`)}
        </Tag>,
      );
      i += 1;
      continue;
    }

    // hr
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      blocks.push(<hr className="help-md__hr" key={`b${blockIndex++}`} />);
      i += 1;
      continue;
    }

    // display math — single line \[ ... \] / $$ ... $$
    const oneLineMath = singleLineDisplayMath(line);
    if (oneLineMath) {
      blocks.push(
        <MathTex
          display
          key={`b${blockIndex++}`}
          tex={oneLineMath}
        />,
      );
      i += 1;
      continue;
    }

    // display math — multi-line \[ ... \] or $$ ... $$
    if (isDisplayMathOpen(line)) {
      const openMarker = line.trim() === "$$" ? "$$" : "\\[";
      const body: string[] = [];
      i += 1;
      while (i < lines.length && !isDisplayMathClose(lines[i] ?? "", openMarker)) {
        body.push(lines[i] ?? "");
        i += 1;
      }
      if (i < lines.length) i += 1; // consume close
      const tex = body.join("\n").trim();
      if (tex) {
        blocks.push(
          <MathTex display key={`b${blockIndex++}`} tex={tex} />,
        );
      }
      continue;
    }

    // blockquote
    if (line.trim().startsWith(">")) {
      const quote: string[] = [];
      while (i < lines.length && (lines[i] ?? "").trim().startsWith(">")) {
        quote.push((lines[i] ?? "").replace(/^\s*>\s?/, ""));
        i += 1;
      }
      blocks.push(
        <blockquote className="help-md__bq" key={`b${blockIndex++}`}>
          {quote.map((q, qi) => (
            <p key={qi}>{renderInline(q, markdownPath, `q${blockIndex}-${qi}`)}</p>
          ))}
        </blockquote>,
      );
      continue;
    }

    // table
    if (startsTable(lines, i)) {
      const header = parseTableRow(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && (lines[i] ?? "").includes("|") && (lines[i] ?? "").trim() !== "") {
        // Stop if a new block starts (heading / fence) even if it has |
        const rowLine = lines[i] ?? "";
        if (/^(#{1,6})\s+/.test(rowLine) || rowLine.trim().startsWith("```")) break;
        rows.push(parseTableRow(rowLine));
        i += 1;
      }
      blocks.push(
        <div className="help-md__table-wrap" key={`b${blockIndex++}`}>
          <table className="help-md__table">
            <thead>
              <tr>
                {header.map((cell, ci) => (
                  <th key={ci}>
                    {renderInline(cell, markdownPath, `th${blockIndex}-${ci}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, ri) => (
                <tr key={ri}>
                  {row.map((cell, ci) => (
                    <td key={ci}>
                      {renderInline(cell, markdownPath, `td${ri}-${ci}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    // unordered list
    if (/^\s*[-*+]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i] ?? "")) {
        items.push((lines[i] ?? "").replace(/^\s*[-*+]\s+/, ""));
        i += 1;
      }
      blocks.push(
        <ul className="help-md__ul" key={`b${blockIndex++}`}>
          {items.map((item, ii) => (
            <li key={ii}>{renderInline(item, markdownPath, `ul${blockIndex}-${ii}`)}</li>
          ))}
        </ul>,
      );
      continue;
    }

    // ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i] ?? "")) {
        // Do not swallow a bare top-section heading into an OL
        if (bareTopSectionHeading(lines[i] ?? "")) break;
        items.push((lines[i] ?? "").replace(/^\s*\d+\.\s+/, ""));
        i += 1;
      }
      if (items.length > 0) {
        blocks.push(
          <ol className="help-md__ol" key={`b${blockIndex++}`}>
            {items.map((item, ii) => (
              <li key={ii}>{renderInline(item, markdownPath, `ol${blockIndex}-${ii}`)}</li>
            ))}
          </ol>,
        );
      }
      continue;
    }

    // paragraph — stop at tables, bare headings, fences, display math
    const para: string[] = [];
    while (
      i < lines.length &&
      (lines[i] ?? "").trim() !== "" &&
      !/^(#{1,6})\s+/.test(lines[i] ?? "") &&
      !(lines[i] ?? "").trim().startsWith("```") &&
      !(lines[i] ?? "").trim().startsWith("'''") &&
      !(lines[i] ?? "").trim().startsWith(">") &&
      !/^\s*[-*+]\s+/.test(lines[i] ?? "") &&
      !/^\s*\d+\.\s+/.test(lines[i] ?? "") &&
      !bareSubsectionHeading(lines[i] ?? "") &&
      !startsTable(lines, i) &&
      !isDisplayMathOpen(lines[i] ?? "") &&
      !singleLineDisplayMath(lines[i] ?? "")
    ) {
      para.push(lines[i] ?? "");
      i += 1;
    }
    blocks.push(
      <p className="help-md__p" key={`b${blockIndex++}`}>
        {renderInline(para.join(" "), markdownPath, `p${blockIndex}`)}
      </p>,
    );
  }

  return (
    <article
      className={className ? `help-md ${className}` : "help-md"}
      data-markdown-path={markdownPath}
    >
      {blocks.length > 0 ? blocks : <p className="help-md__empty">Empty document.</p>}
    </article>
  );
}

/** Escape helper for tests */
export function escapeMarkdownText(text: string): string {
  return escapeHtml(text);
}
