import React, { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types/chat";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface ChatWindowProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingToken?: string;
  onSend: (content: string) => void;
}

export function ChatWindow({ messages, isStreaming, onSend }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px 16px 8px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              margin: "auto",
              color: "#999",
              fontSize: 14,
              textAlign: "center",
            }}
          >
            Ask anything about your project — tasks, sprint status, blockers…
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isStreaming && (
          <div style={{ paddingLeft: 4, marginBottom: 8 }}>
            <LoadingSpinner size="sm" label="Thinking…" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={onSend} disabled={isStreaming} />
    </div>
  );
}
