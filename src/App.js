import React, { Suspense } from "react";
import { Route, Switch } from "react-router-dom";
import { Layout } from "./components/Layout";
import { About } from "./pages/about";
import { History } from "./pages/history";
import { Home } from "./pages/home";
import { BuyNewInsurance } from "./pages/buyNewInsurance";
import { RequestAutoRenewal } from "./pages/requestAutoRenewal";
import { SubmitClaim } from "./pages/submitClaim";
import { SigningComplete } from "./components/SigningComplete.js";
import "./assets/scss/main.scss";

function App() {
  const routes = (
    <Switch>
      <Route path="/history" component={History} />
      <Route path="/about" component={About} />
      <Route path="/byNewInsurance" component={BuyNewInsurance} />
      <Route path="/requestAutoRenewal" component={RequestAutoRenewal} />
      <Route path="/submitClaim" component={SubmitClaim} />
      <Route path="/" exact component={Home} />
      <Route path="/signing_complete" component={SigningComplete} />
    </Switch>
  );
  return (
    <Suspense fallback="">
      <Layout>{routes}</Layout>
    </Suspense>
  );
}

export default App;