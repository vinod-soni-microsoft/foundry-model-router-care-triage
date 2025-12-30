import React, { useState, useRef, useEffect } from 'react';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  telemetry?: Telemetry;
  citations?: Record<string, Citation>;
  warning?: string;
}

interface Telemetry {
  intent: string;
  routing_mode: string;
  model_chosen: string;
  tokens: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  latency_ms: number;
  rationale: string;
}

interface Citation {
  title: string;
  source: string;
  category: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<'balanced' | 'cost' | 'quality'>('balanced');
  const [image, setImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showTelemetry, setShowTelemetry] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const sendMessage = async () => {
    if (!input.trim() && !image) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          mode: mode,
          image: image,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        telemetry: data.telemetry,
        citations: data.citations,
        warning: data.warning,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏥 Care Triage Assistant</h1>
        <p className="disclaimer">
          ⚠️ <strong>Demo Only:</strong> This is a non-diagnostic demonstration tool. Not for actual medical advice or diagnosis.
        </p>
      </header>

      <div className="controls">
        <label>
          Routing Mode:
          <select value={mode} onChange={(e) => setMode(e.target.value as any)}>
            <option value="balanced">⚖️ Balanced</option>
            <option value="cost">�� Cost Optimized</option>
            <option value="quality">⭐ Quality Optimized</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={showTelemetry}
            onChange={(e) => setShowTelemetry(e.target.checked)}
          />
          Show Telemetry
        </label>
      </div>

      <div className="chat-container">
        <div className="chat-column">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome">
                <img 
                  src="/src/image/Designer (7).png" 
                  alt="Healthcare Professional" 
                  className="welcome-image"
                />
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-content">
                  <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong>
                  <div className="text">{msg.content}</div>
                  {msg.warning && (
                    <div className="warning">{msg.warning}</div>
                  )}
                  {msg.citations && Object.keys(msg.citations).length > 0 && (
                    <div className="citations">
                      <strong>📚 Sources:</strong>
                      {Object.entries(msg.citations).map(([num, citation]) => (
                        <div key={num} className="citation">
                          [{num}] {citation.title} ({citation.category})
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                {showTelemetry && msg.telemetry && (
                  <div className="telemetry">
                    <details>
                      <summary>📊 Telemetry</summary>
                      <div className="telemetry-grid">
                        <div>
                          <strong>Intent:</strong> {msg.telemetry.intent}
                        </div>
                        <div>
                          <strong>Model:</strong> {msg.telemetry.model_chosen}
                        </div>
                        <div>
                          <strong>Tokens:</strong> {msg.telemetry.tokens.total_tokens}
                        </div>
                        <div>
                          <strong>Latency:</strong> {msg.telemetry.latency_ms.toFixed(0)}ms
                        </div>
                        <div className="rationale">
                          <strong>Rationale:</strong> {msg.telemetry.rationale}
                        </div>
                      </div>
                    </details>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="message assistant loading">
                <div className="message-content">
                  <strong>Assistant:</strong>
                  <div className="text">Thinking...</div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="sidebar">
          <div className="suggestions-card">
            <h3>💡 Try asking about</h3>
            <ul>
              <li>📋 Administrative tasks (appointments, billing)</li>
              <li>🩺 Clinical information (symptoms, conditions)</li>
              <li>🖼️ Medical images (upload for analysis)</li>
            </ul>
          </div>

          <div className="input-container">
            <h3>💬 Your Message</h3>
            {image && (
              <div className="image-preview">
                <img src={image} alt="Preview" />
                <button onClick={removeImage} className="remove-image">
                  ✕
                </button>
              </div>
            )}
            <div className="input-row">
              <input
                type="file"
                ref={fileInputRef}
                accept="image/*"
                onChange={handleImageUpload}
                style={{ display: 'none' }}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="upload-btn"
                title="Upload image"
              >
                🖼️ Upload Image
              </button>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about appointments, symptoms, or upload an image..."
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || (!input.trim() && !image)}
                className="send-btn"
              >
                {isLoading ? 'Sending...' : 'Send Message'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
