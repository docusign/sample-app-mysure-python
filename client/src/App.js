import React, { Suspense, useState, useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Logout } from "./components/Logout";
import { About } from "./pages/about";
import { History } from "./pages/history";
import { Home } from "./pages/home";
import { BuyNewInsurance } from "./pages/buyNewInsurance";
import { RequestAutoRenewal } from "./pages/requestAutoRenewal";
import { SubmitClaim } from "./pages/submitClaim";
import { SigningComplete } from "./components/SigningComplete.js";
import { logOut, getStatus } from "./api/auth";
import { Callback } from "./components/Callback";
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
    await getStatus(setLogged, setAuthType);
  }

  const routes = (
    <Routes>
      <Route path="/history" element={<History/>} />
      <Route path="/about" element={<About/>} />
      <Route path="/byNewInsurance" element={<BuyNewInsurance/>} />
      <Route path="/requestAutoRenewal" element={<RequestAutoRenewal/>} />
      <Route path="/submitClaim" element={<SubmitClaim/>} />
      <Route path="/" exact element={<Home/>} />
      <Route path="/signing_complete" element={<SigningComplete/>} />
      <Route path="/callback" element={<Callback/>} />
      <Route path="/logout" element={<Logout handleLogOut={handleLogOut}/>} />
    </Routes>
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