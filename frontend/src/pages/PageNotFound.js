import React from "react";
import { Link } from "react-router-dom";
import { Typography, Button } from "@material-ui/core";
import { useLanguage } from "../components/i18n/LanguageProvider";

const PageNotFound = () => {
  const { t } = useLanguage();

  return (
    <div className="not-found">
      <Typography variant="h1" component="h1" className="not-found__code">
        404
      </Typography>
      <Typography variant="h5" component="p" className="not-found__title">
        {t("notFound.title")}
      </Typography>
      <Typography variant="body1" className="not-found__text">
        {t("notFound.text")}
      </Typography>
      <Button component={Link} to="/" variant="contained" color="primary">
        {t("notFound.back")}
      </Button>
    </div>
  );
};

export default PageNotFound;
