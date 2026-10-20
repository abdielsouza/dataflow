import { useState, type FormEvent } from "react";
import { api } from "../../lib/api";

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
	// Formulário de autenticação do usuário com a API FastAPI.
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		setError(null);
		setLoading(true);

		try {
			await api.login({ email, password });
			onSuccess();
		}
		catch (err) {
			setError(err instanceof Error ? err.message : "Unable to login");
		}
		finally {
			setLoading(false);
		}
	}

	return (
		<form
		onSubmit={handleSubmit}
		className="mx-auto flex w-full max-w-sm flex-col gap-4"
		>
			<h1 className="text-2xl font-semibold">Entrar no Dataflow</h1>

			<label className="flex flex-col gap-1">
				<span className="text-sm">E-mail</span>
				<input
				className="rounded-md border px-3 py-2"
				type="email"
				autoComplete="email"
				value={email}
				onChange={(event) => setEmail(event.target.value)}
				required
				/>
			</label>

			<label className="flex flex-col gap-1">
				<span className="text-sm">Senha</span>
				<input
				className="rounded-md border px-3 py-2"
				type="password"
				autoComplete="current-password"
				value={password}
				onChange={(event) => setPassword(event.target.value)}
				required
				/>
			</label>

			{
				error && (
					<p role="alert" className="text-sm text-red-600">
						{error}
					</p>
				)
			}

			<button
			className="rounded-md bg-black px-4 py-2 text-white disabled:opacity-50"
			type="submit"
			disabled={loading}
			>
				{loading ? "Entrando..." : "Entrar"}
			</button>
		</form>
	);
}