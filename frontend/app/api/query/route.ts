import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    console.log("API route handler started");
    const { query } = await req.json();
    console.log("Received query:", query);

    const pythonScriptPath = path.join(
      "C:",
      "Users",
      "eurek",
      "My Desktop",
      "AI Playground",
      "Parent Pulse",
      "main.py"
    );
    console.log("Python script path:", pythonScriptPath);

    const response = await new Promise<NextResponse>((resolve) => {
      const pythonProcess = spawn("python", [
        pythonScriptPath,
        "grades",
        query,
      ]);

      let stdoutData = "";

      pythonProcess.stdout.on("data", (data) => {
        const output = data.toString();
        console.log("Raw Python output:", output);
        stdoutData += output;
      });

      pythonProcess.stderr.on("data", (data) => {
        const error = data.toString();
        console.error("Python stderr:", error);
      });

      pythonProcess.on("close", (code) => {
        console.log("Python process exited with code:", code);

        if (code !== 0) {
          resolve(
            NextResponse.json(
              { error: "Python script failed to execute" },
              { status: 500 }
            )
          );
          return;
        }

        try {
          const jsonData = JSON.parse(stdoutData.trim());
          console.log("Parsed response:", jsonData);

          resolve(NextResponse.json(jsonData));
        } catch (error) {
          console.error("Failed to parse Python output:", error);
          resolve(
            NextResponse.json(
              {
                error: "Failed to process response",
                details: stdoutData,
              },
              { status: 500 }
            )
          );
        }
      });
    });

    return response;
  } catch (error) {
    console.error("Route handler error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
