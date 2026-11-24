import ActionForm from "@/components/ActionForm";
import { login } from "./actions";

export default function LoginPage() {
  return (
    <section className="login">
      <p className="label label--route">AI Atlas India · GPU and cloud</p>
      <h1 className="login__title">Admin sign in</h1>
      <ActionForm action={login} className="so-form" label="Sign in" pendingLabel="Signing in…" buttonClassName="btn btn--primary">
        <label className="so-field">
          <span className="df-label">Username</span>
          <input name="user" className="df-input" autoComplete="username" required autoFocus />
        </label>
        <label className="so-field">
          <span className="df-label">Password</span>
          <input name="password" type="password" className="df-input" autoComplete="current-password" required />
        </label>
      </ActionForm>
    </section>
  );
}
