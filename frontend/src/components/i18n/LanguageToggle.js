import React from "react";
import { Tooltip, IconButton, Zoom } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import { useLanguage } from "./LanguageProvider";

const useStyles = makeStyles((theme) => ({
  iconButton: {
    position: "fixed",
    bottom: theme.spacing(6),
    right: theme.spacing(13),
    height: "2.5rem",
    width: "2.5rem",
    fontSize: "0.75rem",
    fontWeight: 700,
    letterSpacing: "0.04em",
    zIndex: 1100,
  },
  label: {
    fontSize: "0.8rem",
    fontWeight: 700,
    lineHeight: 1,
  },
}));

export const LanguageToggle = () => {
  const { language, toggleLanguage, t } = useLanguage();
  const classes = useStyles();
  const nextLabel = language === "pt" ? "EN" : "PT";

  return (
    <Tooltip
      title={t("language.toggle")}
      placement="right"
      TransitionComponent={Zoom}
    >
      <IconButton
        color="inherit"
        onClick={toggleLanguage}
        aria-label={t("language.ariaLabel")}
        className={classes.iconButton}
      >
        <span className={classes.label}>{nextLabel}</span>
      </IconButton>
    </Tooltip>
  );
};
