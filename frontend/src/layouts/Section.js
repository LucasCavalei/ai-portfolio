import React from "react";
import { Container } from "@material-ui/core";
import { SectionTitle } from "../components/layout/SectionTitle";

export const Section = ({ id, title, subtitle, children, className = "" }) => (
  <section id={id} className={`page-section ${className}`.trim()}>
    <Container component="div" maxWidth="md" className="page-section__container">
      {title && <SectionTitle title={title} subtitle={subtitle} />}
      {children}
    </Container>
  </section>
);
