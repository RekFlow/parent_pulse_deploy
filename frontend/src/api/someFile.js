const baseUrl =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://parent-pulse-deploy-5wuxkxdmy-eurekas-projects-33f9ad9f.vercel.app";

async function fetchApi(endpoint) {
  try {
    const response = await fetch(`${baseUrl}/api/${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
}
