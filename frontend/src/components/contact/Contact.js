import React, { useState } from "react";
import { TextField, Button, Typography } from "@material-ui/core";
import { Section } from "../../layouts/Section";
import { sendContactEmail } from "../../services/contactApi";
import "./Contact.css";

const INITIAL_FORM = {
  from_name: "",
  reply_to: "",
  message: "",
};

export const Contact = () => {
  const [form, setForm] = useState(INITIAL_FORM);
  const [status, setStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const sendEmail = async (e) => {
    e.preventDefault();
    setStatus("sending");
    setErrorMessage("");

    try {
      await sendContactEmail(form);
      setStatus("success");
      setForm(INITIAL_FORM);
    } catch (error) {
      setStatus("error");
      const apiText = error?.text || error?.message;
      setErrorMessage(apiText || "Erro desconhecido ao enviar.");
      console.error("EmailJS error:", error);
    }
  };

  return (
    <Section id="contact" title="Contato" subtitle="Vamos conversar">
      <div className="contact">
        <div className="contact__intro">
          <Typography variant="h5" component="p" className="contact__headline">
            Tem um projeto em mente?
          </Typography>
          <Typography variant="body1" className="contact__description">
            Envie uma mensagem e retorno o mais breve possível.
          </Typography>
        </div>
        <form onSubmit={sendEmail} className="contact__form" noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="from_name"
            label="Seu Nome"
            name="from_name"
            value={form.from_name}
            onChange={handleChange("from_name")}
            autoComplete="name"
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="reply_to"
            label="Seu E-mail"
            name="reply_to"
            type="email"
            value={form.reply_to}
            onChange={handleChange("reply_to")}
            autoComplete="email"
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="message"
            label="Sua Mensagem"
            id="message"
            multiline
            rows={4}
            value={form.message}
            onChange={handleChange("message")}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className="contact__submit"
            disabled={status === "sending"}
          >
            {status === "sending" ? "Enviando..." : "Enviar Mensagem"}
          </Button>
          {status === "success" && (
            <Typography className="contact__feedback contact__feedback--success">
              Mensagem enviada com sucesso!
            </Typography>
          )}
          {status === "error" && (
            <Typography className="contact__feedback contact__feedback--error">
              {errorMessage}
            </Typography>
          )}
        </form>
      </div>
    </Section>
  );
};
