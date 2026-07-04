"use client";

import { useState, type ReactNode } from "react";

export interface TabDefinition {
  id: string;
  label: string;
  content: ReactNode;
}

/**
 * Purely client-side tab switcher. All tab content is fetched server-side
 * by the parent Server Component and passed in as already-rendered nodes —
 * switching tabs here does not trigger any network requests.
 */
export default function Tabs({
  tabs,
  defaultTab,
}: {
  tabs: TabDefinition[];
  defaultTab?: string;
}) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id);

  return (
    <div>
      <div className="flex flex-wrap gap-2 border-b border-sand-200 pb-3">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActive(tab.id)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition ${
              active === tab.id
                ? "bg-leaf-600 text-white"
                : "bg-sand-100 text-ink-700 hover:bg-sand-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="pt-6">
        {tabs.map((tab) => (
          <div key={tab.id} className={active === tab.id ? "block" : "hidden"}>
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
}
