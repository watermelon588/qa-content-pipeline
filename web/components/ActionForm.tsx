"use client";
// One form wrapper for every button: sends the form to a Server Action, disables itself while the
// action runs, and shows the action's result as a toast. useActionState gives us `pending` for free.
// ponytail: needs JavaScript to submit (fine for the desk and the expert; the public pages have no forms).
// Docs: node_modules/next/dist/docs/01-app/02-guides/forms.md (useActionState), sonner.emilkowal.ski (toast)

import { startTransition, useActionState, useEffect } from "react";
import { toast } from "sonner";
import type { Result } from "@/lib/api";

type Props = {
  action: (state: Result, form: FormData) => Promise<Result>;
  label: string;
  pendingLabel?: string;
  className?: string;
  buttonClassName?: string;
  children?: React.ReactNode;
};

export default function ActionForm({ action, label, pendingLabel = "Working…", className, buttonClassName, children }: Props) {
  const [state, formAction, pending] = useActionState(action, null);

  // Each finished action returns a new result object, so this runs once per click.
  useEffect(() => {
    if (!state) return;
    if (state.ok) toast.success(state.message);
    else toast.error(state.message, { duration: Infinity }); // an error waits until you've read it and closed it
  }, [state]);

  // Submitting through onSubmit (not <form action>) stops React from emptying the form afterwards,
  // so an error doesn't wipe what you typed (like the expert's edited answer).
  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    startTransition(() => formAction(data));
  }

  return (
    <form onSubmit={onSubmit} className={className} aria-busy={pending}>
      <fieldset disabled={pending} className="af-fields">
        {children}
        <button type="submit" className={buttonClassName}>{pending ? pendingLabel : label}</button>
      </fieldset>
      {/* Only "send to expert" returns a link. Click the box to select it, then copy. */}
      {state?.link && (
        <label className="af-link">
          Send this one-time link to the expert
          <input readOnly value={state.link} onFocus={(e) => e.currentTarget.select()} />
        </label>
      )}
    </form>
  );
}
