import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { backendFetch, BackendError } from "@/lib/backend";
import type { SavedItem } from "@/lib/types";
import EmptyState from "@/components/EmptyState";
import RecommendationForm from "@/components/RecommendationForm";

async function getSavedItems(): Promise<{
  items: SavedItem[];
  error?: string;
}> {
  try {
    const items = await backendFetch<SavedItem[]>("/api/me/saved", {
      requireAuth: true,
    });
    return { items };
  } catch (err) {
    return {
      items: [],
      error:
        err instanceof BackendError
          ? err.message
          : "Could not load your saved experiences right now.",
    };
  }
}

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user) {
    redirect("/login?callbackUrl=/dashboard");
  }

  const { items, error } = await getSavedItems();

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <div className="mb-10">
        <h1 className="font-serif text-3xl font-semibold text-ink-900">
          Welcome back{session.user.name ? `, ${session.user.name}` : ""}
        </h1>
        <p className="mt-1 text-sm text-ink-700/60">
          Get tailored recommendations and revisit what you've saved.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
        <section>
          <h2 className="mb-4 font-serif text-xl font-semibold text-ink-900">
            Get personalized recommendations
          </h2>
          <RecommendationForm />
        </section>

        <section>
          <h2 className="mb-4 font-serif text-xl font-semibold text-ink-900">
            My saved experiences
          </h2>
          {error ? (
            <EmptyState title="Couldn't load your saved items right now." message={error} />
          ) : items.length === 0 ? (
            <EmptyState
              title="Nothing saved yet."
              message="Save hidden gems, events, and cultural experiences from any destination page to see them here."
            />
          ) : (
            <div className="flex flex-col gap-3">
              {items.map((item) => (
                <div key={item.id} className="card p-4">
                  <p className="font-medium text-ink-900">{item.name}</p>
                  {item.category && (
                    <p className="text-xs uppercase tracking-wide text-ink-700/50">
                      {item.category}
                    </p>
                  )}
                  {item.description && (
                    <p className="mt-1 text-sm text-ink-700">
                      {item.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
