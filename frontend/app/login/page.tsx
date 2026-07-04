"use client";

import { useState, Suspense } from "react";
import { signIn } from "next-auth/react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("callbackUrl") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    setLoading(false);

    if (result?.error) {
      setError("Invalid email or password.");
      return;
    }

    router.push(callbackUrl);
    router.refresh();
  }

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-6 py-20">
      <div className="text-center">
        <h1 className="font-serif text-3xl font-semibold text-ink-900">
          Welcome back
        </h1>
        <p className="mt-2 text-sm text-ink-700/60">
          Sign in to save experiences and chat with your travel concierge.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card flex flex-col gap-4 p-8">
        {error && (
          <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        )}
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-field"
            placeholder="you@example.com"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field"
            placeholder="••••••••"
          />
        </label>
        <button type="submit" disabled={loading} className="btn-primary mt-2">
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="text-center text-sm text-ink-700/60">
        No account yet?{" "}
        <Link href="/register" className="font-medium text-clay-700">
          Create one
        </Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
