import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import history from "./api/history";
import "./i18n";

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

const app = (
  <BrowserRouter history={history}>
    <App />
  </BrowserRouter>
);

root.render(app);
