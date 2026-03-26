import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, X, User, Bot } from 'lucide-react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef(null);
  const chatRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatRef.current && !chatRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleTouchOutside = (event) => {
      if (chatRef.current && !chatRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('touchstart', handleTouchOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleTouchOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleTouchOutside);
    };
  }, [isOpen]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const apiBase = (process.env.REACT_APP_API_URL || '').replace(/\/$/, '');
      const response = await fetch(`${apiBase}/api/chat`, {
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

  if (!isOpen) {
    return (
      <button 
        className="chat-toggle" 
        onClick={() => setIsOpen(true)}
        title="Abrir chat"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className="chat-wrapper" ref={chatRef}>
      <div className="chat-container">
        <div className="chat-header">
          Assistente Virtual - Lucas Rodrigues
          <button 
            className="chat-toggle hidden" 
            onClick={() => setIsOpen(false)}
            title="Fechar chat"
          >
            <X size={20} />
          </button>
        </div>
        <div className="chat-messages-area" ref={scrollRef}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
              Olá! Sou o assistente virtual do Lucas. Como posso ajudar?
            </div>
          )}
          {messages.map((message, index) => (
            <div key={index} className={`msg-row ${message.role}`}>
              <div className="bubble">
                {message.role === 'user' && <User size={16} />}
                {message.role === 'bot' && <Bot size={16} />}
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="msg-row bot">
              <div className="bubble">
                <Bot size={16} />
                Digitando...
              </div>
            </div>
          )}
        </div>
        <form className="chat-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;