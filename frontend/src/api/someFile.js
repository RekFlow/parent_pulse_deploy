// Development
const baseUrl =
  process.env.NODE_ENV === "development" ? "http://localhost:8000" : "";

// Example API call
const response = await fetch(`${baseUrl}/api/your-endpoint`);
