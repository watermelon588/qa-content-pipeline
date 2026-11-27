// The "draft an answer" form: tick known provider pages, type other addresses, or paste a page's text.

import { createDraft } from "../_lib/actions";
import { KNOWN_SOURCES, SOURCE_GROUPS } from "@/lib/sources";
import { hostOf } from "../_lib/api";
import ActionForm from "@/components/ActionForm";

// again: a draft exists already, so this makes a new version (and isn't the main next step, so no yellow button).
export default function DraftForm({ questionId, again }: { questionId: number; again?: boolean }) {
  return (
    <ActionForm
      action={createDraft}
      className="df"
      label={again ? "Draft a new version" : "Draft the answer"}
      pendingLabel="Reading the pages and drafting (1 to 4 minutes, keep this tab open)…"
      buttonClassName={again ? "btn" : "btn btn--primary"}
    >
      <input type="hidden" name="question_id" value={questionId} />

      <p className="df-help">
        Pick 1 to 4 pages in total. To compare providers, pick pages from at least two of them.
      </p>
      {SOURCE_GROUPS.map((group) => (
        <fieldset key={group.key} className="df-group">
          <legend className="df-label">{group.label}</legend>
          <ul className="df-sources">
            {KNOWN_SOURCES.filter((s) => s.group === group.key).map((s) => (
              <li key={s.url}>
                <label className="df-source">
                  <input type="checkbox" name="source" value={s.url} />
                  <span>
                    <strong>{s.provider}</strong> {s.page}
                    <small>{hostOf(s.url)}</small>
                  </span>
                </label>
              </li>
            ))}
          </ul>
        </fieldset>
      ))}

      <details className="df-more">
        <summary>Use another page</summary>
        <label className="df-label" htmlFor={`extra-${questionId}`}>Page addresses, one per line</label>
        <textarea id={`extra-${questionId}`} name="extra_urls" rows={2} className="df-input" spellCheck={false} placeholder="https://" />
        <p className="df-help">
          If a page shows no text when downloaded (it&apos;s drawn by JavaScript), paste its text below instead.
        </p>
        <label className="df-label" htmlFor={`purl-${questionId}`}>Pasted page: address</label>
        <input id={`purl-${questionId}`} name="pasted_url" type="url" className="df-input" placeholder="https://" />
        <label className="df-label" htmlFor={`ptext-${questionId}`}>Pasted page: text</label>
        <textarea id={`ptext-${questionId}`} name="pasted_text" rows={4} className="df-input" />
      </details>
    </ActionForm>
  );
}
