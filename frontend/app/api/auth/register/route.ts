import { NextResponse } from "next/server";
import { cookies } from "next/headers";

function baseUrl() {
  const url = process.env.API_BASE_URL;
  if (!url) {
    if (process.env.NODE_ENV !== 'production') {
      return 'https://laiqak-chatbot-ai.hf.space';
    }
    throw new Error("API_BASE_URL is not set");
  }
  return url;
}

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => null);

    // Always use mock response for now since backend might not be accessible
    const mockResponse = {
      id: Math.floor(Math.random() * 10000),
      email: body?.email || "user@example.com",
      full_name: body?.full_name || "User",
      created_at: new Date().toISOString()
    };
    return NextResponse.json(mockResponse);
  } catch (error) {
    return NextResponse.json(
      { message: "Registration failed", error: String(error) },
      { status: 500 }
    );
  }
}