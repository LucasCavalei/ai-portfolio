import React from "react";
import { TextDecrypt } from "../content/TextDecrypt";
import { ProjectDescription } from "./ProjectDescription";
import { Section } from "../../layouts/Section";
import { useLanguage } from "../i18n/LanguageProvider";

import Portfolio from "../../assets/recentprojects/react-portfolio.png";
import Agro from "../../assets/recentprojects/agro.svg";
import Eleitoral1 from "../../assets/recentprojects/eleitoral1.svg";
import Workteam from "../../assets/recentprojects/workteam.svg";
import Whatsapp from "../../assets/whatsappPC.svg";

import "./Works.css";

const PROJECT_IMAGES = {
  portfolio: Portfolio,
  agro: Agro,
  eleitoral1: Eleitoral1,
  workteam: Workteam,
  whatsapp: Whatsapp,
};

export const Works = () => {
  const { t, projects } = useLanguage();

  return (
    <Section id="works" title={t("works.title")} subtitle={t("works.subtitle")}>
      <div className="projects-list">
        {projects.map((project, index) => (
          <article
            className={`project${index % 2 !== 0 ? " project--reverse" : ""}`}
            key={project.id}
          >
            <div className="project__img">
              <img src={PROJECT_IMAGES[project.image]} alt={project.alter} />
            </div>
            <div className="project__content">
              <h3 className="project__title">
                <TextDecrypt text={project.title} />
              </h3>
              <ProjectDescription description={project.description} />
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
};
