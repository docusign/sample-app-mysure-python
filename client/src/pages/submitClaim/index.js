import React, { useState, useReducer, useEffect, useContext } from "react";
import { RequestForm } from "./components/RequestForm";
import { ApiDescription } from "./components/ApiDescription";
import { reducer } from "./requestReducer";
import { Frame } from "../../components/Frame.js";
import { SEND_REQEUST_SUCCESS } from "./actionTypes";
import * as insuranceAPI from "../../api/insuranceAPI";
import { useTranslation } from "react-i18next";
import LoggedUserContext from "../../contexts/logged-user/logged-user.context";
import { checkUnlogged } from "../../api/auth";
import { ExtensionsModal } from "../../components/ExtensionsModal.js";

const initialState = {
  errors: [],
  request: {
    firstName: "",
    lastName: "",
    street: "",
    city: "",
    state: "",
    zipCode: "",
    email: "",
    type: "",
    description: "",
    country: ""
  }
};

export const SubmitClaim = () => {
  const { t: tCommon } = useTranslation("Common");
  const { t } = useTranslation("SubmitClaim");
  const states = t("States", { returnObjects: true });
  const options = t("Options", { returnObjects: true });
  const [option, setOption] = useState(options[0]);
  const [state, dispatch] = useReducer(reducer, initialState);
  const [areExtensionsPresent, setAreExtensionsPresent] = useState(false);
  const [modalShow, setModalShow] = useState(false);
  const [request, setRequestData] = useState({ ...initialState.request });
  const [requesting, setRequesting] = useState(false);
  const [errors, setErrors] = useState({});
  const [date, setDate] = useState(new Date());
  const { logged, setLogged, setAuthType } = useContext(LoggedUserContext);
  const [isLoading, setLoading] = useState(false);

  useEffect(() => {
    checkUnlogged(logged, setLogged, setAuthType);
  })

  async function handleSave(event) {
    event.preventDefault();
    if (!formIsValid()) {
      return;
    }
    setLoading(true);

    const useWithoutExtension = sessionStorage.getItem("useWithoutExtensions") === "true";
    const body = {
      "callback-url": process.env.REACT_APP_DS_RETURN_URL + "/signing_complete",
      claim: {
        first_name: request.firstName,
        last_name: request.lastName,
        email: request.email,
        street: request.street,
        city: request.city,
        state: request.state,
        country: request.country,
        zip_code: request.zipCode,
        type: option.name,
        timestamp: date.toGMTString(),
        description: request.description,
        useWithoutExtension: useWithoutExtension
      }
    };
    setRequesting(true);
    try {
      sessionStorage.setItem("useWithoutExtensions", "false");
      if (!useWithoutExtension) {
        const extensions = await insuranceAPI.getExtensions();
        if(extensions.areExtensionsPresent === false){
          setAreExtensionsPresent(true);
          setModalShow(true);
          return;
        }
      }

      const savedRequest = await insuranceAPI.submitClaim(body);
      dispatch({
        type: SEND_REQEUST_SUCCESS,
        payload: {
          envelopeId: savedRequest.envelope_id,
          redirectUrl: savedRequest.redirect_url,
        }
      });
    } catch (error) {
      setErrors({ ...errors, onSave: error.message });
    } finally {
      setRequesting(false);
      setLoading(false);
    }
  }

  function handleChange(event) {
    const { name, value } = event.target;
    const { [name]: removed, ...updatedErrors } = errors;
    setErrors(updatedErrors);
    setRequestData(request => ({
      ...request,
      [name]: value
    }));
  }

  function handleSelect(event) {
    const { name, value } = event.target;
    const { [name]: removed, ...updatedErrors } = errors;
    setErrors(updatedErrors);
    setRequestData(request => ({
      ...request,
      [name]: states[value]
    }));
  }

  function formIsValid() {
    const {
      firstName,
      lastName,
      email,
      street,
      state,
      city,
      zipCode,
      description
    } = request;
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

    if (!street) {
      errors.street = t("Error.Street");
    }
    if (!state) {
      errors.state = t("Error.State");
    }
    if (!state) {
      errors.country = t("Error.Country");
    }
    if (!city) {
      errors.city = t("Error.City");
    }
    if (!zipCode) {
      errors.zipCode = t("Error.ZipCode");
    }
    if (!description) {
      errors.description = t("Error.Description");
    }

    setErrors(errors);
    return Object.keys(errors).length === 0;
  }
  
  if (!state.redirectUrl) {
  return (
    <section className="container content-section">
      <div className="row">
        <RequestForm
          request={request}
          states={states}
          options={options}
          requesting={requesting}
          onChange={handleChange}
          onSelect={handleSelect}
          onSave={handleSave}
          errors={errors}
          setDate={setDate}
          setOption={setOption}
          date={date}
          isLoading={isLoading}
        />
        <ApiDescription />
      </div>

      {areExtensionsPresent && (
        <ExtensionsModal
          show={modalShow}
          onDownloadExtensions={
              () => {
              setModalShow(false);
            }
          }
          onHide={
              () => {
              sessionStorage.setItem("useWithoutExtensions", "true");
              setModalShow(false);
            }
          }
          title={tCommon("DownloadExtensionsHeader")}
          message= {tCommon("DownloadExtensionsMessage")}
        />
      )}
    </section>
  );
} else {
  return <Frame src={state.redirectUrl} />;
}

};