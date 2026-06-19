import React from "react";
import { Typography } from "@material-ui/core";
import { TextDecrypt } from "../content/TextDecrypt";

export const SectionTitle = ({ title, subtitle }) => (
  <div className="section-title">
    {subtitle && (
      <Typography variant="overline" component="p" className="section-title__subtitle">
        {subtitle}
      </Typography>
    )}
    <Typography variant="h4" component="h2" className="section-title__heading">
      <TextDecrypt text={title} />
    </Typography>
    <div className="section-title__divider" aria-hidden="true" />
  </div>
);
