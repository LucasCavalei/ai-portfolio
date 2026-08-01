import React, { lazy, Suspense } from "react";
import { ClickToComponent } from "click-to-react-component";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { CircularProgress, Box } from "@material-ui/core";
import { HelmetMeta } from "./HelmetMeta";
import { ThemeProvider } from "../components/theme/ThemeProvider";
import { LanguageProvider } from "../components/i18n/LanguageProvider";
import { CssBaseline } from "@material-ui/core";
import { logCredits } from "../utils/logCredits";
import { Home } from "../pages/Home";

const PageNotFound = lazy(() => import("../pages/PageNotFound"));

const PageLoader = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
    <CircularProgress color="primary" />
  </Box>
);

export const App = () => {
  logCredits();

  return (
    <ThemeProvider>
      <LanguageProvider>
        <CssBaseline />
        <ClickToComponent />
        <Router>
          <HelmetMeta />
          <Suspense fallback={<PageLoader />}>
            <Switch>
              <Route path="/" exact component={Home} />
              <Route path="*" component={PageNotFound} />
            </Switch>
          </Suspense>
        </Router>
      </LanguageProvider>
    </ThemeProvider>
  );
};
