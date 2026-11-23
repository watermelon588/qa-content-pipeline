// Shown instead of a screen when the API call fails (API not running, wrong secret, unknown draft).
export default function Problem({ error }: { error: Error }) {
  return (
    <div className="adm-problem" role="alert">
      <p><strong>Could not load this screen.</strong> {error.message}</p>
      <p>
        Check that the API is running (<code>api/.venv/Scripts/python -m uvicorn main:app --app-dir api --port 8000</code>) and that
        CRON_SECRET in <code>web/.env.local</code> matches <code>api/.env</code>.
      </p>
    </div>
  );
}
