"use client";
// The home page's published answers with a search box. All the answers (20 at most) are already on the page, so
// searching just hides the ones that don't match: no request is sent, and nothing typed leaves the browser.
// The server renders the full list first, so search engines and readers without JavaScript still see everything.

import Link from "next/link";
import { useState } from "react";
import { matches, type AnswerCard } from "@/lib/answers";

export default function AnswerList({ cards }: { cards: AnswerCard[] }) {
  const [query, setQuery] = useState("");
  const shown = cards.filter((card) => matches(card, query));

  return (
    <>
      <search className="answer-search">
        <label className="label" htmlFor="answer-search">Search the answers</label>
        <input
          id="answer-search"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="A question, GPU or provider"
          autoComplete="off"
        />
        {/* Read out by screen readers whenever the number changes */}
        <p className="muted" role="status">
          {query.trim() ? `${shown.length} of ${cards.length} answers match` : `${cards.length} published`}
        </p>
      </search>

      {shown.length === 0 ? (
        <div className="empty">
          <p><strong>No answer matches “{query.trim()}”.</strong></p>
          <p><button type="button" className="btn" onClick={() => setQuery("")}>Show all answers</button></p>
        </div>
      ) : (
        <ol className="entry-list">
          {shown.map((card) => (
            <li key={card.slug}>
              <span className="entry-list__n">{String(cards.indexOf(card) + 1).padStart(2, "0")}</span>
              <div>
                <Link className="entry-list__title" href={`/q/${card.slug}`}>{card.title}</Link>
                <p className="entry-list__preview">{card.preview}</p>
                {card.trust && <p className="entry-list__trust">{card.trust}</p>}
                {card.providers.length > 0 && (
                  <ul className="provider-tags" aria-label="Sources cited from">
                    <li aria-hidden="true">Sources:</li>
                    {card.providers.map((name) => (
                      <li key={name}>
                        <button type="button" aria-pressed={query === name} onClick={() => setQuery(query === name ? "" : name)}>
                          {name}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}
