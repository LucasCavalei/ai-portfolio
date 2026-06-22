import React from "react";
import { Typography } from "@material-ui/core";
import { TextDecrypt } from "../content/TextDecrypt";
import { FirstName, LastName } from "../../utils/getName";
import { Section } from "../../layouts/Section";
import profile from "../../assets/profile-transparent.png";
import "./About.css";

export const About = () => {
  const greetings = "Olá!";
  const aboutme = `Me chamo ${FirstName} ${LastName}, Full Stack Developer multidisciplinar.
Embora minha base seja o desenvolvimento web, estou expandindo minha atuação para o campo de Automação e Bots (IA).
Sempre topando qualquer desafio.
Estou aqui para lhe ajudar a criar sistemas tops.`;

  return (
    <Section id="about" title="Sobre mim" subtitle="Quem sou">
      <div className="about">
        <div className="about__photo-frame">
          <img
            src={profile}
            alt={`Foto de ${FirstName} ${LastName}`}
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
            <Typography component="span">Manda um olá</Typography>
          </a>
        </div>
      </div>
    </Section>
  );
};
