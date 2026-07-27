/**
 * Safe-ish markdown → React rendering with relative asset resolution.
 * Lightweight GFM subset (no external markdown package).
 */

import React, { type ReactNode } from "react";

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

function renderInline(
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

function parseTableRow(line: string): string[] {
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return trimmed.split("|").map((cell) => cell.trim());
}

function isTableSeparator(line: string): boolean {
  return /^\s*\|?[\s:-]+\|[\s|:-]*$/.test(line);
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

    // fenced code
    if (line.trim().startsWith("```")) {
      const lang = line.trim().slice(3).trim();
      const body: string[] = [];
      i += 1;
      while (i < lines.length && !(lines[i] ?? "").trim().startsWith("```")) {
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

    // hr
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      blocks.push(<hr className="help-md__hr" key={`b${blockIndex++}`} />);
      i += 1;
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
    if (
      line.includes("|") &&
      i + 1 < lines.length &&
      isTableSeparator(lines[i + 1] ?? "")
    ) {
      const header = parseTableRow(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && (lines[i] ?? "").includes("|")) {
        rows.push(parseTableRow(lines[i] ?? ""));
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
        items.push((lines[i] ?? "").replace(/^\s*\d+\.\s+/, ""));
        i += 1;
      }
      blocks.push(
        <ol className="help-md__ol" key={`b${blockIndex++}`}>
          {items.map((item, ii) => (
            <li key={ii}>{renderInline(item, markdownPath, `ol${blockIndex}-${ii}`)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    // paragraph
    const para: string[] = [];
    while (
      i < lines.length &&
      (lines[i] ?? "").trim() !== "" &&
      !/^(#{1,6})\s+/.test(lines[i] ?? "") &&
      !(lines[i] ?? "").trim().startsWith("```") &&
      !(lines[i] ?? "").trim().startsWith(">") &&
      !/^\s*[-*+]\s+/.test(lines[i] ?? "") &&
      !/^\s*\d+\.\s+/.test(lines[i] ?? "")
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
