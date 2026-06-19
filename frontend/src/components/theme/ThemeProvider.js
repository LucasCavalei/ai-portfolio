import React, { useEffect, useState, createContext } from "react";
import { MuiThemeProvider } from "@material-ui/core/styles";
import { LightTheme, DarkTheme, primary, secondary, black, white } from "./Themes";
import { THEME_STORAGE_KEY } from "../../constants/storage";

export const ThemeContext = createContext();

const applyCssVariables = (mode) => {
  const root = document.documentElement;
  const isDark = mode === "dark";

  root.setAttribute("data-theme", mode);
  root.style.setProperty("--color-primary", primary);
  root.style.setProperty("--color-primary-dark", "#36a2a2");
  root.style.setProperty("--color-primary-light", isDark ? "rgba(66, 188, 188, 0.15)" : "rgba(66, 188, 188, 0.1)");
  root.style.setProperty("--color-secondary", secondary);
  root.style.setProperty("--color-black", black);
  root.style.setProperty("--color-white", white);
  root.style.setProperty("--color-background", isDark ? black : white);
  root.style.setProperty("--color-foreground", isDark ? white : black);
  root.style.setProperty("--color-surface", isDark ? "#1a1a1a" : "#ffffff");
  root.style.setProperty("--color-muted", isDark ? "#a0a0a0" : "#575757");
  root.style.setProperty("--color-border", isDark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.08)");
  root.style.setProperty("--shadow-card", isDark
    ? "0 4px 24px rgba(0,0,0,0.4)"
    : "0 4px 24px rgba(0,0,0,0.08)");
};

export const ThemeProvider = ({ children }) => {
  const getInitialMode = () => {
    if (typeof localStorage === "undefined") return true;
    const isReturningUser = THEME_STORAGE_KEY in localStorage;
    const savedMode = JSON.parse(localStorage.getItem(THEME_STORAGE_KEY));
    const userPrefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    if (isReturningUser) {
      return savedMode;
    }
    return !!userPrefersDark;
  };

  const [theme, setTheme] = useState(getInitialMode() ? "dark" : "light");

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  useEffect(() => {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(theme === "dark"));
    }
    applyCssVariables(theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <MuiThemeProvider theme={theme === "light" ? LightTheme : DarkTheme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
