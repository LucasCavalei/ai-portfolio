import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot } from 'lucide-react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta: input }),
      });
      const data = await response.json();
      if (data.status === 'sucesso') {
        setMessages((prev) => [...prev, { role: 'bot', content: data.resposta }]);
      } else {
        setMessages((prev) => [...prev, { role: 'bot', content: 'Erro: ' + data.mensagem }]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'Erro ao conectar com o servidor.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        <div className="chat-header">
          Assistente de Suporte Técnico
        </div>

        <div ref={scrollRef} className="chat-messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`msg-row ${msg.role}`}>
              <div className="bubble">
                {msg.role === 'bot' ? <Bot size={8} /> : <User size={18} />}
                <span>{msg.content}</span>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="msg-row bot">
              <div className="bubble">Digitando...</div>
            </div>
          )}
        </div>

        <form onSubmit={sendMessage} className="chat-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua dúvida..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;