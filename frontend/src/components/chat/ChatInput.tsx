import React, { useState } from "react";

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  // TODO: implement
  // - Textarea with auto-resize
  // - Submit on Enter (Shift+Enter for newline)
  // - Disabled state while streaming
  return <div className="chat-input">TODO: ChatInput</div>;
}
