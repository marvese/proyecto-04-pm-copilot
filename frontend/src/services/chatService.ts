import type { ChatSession, ChatMessage, SourceCitation, StreamEvent } from "../types/chat";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8080";
const WS_BASE = API_BASE.replace(/^http/, "ws");

export const chatService = {
  async createSession(projectId: string): Promise<ChatSession> {
    const res = await fetch(`${API_BASE}/api/v1/chat/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId }),
    });
    if (!res.ok) throw new Error(`createSession failed: ${res.status}`);
    return res.json();
  },

  async listSessions(projectId?: string): Promise<ChatSession[]> {
    const url = new URL(`${API_BASE}/api/v1/chat/sessions`);
    if (projectId) url.searchParams.set("project_id", projectId);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`listSessions failed: ${res.status}`);
    return res.json();
  },

  async sendMessage(
    sessionId: string,
    content: string
  ): Promise<{ message_id: string; stream_url: string }> {
    const res = await fetch(`${API_BASE}/api/v1/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error(`sendMessage failed: ${res.status}`);
    return res.json();
  },

  async getMessages(sessionId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/api/v1/chat/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error(`getMessages failed: ${res.status}`);
    return res.json();
  },

  streamResponse(
    messageId: string,
    onToken: (token: string) => void,
    onDone: (event: { type: "done"; sources: SourceCitation[] }) => void,
    onError: (detail: string) => void
  ): WebSocket {
    const ws = new WebSocket(`${WS_BASE}/api/v1/chat/stream/${messageId}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string) as StreamEvent;
        if (data.type === "token") onToken(data.content);
        else if (data.type === "done") onDone(data);
        else if (data.type === "error") onError(data.detail);
      } catch {
        onError("Failed to parse server event");
      }
    };
    ws.onerror = () => onError("WebSocket connection error");
    return ws;
  },
};
