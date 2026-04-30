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
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [session, setSession] = useState<ChatSession | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sources, setSources] = useState<SourceCitation[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const startSession = useCallback(async (projectId: string) => {
    const newSession = await chatService.createSession(projectId);
    setSession(newSession);
    setMessages([]);
    setSources([]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!session || isStreaming) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      session_id: session.id,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setSources([]);

    const assistantId = crypto.randomUUID();
    const assistantMsg: ChatMessage = {
      id: assistantId,
      session_id: session.id,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const { message_id } = await chatService.sendMessage(session.id, content);

      wsRef.current?.close();
      const ws = chatService.streamResponse(
        message_id,
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m
            )
          );
        },
        (doneEvent) => {
          setSources(doneEvent.sources);
          setIsStreaming(false);
          ws.close();
        },
        (detail) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: `Error: ${detail}` } : m
            )
          );
          setIsStreaming(false);
        }
      );
      wsRef.current = ws;
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== assistantId));
      setIsStreaming(false);
    }
  }, [session, isStreaming]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSources([]);
  }, []);

  return { messages, session, isStreaming, sources, sendMessage, startSession, clearMessages };
}
