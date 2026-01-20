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
      id: 2,
      title: 'Pesquisa Política', 
      description: `A political research project built using ReactJS and Node.js 
      to analyze political data and trends.`,
      alter: 'Pesquisa Política',
      image: `${Eleitoral1}`,
    },
    { 
      id: 3,
      title: 'Agro desefa', 
      description: `ALorem Ipsum is not simply random text.
       It has roots in a piece of classical Latin literature from 45 BC,
        making it over 2000 years old`,
      alter: 'VeriTru Project',
      image: `${Agro}`,
    },
    { 
      id: 3,
      title: 'Ligação', 
      description: `Lorem Ipsum is not simply random text.
       It has roots in a piece of classical Latin literature from 45 BC,
        making it over 2000 years old.`,
      alter: 'LoFo Project',
      image: `${Eleitoral2png}`,
    },
    { 
      id: 1,
      title: 'React Portfolio', 
      description: `Lorem Ipsum is not simply random text.
       It has roots in a piece of classical Latin literature from 45 BC,
        making it over 2000 years oldt.`,
      alter: 'React Portfolio',
      image: `${Portfolio}`,
    },
    { 
      id: 5,
      title: 'Teamwork', 
      description: `Lorem Ipsum is not simply random text.
       It has roots in a piece of classical Latin literature from 45 BC,
        making it over 2000 years old`,
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
