import { NextResponse } from "next/server";
import { getSessionServer } from "@/lib/auth";

function isDevelopment() {
  return process.env.NODE_ENV !== 'production';
}

function baseUrl() {
  // First try API_BASE_URL (server-side env var)
  const url = process.env.API_BASE_URL;
  if (url) return url;
  
  // Fall back to NEXT_PUBLIC_API_BASE_URL (client-side env var, also available server-side)
  const publicUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (publicUrl) return publicUrl;
  
  return null;
}

async function handler(req: Request, ctx: { params: Promise<{ path: string[] }> }) {
  try {
    const { path } = await ctx.params;
    let requestBody = '';
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      requestBody = await req.text();
    }

    let transformedPath = `/${path.join("/")}`;
    
    // Handle chat endpoints
    if (transformedPath.match(/^\/\d+\/chat$/)) {
      transformedPath = transformedPath.replace(/^\/(\d+)\/chat$/, '/api/v1/$1/chat');
    }
    // Handle new conversation endpoints
    else if (transformedPath.match(/^\/\d+\/new_conversation$/)) {
      transformedPath = transformedPath.replace(/^\/(\d+)\/new_conversation$/, '/api/v1/$1/new_conversation');
    }
    // Handle conversation history endpoints
    else if (transformedPath.match(/^\/conversations\/\d+\/\d+$/)) {
      transformedPath = `/api/v1${transformedPath}`;
    }
    // Handle /me endpoint
    else if (transformedPath === '/me') {
      transformedPath = '/api/v1/auth/me';
    }
    // Handle task endpoints (remove /me prefix)
    else if (transformedPath.startsWith('/me/tasks')) {
      transformedPath = `/api/v1/tasks${transformedPath.replace('/me/tasks', '')}`;
    }
    // Handle /tasks endpoint
    else if (transformedPath.startsWith('/tasks')) {
      transformedPath = `/api/v1${transformedPath}`;
    }
    // Handle auth endpoints (already have /api/v1 prefix)
    else if (transformedPath.startsWith('/api/v1/auth')) {
      // Keep as is
    }
    // Handle other /api/ endpoints
    else if (transformedPath.startsWith('/api/')) {
      transformedPath = transformedPath.replace('/api/', '/api/v1/');
    }
    // Default: add /api/v1 prefix if not present
    else if (!transformedPath.startsWith('/api/v1/')) {
      transformedPath = `/api/v1${transformedPath}`;
    }

    const headers: Record<string, string> = {
      Accept: "application/json",
      "Content-Type": "application/json",
    };

    const isPublicEndpoint = transformedPath.includes('/auth');
    if (!isPublicEndpoint) {
      const session = await getSessionServer();
      const token = session?.accessToken || (isDevelopment() ? "mock-token" : null);
      if (token) headers.Authorization = `Bearer ${token}`;
    }

    let res;
    const apiBaseUrl = baseUrl();
    
    if (!apiBaseUrl) {
      return NextResponse.json({ error: "API backend not configured. Please set API_BASE_URL or NEXT_PUBLIC_API_BASE_URL environment variable." }, { status: 503 });
    }
    
    try {
      res = await fetch(`${apiBaseUrl}${transformedPath}`, {
        method: req.method,
        headers,
        body: req.method === "GET" || req.method === "HEAD" ? undefined : requestBody,
      });
    } catch (fetchError) {
      throw new Error(`Failed to connect to backend at ${apiBaseUrl}: ${fetchError instanceof Error ? fetchError.message : String(fetchError)}`);
    }

    if (!res.ok) {
      const errorText = await res.text();
      let errorDetail = errorText;
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorJson.message || errorText;
      } catch {}
      
      // For chat endpoints, try to return a helpful error response
      if (transformedPath.includes('/chat')) {
        return NextResponse.json({
          conversation_id: 1,
          response: `Sorry, I encountered an error: ${errorDetail}`,
          has_tools_executed: false,
          tool_results: [],
          message_id: null
        }, { status: res.status });
      }
      
      return NextResponse.json({ error: errorDetail }, { status: res.status });
    }

    // Handle successful response
    const contentType = res.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const json = await res.json().catch(() => null);
      return NextResponse.json(json, { status: res.status });
    }
    const text = await res.text();
    return new NextResponse(text, { status: res.status });
  } catch (error) {
    return NextResponse.json({
      message: "Proxy error occurred",
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
