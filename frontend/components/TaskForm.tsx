"use client";

import { useMemo, useState } from "react";

import type { Task } from "@/types/task";

type TaskDraft = Pick<Task, "title" | "description" | "dueDate" | "priority">;

export function TaskForm({
  mode,
  initialValues,
  onSubmit,
  onCancel,
}: {
  mode: "create" | "edit";
  initialValues?: TaskDraft;
  onSubmit?: (draft: TaskDraft) => Promise<void> | void;
  onCancel?: () => void;
}) {
  const initial = useMemo<TaskDraft>(
    () => ({
      title: initialValues?.title ?? "",
      description: initialValues?.description ?? "",
      dueDate: initialValues?.dueDate ?? "",
      priority: initialValues?.priority ?? "",
    }),
    [initialValues],
  );

  const [draft, setDraft] = useState<TaskDraft>(initial);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!draft.title.trim()) {
      setError("Title is required.");
      return;
    }

    try {
      setSubmitting(true);
      await onSubmit?.({
        title: draft.title.trim(),
        description: draft.description?.trim() || undefined,
        dueDate: draft.dueDate || undefined,
        priority: draft.priority || undefined,
      });
      if (mode === "create") setDraft({ title: "", description: "", dueDate: "", priority: "" });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="glass-card rounded-xl p-4 sm:p-6">
      <div className="grid gap-4 sm:gap-3">
        {/* Title - Full width on mobile */}
        <label className="grid gap-1">
          <span className="text-sm font-medium text-white/90">Title</span>
          <input
            value={draft.title}
            onChange={(e) => setDraft((d) => ({ ...d, title: e.target.value }))}
            className="h-10 sm:h-11 rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-3 text-sm sm:text-base text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent"
            placeholder="e.g., Pay rent"
          />
        </label>

        {/* Due date and Priority - Stack on mobile, side by side on desktop */}
        <div className="grid gap-4 sm:gap-3 sm:grid-cols-2">
          <label className="grid gap-1">
            <span className="text-sm font-medium text-white/90">Due date</span>
            <input
              type="date"
              value={draft.dueDate ?? ""}
              onChange={(e) => setDraft((d) => ({ ...d, dueDate: e.target.value }))}
              className="h-10 sm:h-11 rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-3 text-sm sm:text-base text-white focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent [color-scheme:dark]"
            />
          </label>

          <label className="grid gap-1">
            <span className="text-sm font-medium text-white/90">Priority</span>
            <select
              value={draft.priority ?? ""}
              onChange={(e) => setDraft((d) => ({ ...d, priority: e.target.value }))}
              className="h-10 sm:h-11 rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-3 text-sm sm:text-base text-white focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent"
            >
              <option value="">Select priority</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>

        {/* Description - Full width */}
        <label className="grid gap-1">
          <span className="text-sm font-medium text-white/90">Description</span>
          <textarea
            value={draft.description ?? ""}
            onChange={(e) => setDraft((d) => ({ ...d, description: e.target.value }))}
            className="min-h-20 sm:min-h-24 rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-3 py-2 text-sm sm:text-base text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent resize-y"
            placeholder="Optional details"
            rows={3}
          />
        </label>

        {/* Buttons - Stack on mobile, inline on desktop */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2 sm:gap-3 pt-2">
          {onCancel ? (
            <button
              type="button"
              onClick={onCancel}
              className="h-10 sm:h-11 rounded-md border border-white/20 bg-white/10 backdrop-blur-sm px-4 text-sm sm:text-base text-white hover:bg-white/20 transition-colors order-2 sm:order-1"
            >
              Cancel
            </button>
          ) : null}
          <button
            disabled={submitting}
            type="submit"
            className="h-10 sm:h-11 rounded-md bg-gradient-to-r from-purple-500 to-pink-500 px-4 text-sm sm:text-base text-white hover:from-purple-600 hover:to-pink-600 disabled:opacity-60 transition-all order-1 sm:order-2 font-medium shadow-lg"
          >
            {submitting ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {mode === "create" ? "Adding..." : "Saving..."}
              </div>
            ) : (
              mode === "create" ? "Add task" : "Save"
            )}
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-3 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
          <p className="text-sm text-red-200">{error}</p>
        </div>
      ) : null}
    </form>
  );
}
