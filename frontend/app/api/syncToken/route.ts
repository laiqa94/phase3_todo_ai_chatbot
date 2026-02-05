import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const text = await req.text();
    if (!text || text.trim() === '') {
      return NextResponse.json({ error: "Empty request body" }, { status: 400 });
    }
    
    const { token, userId } = JSON.parse(text);

    if (!token) {
      return NextResponse.json({ error: "Token is required" }, { status: 400 });
    }

    // Create a response with cookies set
    const response = NextResponse.json({ success: true });

    // Set the access token cookie
    response.cookies.set("access_token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 30 * 60, // 30 minutes
    });

    // Set the user ID cookie if provided
    if (userId) {
      response.cookies.set("user_id", userId.toString(), {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 30 * 60, // 30 minutes
      });
    }

    return response;
  } catch (error) {
    console.error("Token sync error:", error);
    return NextResponse.json({ error: "Invalid JSON or server error" }, { status: 500 });
  }
}