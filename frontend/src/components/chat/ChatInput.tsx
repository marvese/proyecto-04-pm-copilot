import React, { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled = false, placeholder }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        display: "flex",
        gap: 8,
        padding: "12px 16px",
        borderTop: "1px solid #e0e0e0",
        background: "#fff",
      }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          placeholder ?? "Ask about your project… (Enter to send, Shift+Enter for new line)"
        }
        disabled={disabled}
        rows={1}
        style={{
          flex: 1,
          resize: "none",
          overflow: "hidden",
          minHeight: 38,
          maxHeight: 160,
          padding: "8px 12px",
          borderRadius: 6,
          border: "1px solid #ccc",
          fontSize: 14,
          fontFamily: "inherit",
          outline: "none",
          background: disabled ? "#f5f5f5" : "#fff",
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        style={{
          padding: "8px 20px",
          borderRadius: 6,
          border: "none",
          background: disabled || !value.trim() ? "#b0c8e8" : "#0066cc",
          color: "#fff",
          fontSize: 14,
          cursor: disabled || !value.trim() ? "not-allowed" : "pointer",
          alignSelf: "flex-end",
          height: 38,
        }}
      >
        Send
      </button>
    </div>
  );
}
