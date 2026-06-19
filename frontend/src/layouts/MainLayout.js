import React from "react";
import { Hidden, makeStyles } from "@material-ui/core";
import DisplacementSphere from "../components/background/DisplacementSphere";
import { LogoLink } from "../components/logo/LogoLink";
import { Content } from "../components/content/Content";
import { ThemeToggle } from "../components/theme/ThemeToggle";
import { Resume } from "../components/resume/Resume";
import { SocialIcons } from "../components/content/SocialIcons";
import { SpeedDials } from "../components/speedDial/SpeedDial";
import { SideNavbar } from "../components/nav/SideNavbar";
import { Footer } from "../components/layout/Footer";

const useStyles = makeStyles(() => ({
  hero: {
    display: "flex",
    flexDirection: "column",
    minHeight: "100vh",
    position: "relative",
  },
}));

export const MainLayout = ({ children }) => {
  const classes = useStyles();

  return (
    <>
      <header className={classes.hero} id="home">
        <DisplacementSphere />
        <LogoLink />
        <Content />
        <ThemeToggle />
        <Hidden smDown>
          <SocialIcons />
        </Hidden>
        <Hidden mdUp>
          <SpeedDials />
        </Hidden>
        <Resume />
      </header>

      <SideNavbar />
      <main>{children}</main>
      <Footer />
    </>
  );
};
