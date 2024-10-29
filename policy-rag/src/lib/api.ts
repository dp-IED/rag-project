import {
  UploadResponse,
  QueryResponse,
  DocumentCount,
  TopicResponse,
  PolicyResult,
  StreamCallbacks,
} from "../types";

const API_BASE_URL = "http://localhost:8000";

export const api = {
  async checkDocuments(): Promise<DocumentCount> {
    try {
      const response = await fetch(`${API_BASE_URL}/get_existing_documents/`, {
        method: "GET",
      });
      const data = await response.json();
      return { files: data.files };
    } catch (error) {
      return { files: [] };
    }
  },

  async summarizeFindings(
    results: PolicyResult[],
    query: string,
    callbacks: StreamCallbacks = {}
  ): Promise<void> {
    const prompt = `Use the excerpts of the following documents and answer the query, USE MARKDOWN: 
Query: ${query}
Excerpts:
${results.map((result) => result.statement).join("\n")}`;

    try {
      const response = await fetch(`http://localhost:11434/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "llama3.2",
          prompt: prompt,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to connect to Ollama");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";

      if (!reader) {
        throw new Error("Failed to initialize stream reader");
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk
          .split("\n")
          .filter((line) => line.trim())
          .map((line) => JSON.parse(line));

        for (const line of lines) {
          if (line.response) {
            const token = line.response;
            fullResponse += token;
            callbacks.onToken?.(token);
          }
          if (line.done) {
            callbacks.onComplete?.(fullResponse);
            return;
          }
        }
      }
    } catch (error) {
      const err =
        error instanceof Error ? error : new Error("Unknown error occurred");
      callbacks.onError?.(err);
      throw err;
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
    const j = await response.json();
    console.log(j);

    return j;
  },

  async getTopics(): Promise<TopicResponse> {
    const response = await fetch(`${API_BASE_URL}/topics/`);
    if (!response.ok) {
      throw new Error("Failed to fetch topics");
    }
    return response.json();
  },
};
