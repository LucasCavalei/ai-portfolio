import React from "react";
import { Typography } from "@material-ui/core";
import { Resume } from "../resume/Resume";
import { useLanguage } from "../i18n/LanguageProvider";

export const Footer = () => {
  const year = new Date().getFullYear();
  const { resume } = useLanguage();

  return (
    <footer className="site-footer">
      <Resume />
      <div className="site-footer__inner">
        <Typography variant="body2" component="p">
          © {year} {resume.basics.name}
        </Typography>
        <Typography variant="body2" component="p" className="site-footer__tagline">
          {resume.basics.summary}
        </Typography>
      </div>
    </footer>
  );
};
