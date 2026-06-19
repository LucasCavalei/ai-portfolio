import { useState, useEffect, useRef } from "react";
import { SESSION_STORAGE_KEY } from "../constants/storage";
import { sendChatMessage } from "../services/chatApi";

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState(
    () => sessionStorage.getItem(SESSION_STORAGE_KEY) || null,
  );
  const scrollRef = useRef(null);
  const chatRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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

  const sendMessage = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;

    setMessages((prev) => [...prev, { id: Date.now(), role: "user", content: text }]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendChatMessage({ pergunta: text, sessionId });
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
    scrollRef,
    chatRef,
    sendMessage,
  };
};
