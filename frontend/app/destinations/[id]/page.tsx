import { notFound } from "next/navigation";
import { auth } from "@/lib/auth";
import SafeImage from "@/components/SafeImage";
import { backendFetch, BackendError, type BackendFetchOptions } from "@/lib/backend";
import type {
  AiEntity,
  Destination,
  HeritageStory,
  RecommendationResponse,
} from "@/lib/types";
import AiBadge from "@/components/AiBadge";
import EmptyState from "@/components/EmptyState";
import EntityList from "@/components/EntityList";
import Tabs from "@/components/Tabs";
import ChatWidget from "@/components/ChatWidget";

async function safeFetch<T>(path: string, init?: BackendFetchOptions) {
  try {
    const data = await backendFetch<T>(path, init);
    return { data, error: undefined as string | undefined };
  } catch (err) {
    return {
      data: undefined as T | undefined,
      error:
        err instanceof BackendError
          ? err.message
          : "Something went wrong reaching the backend.",
    };
  }
}

export default async function DestinationDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const session = await auth();
  const isSignedIn = Boolean(session?.user?.id);

  let destination: Destination;
  try {
    destination = await backendFetch<Destination>(
      `/api/destinations/${params.id}`
    );
  } catch (err) {
    if (err instanceof BackendError && err.status === 404) {
      notFound();
    }
    return (
      <div className="mx-auto max-w-4xl px-6 py-16">
        <EmptyState
          title="We couldn't load this destination right now."
          message={
            err instanceof BackendError
              ? err.message
              : "The destination service may be unavailable. Please try again shortly."
          }
        />
      </div>
    );
  }

  const [hiddenGems, heritage, events, experiences, recommendations] =
    await Promise.all([
      safeFetch<AiEntity[]>(`/api/destinations/${params.id}/hidden-gems`),
      safeFetch<HeritageStory>(`/api/destinations/${params.id}/heritage`),
      safeFetch<AiEntity[]>(`/api/destinations/${params.id}/events`),
      safeFetch<AiEntity[]>(`/api/destinations/${params.id}/experiences`),
      safeFetch<RecommendationResponse>("/api/recommendations", {
        method: "POST",
        body: {
          interests: destination.tags?.length ? destination.tags : ["culture"],
          region: destination.region,
          duration_days: 5,
        },
      }),
    ]);

  const tabs = [
    {
      id: "attractions",
      label: "Attractions & Recommendations",
      content: (
        <div className="flex flex-col gap-6">
          <div>
            <h3 className="font-serif text-lg font-semibold text-ink-900">
              About {destination.name}
            </h3>
            <p className="mt-2 text-sm text-ink-700">
              {destination.description}
            </p>
          </div>

          <div>
            <div className="mb-3 flex items-center gap-2">
              <h3 className="font-serif text-lg font-semibold text-ink-900">
                Personalized recommendations
              </h3>
              <AiBadge />
            </div>
            {recommendations.error || !recommendations.data ? (
              <EmptyState
                title="Couldn't load recommendations right now."
                message={recommendations.error}
              />
            ) : (
              <div className="flex flex-col gap-4">
                <p className="text-sm text-ink-700">
                  {recommendations.data.summary}
                </p>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-700/50">
                      Attractions
                    </p>
                    <ul className="flex flex-col gap-2">
                      {recommendations.data.attractions.map((a, i) => (
                        <li key={i} className="card p-4 text-sm">
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
                      {recommendations.data.hidden_gems.map((g, i) => (
                        <li key={i} className="card p-4 text-sm">
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
        </div>
      ),
    },
    {
      id: "hidden-gems",
      label: "Hidden Gems",
      content: (
        <EntityList
          items={hiddenGems.data ?? []}
          error={hiddenGems.error}
          emptyTitle="No hidden gems uncovered yet for this destination."
          isSignedIn={isSignedIn}
          itemType="hidden_gem"
        />
      ),
    },
    {
      id: "heritage",
      label: "Heritage Story",
      content: heritage.error || !heritage.data ? (
        <EmptyState
          title="Couldn't load the heritage story right now."
          message={heritage.error}
        />
      ) : (
        <div className="card flex flex-col gap-3 p-6">
          <div className="flex items-center justify-between">
            {heritage.data.title && (
              <h3 className="font-serif text-lg font-semibold text-ink-900">
                {heritage.data.title}
              </h3>
            )}
            {heritage.data.ai_generated && <AiBadge />}
          </div>
          <p className="whitespace-pre-line text-sm leading-relaxed text-ink-700">
            {heritage.data.narrative}
          </p>
        </div>
      ),
    },
    {
      id: "events",
      label: "Local Events",
      content: (
        <EntityList
          items={events.data ?? []}
          error={events.error}
          emptyTitle="No upcoming events found for this destination."
          isSignedIn={isSignedIn}
          itemType="event"
          savable={false}
        />
      ),
    },
    {
      id: "experiences",
      label: "Cultural Experiences",
      content: (
        <EntityList
          items={experiences.data ?? []}
          error={experiences.error}
          emptyTitle="No cultural experiences listed yet for this destination."
          isSignedIn={isSignedIn}
          itemType="experience"
        />
      ),
    },
  ];

  return (
    <div>
      <section className="relative h-72 w-full overflow-hidden bg-leaf-100 sm:h-96">
        {destination.image_url ? (
          <SafeImage
            src={destination.image_url}
            alt={destination.name}
            loading="eager"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <span className="font-serif text-3xl text-leaf-600">
              {destination.name}
            </span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-ink-900/70 via-ink-900/10 to-transparent" />
        <div className="absolute bottom-0 left-0 w-full px-6 py-6 sm:px-10">
          <p className="text-sm font-medium uppercase tracking-widest text-sand-100">
            {destination.region} · {destination.country}
          </p>
          <h1 className="font-serif text-3xl font-semibold text-white sm:text-4xl">
            {destination.name}
          </h1>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-10 sm:px-10">
        <Tabs tabs={tabs} />
      </section>

      <ChatWidget isSignedIn={isSignedIn} destinationName={destination.name} />
    </div>
  );
}
