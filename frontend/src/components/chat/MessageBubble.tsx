import type { ChatMessage } from "../../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 12,
      }}
    >
      <div
        style={{
          maxWidth: "72%",
          padding: "10px 14px",
          borderRadius: 12,
          background: isUser ? "#0066cc" : "#f0f0f0",
          color: isUser ? "#fff" : "#222",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          fontSize: 14,
          lineHeight: 1.5,
        }}
      >
        {message.content || <span style={{ opacity: 0.4 }}>▋</span>}
      </div>
    </div>
  );
}
