import Link from "next/link";
import { auth, signOut } from "@/lib/auth";

export default async function Navbar() {
  const session = await auth();

  return (
    <header className="sticky top-0 z-40 border-b border-sand-200 bg-sand-50/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="font-serif text-2xl font-semibold tracking-tight text-ink-900"
        >
          Wayfare
        </Link>

        <nav className="flex items-center gap-6 text-sm font-medium text-ink-800">
          <Link href="/" className="hover:text-clay-600">
            Discover
          </Link>
          {session?.user ? (
            <>
              <Link href="/dashboard" className="hover:text-clay-600">
                Dashboard
              </Link>
              <span className="hidden text-ink-700/50 sm:inline">
                {session.user.email}
              </span>
              <form
                action={async () => {
                  "use server";
                  await signOut({ redirectTo: "/" });
                }}
              >
                <button type="submit" className="btn-secondary">
                  Sign out
                </button>
              </form>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-clay-600">
                Sign in
              </Link>
              <Link href="/register" className="btn-primary">
                Join
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
