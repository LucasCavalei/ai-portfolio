import React from "react";
import { Typography } from "@material-ui/core";
import { NAV_ITEMS } from "../../constants/navigation";
import { useActiveSection } from "../../hooks/useActiveSection";
import "./SideNavbar.css";

export const SideNavbar = () => {
  const activeSection = useActiveSection();

  return (
    <nav className="side-nav" aria-label="Navegação principal">
      {NAV_ITEMS.map(({ id, label, href }) => (
        <a
          key={id}
          href={href}
          className={activeSection === id ? "active" : ""}
          aria-current={activeSection === id ? "true" : undefined}
        >
          <Typography component="span" variant="body2">
            {label}
          </Typography>
        </a>
      ))}
    </nav>
  );
};
