"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatWidget({
  isSignedIn,
  destinationName,
}: {
  isSignedIn: boolean;
  destinationName?: string;
}) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, open]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, thread_id: threadId }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "The concierge couldn't respond right now.");
        setLoading(false);
        return;
      }

      setThreadId(data.thread_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    } catch {
      setError("Couldn't reach the concierge. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {open && (
        <div className="mb-4 flex h-[28rem] w-80 flex-col overflow-hidden rounded-2xl border border-sand-200 bg-white shadow-soft sm:w-96">
          <div className="flex items-center justify-between border-b border-sand-200 bg-clay-50 px-4 py-3">
            <div>
              <p className="font-serif text-sm font-semibold text-ink-900">
                Travel concierge
              </p>
              {destinationName && (
                <p className="text-xs text-ink-700/60">
                  Ask about {destinationName}
                </p>
              )}
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close chat"
              className="text-ink-700/50 hover:text-ink-900"
            >
              ✕
            </button>
          </div>

          {!isSignedIn ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
              <p className="text-sm text-ink-700/70">
                Sign in to chat with the AI travel concierge.
              </p>
              <Link href="/login" className="btn-primary">
                Sign in to chat
              </Link>
            </div>
          ) : (
            <>
              <div
                ref={scrollRef}
                className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
              >
                {messages.length === 0 && (
                  <p className="text-sm text-ink-700/50">
                    Ask me anything about this destination — customs,
                    itineraries, hidden gems, or the best time to visit.
                  </p>
                )}
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                      m.role === "user"
                        ? "ml-auto bg-clay-600 text-white"
                        : "bg-sand-100 text-ink-900"
                    }`}
                  >
                    {m.content}
                  </div>
                ))}
                {loading && (
                  <div className="max-w-[85%] rounded-xl bg-sand-100 px-3 py-2 text-sm text-ink-700/60">
                    Thinking…
                  </div>
                )}
                {error && (
                  <div className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
                    {error}
                  </div>
                )}
              </div>
              <form
                onSubmit={sendMessage}
                className="flex gap-2 border-t border-sand-200 p-3"
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type a message…"
                  className="input-field flex-1 text-sm"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary px-4"
                >
                  Send
                </button>
              </form>
            </>
          )}
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-clay-600 text-white shadow-soft transition hover:bg-clay-700"
        aria-label="Toggle chat"
      >
        {open ? "✕" : "💬"}
      </button>
    </div>
  );
}
