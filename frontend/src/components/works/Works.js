/* eslint-disable no-unused-vars */
import React from "react";
import { useState } from "react";
import { Container } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import { TextDecrypt } from "../content/TextDecrypt";

import './Works.css';

// Import ../../assets/recentprojects/
import Portfolio from '../../assets/recentprojects/react-portfolio.png';
import Agro from '../../assets/recentprojects/agro.svg';
import Eleitoral1 from '../../assets/recentprojects/eleitoral1.svg'
import Eleitoral2 from '../../assets/recentprojects/eleitoral2.svg'
import Eleitoral2png from '../../assets/recentprojects/eleitoral2png.png'
import Workteam from '../../assets/recentprojects/workteam.svg'


const useStyles = makeStyles((theme) => ({
  main: {
    maxWidth: '100vw',
    marginTop: '3em',
    marginBottom: "auto",
  },
}));

export const Works = () => {
  const classes = useStyles();
  const [projects, setProjects] = useState([
    { 
      id: 1,
      title: 'Pesquisa Política', 
      description: `Plataforma para automação de sondagens eleitorais o usuário dispara chamadas onde um agente de IA conversacional entrevista os eleitores,
       seguindo um roteiro para captar intenções de voto.`,
      alter: 'Pesquisa Política',
      image: `${Eleitoral1}`,
    },
    { 
      id: 2,
      title: 'Agro Defesa', 
      description: `Aplicação web desenvolvida para o evento Agro Defesa da Agendacia de Defesa Agropecuária e Florestal (ADAF) realizado no Centro de Convenções Vasco Vasques. O sistema foi criado para apresentar de forma interativa os tópicos abordados nas palestras, detalhando as
       responsabilidades e áreas de atuação da Agência de Defesa Agropecuária e Florestal (ADAF).`,
      alter: 'VeriTru Project',
      image: `${Agro}`,
    },
    // { 
    //   id: 3,
    //   title: 'Ligação', 
    //   description: `Lorem Ipsum is not simply random text.
    //    It has roots in a piece of classical Latin literature from 45 BC,
    //     making it over 2000 years old.`,
    //   alter: 'LoFo Project',
    //   image: `${Eleitoral2png}`,
    // },
    { 
      id: 3,
      title: 'Design de Interface moderno', 
     description: `Interface adaptativa de alta performance desenvolvida com Mobile-First. 
  Utiliza React js , Angular JS, Tailwind CSS e Grid Layout para garantir uma experiência fluida em qualquer 
  dispositivo, priorizando velocidade e acessibilidade.`,
      alter: 'React Portfolio',
      image: `${Portfolio}`,
    },
    { 
      id: 4,
      title: 'Checklist', 
      description: `Minimalista focado em produtividade pessoal. O app permite que usuários organizem 
      sua rotina através da criação, edição e priorização de afazeres diários`,
      alter: 'Startup Project',
      image: `${Workteam}`,
    },
  ]);

  return (
    <section id="works">
      <Container component="main" className={classes.main} maxWidth="md">
        {projects.map((project) => (
          <div className="project" key={ project.id }>
            <div className="__img_wrapper">
              <img src={ project.image } alt={ project.alter }/>
            </div>
            <div className="__content_wrapper">
              <h3 className="title">
                <TextDecrypt text={ project.id + '. ' + project.title } />
              </h3>
              <p className="description">
                { project.description }
              </p>
            </div>
          </div>
        ))}
      </Container>
    </section>
  );
};
