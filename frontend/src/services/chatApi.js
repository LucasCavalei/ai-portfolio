const getApiBase = () =>
  (process.env.REACT_APP_API_URL || "").replace(/\/$/, "");

export const sendChatMessage = async ({ pergunta, sessionId }) => {
  const payload = { pergunta };
  if (sessionId) {
    payload.session_id = sessionId;
  }

  const response = await fetch(`${getApiBase()}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
};
