import type { ApiErrorPayload } from "@/lib/apiTypes";
import { getAccessToken } from "./auth";

// NOTE: For 401/session-expiry policy, the server-side API wrapper (`apiFetchServer`)
// and middleware are the primary enforcement points.
// Client-side calls now use JWT tokens in Authorization header for auth.

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  // For client-side API calls, we should use the frontend's proxy route
  // This ensures proper authentication handling and cookie management
  // The proxy route will handle path transformations and backend communication

  // Check if path already starts with /api/proxy to avoid double-prefixing
  let proxyPath: string;
  if (path.startsWith('/api/proxy/')) {
    proxyPath = path; // Path already includes proxy prefix
  } else {
    proxyPath = `/api/proxy${path.startsWith('/') ? path : '/' + path}`;
  }

  const url = proxyPath; // Use relative path so it goes to the same origin (frontend)

  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  // Add JWT token to Authorization header if available
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(url, {
    ...options,
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    payload = await res.json().catch(() => null);
  } else {
    payload = await res.text().catch(() => null);
  }

  if (!res.ok) {
    const maybeObj = typeof payload === "object" && payload ? (payload as ApiErrorPayload) : null;
    const message = maybeObj?.message ? String(maybeObj.message) : `Request failed (${res.status})`;
    throw new ApiError(message, res.status, payload);
  }

  return payload as T;
}

// Specific API functions for the AI Chatbot
export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  has_tools_executed: boolean;
  tool_results: Array<{
    tool_name: string;
    result: any;
    arguments: any;
  }>;
  message_id?: number;
}

export interface NewConversationRequest {
  message: string;
  title?: string;
}

export interface ConversationHistoryResponse {
  conversation_id: number;
  title: string;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    timestamp: string;
  }>;
}

/**
 * Send a message to the AI chatbot
 */
export async function sendChatMessage(userId: number, request: ChatRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>(`/${userId}/chat`, {
    method: 'POST',
    body: request,
  });
}

/**
 * Start a new conversation with the AI chatbot
 */
export async function startNewConversation(userId: number, request: NewConversationRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>(`/${userId}/new_conversation`, {
    method: 'POST',
    body: request,
  });
}

/**
 * Get conversation history
 */
export async function getConversationHistory(userId: number, conversationId: number): Promise<ConversationHistoryResponse> {
  return apiFetch<ConversationHistoryResponse>(`/conversations/${userId}/${conversationId}`, {
    method: 'GET',
  });
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<{ id: number; email: string; }> {
  return apiFetch(`/me`, {
    method: 'GET',
  });
}

/**
 * Task management functions
 */
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * Create a new task
 */
export async function createTask(task: TaskCreate): Promise<Task> {
  return apiFetch<Task>(`/tasks/`, {
    method: 'POST',
    body: task,
  });
}

/**
 * Get all tasks
 */
export async function getTasks(): Promise<Task[]> {
  return apiFetch<Task[]>(`/tasks`, {
    method: 'GET',
  });
}

/**
 * Get a specific task
 */
export async function getTask(taskId: number): Promise<Task> {
  return apiFetch<Task>(`/tasks/${taskId}`, {
    method: 'GET',
  });
}

/**
 * Update a task
 */
export async function updateTask(taskId: number, task: TaskUpdate): Promise<Task> {
  return apiFetch<Task>(`/tasks/${taskId}`, {
    method: 'PUT',
    body: task,
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: number): Promise<void> {
  return apiFetch<void>(`/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

/**
 * Toggle task completion status
 */
export async function toggleTask(taskId: number): Promise<Task> {
  return apiFetch<Task>(`/tasks/${taskId}/toggle`, {
    method: 'PATCH',
  });
}
