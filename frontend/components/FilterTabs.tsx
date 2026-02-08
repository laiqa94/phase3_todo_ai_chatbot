"use client";

export type TaskFilter = "all" | "pending" | "completed";

export function FilterTabs({
  value,
  onChange,
}: {
  value: TaskFilter;
  onChange?: (next: TaskFilter) => void;
}) {
  const items: Array<{ key: TaskFilter; label: string }> = [
    { key: "all", label: "All" },
    { key: "pending", label: "Active" },
    { key: "completed", label: "Completed" },
  ];

  return (
    <div className="inline-flex rounded-lg border border-white/20 bg-white/10 backdrop-blur-sm p-1">
      {items.map((it) => (
        <button
          key={it.key}
          type="button"
          onClick={() => onChange?.(it.key)}
          className={
            it.key === value
              ? "rounded-md bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm text-white border border-white/30"
              : "rounded-md px-3 py-1.5 text-sm text-white/80 hover:bg-white/10 transition-colors"
          }
        >
          {it.label}
        </button>
      ))}
    </div>
  );
}
