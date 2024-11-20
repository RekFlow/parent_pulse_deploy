"use client";
import { useState, useEffect } from "react";

export default function TestPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const testAPI = async () => {
      try {
        console.log("Testing API connection...");
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
    <div className="p-4">
      <h1 className="text-2xl mb-4">API Test Page</h1>
      {message && <p className="text-green-600">Message: {message}</p>}
      {error && <p className="text-red-600">Error: {error}</p>}
    </div>
  );
}
