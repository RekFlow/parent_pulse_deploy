const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";

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