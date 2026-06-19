import React from "react";
import { Typography } from "@material-ui/core";
import Resume from "../../settings/resume.json";

export const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="site-footer__inner">
        <Typography variant="body2" component="p">
          © {year} {Resume.basics.name}
        </Typography>
        <Typography variant="body2" component="p" className="site-footer__tagline">
          {Resume.basics.summary}
        </Typography>
      </div>
    </footer>
  );
};
