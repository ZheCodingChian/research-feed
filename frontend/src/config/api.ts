const API_BASE_URL = import.meta.env.VITE_API_URL;

// Debug: Log the API URL being used
console.log('API_BASE_URL:', API_BASE_URL);

export const API_ENDPOINTS = {
  PAPERS: '/papers',
  PAPERS_METADATA: '/papers/metadata',
  PAPER_DETAILS: '/papers/details',
};

export const apiCall = async (endpoint: string, options: RequestInit = {}): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!response.ok) {
      // Log actual error for debugging
      try {
        const errorData = await response.json();
        console.error('API Error:', errorData);
      } catch {
        console.error('API Error: Status', response.status);
      }

      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

export default API_BASE_URL;