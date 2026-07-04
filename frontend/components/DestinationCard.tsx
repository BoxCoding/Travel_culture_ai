import Link from "next/link";
import SafeImage from "@/components/SafeImage";
import type { Destination } from "@/lib/types";

export default function DestinationCard({
  destination,
}: {
  destination: Destination;
}) {
  return (
    <Link
      href={`/destinations/${destination.id}`}
      className="card group flex flex-col overflow-hidden transition hover:-translate-y-1 hover:shadow-lg"
    >
      <div className="relative h-48 w-full overflow-hidden bg-leaf-100">
        {destination.image_url ? (
          <SafeImage
            src={destination.image_url}
            alt={destination.name}
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-leaf-600">
            <span className="font-serif text-lg">{destination.name}</span>
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-5">
        <div className="flex items-center justify-between">
          <h3 className="font-serif text-xl font-semibold text-ink-900">
            {destination.name}
          </h3>
          <span className="text-xs uppercase tracking-wide text-ink-700/50">
            {destination.region}
          </span>
        </div>
        <p className="text-sm text-ink-700/50">{destination.country}</p>
        <p className="line-clamp-3 text-sm text-ink-700">
          {destination.description}
        </p>
        {destination.tags?.length > 0 && (
          <div className="mt-auto flex flex-wrap gap-2 pt-2">
            {destination.tags.slice(0, 4).map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-sand-100 px-3 py-1 text-xs text-ink-700"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
