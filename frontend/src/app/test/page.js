"use client";
import { useState, useEffect } from "react";

export default function TestPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const testAPI = async () => {
      try {
        const response = await fetch("/api/test");
        console.log("Response status:", response.status);
        const data = await response.json();
        console.log("Response data:", data);
        setMessage(data.message);
      } catch (err) {
        console.error("Error:", err);
        setError(err.message);
      }
    };

    testAPI();
  }, []);

  return (
    <div>
      <h1>API Test Page</h1>
      {message && <p>Message: {message}</p>}
      {error && <p>Error: {error}</p>}
    </div>
  );
}
