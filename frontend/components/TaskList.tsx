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
      <div className="rounded-lg border border-dashed border-white/30 bg-white/10 backdrop-blur-sm p-6 sm:p-8 text-center text-white/80">
        <div className="mx-auto w-16 h-16 sm:w-20 sm:h-20 mb-4 rounded-full bg-white/10 flex items-center justify-center">
          <svg className="w-8 h-8 sm:w-10 sm:h-10 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-sm sm:text-base font-medium text-white mb-1">No tasks yet</h3>
        <p className="text-xs sm:text-sm text-white/60">Create your first task to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 sm:space-y-4">
      <div className="grid gap-3 sm:gap-4">
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
    </div>
  );
}
