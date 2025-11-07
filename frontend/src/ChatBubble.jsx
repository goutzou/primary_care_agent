export default function ChatBubble({ role, content }) {
  const isUser = role === "user";
  return (
    <div
      className={isUser ? "user-bubble" : "assistant-bubble"}
      style={{ whiteSpace: "pre-wrap" }} // preserves LLM formatting
    >
      {content}
    </div>
  );
}
