// Turns a draft's markdown into React elements. It handles only what the draft prompt asks for:
// ## headings, "-" or "*" bullet lists, "| a | b |" tables, **bold**, and [n] fact markers (linked to the fact list).
// No raw HTML is ever inserted, so nothing inside a draft can run as code in the page.
// ponytail: tiny on purpose. Swap in a markdown library if drafts ever need links or nested lists.
// Shared by the admin draft view, the expert review page and the public answer page.

import type { ReactNode } from "react";

function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|\[\d+\])/g).map((part, i) => {
    if (/^\*\*[^*]+\*\*$/.test(part)) return <strong key={i}>{part.slice(2, -2)}</strong>;
    const marker = part.match(/^\[(\d+)\]$/);
    if (marker) {
      return (
        <sup key={i} className="md-ref">
          <a href={`#fact-${marker[1]}`}>[{marker[1]}]</a>
        </sup>
      );
    }
    return part;
  });
}

export default function Markdown({ text, className }: { text: string; className?: string }) {
  const out: ReactNode[] = [];
  let para: string[] = [];
  let list: string[] = [];
  let rows: string[][] = [];
  const flushTable = () => {
    // First row is the header; the "|---|---|" separator row was already skipped.
    if (rows.length) {
      const [head, ...body] = rows;
      out.push(
        <div key={out.length} className="md-table">
          <table>
            <thead><tr>{head.map((c, i) => <th key={i}>{inline(c)}</th>)}</tr></thead>
            <tbody>{body.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}>{inline(c)}</td>)}</tr>)}</tbody>
          </table>
        </div>,
      );
    }
    rows = [];
  };
  const flushPara = () => {
    if (para.length) out.push(<p key={out.length}>{inline(para.join(" "))}</p>);
    para = [];
  };
  const flushList = () => {
    if (list.length) out.push(<ul key={out.length}>{list.map((item, i) => <li key={i}>{inline(item)}</li>)}</ul>);
    list = [];
  };

  for (const raw of text.replace(/\r/g, "").split("\n")) {
    const line = raw.trim();
    const heading = line.match(/^#{1,4}\s+(.*)$/);
    const bullet = line.match(/^[-*]\s+(.*)$/);
    if (line.startsWith("|")) {
      flushPara();
      flushList();
      if (!/^[|\s:-]+$/.test(line)) rows.push(line.replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
      continue;
    }
    flushTable();
    if (!line) {
      flushPara();
      flushList();
    } else if (heading) {
      flushPara();
      flushList();
      out.push(<h2 key={out.length}>{inline(heading[1])}</h2>); // h2: the draft title is the page's h1
    } else if (bullet) {
      flushPara();
      list.push(bullet[1]);
    } else {
      flushList();
      para.push(line);
    }
  }
  flushPara();
  flushList();
  flushTable();
  return <div className={className}>{out}</div>;
}
