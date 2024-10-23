export interface PolicyResult {
  statement: string;
  score: number;
  source: string;
  context: string[];
  topics: string[];
}

export interface UploadResponse {
  message: string;
  doc_id: string;
}

export interface QueryResponse {
  responses: PolicyResult[];
}

export interface StatusMessage {
  type: "error" | "success" | "info";
  message: string;
}

export interface DocumentCount {
  count: number;
}
