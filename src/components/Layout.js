import React from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet";

export const Layout = props => {
  const { t } = useTranslation("Common");
  return (
    <>
      <Helmet>
        <title>{t("Title")}</title>
      </Helmet>
      <Header />
      <main role="main" className="content">
        {props.children}
      </main>
      <Footer />
    </>
  );
};