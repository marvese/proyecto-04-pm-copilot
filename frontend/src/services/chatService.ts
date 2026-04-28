import type { ChatSession, ChatMessage, StreamEvent } from "../types/chat";

const BASE = "/api/v1/chat";

export const chatService = {
  async createSession(projectId: string): Promise<ChatSession> {
    // TODO: implement — POST /api/v1/chat/sessions
    throw new Error("Not implemented");
  },

  async listSessions(projectId?: string): Promise<ChatSession[]> {
    // TODO: implement — GET /api/v1/chat/sessions
    throw new Error("Not implemented");
  },

  async sendMessage(
    sessionId: string,
    content: string
  ): Promise<{ message_id: string; stream_url: string }> {
    // TODO: implement — POST /api/v1/chat/sessions/{sessionId}/messages
    throw new Error("Not implemented");
  },

  async getMessages(sessionId: string): Promise<ChatMessage[]> {
    // TODO: implement — GET /api/v1/chat/sessions/{sessionId}/messages
    throw new Error("Not implemented");
  },

  streamResponse(
    messageId: string,
    onToken: (token: string) => void,
    onDone: (sources: StreamEvent & { type: "done" }) => void,
    onError: (detail: string) => void
  ): WebSocket {
    // TODO: implement — open WebSocket to /api/v1/chat/stream/{messageId}
    // Parse StreamEvent JSON and dispatch to callbacks
    throw new Error("Not implemented");
  },
};
