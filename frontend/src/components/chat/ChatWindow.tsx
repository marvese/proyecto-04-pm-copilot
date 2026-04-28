import React from "react";
import type { ChatMessage } from "../../types/chat";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";

interface ChatWindowProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingToken: string;
  onSend: (content: string) => void;
}

export function ChatWindow({ messages, isStreaming, streamingToken, onSend }: ChatWindowProps) {
  // TODO: implement
  // - Scrollable message list
  // - Auto-scroll to bottom on new messages
  // - Streaming indicator while isStreaming
  return <div className="chat-window">TODO: ChatWindow</div>;
}
