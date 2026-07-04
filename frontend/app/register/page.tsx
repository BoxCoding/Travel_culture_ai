"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Could not create account.");
        setLoading(false);
        return;
      }

      // Auto sign-in after successful registration.
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      setLoading(false);

      if (result?.error) {
        router.push("/login");
        return;
      }

      router.push("/dashboard");
      router.refresh();
    } catch {
      setLoading(false);
      setError("Something went wrong. Please try again.");
    }
  }

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-6 py-20">
      <div className="text-center">
        <h1 className="font-serif text-3xl font-semibold text-ink-900">
          Create your account
        </h1>
        <p className="mt-2 text-sm text-ink-700/60">
          Save cultural experiences and get personalized recommendations.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card flex flex-col gap-4 p-8">
        {error && (
          <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        )}
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
          Name
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input-field"
            placeholder="Ada Lovelace"
          />
        </label>
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
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field"
            placeholder="At least 8 characters"
          />
        </label>
        <button type="submit" disabled={loading} className="btn-primary mt-2">
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-center text-sm text-ink-700/60">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-clay-700">
          Sign in
        </Link>
      </p>
    </div>
  );
}
