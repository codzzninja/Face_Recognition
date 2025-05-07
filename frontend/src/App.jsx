import React, { useState } from "react";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Recognize from "./components/Recognize"; // ✅ Import Recognize component

function App() {
  const [tab, setTab] = useState("register");

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Face Recognition + RAG Q&A</h1>
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={() => setTab("register")}>Register</button>
        <button onClick={() => setTab("recognize")}>Recognize</button> {/* ✅ Add Recognize button */}
        <button onClick={() => setTab("chat")}>Q&A</button>
      </div>
      <div style={{ marginTop: "2rem" }}>
        {tab === "register" && <Register />}
        {tab === "recognize" && <Recognize />} {/* ✅ Render Recognize when selected */}
        {tab === "chat" && <Chat />}
      </div>
    </div>
  );
}

export default App;
