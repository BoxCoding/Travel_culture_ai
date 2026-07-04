"use client";

import { useState } from "react";
import Link from "next/link";

export default function SaveButton({
  id,
  isSignedIn,
}: {
  id: number;
  isSignedIn: boolean;
}) {
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle"
  );

  if (!isSignedIn) {
    return (
      <Link
        href="/login"
        className="text-xs font-medium text-clay-700 underline decoration-dotted"
      >
        Sign in to save
      </Link>
    );
  }

  async function handleSave() {
    setStatus("saving");
    try {
      const res = await fetch("/api/saved", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      setStatus(res.ok ? "saved" : "error");
    } catch {
      setStatus("error");
    }
  }

  return (
    <button
      onClick={handleSave}
      disabled={status === "saving" || status === "saved"}
      className="text-xs font-medium text-clay-700 disabled:text-ink-700/40"
    >
      {status === "saved"
        ? "Saved ✓"
        : status === "saving"
          ? "Saving…"
          : status === "error"
            ? "Couldn't save — retry"
            : "Save this"}
    </button>
  );
}
