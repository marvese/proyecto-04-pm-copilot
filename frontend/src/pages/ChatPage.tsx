import React from "react";
import { ChatWindow } from "../components/chat/ChatWindow";
import { useCopilotChat } from "../hooks/useCopilotChat";
import { useProjectContext } from "../hooks/useProjectContext";

export function ChatPage() {
  // TODO: implement
  // - useCopilotChat() + useProjectContext()
  // - Start session on project load
  // - Render ChatWindow with messages and sendMessage handler
  return (
    <div className="chat-page">
      <h1>Copilot Chat</h1>
      <p>TODO: implement ChatPage</p>
    </div>
  );
}
