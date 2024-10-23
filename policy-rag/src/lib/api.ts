import { UploadResponse, QueryResponse, DocumentCount } from "../types";

const API_BASE_URL = "http://localhost:8000";

export const api = {
  async checkDocuments(): Promise<DocumentCount> {
    try {
      const response = await fetch(`${API_BASE_URL}/topics/`);
      const data = await response.json();
      return { count: data.documentCount || 0 }; // Your backend needs to provide this
    } catch (error) {
      return { count: 0 };
    }
  },

  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  },

  async queryDocuments(
    text: string,
    maxResponses: number = 5
  ): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/query/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        max_responses: maxResponses,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Query failed");
    }

    return response.json();
  },
};
