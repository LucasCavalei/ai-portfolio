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
    topic,
    selectTopic,
    resetTopic,
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

  const headerTitle = topic === "lucas"
    ? "Assistente — Lucas Rodrigues"
    : topic === "whamais"
      ? "Assistente — Whamais"
      : "Assistente Virtual";

  return (
    <div className="chat-wrapper" ref={chatRef}>
      <div className="chat-container">
        <div className="chat-header">
          <span>{headerTitle}</span>
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
          {!topic && (
            <div className="chat-topic-picker">
              <p className="chat-topic-picker__intro">
                Olá! Sou o assistente da <strong>Whamais</strong>.
                <br />
                Sobre o que você quer conversar?
              </p>
              <div className="chat-topic-picker__actions">
                <button
                  type="button"
                  className="chat-topic-btn chat-topic-btn--primary"
                  onClick={() => selectTopic("whamais")}
                >
                  Conversar sobre a Whamais
                </button>
                <button
                  type="button"
                  className="chat-topic-btn"
                  onClick={() => selectTopic("lucas")}
                >
                  Conversar sobre o Lucas
                </button>
              </div>
            </div>
          )}

          {topic && (
            <button type="button" className="chat-topic-switch" onClick={resetTopic}>
              Trocar assunto
            </button>
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
            placeholder={
              topic
                ? "Digite sua pergunta..."
                : "Escolha um assunto acima para começar"
            }
            disabled={isLoading || !topic}
            aria-label="Mensagem do chat"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !topic}
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
