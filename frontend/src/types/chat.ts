export type MessageRole = "user" | "assistant";

export interface ChatSession {
  id: string;
  project_id: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface SourceCitation {
  source: string;
  document_id: string;
  url: string | null;
  score: number;
}

export type StreamEvent =
  | { type: "token"; content: string }
  | { type: "done"; sources: SourceCitation[] }
  | { type: "error"; detail: string };
