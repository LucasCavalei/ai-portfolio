import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { LANGUAGE_STORAGE_KEY } from "../../constants/storage";
import pt from "../../locales/pt.json";
import en from "../../locales/en.json";
import resumePt from "../../settings/resume.json";
import resumeEn from "../../settings/resume.en.json";
import projectsPt from "../../data/projects.json";
import projectsEn from "../../data/projects.en.json";

export const LanguageContext = createContext(null);

const DICTS = { pt, en };
const RESUMES = { pt: resumePt, en: resumeEn };
const PROJECTS = { pt: projectsPt, en: projectsEn };

const interpolate = (template, vars = {}) =>
  String(template || "").replace(/\{(\w+)\}/g, (_, key) =>
    vars[key] != null ? String(vars[key]) : `{${key}}`,
  );

const getNested = (obj, path) =>
  path.split(".").reduce((acc, key) => (acc && acc[key] != null ? acc[key] : null), obj);

const readStoredLanguage = () => {
  if (typeof localStorage === "undefined") return "pt";
  const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return saved === "en" ? "en" : "pt";
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(readStoredLanguage);

  useEffect(() => {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    }
    if (typeof document !== "undefined") {
      document.documentElement.lang = language === "en" ? "en" : "pt-BR";
    }
  }, [language]);

  const setLanguage = useCallback((next) => {
    setLanguageState(next === "en" ? "en" : "pt");
  }, []);

  const toggleLanguage = useCallback(() => {
    setLanguageState((prev) => (prev === "pt" ? "en" : "pt"));
  }, []);

  const t = useCallback(
    (path, vars) => {
      const value = getNested(DICTS[language], path) ?? getNested(DICTS.pt, path) ?? path;
      return typeof value === "string" ? interpolate(value, vars) : value;
    },
    [language],
  );

  const resume = RESUMES[language] || RESUMES.pt;
  const projects = PROJECTS[language] || PROJECTS.pt;

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      toggleLanguage,
      t,
      resume,
      projects,
      isEnglish: language === "en",
    }),
    [language, setLanguage, toggleLanguage, t, resume, projects],
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return ctx;
};
