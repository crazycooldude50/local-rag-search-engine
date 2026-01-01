import { useState } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! I've read your document. Ask me anything." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. Add User Message to UI
    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // 2. Send to Backend
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.text }),
      });

      const data = await response.json();

      // 3. Add Bot Response to UI
      const botMessage = { 
        role: "bot", 
        text: data.answer, 
        sources: data.sources 
      };
      setMessages((prev) => [...prev, botMessage]);
    
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { role: "bot", text: "Error connecting to server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-4">
      {/* Header */}
      <div className="w-full max-w-2xl flex items-center gap-3 mb-6 mt-4">
        <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
          <Bot className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Local RAG Search</h1>
      </div>

      {/* Chat Container */}
      <div className="flex-1 w-full max-w-2xl bg-gray-800 rounded-2xl shadow-xl overflow-hidden flex flex-col border border-gray-700">
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === "user" ? "bg-purple-600" : "bg-blue-600"
              }`}>
                {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>

              {/* Bubble */}
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                msg.role === "user" 
                  ? "bg-purple-600 text-white rounded-br-none" 
                  : "bg-gray-700 text-gray-100 rounded-bl-none"
              }`}>
                <p className="leading-relaxed">{msg.text}</p>
                
                {/* Sources (Bot only) */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-600 text-xs text-gray-400">
                    <p className="font-semibold mb-1">Sources:</p>
                    {msg.sources.map((src, i) => (
                      <div key={i} className="bg-gray-800 px-2 py-1 rounded mb-1 inline-block mr-2">
                        Page {src.page_label || src.page || "?"}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Loader2 className="animate-spin" size={16} />
              </div>
              <div className="bg-gray-700 px-5 py-3 rounded-2xl rounded-bl-none text-gray-400 animate-pulse">
                Thinking...
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-800 border-t border-gray-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask a question about your document..."
              className="flex-1 bg-gray-900 border border-gray-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}