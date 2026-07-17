import { useState, useEffect, useRef } from "react";
import { SESSION_STORAGE_KEY, CHAT_TOPIC_STORAGE_KEY } from "../constants/storage";
import { sendChatMessage } from "../services/chatApi";

const TOPIC_GREETINGS = {
  whamais:
    "Perfeito! Posso te contar sobre a Whamais — soluções de comunicação com IA, WhatsApp, voz e agendamentos. O que você gostaria de saber?",
  lucas:
    "Certo! Posso falar sobre Lucas Rodrigues — trajetória, skills e projetos. O que você quer saber?",
};

export const useChat = () => {
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

  const selectTopic = (nextTopic) => {
    setTopic(nextTopic);
    sessionStorage.setItem(CHAT_TOPIC_STORAGE_KEY, nextTopic);
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        content: TOPIC_GREETINGS[nextTopic],
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
      const data = await sendChatMessage({ pergunta: text, sessionId, topico: topic });
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
          { id: Date.now() + 1, role: "bot", content: `Erro: ${data.mensagem}` },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "bot", content: "Erro ao conectar com o servidor." },
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
