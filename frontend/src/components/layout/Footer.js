import React from "react";
import { Typography } from "@material-ui/core";
import { Resume } from "../resume/Resume";
import ResumeData from "../../settings/resume.json";

export const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <Resume />
      <div className="site-footer__inner">
        <Typography variant="body2" component="p">
          © {year} {ResumeData.basics.name}
        </Typography>
        <Typography variant="body2" component="p" className="site-footer__tagline">
          {ResumeData.basics.summary}
        </Typography>
      </div>
    </footer>
  );
};
