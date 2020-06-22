import React, { Suspense, useState, useEffect } from "react";
import { Route, Switch } from "react-router-dom";
import { Layout } from "./components/Layout";
import { About } from "./pages/about";
import { History } from "./pages/history";
import { Home } from "./pages/home";
import { BuyNewInsurance } from "./pages/buyNewInsurance";
import { RequestAutoRenewal } from "./pages/requestAutoRenewal";
import { SubmitClaim } from "./pages/submitClaim";
import { SigningComplete } from "./components/SigningComplete.js";
import { logOut, getStatus } from "./api/auth";
import { Callback } from "./components/Callback";
import history from "./api/history";
import LoggedUserContext from "./contexts/logged-user/logged-user.context";
import "./assets/scss/main.scss";

function App() {
  const [ logged, setLogged ] = useState(false);
  const [ redirectUrl, setRedirectUrl ] = useState("/");
  const [ showAlert, setShowAlert ] = useState(false);
  const [ showJWTModal, setShowJWTModal] = useState(false);
  const [ authType, setAuthType ] = useState(undefined);

  useEffect(() => {
    getStatus(setLogged, setAuthType);
  }, []);

  async function handleLogOut() {
    await logOut();
    history.push("/");
    await getStatus(setLogged, setAuthType);
  }

  const routes = (
    <Switch>
      <Route path="/history" component={History} />
      <Route path="/about" component={About} />
      <Route path="/byNewInsurance" component={BuyNewInsurance} />
      <Route path="/requestAutoRenewal" component={RequestAutoRenewal} />
      <Route path="/submitClaim" component={SubmitClaim} />
      <Route path="/" exact component={Home} />
      <Route path="/signing_complete" component={SigningComplete} />
      <Route path="/callback" component={Callback} />
      <Route path="/logout" render={() => {
        handleLogOut();
      }} />
    </Switch>
  );
  return (
    <Suspense fallback="">
      <LoggedUserContext.Provider value={{ logged, setLogged, redirectUrl, setRedirectUrl, 
                                          showAlert, setShowAlert, showJWTModal, setShowJWTModal,
                                          authType, setAuthType }}>
        <Layout>{routes}</Layout>
      </LoggedUserContext.Provider>
    </Suspense>
  );
}

export default App;