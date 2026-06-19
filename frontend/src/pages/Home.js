import React from "react";
import { MainLayout } from "../layouts/MainLayout";
import { Works } from "../components/works/Works";
import { About } from "../components/about/About";
import { Contact } from "../components/contact/Contact";

export const Home = () => (
  <MainLayout>
    <Works />
    <About />
    <Contact />
  </MainLayout>
);
