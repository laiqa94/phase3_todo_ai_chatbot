"use client";

import Link from "next/link";
import { useState } from "react";

export default function DashboardPage() {
  const [tasks] = useState([
    {
      id: 1,
      title: "Sample Task 1",
      description: "This is a sample task",
      completed: false,
      ownerId: 1
    },
    {
      id: 2,
      title: "Sample Task 2",
      description: "This is another sample task",
      completed: true,
      ownerId: 1
    }
  ]);

  const total = tasks.length;
  const completed = tasks.filter((t) => t.completed).length;
  const active = total - completed;

  return (
    <div className="p-4 space-y-6 min-h-screen">
      <div className="glass-card p-6 rounded-xl">
          <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
          <p className="text-white/80">Overview of your tasks.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card p-6 rounded-xl">
          <div className="text-sm text-white/80">Total</div>
          <div className="text-3xl font-semibold text-white">{total}</div>
        </div>
        <div className="glass-card p-6 rounded-xl">
          <div className="text-sm text-white/80">Active</div>
          <div className="text-3xl font-semibold text-white">{active}</div>
        </div>
        <div className="glass-card p-6 rounded-xl">
          <div className="text-sm text-white/80">Completed</div>
          <div className="text-3xl font-semibold text-white">{completed}</div>
        </div>
      </div>

      <div className="glass-card p-6 rounded-xl">
        <h2 className="font-medium text-white">Quick actions</h2>
        <div className="mt-3 flex gap-3">
          <Link
            href="/tasks"
            className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-md hover:bg-white/30 transition-colors border border-white/30"
          >
            View tasks
          </Link>
          <Link
            href="/tasks?compose=1"
            className="bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-md hover:bg-white/20 transition-colors border border-white/30"
          >
            Add task
          </Link>
        </div>
      </div>
    </div>
  );
}
