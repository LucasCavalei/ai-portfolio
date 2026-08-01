import React, { useState } from "react";
import { TextField, Button, Typography } from "@material-ui/core";
import { Section } from "../../layouts/Section";
import { sendContactEmail } from "../../services/contactApi";
import { useLanguage } from "../i18n/LanguageProvider";
import "./Contact.css";

const INITIAL_FORM = {
  from_name: "",
  reply_to: "",
  message: "",
};

export const Contact = () => {
  const { t } = useLanguage();
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
      setErrorMessage(apiText || t("contact.errorFallback"));
      console.error("EmailJS error:", error);
    }
  };

  return (
    <Section id="contact" title={t("contact.title")} subtitle={t("contact.subtitle")}>
      <div className="contact">
        <div className="contact__intro">
          <Typography variant="h5" component="p" className="contact__headline">
            {t("contact.headline")}
          </Typography>
          <Typography variant="body1" className="contact__description">
            {t("contact.description")}
          </Typography>
        </div>
        <form onSubmit={sendEmail} className="contact__form" noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="from_name"
            label={t("contact.name")}
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
            label={t("contact.email")}
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
            label={t("contact.message")}
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
            {status === "sending" ? t("contact.sending") : t("contact.submit")}
          </Button>
          {status === "success" && (
            <Typography className="contact__feedback contact__feedback--success">
              {t("contact.success")}
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
