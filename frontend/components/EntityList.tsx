import AiBadge from "@/components/AiBadge";
import EmptyState from "@/components/EmptyState";
import SaveButton from "@/components/SaveButton";
import type { AiEntity } from "@/lib/types";

export default function EntityList({
  items,
  error,
  emptyTitle,
  isSignedIn,
  savable = true,
}: {
  items: AiEntity[];
  error?: string;
  emptyTitle: string;
  isSignedIn: boolean;
  savable?: boolean;
}) {
  if (error) {
    return (
      <EmptyState
        title="Couldn't load this right now."
        message={error}
      />
    );
  }

  if (items.length === 0) {
    return <EmptyState title={emptyTitle} />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {items.map((item) => (
        <div key={item.id} className="card flex flex-col gap-2 p-5">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-serif text-lg font-semibold text-ink-900">
              {item.name}
            </h4>
            {item.ai_generated && <AiBadge />}
          </div>
          <p className="text-xs uppercase tracking-wide text-ink-700/50">
            {item.category}
          </p>
          <p className="text-sm text-ink-700">{item.description}</p>
          {savable && (
            <div className="mt-2">
              <SaveButton id={item.id} isSignedIn={isSignedIn} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
