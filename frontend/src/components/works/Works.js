import React from "react";
import { TextDecrypt } from "../content/TextDecrypt";
import { ProjectDescription } from "./ProjectDescription";
import { Section } from "../../layouts/Section";
import projectsData from "../../data/projects.json";

import Portfolio from "../../assets/recentprojects/react-portfolio.png";
import Agro from "../../assets/recentprojects/agro.svg";
import Eleitoral1 from "../../assets/recentprojects/eleitoral1.svg";
import Workteam from "../../assets/recentprojects/workteam.svg";

import "./Works.css";

const PROJECT_IMAGES = {
  portfolio: Portfolio,
  agro: Agro,
  eleitoral1: Eleitoral1,
  workteam: Workteam,
};

export const Works = () => (
  <Section id="works" title="Projetos" subtitle="Portfólio">
    <div className="projects-list">
      {projectsData.map((project, index) => (
        <article
          className={`project${index % 2 !== 0 ? " project--reverse" : ""}`}
          key={project.id}
        >
          <div className="project__img">
            <img src={PROJECT_IMAGES[project.image]} alt={project.alter} />
          </div>
          <div className="project__content">
            <h3 className="project__title">
              <TextDecrypt text={`${project.id}. ${project.title}`} />
            </h3>
            <ProjectDescription description={project.description} />
          </div>
        </article>
      ))}
    </div>
  </Section>
);
