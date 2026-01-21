import React, { useRef } from 'react';
import emailjs from '@emailjs/browser';
import { Container, TextField, Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  form: {
    width: '100%',
    marginTop: theme.spacing(3),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

export const Contact = () => {
  const classes = useStyles();
  const form = useRef();

  const sendEmail = (e) => {
    e.preventDefault();

    emailjs
      .sendForm(
        process.env.REACT_APP_EMAILJS_SERVICE_ID,
        process.env.REACT_APP_EMAILJS_TEMPLATE_ID,
        form.current,
        process.env.REACT_APP_EMAILJS_USER_ID // This is the Public Key fix
      )
      .then(
        (result) => {
          console.log('SUCCESS!', result.text);
          alert('Mensagem enviada com sucesso!');
          form.current.reset();
        },
        (error) => {
          console.log('FAILED...', error.text);
          alert('Ocorreu um erro. Verifique o console para mais detalhes.');
        }
      );
  };

  return (
    <Container component="section" id="contact" maxWidth="sm">
      <Typography variant="h4" component="h2" gutterBottom align="center">
        Entre em Contato
      </Typography>
      <form ref={form} onSubmit={sendEmail} className={classes.form} noValidate>
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          id="from_name"
          label="Seu Nome"
          name="from_name"
          autoComplete="name"
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          id="reply_to"
          label="Seu E-mail"
          name="reply_to"
          autoComplete="email"
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          name="message"
          label="Sua Mensagem"
          type="text"
          id="message"
          multiline
          rows={4}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
        >
          Enviar Mensagem
        </Button>
      </form>
    </Container>
  );
};