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

export interface OllamaResponse {
  summary: string;
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  total_duration: number;
  load_duration: number;
  prompt_eval_count: number;
  prompt_eval_duration: number;
  eval_count: number;
  eval_duration: number;
}

export interface StreamCallbacks {
  onToken?: (token: string) => void;
  onComplete?: (fullResponse: string) => void;
  onError?: (error: Error) => void;
}

export interface StatusMessage {
  type: "error" | "success" | "info";
  message: string;
}

export interface DocumentCount {
  files: string[];
}

export interface TopicResponse {
  topics: string[];
}
