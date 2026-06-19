import emailjs from "@emailjs/browser";

const getConfig = () => ({
  serviceId: process.env.REACT_APP_EMAILJS_SERVICE_ID,
  templateId: process.env.REACT_APP_EMAILJS_TEMPLATE_ID,
  publicKey: process.env.REACT_APP_EMAILJS_USER_ID,
});

export const sendContactEmail = async ({ from_name, reply_to, message }) => {
  const { serviceId, templateId, publicKey } = getConfig();

  if (!serviceId || !templateId || !publicKey) {
    throw new Error(
      "Configuração EmailJS incompleta. Verifique frontend/.env e faça rebuild do web.",
    );
  }

  emailjs.init(publicKey);

  return emailjs.send(serviceId, templateId, {
    from_name,
    reply_to,
    message,
  });
};
