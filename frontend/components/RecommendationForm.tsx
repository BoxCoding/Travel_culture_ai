"use client";

import { useState } from "react";
import type { RecommendationResponse } from "@/lib/types";

const TRAVEL_STYLES = ["relaxed", "adventurous", "cultural", "luxury", "budget"];

export default function RecommendationForm() {
  const [interests, setInterests] = useState("");
  const [budget, setBudget] = useState("");
  const [durationDays, setDurationDays] = useState("");
  const [region, setRegion] = useState("");
  const [travelStyle, setTravelStyle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interests: interests
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          budget: budget || undefined,
          duration_days: durationDays ? Number(durationDays) : undefined,
          region: region || undefined,
          travel_style: travelStyle || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Couldn't generate recommendations right now.");
        return;
      }
      setResult(data);
    } catch {
      setError("Couldn't reach the recommendation service. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleSubmit} className="card flex flex-col gap-4 p-6">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
          Interests (comma-separated)
          <input
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="temples, street food, hiking"
            className="input-field"
            required
          />
        </label>

        <div className="grid grid-cols-2 gap-4">
          <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
            Budget
            <input
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="mid-range"
              className="input-field"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
            Duration (days)
            <input
              type="number"
              min={1}
              value={durationDays}
              onChange={(e) => setDurationDays(e.target.value)}
              placeholder="7"
              className="input-field"
            />
          </label>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
            Region
            <input
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="Southeast Asia"
              className="input-field"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
            Travel style
            <select
              value={travelStyle}
              onChange={(e) => setTravelStyle(e.target.value)}
              className="input-field"
            >
              <option value="">Any</option>
              {TRAVEL_STYLES.map((style) => (
                <option key={style} value={style}>
                  {style}
                </option>
              ))}
            </select>
          </label>
        </div>

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? "Generating…" : "Get recommendations"}
        </button>
      </form>

      {error && (
        <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {result && (
        <div className="card flex flex-col gap-4 p-6">
          <p className="text-sm text-ink-700">{result.summary}</p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-700/50">
                Attractions
              </p>
              <ul className="flex flex-col gap-2">
                {result.attractions.map((a, i) => (
                  <li key={i} className="rounded-lg bg-sand-50 p-3 text-sm">
                    <p className="font-medium text-ink-900">{a.name}</p>
                    <p className="mt-1 text-ink-700/70">{a.reason}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-700/50">
                Hidden gems
              </p>
              <ul className="flex flex-col gap-2">
                {result.hidden_gems.map((g, i) => (
                  <li key={i} className="rounded-lg bg-sand-50 p-3 text-sm">
                    <p className="font-medium text-ink-900">{g.name}</p>
                    <p className="mt-1 text-ink-700/70">{g.reason}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
