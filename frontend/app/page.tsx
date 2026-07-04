import { backendFetch, BackendError } from "@/lib/backend";
import type { Destination } from "@/lib/types";
import DestinationCard from "@/components/DestinationCard";
import EmptyState from "@/components/EmptyState";

async function getDestinations(params: {
  q?: string;
  region?: string;
}): Promise<{ destinations: Destination[]; error?: string }> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.region) search.set("region", params.region);
  const qs = search.toString();

  try {
    const destinations = await backendFetch<Destination[]>(
      `/api/destinations${qs ? `?${qs}` : ""}`
    );
    return { destinations };
  } catch (err) {
    const message =
      err instanceof BackendError
        ? err.message
        : "Something went wrong loading destinations.";
    return { destinations: [], error: message };
  }
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: { q?: string; region?: string };
}) {
  const { destinations, error } = await getDestinations(searchParams);

  return (
    <div>
      <section className="border-b border-sand-200 bg-gradient-to-b from-clay-50 to-sand-50">
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-clay-600">
            Travel, guided by culture
          </p>
          <h1 className="mx-auto max-w-3xl font-serif text-4xl font-semibold leading-tight text-ink-900 sm:text-5xl">
            Discover destinations through their stories, not just their
            sights.
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-ink-700/70">
            Hidden gems, heritage narratives, local events, and authentic
            cultural experiences — surfaced for you by AI, curated by
            travelers.
          </p>

          <form
            action="/"
            className="mx-auto mt-10 flex max-w-xl flex-col gap-3 sm:flex-row"
          >
            <input
              type="text"
              name="q"
              defaultValue={searchParams.q}
              placeholder="Search by region or interest — e.g. 'temples', 'street food'"
              className="input-field flex-1"
            />
            <button type="submit" className="btn-primary whitespace-nowrap">
              Search destinations
            </button>
          </form>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-14">
        <div className="mb-8 flex items-end justify-between">
          <h2 className="font-serif text-2xl font-semibold text-ink-900">
            {searchParams.q ? `Results for "${searchParams.q}"` : "Featured destinations"}
          </h2>
        </div>

        {error ? (
          <EmptyState
            title="We couldn't reach the destination service right now."
            message={`${error} — please try again shortly. The rest of the site still works.`}
          />
        ) : destinations.length === 0 ? (
          <EmptyState
            title="No destinations found."
            message="Try a different search term, or check back soon as we add more places."
          />
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {destinations.map((destination) => (
              <DestinationCard key={destination.id} destination={destination} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
