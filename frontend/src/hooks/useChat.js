import { useState, useEffect, useRef } from "react";
import { SESSION_STORAGE_KEY, CHAT_TOPIC_STORAGE_KEY } from "../constants/storage";
import { sendChatMessage } from "../services/chatApi";
import { useLanguage } from "../components/i18n/LanguageProvider";

export const useChat = () => {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [topic, setTopic] = useState(
    () => sessionStorage.getItem(CHAT_TOPIC_STORAGE_KEY) || null,
  );
  const [sessionId, setSessionId] = useState(
    () => sessionStorage.getItem(SESSION_STORAGE_KEY) || null,
  );
  const scrollRef = useRef(null);
  const chatRef = useRef(null);
  const prevLanguageRef = useRef(language);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, topic]);

  useEffect(() => {
    const handleOutside = (event) => {
      if (chatRef.current && !chatRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (!isOpen) return undefined;

    document.addEventListener("mousedown", handleOutside);
    document.addEventListener("touchstart", handleOutside);
    return () => {
      document.removeEventListener("mousedown", handleOutside);
      document.removeEventListener("touchstart", handleOutside);
    };
  }, [isOpen]);

  // Ao trocar o idioma, reinicia a conversa para não misturar PT/EN no histórico.
  useEffect(() => {
    if (prevLanguageRef.current === language) return;
    prevLanguageRef.current = language;
    setMessages([]);
    setTopic(null);
    setSessionId(null);
    sessionStorage.removeItem(CHAT_TOPIC_STORAGE_KEY);
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
  }, [language]);

  const selectTopic = (nextTopic) => {
    setTopic(nextTopic);
    sessionStorage.setItem(CHAT_TOPIC_STORAGE_KEY, nextTopic);
    const greetingKey =
      nextTopic === "lucas" ? "chat.greetingLucas" : "chat.greetingWhamais";
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        content: t(greetingKey),
      },
    ]);
  };

  const resetTopic = () => {
    setTopic(null);
    sessionStorage.removeItem(CHAT_TOPIC_STORAGE_KEY);
    setMessages([]);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isLoading || !topic) return;

    setMessages((prev) => [...prev, { id: Date.now(), role: "user", content: text }]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendChatMessage({
        pergunta: text,
        sessionId,
        topico: topic,
        idioma: language,
      });
      if (data.status === "sucesso") {
        if (data.session_id) {
          setSessionId(data.session_id);
          sessionStorage.setItem(SESSION_STORAGE_KEY, data.session_id);
        }
        setMessages((prev) => [
          ...prev,
          { id: Date.now() + 1, role: "bot", content: data.resposta },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "bot",
            content: `${t("chat.errorPrefix")} ${data.mensagem}`,
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "bot", content: t("chat.connectionError") },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return {
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
  };
};
