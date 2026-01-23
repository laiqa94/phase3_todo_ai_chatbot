"use client";

import type { Task } from "@/types/task";

import { TaskCard } from "@/components/TaskCard";

export function TaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
}: {
  tasks: Task[];
  onToggleComplete?: (taskId: string | number, nextCompleted: boolean) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string | number) => void;
}) {
  if (tasks.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-zinc-300 bg-white p-8 text-center text-zinc-600">
        No tasks yet.
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {tasks.map((t, index) => (
        <TaskCard
          key={`${t.id}-${index}`}
          task={t}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
