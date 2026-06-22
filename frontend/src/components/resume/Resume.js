import React from "react";
import { Typography, Link } from "@material-ui/core";
import { TextDecrypt } from "../content/TextDecrypt";
import { ResumeIcon } from "../content/ResumeButton";
import ResumePDF from "../../assets/lucasResume.pdf";

export const Resume = () => (
  <div className="site-footer__resume">
    <Link
      color="inherit"
      underline="none"
      href={ResumePDF}
      target="_blank"
      rel="noopener noreferrer"
      className="site-footer__resume-link"
    >
      <ResumeIcon />
      <Typography component="span">
        <TextDecrypt text=" Currículo" />
      </Typography>
    </Link>
  </div>
);
