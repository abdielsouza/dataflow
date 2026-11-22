import { useState, type FormEvent } from "react";
import { AlertTriangle, Save, Trash2 } from "lucide-react";
import type { UserResponse } from "../../lib/api";
import {
  useDeleteCurrentUser,
  useUpdateCurrentUser,
} from "./userQueries";

interface UserSettingsPageProps {
  user: UserResponse | null;
  isLoading: boolean;
  error: string | null;
  onAccountDeleted: () => void;
}

export function UserSettingsPage({
  user,
  isLoading,
  error,
  onAccountDeleted,
}: UserSettingsPageProps) {
  const [usernameDraft, setUsernameDraft] = useState<string | null>(null);
  const [emailDraft, setEmailDraft] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const updateUser = useUpdateCurrentUser();
  const deleteUser = useDeleteCurrentUser();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice(null);
    setFormError(null);

    if (!user) return;

    const changes: { username?: string; email?: string; password?: string } = {};
    const username = (usernameDraft ?? user.username).trim();
    const email = (emailDraft ?? user.email).trim();
    if (username !== user.username) changes.username = username;
    if (email.toLowerCase() !== user.email) changes.email = email;
    if (password) changes.password = password;

    if (Object.keys(changes).length === 0) {
      setNotice("Seus dados já estão atualizados.");
      return;
    }

    try {
      await updateUser.mutateAsync(changes);
      setUsernameDraft(null);
      setEmailDraft(null);
      setPassword("");
      setNotice("Dados da conta atualizados.");
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "Não foi possível atualizar a conta.");
    }
  }

  async function handleDelete() {
    const confirmed = window.confirm(
      "Excluir sua conta permanentemente? Esta ação não pode ser desfeita.",
    );
    if (!confirmed) return;

    setFormError(null);
    try {
      await deleteUser.mutateAsync();
      onAccountDeleted();
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "Não foi possível excluir a conta.");
    }
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Carregando os dados da conta...</p>;
  }

  if (!user) {
    return (
      <p role="alert" className="text-sm text-red-600">
        {error ?? "Não foi possível carregar os dados da conta."}
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <section>
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
          Conta
        </p>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-950">
          Configurações
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Gerencie seus dados de acesso e sua conta Dataflow.
        </p>
      </section>

      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div>
          <h2 className="text-base font-semibold text-slate-900">Perfil</h2>
          <p className="mt-1 text-sm text-slate-500">
            ID da conta: <span className="font-mono text-xs">{user.id}</span>
          </p>
        </div>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-700">
            Nome de usuário
          </span>
          <input
            value={usernameDraft ?? user.username}
            onChange={(event) => setUsernameDraft(event.target.value)}
            autoComplete="username"
            required
            className="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-700">
            E-mail
          </span>
          <input
            type="email"
            value={emailDraft ?? user.email}
            onChange={(event) => setEmailDraft(event.target.value)}
            autoComplete="email"
            required
            className="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-700">
            Nova senha
          </span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="new-password"
            placeholder="Deixe em branco para manter a senha atual"
            className="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
          />
        </label>

        {notice && <p role="status" className="text-sm text-emerald-700">{notice}</p>}
        {(formError || error) && (
          <p role="alert" className="text-sm text-red-600">{formError ?? error}</p>
        )}

        <button
          type="submit"
          disabled={updateUser.isPending}
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          <Save size={16} />
          {updateUser.isPending ? "Salvando..." : "Salvar alterações"}
        </button>
      </form>

      <section className="rounded-xl border border-red-200 bg-white p-6">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-50 text-red-600">
            <AlertTriangle size={18} />
          </div>
          <div className="flex-1">
            <h2 className="text-base font-semibold text-slate-900">Excluir conta</h2>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              A exclusão encerra sua sessão e remove o acesso à sua conta.
            </p>
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleteUser.isPending}
              className="mt-4 inline-flex h-9 items-center gap-2 rounded-lg border border-red-200 px-3 text-sm font-medium text-red-700 transition hover:bg-red-50 disabled:opacity-50"
            >
              <Trash2 size={15} />
              {deleteUser.isPending ? "Excluindo..." : "Excluir minha conta"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
