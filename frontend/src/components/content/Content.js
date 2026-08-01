// Alteração 1 — Original: Whamais+Web grande, Lucas pequeno (h5) + tagline e botões
// Alteração 2 — Portfólio pessoal: Lucas grande, Whamais menor
// Alteração 3 — Híbrido: Whamais (marca) + Lucas Rodrigues (fundador)
// Alteração 4 — Bento glass: grid moderno, cards glass, pills de serviço

import React from "react";
import Chat from "../chat/Chat";
import { Typography, Container } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import { TextDecrypt } from "./TextDecrypt";
import { FirstName, LastName } from "../../utils/getName";
import { useLanguage } from "../i18n/LanguageProvider";
import "./Content.css";

const useStyles = makeStyles((theme) => ({
  main: {
    maxWidth: "100vw",
    marginTop: "auto",
    marginBottom: "auto",
  },
  heading: {
    marginLeft: theme.spacing(50),
    "@media (max-width: 768px)": {
      marginLeft: theme.spacing(10),
    },
  },
  jobs: {
    "@media (max-width: 768px)": {
      fontSize: "3rem",
    },
  },
}));

export const Content = () => {
  const classes = useStyles();
  const { t, resume } = useLanguage();

  return (
    <>
      <Container component="div" className={classes.main} maxWidth="md">
        <div className={`hero-content ${classes.heading}`}>
          <Typography variant="h5" component="p" className="hero-content__name">
            <TextDecrypt text={`${FirstName} ${LastName}`} />
          </Typography>

          <Typography variant="h1" component="h1" className={classes.jobs}>
            <TextDecrypt text={`${resume.basics.job1} + `} />
            <TextDecrypt text={resume.basics.job2} />
          </Typography>

          <p className="hero-content__tagline">{resume.basics.tagline}</p>

          <div className="hero-content__actions">
            <a
              href="#works"
              className="hero-content__btn hero-content__btn--primary"
            >
              <i className="fas fa-briefcase" aria-hidden="true" />
              {t("hero.viewProjects")}
            </a>
            <a
              href="#contact"
              className="hero-content__btn hero-content__btn--secondary"
            >
              <i className="fas fa-envelope" aria-hidden="true" />
              {t("hero.contact")}
            </a>
          </div>
        </div>
      </Container>
      <Chat />
    </>
  );
};
