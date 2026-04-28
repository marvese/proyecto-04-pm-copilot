import { useState, useCallback, useRef } from "react";
import type { ChatMessage, ChatSession, SourceCitation } from "../types/chat";
import { chatService } from "../services/chatService";

interface UseCopilotChatReturn {
  messages: ChatMessage[];
  session: ChatSession | null;
  isStreaming: boolean;
  sources: SourceCitation[];
  sendMessage: (content: string) => Promise<void>;
  startSession: (projectId: string) => Promise<void>;
  clearMessages: () => void;
}

export function useCopilotChat(): UseCopilotChatReturn {
  // TODO: implement
  // State: messages, session, isStreaming, sources
  // sendMessage: POST message → open WS → stream tokens → update messages
  // startSession: POST /sessions → set session state
  throw new Error("Not implemented");
}
