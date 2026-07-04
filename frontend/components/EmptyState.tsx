export default function EmptyState({
  title,
  message,
}: {
  title: string;
  message?: string;
}) {
  return (
    <div className="card flex flex-col items-center gap-2 px-6 py-12 text-center">
      <p className="font-serif text-lg text-ink-900">{title}</p>
      {message && (
        <p className="max-w-md text-sm text-ink-700/60">{message}</p>
      )}
    </div>
  );
}
