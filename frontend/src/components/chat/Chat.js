import React from "react";
import { Send, MessageCircle, X, User, Bot } from "lucide-react";
import { useChat } from "../../hooks/useChat";
import "./Chat.css";

export const Chat = () => {
  const {
    messages,
    input,
    setInput,
    isLoading,
    isOpen,
    setIsOpen,
    scrollRef,
    chatRef,
    sendMessage,
  } = useChat();

  if (!isOpen) {
    return (
      <button
        className="chat-toggle"
        onClick={() => setIsOpen(true)}
        title="Abrir chat"
        aria-label="Abrir assistente virtual"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className="chat-wrapper" ref={chatRef}>
      <div className="chat-container">
        <div className="chat-header">
          <span>Assistente Virtual — Lucas Rodrigues</span>
          <button
            className="chat-close"
            onClick={() => setIsOpen(false)}
            title="Fechar chat"
            aria-label="Fechar chat"
          >
            <X size={20} />
          </button>
        </div>
        <div className="chat-messages-area" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="chat-empty">
              Olá! Sou o assistente virtual do Lucas. Como posso ajudar?
            </div>
          )}
          {messages.map((message) => (
            <div key={message.id} className={`msg-row ${message.role}`}>
              <div className="bubble">
                {message.role === "user" ? <User size={16} /> : <Bot size={16} />}
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
            aria-label="Mensagem do chat"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            aria-label="Enviar mensagem"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
