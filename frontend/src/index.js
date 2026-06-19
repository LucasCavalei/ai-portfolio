import React from "react";
import { render } from "react-snapshot";
import { App } from "./app/App";
import "./index.css";
import "./styles/sections.css";

render(<App />, document.getElementById("root"));
