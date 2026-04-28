import React from "react";
import type { ChatMessage } from "../../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  // TODO: implement
  // - Different style for user vs assistant
  // - Render assistant content as Markdown
  // - Show source citations if present
  return <div className={`bubble bubble--${message.role}`}>{message.content}</div>;
}
