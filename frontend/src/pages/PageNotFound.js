import React from "react";
import { Link } from "react-router-dom";
import { Typography, Button } from "@material-ui/core";

const PageNotFound = () => (
  <div className="not-found">
    <Typography variant="h1" component="h1" className="not-found__code">
      404
    </Typography>
    <Typography variant="h5" component="p" className="not-found__title">
      Página não encontrada
    </Typography>
    <Typography variant="body1" className="not-found__text">
      O endereço que você acessou não existe ou foi movido.
    </Typography>
    <Button component={Link} to="/" variant="contained" color="primary">
      Voltar ao início
    </Button>
  </div>
);

export default PageNotFound;
