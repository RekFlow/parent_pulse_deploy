import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query_type, query_text } = body;

    console.log("API Route - Processing request:", { query_type, query_text });

    const apiUrl =
      process.env.NODE_ENV === "development"
        ? "http://localhost:8000/api/query"
        : "https://your-production-url.com/api/query";

    console.log("Sending request to Python backend:", apiUrl);

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query_type,
        query_text,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Python Backend Error:", response.status, errorText);
      throw new Error(`Backend API returned ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log("Received response from Python backend:", data);

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in API route:", error);
    return NextResponse.json(
      {
        error: "Internal Server Error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

// Add logging for development/debugging
if (process.env.NODE_ENV === "development") {
  console.log("Query API route loaded");
}
