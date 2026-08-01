import React from "react";
import { Send, MessageCircle, X, User, Bot } from "lucide-react";
import { useChat } from "../../hooks/useChat";
import { useLanguage } from "../i18n/LanguageProvider";
import "./Chat.css";

export const Chat = () => {
  const { t } = useLanguage();
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
        title={t("chat.open")}
        aria-label={t("chat.openAria")}
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  const headerTitle =
    topic === "lucas"
      ? t("chat.titleLucas")
      : topic === "whamais"
        ? t("chat.titleWhamais")
        : t("chat.title");

  return (
    <div className="chat-wrapper" ref={chatRef}>
      <div className="chat-container">
        <div className="chat-header">
          <span>{headerTitle}</span>
          <button
            className="chat-close"
            onClick={() => setIsOpen(false)}
            title={t("chat.close")}
            aria-label={t("chat.close")}
          >
            <X size={20} />
          </button>
        </div>
        <div className="chat-messages-area" ref={scrollRef}>
          {!topic && (
            <div className="chat-topic-picker">
              <p className="chat-topic-picker__intro">
                {(() => {
                  const intro = t("chat.intro", { brand: "Whamais" });
                  const parts = intro.split("Whamais");
                  if (parts.length < 2) return intro;
                  return (
                    <>
                      {parts[0]}
                      <strong>Whamais</strong>
                      {parts.slice(1).join("Whamais")}
                    </>
                  );
                })()}
                <br />
                {t("chat.introAsk")}
              </p>
              <div className="chat-topic-picker__actions">
                <button
                  type="button"
                  className="chat-topic-btn chat-topic-btn--primary"
                  onClick={() => selectTopic("whamais")}
                >
                  {t("chat.topicWhamais")}
                </button>
                <button
                  type="button"
                  className="chat-topic-btn"
                  onClick={() => selectTopic("lucas")}
                >
                  {t("chat.topicLucas")}
                </button>
              </div>
            </div>
          )}

          {topic && (
            <button type="button" className="chat-topic-switch" onClick={resetTopic}>
              {t("chat.switchTopic")}
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
                {t("chat.typing")}
              </div>
            </div>
          )}
        </div>
        <form className="chat-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={topic ? t("chat.placeholder") : t("chat.placeholderNoTopic")}
            disabled={isLoading || !topic}
            aria-label={t("chat.inputAria")}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !topic}
            aria-label={t("chat.sendAria")}
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
