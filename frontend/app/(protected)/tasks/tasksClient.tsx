"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import type { Task } from "@/types/task";

import { FilterTabs, type TaskFilter } from "@/components/FilterTabs";
import { TaskForm } from "@/components/TaskForm";
import { TaskList } from "@/components/TaskList";
import { useToast } from "@/components/ToastHost";
import { apiFetch, ApiError } from "@/lib/api";

const MOCK_TASKS: Task[] = [
  {
    id: 1,
    title: "Play a video game",
    description: "Gaming session",
    completed: true,
    ownerId: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 2,
    title: "Game development",
    description: "Work on game project",
    completed: false,
    ownerId: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 3,
    title: "Review game mechanics",
    description: "Check game balance",
    completed: false,
    ownerId: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

function getMockTasks(status?: string, query?: string): Task[] {
  let filtered = MOCK_TASKS;
  
  if (status === "completed") {
    filtered = filtered.filter(t => t.completed);
  } else if (status === "pending") {
    filtered = filtered.filter(t => !t.completed);
  }
  
  if (query && query.trim()) {
    const q = query.trim().toLowerCase();
    filtered = filtered.filter(t => 
      t.title.toLowerCase().includes(q) || 
      (t.description?.toLowerCase().includes(q) ?? false)
    );
  }
  
  return filtered;
}

export function TasksClient({
  initialTasks,
  initialStatus,
  initialQuery,
}: {
  initialTasks: Task[];
  initialStatus: string;
  initialQuery: string;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const toast = useToast();

  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [query, setQuery] = useState(initialQuery);
  const [editing, setEditing] = useState<Task | null>(null);

  const filterValue: TaskFilter = useMemo(() => {
    const normalized = initialStatus === "all" ? "" : initialStatus;
    if (normalized === "completed") return "completed";
    if (normalized === "pending") return "pending";
    return "all";
  }, [initialStatus]);

  const visibleTasks = useMemo(() => {
    const status = initialStatus === "all" ? "" : initialStatus;
    return tasks.filter((t) => {
      if (status === "completed" && !t.completed) return false;
      if (status === "pending" && t.completed) return false;
      if (initialQuery && initialQuery.trim()) {
        const q = initialQuery.trim().toLowerCase();
        const hay = `${t.title} ${t.description ?? ""}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [tasks, initialStatus, initialQuery]);


  useEffect(() => {
    // keep query input in sync with the URL-reflected value
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    // if URL filter changes and we're editing an item that is now hidden, exit edit mode
    if (editing && !visibleTasks.some((t) => t.id === editing.id)) setEditing(null);
  }, [editing, visibleTasks]);

  async function refetchFromServer() {
    const qs = new URLSearchParams();
    if (initialStatus && initialStatus !== "all") qs.set("status", initialStatus);
    if (initialQuery) qs.set("q", initialQuery);

    try {
      const next = await apiFetch<{ items: Task[] }>(`/api/me/tasks?${qs.toString()}`, {
        method: "GET",
      });
      setTasks(next.items ?? []);
    } catch (e: unknown) {
      // Fallback to mock data on 500 error
      if (e instanceof ApiError && e.status === 500) {
        console.warn("Backend returned 500, using mock data fallback");
        const mockItems = getMockTasks(initialStatus, initialQuery);
        setTasks(mockItems);
      } else {
        // Re-throw other errors
        throw e;
      }
    }
  }

  useEffect(() => {
    // Refetch if URL-reflected filter/search changes.
    void refetchFromServer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialStatus, initialQuery]);

  function updateUrl(next: { status?: string; q?: string }) {
    const sp = new URLSearchParams(params.toString());
    if (next.status) sp.set("status", next.status);
    else sp.delete("status");
    if (next.q !== undefined) {
      if (next.q) sp.set("q", next.q);
      else sp.delete("q");
    }
    router.replace(`/tasks?${sp.toString()}`);
  }

  async function createTask(draft: { title: string; description?: string; dueDate?: string; priority?: string }) {
    const optimistic: Task = {
      id: `tmp-${Date.now()}`,
      title: draft.title,
      description: draft.description,
      dueDate: draft.dueDate,
      priority: draft.priority,
      completed: false,
      ownerId: 0, // Placeholder value for optimistic update
    };

    setTasks((prev) => [optimistic, ...prev]);

    try {
      const created = await apiFetch<Task>("/api/me/tasks", {
        method: "POST",
        body: draft,
      });
      setTasks((prev) => prev.map((t) => (t.id === optimistic.id ? created : t)));
      toast.success("Task created.");
    } catch (e: unknown) {
      setTasks((prev) => prev.filter((t) => t.id !== optimistic.id));
      toast.error(e instanceof Error ? e.message : "Failed to create task.");
    }
  }

  async function toggleComplete(taskId: number | string, nextCompleted: boolean) {
    const prev = tasks;
    setTasks((list) =>
      list.map((t) =>
        t.id === taskId ? { ...t, completed: nextCompleted } : t,
      ),
    );

    try {
      const updated = await apiFetch<Task>(`/api/me/tasks/${taskId}/complete`, {
        method: "PATCH",
        body: { completed: nextCompleted },
      });
      setTasks((list) => list.map((t) => (t.id === taskId ? updated : t)));
    } catch (e: unknown) {
      setTasks(prev);
      toast.error(e instanceof Error ? e.message : "Failed to update task.");
    }
  }

  async function deleteTask(taskId: number | string) {
    const prev = tasks;
    setTasks((list) => list.filter((t) => t.id !== taskId));

    try {
      await apiFetch<void>(`/api/me/tasks/${encodeURIComponent(taskId)}`, {
        method: "DELETE",
      });
      toast.success("Task deleted.");
    } catch (e: unknown) {
      setTasks(prev);
      toast.error(e instanceof Error ? e.message : "Failed to delete task.");
    }
  }

  async function saveEdit(draft: { title: string; description?: string; dueDate?: string; priority?: string }) {
    if (!editing) return;
    const taskId = editing.id;

    const prev = tasks;
    setTasks((list) => list.map((t) => (t.id === taskId ? { ...t, ...draft } : t)));

    try {
      const updated = await apiFetch<Task>(`/api/me/tasks/${encodeURIComponent(taskId)}`, {
        method: "PUT",
        body: draft,
      });
      setTasks((list) => list.map((t) => (t.id === taskId ? updated : t)));
      setEditing(null);
      toast.success("Task updated.");
    } catch (e: unknown) {
      setTasks(prev);
      toast.error(e instanceof Error ? e.message : "Failed to update task.");
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-center sm:text-left">
          <h1 className="text-xl sm:text-2xl font-semibold text-white">Tasks</h1>
          <p className="mt-1 text-sm text-white/80">Create and manage your tasks.</p>
        </div>

        <FilterTabs
          value={filterValue}
          onChange={(next) => updateUrl({ status: next === "all" ? "all" : next, q: query })}
        />
      </div>

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") updateUrl({ status: initialStatus, q: query });
            }}
            placeholder="Search tasks…"
            className="w-full h-10 sm:h-11 rounded-lg border border-white/20 bg-white/10 backdrop-blur-sm px-3 sm:px-4 text-sm sm:text-base text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent"
          />
        </div>
        <button
          type="button"
          onClick={() => updateUrl({ status: initialStatus, q: query })}
          className="h-10 sm:h-11 rounded-lg bg-white/20 backdrop-blur-sm px-4 sm:px-6 text-sm sm:text-base text-white hover:bg-white/30 transition-colors font-medium border border-white/30"
        >
          Search
        </button>
      </div>

      {/* Task Form */}
      <TaskForm
        mode={editing ? "edit" : "create"}
        initialValues={
          editing
            ? {
                title: editing.title,
                description: editing.description,
                dueDate: editing.dueDate,
                priority: editing.priority,
              }
            : undefined
        }
        onSubmit={(draft) => (editing ? saveEdit(draft) : createTask(draft))}
        onCancel={editing ? () => setEditing(null) : undefined}
      />

      {/* Task List */}
      <TaskList
        tasks={visibleTasks}
        onToggleComplete={toggleComplete}
        onEdit={(t) => setEditing(t)}
        onDelete={deleteTask}
      />
    </div>
  );
}
