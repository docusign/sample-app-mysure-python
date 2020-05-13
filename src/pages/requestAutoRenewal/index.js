import React, { useState, useReducer } from "react";
import { useTranslation } from "react-i18next";
import { RequestForm } from "./components/RequestForm";
import { ApiDescription } from "./components/ApiDescription";
import { reducer } from "./requestReducer";
import * as api from "../../api/insuranceAPI";
import * as Actions from "./actionTypes";

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
  const [errors, setErrors] = useState({});

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
    try {
      const response = await api.getCliwrapForRequestRenewal(body);
      dispatch({
        type: Actions.GET_CLICKWRAP_SUCCESS,
        payload: {
          clickwrap: response.clickwrap,
          envelopeId: response.envelope_id,
          redirectUrl: response.redirect_url
        }
      });
      window.addEventListener(
        "message",
        event => goToSigningComplete(event),
        false
      );
    } catch (error) {
      throw error;
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