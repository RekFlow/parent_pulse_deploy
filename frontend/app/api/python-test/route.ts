import { NextResponse } from "next/server";

export async function POST(req: Request) {
  console.log("Test API route handler started");

  try {
    const { query } = await req.json();
    console.log("Test received query:", query);

    // Test response without Python integration first
    return NextResponse.json({
      response: `Test response received: ${query}`,
      status: 200,
    });
  } catch (error) {
    console.error("Test API Route Error:", error);
    return NextResponse.json(
      { error: "An error occurred in test route" },
      { status: 500 }
    );
  }
}
