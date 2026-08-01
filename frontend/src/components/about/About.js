import React from "react";
import { Typography } from "@material-ui/core";
import { TextDecrypt } from "../content/TextDecrypt";
import { FirstName, LastName } from "../../utils/getName";
import { Section } from "../../layouts/Section";
import { useLanguage } from "../i18n/LanguageProvider";
import profile from "../../assets/profile-transparent.png";
import "./About.css";

export const About = () => {
  const { t } = useLanguage();
  const greetings = t("about.greeting");
  const aboutme = t("about.bio", { firstName: FirstName, lastName: LastName });

  return (
    <Section id="about" title={t("about.title")} subtitle={t("about.subtitle")}>
      <div className="about">
        <div className="about__photo-frame">
          <img
            src={profile}
            alt={t("about.photoAlt", { firstName: FirstName, lastName: LastName })}
            className="about__photo"
          />
        </div>
        <div className="about__content">
          <Typography component="h3" variant="h5" className="about__greeting">
            <TextDecrypt text={greetings} />
          </Typography>
          <p className="about__text">{aboutme}</p>
          <a href="#contact" className="about__cta">
            <i className="fas fa-terminal" aria-hidden="true" />
            <Typography component="span">{t("about.cta")}</Typography>
          </a>
        </div>
      </div>
    </Section>
  );
};
