import React, { useState, useRef, useEffect } from 'react';
import { Send, ChevronDown, Minus } from 'lucide-react';
import './ChatbotWidget.css';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Initial bot message
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      type: 'primary',
      text: 'Hi there! I am Chip, your Specs-to-Need Assistant. Tell me what you need and your budget (e.g. "gaming desktop under 2500" or "ipad for student with keyboard")!',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToQuery = query) => {
    if (!textToQuery.trim()) return;

    const newQueryText = textToQuery.trim();
    setQuery('');
    
    // Add user message
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: newQueryText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: newQueryText })
      });
      
      const data = await response.json();
      
      let botResponseText = '';
      let botContentData = null;

      if (data.summary?.error) {
        botResponseText = data.summary.error;
      } else if (!data.laptops?.length && !data.desktop_cpu?.length && !data.keyboards?.length && !data.phones?.length && !data.ipads?.length) {
        botResponseText = "No matching devices found for this query.";
      } else {
        botResponseText = `Here are some recommendations for ${data.summary.job_label || 'General Use'}. Budget: ${data.summary.budget ? 'S$' + data.summary.budget : 'N/A'}`;
        botContentData = data; // store full data to render tables
      }

      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        type: messages.length % 2 === 0 ? 'primary' : 'secondary',
        text: botResponseText,
        data: botContentData,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        type: 'secondary',
        text: 'Sorry, I am having trouble connecting to the server. Is the Python backend running?',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderDataTables = (data) => {
    if (!data) return null;
    return (
      <div style={{ marginTop: 10 }}>
        {data.laptops && data.laptops.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            <strong style={{ fontSize: 13, color: '#ff9100' }}>Laptops</strong>
            <table className="message-table">
              <thead><tr><th>Brand/Model</th><th>New</th><th>Used</th></tr></thead>
              <tbody>
                {data.laptops.slice(0, 3).map((l, i) => (
                  <tr key={i}><td>{l.brand} {l.model}</td><td>S${Math.round(l.new)}</td><td>S${Math.round(l.used)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {data.desktop_cpu && data.desktop_cpu.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            <strong style={{ fontSize: 13, color: '#ff9100' }}>Desktop Build Parts</strong>
            <table className="message-table">
              <thead><tr><th>Component</th><th>New</th><th>Used</th></tr></thead>
              <tbody>
                {data.desktop_cpu.slice(0, 1).map((c, i) => (
                  <tr key={'cpu'+i}><td>CPU: {c.brand}</td><td>S${Math.round(c.new)}</td><td>S${Math.round(c.used)}</td></tr>
                ))}
                {data.desktop_ram && data.desktop_ram.slice(0, 1).map((r, i) => (
                  <tr key={'ram'+i}><td>RAM: {r.ram_gb}GB</td><td>S${Math.round(r.new)}</td><td>S${Math.round(r.used)}</td></tr>
                ))}
                {data.desktop_storage && data.desktop_storage.slice(0, 1).map((s, i) => (
                  <tr key={'storage'+i}><td>Storage: {s.storage_gb}GB</td><td>S${Math.round(s.new)}</td><td>S${Math.round(s.used)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.ipads && data.ipads.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            <strong style={{ fontSize: 13, color: '#ff9100' }}>Tablets</strong>
            <table className="message-table">
              <thead><tr><th>Model/Storage</th><th>New</th><th>Used</th></tr></thead>
              <tbody>
                {data.ipads.slice(0, 3).map((p, i) => (
                  <tr key={i}><td>{p.model} {p.storage}</td><td>S${Math.round(p.new)}</td><td>S${Math.round(p.used)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data.phones && data.phones.length > 0 && (
           <div style={{ marginBottom: 10 }}>
            <strong style={{ fontSize: 13, color: '#ff9100' }}>Phones</strong>
            <table className="message-table">
              <thead><tr><th>Model</th><th>New</th><th>Used</th></tr></thead>
              <tbody>
                {data.phones.slice(0, 3).map((p, i) => (
                  <tr key={i}><td>{p.brand} {p.model}</td><td>S${Math.round(p.new)}</td><td>S${Math.round(p.used)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="chatbot-widget-container">
      {isOpen ? (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <div className="chatbot-avatar">
                {/* Fallback to simple icon since img path may vary */}
                <span><img src="img/chipcycle logo.png" alt="logo"/></span>
              </div>
              <div className="chatbot-title">
                <span className="chatbot-name">Ask Chip</span>
                <span className="chatbot-status">
                  <span className="status-dot"></span> Online
                </span>
              </div>
            </div>
            <Minus className="chatbot-close" size={24} onClick={() => setIsOpen(false)} />
          </div>

          {/* Chat Messages */}
          <div className="chatbot-messages">
            {messages.map((msg, index) => (
              <div key={msg.id} className={`message-row ${msg.sender}`}>
                {msg.sender === 'bot' ? (
                  <div className="message-avatar bot">
                    <span><img src="img/chipcycle logo.png" alt="logo"/></span>
                  </div>
                ) : (
                  <div className="message-avatar" style={{backgroundColor: '#e1e1e1'}}>
                     <span role="img" aria-label="User" style={{ fontSize: 20 }}>👤</span>
                  </div>
                )}
                
                <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '85%' }}>
                   <div style={
                     msg.sender === 'user' 
                     ? { backgroundColor: '#f1f1f1', color: '#333', padding: '12px 16px', borderRadius: '12px 12px 0 12px', fontSize: 14 }
                     : msg.type === 'primary' 
                       ? { backgroundColor: '#3b0764', color: 'white', padding: '12px 16px', borderRadius: '12px 12px 12px 0', fontSize: 14 }
                       : { backgroundColor: '#e5e7eb', color: '#1f2937', padding: '12px 16px', borderRadius: '12px 12px 12px 0', fontSize: 14 }
                   }>
                     {msg.text}
                     {msg.data && renderDataTables(msg.data)}
                   </div>
                   <div className="message-time" style={msg.sender === 'user' ? { justifyContent: 'flex-end'} : {}}>
                     {msg.time} {msg.sender === 'user' && <span style={{color: '#9d4edd', marginLeft: 2}}>✔</span>}
                   </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-row bot">
                 <div className="message-avatar bot">
                    <span><img src="img/chipcycle logo.png" alt="logo"/></span>
                  </div>
                 <div style={{ backgroundColor: '#e5e7eb', padding: '12px', borderRadius: '12px 12px 12px 0' }}>
                   <div className="chat-loading">
                    <div className="chat-loading-dot"></div>
                    <div className="chat-loading-dot"></div>
                    <div className="chat-loading-dot"></div>
                   </div>
                 </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          {/* Quick Actions (Mock-like) */}
          <div className="chatbot-quick-actions">
            <button className="chatbot-quick-action" onClick={() => handleSend('🤔 What is Specs-to-Need?')}>
              🤔 What is Specs-to-Need?
            </button>
            <button className="chatbot-quick-action" onClick={() => handleSend('💻 Need a Gaming Desktop')}>
              💻 Gaming Desktop
            </button>
            <button className="chatbot-quick-action" onClick={() => handleSend('🙋 Student iPad Recommendations')}>
              🙋 Student Recommendations
            </button>
          </div>
          
          {/* Input Area */}
          <div className="chatbot-input-area">
            <div className="chatbot-input-container">
              <input 
                type="text" 
                className="chatbot-input" 
                placeholder="Type your message here..." 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend();
                }}
              />
              <button className="chatbot-send-btn" onClick={() => handleSend()}>
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {/* Floating Toggle Button */}
      <div className="chatbot-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? (
          <ChevronDown color="white" size={32} />
        ) : (
          <>
             <div className="chatbot-hover-pill">Ask Chip!</div>
             <span><img src="img/chipcycle logo.png" alt="logo"/></span>
          </>
        )}
      </div>
    </div>
  );
}
