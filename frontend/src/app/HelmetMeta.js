import React from "react";
import Helmet from "react-helmet";
import Settings from "../settings/settings.json";
import { useLanguage } from "../components/i18n/LanguageProvider";

export const HelmetMeta = () => {
  const { resume, language } = useLanguage();

  return (
    <Helmet>
      <html lang={language === "en" ? "en" : "pt-BR"} />
      <meta name="theme-color" content={Settings.colors.primary} />
      <title>
        {resume.basics.name} | {resume.basics.location.city}, {resume.basics.location.country}
      </title>
      <meta name="author" content={resume.basics.name} />
      <meta name="description" content={resume.basics.description} />
      <meta name="keywords" content={resume.basics.keywords} />
    </Helmet>
  );
};
