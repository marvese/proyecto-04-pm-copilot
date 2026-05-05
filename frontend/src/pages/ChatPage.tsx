import { useState } from "react";
import { ChatWindow } from "../components/chat/ChatWindow";
import { useCopilotChat } from "../hooks/useCopilotChat";

export function ChatPage() {
  const { messages, isStreaming, sendMessage, startSession, session } = useCopilotChat();
  const [projectId, setProjectId] = useState("");
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    const id = projectId.trim();
    if (!id) return;
    setStarting(true);
    setError(null);
    try {
      await startSession(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start session");
    } finally {
      setStarting(false);
    }
  };

  if (!session) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          gap: 16,
          fontFamily: "sans-serif",
        }}
      >
        <h1 style={{ margin: 0, fontSize: 24 }}>PM Copilot Chat</h1>
        <p style={{ margin: 0, color: "#666", fontSize: 14 }}>
          Enter your Project ID to start a chat session
        </p>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleStart()}
            placeholder="Project UUID"
            disabled={starting}
            style={{
              padding: "8px 12px",
              borderRadius: 6,
              border: "1px solid #ccc",
              fontSize: 14,
              width: 280,
            }}
          />
          <button
            onClick={handleStart}
            disabled={starting || !projectId.trim()}
            style={{
              padding: "8px 20px",
              borderRadius: 6,
              border: "none",
              background: starting || !projectId.trim() ? "#b0c8e8" : "#0066cc",
              color: "#fff",
              fontSize: 14,
              cursor: starting || !projectId.trim() ? "not-allowed" : "pointer",
            }}
          >
            {starting ? "Starting…" : "Start Chat"}
          </button>
        </div>
        {error && <p style={{ color: "#cc0000", fontSize: 13 }}>{error}</p>}
      </div>
    );
  }

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", fontFamily: "sans-serif" }}>
      <div
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid #e0e0e0",
          background: "#0066cc",
          color: "#fff",
          fontSize: 16,
          fontWeight: 600,
        }}
      >
        PM Copilot
      </div>
      <div style={{ flex: 1, overflow: "hidden" }}>
        <ChatWindow
          messages={messages}
          isStreaming={isStreaming}
          onSend={sendMessage}
        />
      </div>
    </div>
  );
}
