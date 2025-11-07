import { useState } from "react";
import "./index.css";
import ChatBubble from "./ChatBubble";

function App() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [stage, setStage] = useState(1);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMsg = { role: "user", content: message };
    setHistory((prev) => [...prev, userMsg]);

    const resp = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        history: history,
        stage: stage,
      }),
    });

    const data = await resp.json();

    setHistory([
      ...history,
      userMsg,
      { role: "assistant", content: data.reply },
    ]);
    setStage(data.stage);
    setMessage("");
  };

  return (
    <div className="app-container">
      <div className="chat-window">
        {history.map((m, i) => (
          <ChatBubble key={i} role={m.role} content={m.content} />
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          placeholder="Describe your symptoms…"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
