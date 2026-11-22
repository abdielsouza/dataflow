import { useState, type FormEvent } from "react";
import { api } from "../../lib/api";

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "register") {
        await api.register({ username, email, password });
        setMode("login");
        setPassword("");
        setNotice("Conta criada. Entre com seu e-mail e senha.");
      } else {
        await api.login({ email, password });
        onSuccess();
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Não foi possível concluir a solicitação.",
      );
    } finally {
      setLoading(false);
    }
  }

  function toggleMode() {
    setMode((current) => (current === "login" ? "register" : "login"));
    setPassword("");
    setError(null);
    setNotice(null);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-sm flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-7 shadow-sm"
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
            Dataflow
          </p>
          <h1 className="mt-2 text-2xl font-semibold">
            {mode === "login" ? "Entrar na sua conta" : "Criar sua conta"}
          </h1>
        </div>

        {mode === "register" && (
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium">Nome de usuário</span>
            <input
              className="rounded-lg border border-slate-200 px-3 py-2"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
        )}

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium">E-mail</span>
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium">Senha</span>
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>

        {notice && (
          <p role="status" className="text-sm text-emerald-700">
            {notice}
          </p>
        )}
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}

        <button
          className="rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition hover:bg-blue-700 disabled:opacity-50"
          type="submit"
          disabled={loading}
        >
          {loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}
        </button>

        <p className="text-center text-sm text-slate-500">
          {mode === "login" ? "Ainda não tem uma conta?" : "Já tem uma conta?"}{" "}
          <button
            type="button"
            className="font-medium text-blue-600 hover:text-blue-700"
            onClick={toggleMode}
          >
            {mode === "login" ? "Cadastre-se" : "Entrar"}
          </button>
        </p>
      </form>
    </div>
  );
}