import React from "react";
import { Typography } from "@material-ui/core";
import { NAV_ITEM_IDS } from "../../constants/navigation";
import { useActiveSection } from "../../hooks/useActiveSection";
import { useLanguage } from "../i18n/LanguageProvider";
import "./SideNavbar.css";

export const SideNavbar = () => {
  const activeSection = useActiveSection();
  const { t } = useLanguage();

  return (
    <nav className="side-nav" aria-label={t("nav.ariaLabel")}>
      {NAV_ITEM_IDS.map(({ id, labelKey, href }) => (
        <a
          key={id}
          href={href}
          className={activeSection === id ? "active" : ""}
          aria-current={activeSection === id ? "true" : undefined}
        >
          <Typography component="span" variant="body2">
            {t(labelKey)}
          </Typography>
        </a>
      ))}
    </nav>
  );
};
