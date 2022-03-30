import React, { useState, useReducer, useContext, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { RequestForm } from "./components/RequestForm";
import { ApiDescription } from "./components/ApiDescription";
import { reducer } from "./requestReducer";
import * as api from "../../api/insuranceAPI";
import * as Actions from "./actionTypes";
import LoggedUserContext from "../../contexts/logged-user/logged-user.context";
import { checkUnlogged } from "../../api/auth";

const initialState = {
  errors: [],
  request: {
    firstName: "",
    lastName: "",
    email: ""
  },
  clickwrap: null
};

export const RequestAutoRenewal = () => {
  const { t } = useTranslation("RequestAutoRenewal");
  const [state, dispatch] = useReducer(reducer, initialState);
  const [request, setRequestData] = useState({ ...initialState.request });
  const [requesting, setRequesting] = useState(false);
  const [errors, setErrors] = useState({});
  const { logged, setLogged, setAuthType } = useContext(LoggedUserContext);

  useEffect(() => {
    checkUnlogged(logged, setLogged, setAuthType);
  })

  async function handleSave(event) {
    event.preventDefault();
    if (!formIsValid()) {
      return;
    }

    const body = {
      "callback-url": process.env.REACT_APP_DS_RETURN_URL + "/signing_complete",
      "terms-name": t("Renewal.TermsName"),
      "display-name": t("Renewal.DisplayName"),
      "terms-renewal": t("Renewal.TermsRenewal")
    };
    setRequesting(true);
    try {
      const response = await api.getCliwrapForRequestRenewal(body);
      dispatch({
        type: Actions.GET_CLICKWRAP_SUCCESS,
        payload: {
          clickwrap: response.clickwrap
        }
      });
      window.addEventListener(
        "message",
        event => goToSigningComplete(event),
        false
      );
    } catch (error) {
      setErrors({ ...errors, onSave: error.message });
      setRequesting(false);
    }
  }

  function goToSigningComplete(event) {
    if (event.data.type === "HAS_AGREED") {
      window.top.location.href =
        process.env.REACT_APP_DS_RETURN_URL + "/signing_complete";
    }
  }

  function handleChange(event) {
    const { name } = event.target;
    const { [name]: removed, ...updatedErrors } = errors;
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;
    setErrors(updatedErrors);
    setRequestData(request => ({
      ...request,
      [name]: value
    }));
  }

  function formIsValid() {
    const { firstName, lastName, email } = request;
    const errors = {};
    if (!firstName) {
      errors.firstName = t("Error.FirstName");
    }
    if (!lastName) {
      errors.lastName = t("Error.LastName");
    }
    if (!email) {
      errors.email = t("Error.Email");
    }
    setErrors(errors);
    return Object.keys(errors).length === 0;
  }

  return (
    <section className="container content-section">
      <div className="row">
        <RequestForm
          request={request}
          requesting={requesting}
          onChange={handleChange}
          onSave={handleSave}
          errors={errors}
          clickwrap={state.clickwrap}
        />
        <ApiDescription />
      </div>
    </section>
  );
};