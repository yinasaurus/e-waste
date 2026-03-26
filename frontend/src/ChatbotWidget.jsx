import React, { useState, useRef, useEffect } from 'react';
import { Send, Minus, ChevronDown } from 'lucide-react';
import { API_BASE } from './config';
import './ChatbotWidget.css';

const RESULT_KEYS = [
  'laptops',
  'keyboards',
  'phones',
  'ipads',
  'desktop_cpu',
  'desktop_ram',
  'desktop_storage',
  'desktop_gpu',
];

function hasRecommendations(data) {
  if (!data) return false;
  return RESULT_KEYS.some((k) => Array.isArray(data[k]) && data[k].length > 0);
}

function buildSummaryIntro(data) {
  const s = data.summary || {};
  const parts = [];
  if (s.job_label) parts.push(s.job_label);
  if (s.quantity != null && s.quantity !== '') {
    parts.push(`Qty: ${s.quantity}`);
  }
  if (s.budget != null && s.budget !== '') {
    parts.push(`Budget cap: S$${s.budget}`);
  }
  const head = parts.length ? parts.join(' · ') : 'General use';
  return `Here are some picks for ${head}. “Used” is a rough second-hand guide (~⅔ of new).`;
}

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      type: 'primary',
      text: `Hi — I'm Chip, your Specs-to-Need assistant. Say what you need and a budget (e.g. "gaming laptop under 2000" or "office desktop 3500").`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const handleSend = async (textToQuery = query) => {
    if (!textToQuery.trim()) return;

    const newQueryText = textToQuery.trim();
    setQuery('');
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: newQueryText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: newQueryText }),
      });

      let data = {};
      try {
        data = await response.json();
      } catch {
        data = {};
      }

      let botResponseText = '';
      let botContentData = null;
      let preformatted = false;

      if (!response.ok) {
        botResponseText =
          data.error ||
          data.message ||
          `Request failed (${response.status}). Check that the Flask app is running on ${API_BASE}.`;
      } else if (data.summary?.info) {
        botResponseText = data.summary.info;
        preformatted = true;
      } else if (data.summary?.error) {
        botResponseText = data.summary.error;
      } else if (!hasRecommendations(data)) {
        botResponseText =
          'No matching rows for this query. Try naming a device type (laptop, desktop, phone, iPad, keyboard) and a budget, e.g. “student laptop under 1200”.';
      } else {
        botResponseText = buildSummaryIntro(data);
        botContentData = data;
      }

      // Add a 2-3 second delay to simulate bot processing
      const delayMs = Math.floor(Math.random() * 1000) + 2000;
      await new Promise(resolve => setTimeout(resolve, delayMs));

      setMessages((prev) => {
        const botMsg = {
          id: Date.now() + 1,
          sender: 'bot',
          type: prev.length % 2 === 0 ? 'primary' : 'secondary',
          text: botResponseText,
          data: botContentData,
          preformatted,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        return [...prev, botMsg];
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          type: 'secondary',
          text: `Sorry — I could not reach the server. Is the Python backend running at ${API_BASE}?`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderDataTables = (data) => {
    if (!data) return null;
    const maxRows = 5;
    return (
      <div className="message-tables">
        {data.laptops && data.laptops.length > 0 && (
          <div className="message-table-section">
            <strong className="message-table-title">Laptops</strong>
            <table className="message-table">
              <thead>
                <tr>
                  <th>Brand / model</th>
                  <th>New</th>
                  <th>Used</th>
                </tr>
              </thead>
              <tbody>
                {data.laptops.slice(0, maxRows).map((l, i) => (
                  <tr key={i}>
                    <td>
                      {l.brand} {l.model}
                    </td>
                    <td>S${Math.round(l.new)}</td>
                    <td>S${Math.round(l.used)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.desktop_cpu &&
          (data.desktop_cpu.length > 0 ||
            (data.desktop_ram && data.desktop_ram.length > 0) ||
            (data.desktop_storage && data.desktop_storage.length > 0) ||
            (data.desktop_gpu && data.desktop_gpu.length > 0)) && (
            <div className="message-table-section">
              <strong className="message-table-title">Desktop parts</strong>
              <table className="message-table">
                <thead>
                  <tr>
                    <th>Part</th>
                    <th>New</th>
                    <th>Used</th>
                  </tr>
                </thead>
                <tbody>
                  {data.desktop_cpu?.slice(0, 1).map((c, i) => (
                    <tr key={`cpu${i}`}>
                      <td>
                        CPU: {c.brand} {c.item}
                      </td>
                      <td>S${Math.round(c.new)}</td>
                      <td>S${Math.round(c.used)}</td>
                    </tr>
                  ))}
                  {data.desktop_ram?.slice(0, 1).map((r, i) => (
                    <tr key={`ram${i}`}>
                      <td>RAM: {r.ram_gb} GB</td>
                      <td>S${Math.round(r.new)}</td>
                      <td>S${Math.round(r.used)}</td>
                    </tr>
                  ))}
                  {data.desktop_storage?.slice(0, 1).map((s, i) => (
                    <tr key={`st${i}`}>
                      <td>
                        Storage: {s.storage_gb} GB ({s.storage_type})
                      </td>
                      <td>S${Math.round(s.new)}</td>
                      <td>S${Math.round(s.used)}</td>
                    </tr>
                  ))}
                  {data.desktop_gpu?.slice(0, 1).map((g, i) => (
                    <tr key={`gpu${i}`}>
                      <td>
                        GPU: {g.brand} {g.item}
                      </td>
                      <td>S${Math.round(g.new)}</td>
                      <td>S${Math.round(g.used)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        {data.keyboards && data.keyboards.length > 0 && (
          <div className="message-table-section">
            <strong className="message-table-title">Keyboards</strong>
            <table className="message-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>New</th>
                  <th>Used</th>
                </tr>
              </thead>
              <tbody>
                {data.keyboards.slice(0, maxRows).map((k, i) => (
                  <tr key={i}>
                    <td>
                      {k.name}
                      {k.connection ? ` (${k.connection})` : ''}
                    </td>
                    <td>S${Math.round(k.new)}</td>
                    <td>S${Math.round(k.used)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.ipads && data.ipads.length > 0 && (
          <div className="message-table-section">
            <strong className="message-table-title">Tablets</strong>
            <table className="message-table">
              <thead>
                <tr>
                  <th>Model / storage</th>
                  <th>New</th>
                  <th>Used</th>
                </tr>
              </thead>
              <tbody>
                {data.ipads.slice(0, maxRows).map((p, i) => (
                  <tr key={i}>
                    <td>
                      {p.model} {p.storage}
                    </td>
                    <td>S${Math.round(p.new)}</td>
                    <td>S${Math.round(p.used)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.phones && data.phones.length > 0 && (
          <div className="message-table-section">
            <strong className="message-table-title">Phones</strong>
            <table className="message-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>New</th>
                  <th>Used</th>
                </tr>
              </thead>
              <tbody>
                {data.phones.slice(0, maxRows).map((p, i) => (
                  <tr key={i}>
                    <td>
                      {p.brand} {p.model}
                    </td>
                    <td>S${Math.round(p.new)}</td>
                    <td>S${Math.round(p.used)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const bubbleStyle = (msg) => {
    if (msg.sender === 'user') {
      return {
        backgroundColor: '#e0e0e0',
        color: '#333',
        padding: '12px 16px',
        borderRadius: '12px 12px 0 12px',
        fontSize: 14,
        whiteSpace: 'pre-wrap',
        overflowWrap: 'anywhere',
        wordBreak: 'break-word',
      };
    }
    const base = {
      color: 'white',
      padding: '12px 16px',
      borderRadius: '12px 12px 12px 0',
      fontSize: 14,
      whiteSpace: msg.preformatted ? 'pre-wrap' : 'normal',
      overflowWrap: 'anywhere',
      wordBreak: 'break-word',
    };
    if (msg.type === 'primary') {
      return { ...base, backgroundColor: '#3b0764' };
    }
    return { ...base, backgroundColor: '#e5e7eb', color: '#1f2937' };
  };

  return (
    <div className="chatbot-widget-container">
      {isOpen ? (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <div className="chatbot-avatar">
                <span>
                  <img src="img/chipcycle logo.png" alt="" />
                </span>
              </div>
              <div className="chatbot-title">
                <span className="chatbot-name">Ask Chip</span>
                <span className="chatbot-status">
                  <span className="status-dot" /> Online
                </span>
              </div>
            </div>
            <button
              type="button"
              className="chatbot-close-btn"
              aria-label="Close chat"
              onClick={() => setIsOpen(false)}
            >
              <Minus className="chatbot-close" size={24} />
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-row ${msg.sender}`}>
                {msg.sender === 'bot' ? (
                  <div className="message-avatar bot">
                    <span>
                      <img src="img/chipcycle logo.png" alt="" />
                    </span>
                  </div>
                ) : (
                  <div className="message-avatar user-avatar" aria-hidden>
                    <span style={{ fontSize: 20 }}>👤</span>
                  </div>
                )}

                <div className="message-body">
                  <div style={bubbleStyle(msg)}>
                    {msg.text}
                    {msg.data && renderDataTables(msg.data)}
                  </div>
                  <div
                    className="message-time"
                    style={msg.sender === 'user' ? { justifyContent: 'flex-end' } : {}}
                  >
                    {msg.time}{' '}
                    {msg.sender === 'user' && (
                      <span style={{ color: '#9d4edd', marginLeft: 2 }}>✔</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-row bot">
                <div className="message-avatar bot">
                  <span>
                    <img src="img/chipcycle logo.png" alt="" />
                  </span>
                </div>
                <div
                  style={{
                    backgroundColor: '#e5e7eb',
                    padding: '12px',
                    borderRadius: '12px 12px 12px 0',
                  }}
                >
                  <div className="chat-loading">
                    <div className="chat-loading-dot" />
                    <div className="chat-loading-dot" />
                    <div className="chat-loading-dot" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-quick-actions">
            <button
              type="button"
              className="chatbot-quick-action"
              onClick={() => handleSend('What is Specs-to-Need?')}
            >
              What is Specs-to-Need?
            </button>
            <button
              type="button"
              className="chatbot-quick-action"
              onClick={() => handleSend('Gaming desktop under 2500')}
            >
              Gaming desktop
            </button>
            <button
              type="button"
              className="chatbot-quick-action"
              onClick={() => handleSend('Student iPad under 1200')}
            >
              Student iPad
            </button>
          </div>

          <div className="chatbot-input-area">
            <div className="chatbot-input-container">
              <textarea
                ref={inputRef}
                className="chatbot-input"
                placeholder="What do you need? (device + budget)"
                value={query}
                onChange={handleInputChange}
                aria-label="Message to Chip"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
              />
              <button type="button" className="chatbot-send-btn" aria-label="Send" onClick={() => handleSend()}>
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <button
        type="button"
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label={isOpen ? "Close Ask Chip" : "Open Ask Chip"}
      >
        {!isOpen && <div className="chatbot-hover-pill">Ask Chip!</div>}
        <span>
          {isOpen ? <ChevronDown size={36} color="white" /> : <img src="img/chipcycle logo.png" alt="" />}
        </span>
      </button>
    </div>
  );
}
