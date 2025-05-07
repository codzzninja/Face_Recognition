import React, { useState, useRef, useEffect } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null); // Ref for auto-scrolling

  // Scroll to the bottom when new message is added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const question = input;
    setMessages((prev) => [...prev, { sender: "You", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5002/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      if (data.answer) {
        setMessages((prev) => [...prev, { sender: "AI", text: data.answer }]);
      } else if (data.suggestions) {
        setMessages((prev) => [
          ...prev,
          {
            sender: "AI",
            text: `Did you mean: ${data.suggestions.join(", ")}?`,
          },
        ]);
      } else if (data.error) {
        setMessages((prev) => [
          ...prev,
          { sender: "AI", text: `Error: ${data.error}` },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "AI", text: "No response received." },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "AI", text: "Failed to fetch answer." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "auto", padding: "1rem" }}>
      <h2 style={{ textAlign: "center", marginBottom: "1rem" }}>Q&A Chat</h2>
      <div
        style={{
          maxHeight: "300px",
          overflowY: "auto",
          border: "1px solid gray",
          padding: "1rem",
          marginBottom: "1rem",
          backgroundColor: "#f9f9f9",
          borderRadius: "8px",
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.sender === "You" ? "right" : "left",
              marginBottom: "0.5rem",
            }}
          >
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ display: "flex", alignItems: "center" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          style={{
            width: "70%",
            padding: "0.5rem",
            borderRadius: "4px",
            border: "1px solid #ccc",
            marginRight: "10px",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#007BFF",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Loading..." : "Send"}
        </button>
      </div>
    </div>
  );
}
