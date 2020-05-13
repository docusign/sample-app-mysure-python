import React, { useState } from "react";
import { InputText } from "../../../components/InputText";
import { InputSelect } from "../../../components/InputSelect";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import parse from "html-react-parser";

export const RequestForm = ({
  request,
  onSave,
  onSelect,
  onChange,
  onNumberChange,
  states,
  options,
  setOption,
  requesting = false,
  errors = {}
}) => {
  const { t } = useTranslation("BuyNewInsurance");
  const [submitted, setSubmitted] = useState(false);

  return (
    <div className="col-lg-6">
      <div className="form-holder bg-white pt-5 pb-5">
        <h2 className="mb-4">{parse(t("Title"))}</h2>
        <h3>{t("General")}</h3>
        <ul className="nav nav-tabs" id="myTab" role="tablist">
          <li className="nav-item">
            <a
              className="nav-link active"
              id="1-nav"
              data-toggle="tab"
              href="#1-content"
              role="tab"
              aria-controls="1-content"
              aria-selected="true"
              onClick={() => setOption(options[0])}
            >
              <span className="icon-holder">
                <svg
                  className="icon"
                  xmlns="http://www.w3.org/2000/svg"
                  width="64"
                  height="44"
                  viewBox="0 0 64 44"
                >
                  <path
                    fill=""
                    fillRule="evenodd"
                    d="M31.757 0C36.193.011 49.68.395 51.45 4.578l4.148 9.909 5.613 5.358c3.03 2.776 1.552 13.76 1.488 14.226-.077.558-.358 1.103-1.857 1.61v4.77a3 3 0 0 1-2.997 2.998h-6.16a3 3 0 0 1-2.997-2.998v-3.186c-5.017.311-11.053.487-17.133.487-6.079 0-12.113-.176-17.13-.487v3.186a3 3 0 0 1-2.997 2.998h-6.16a3 3 0 0 1-2.997-2.998v-4.77C.772 35.174.491 34.628.413 34.07c-.063-.465-1.54-11.449 1.503-14.239l5.6-5.344 4.145-9.905C13.461.33 27.343 0 31.555 0zm27.085 36.185c-1.544.3-3.704.582-6.75.838-.449.037-.93.071-1.404.107v3.321c0 .551.447.998.996.998h6.161c.55 0 .997-.447.997-.998zm-54.57 0v4.266c0 .551.446.998.995.998h6.161c.55 0 .997-.447.997-.998V37.13c-.474-.036-.956-.07-1.405-.107-3.046-.256-5.205-.538-6.749-.838zm50.114-20.09c-2.153.151-11.905.787-22.719.787h-.499c-10.633-.02-20.298-.64-22.44-.787l-5.445 5.197c-1.559 1.429-1.469 8.078-.918 12.281 1.665 1.063 13.05 2.179 29.19 2.179h.555c15.848-.026 26.992-1.128 28.638-2.179.551-4.204.641-10.852-.903-12.268zM7.684 23.172c.261 0 .527.032.793.096l5.985 1.741c1.73.41 3.122 2.143 3.122 3.934v.886c0 1.761-1.37 3.141-3.122 3.141a3.29 3.29 0 0 1-.394-.023l-5.938-.68c-1.844-.213-3.287-1.825-3.287-3.671v-2.53c0-1.65 1.222-2.894 2.841-2.894zm47.744 0c1.62 0 2.84 1.244 2.84 2.894v2.53c0 1.845-1.443 3.458-3.285 3.671l-5.94.681a3.49 3.49 0 0 1-.393.022c-1.75 0-3.123-1.38-3.123-3.141v-.886c0-1.791 1.392-3.524 3.171-3.947l5.89-1.716a3.48 3.48 0 0 1 .84-.108zM40.96 30.459a1 1 0 1 1 0 2H22.153a1 1 0 1 1 0-2zM7.684 25.172c-.526 0-.84.334-.84.894v2.53c0 .818.693 1.589 1.516 1.684l5.937.681c.755.092 1.287-.405 1.287-1.132v-.886c0-.859-.762-1.794-1.633-2.001L7.965 25.2a1.491 1.491 0 0 0-.28-.028zm47.744 0c-.104 0-.215.014-.328.041l-5.892 1.716c-.918.22-1.68 1.155-1.68 2.014v.886c0 .672.461 1.141 1.122 1.141.054 0 .11-.003.164-.009l5.94-.681c.82-.095 1.514-.866 1.514-1.684v-2.53c0-.56-.315-.894-.84-.894zm-14.468.706a1 1 0 1 1 0 2H22.153a1 1 0 1 1 0-2zM31.555 2c-12.114 0-17.5 2.06-18.05 3.358L9.82 14.163c3.332.213 12.235.719 21.847.719h.532c9.378-.019 17.863-.507 21.095-.717l-3.688-8.811C49.06 4.06 43.672 2 31.556 2z"
                  />
                </svg>
              </span>
              {t("CarLabel")}
            </a>
          </li>
          <li className="nav-item">
            <a
              className="nav-link"
              id="2-nav"
              data-toggle="tab"
              href="#2-content"
              role="tab"
              aria-controls="2-content"
              aria-selected="false"
              onClick={() => setOption(options[1])}
            >
              <span className="icon-holder">
                <svg
                  className="icon"
                  xmlns="http://www.w3.org/2000/svg"
                  width="62"
                  height="55"
                  viewBox="0 0 62 55"
                >
                  <path
                    fill=""
                    fillRule="evenodd"
                    d="M61.02 52.917a1 1 0 1 1 0 2H1a1 1 0 0 1 0-2zM38.76 31.824a.998.998 0 0 1 1 1.002l-.022 15.747a1 1 0 0 1-2-.003l.02-14.746H24.282l-.022 14.749a1 1 0 0 1-2-.003l.023-15.747a1 1 0 0 1 1-1zM30.4 8.216a1 1 0 0 1 1.22 0l21.318 16.41c.246.189.39.482.39.792v23.154a1 1 0 0 1-2 0V25.91L31.01 10.27 10.691 25.91v22.662a1 1 0 1 1-2 0V25.418c0-.31.144-.603.39-.792zm.007-8.014a1 1 0 0 1 1.205 0L43.368 9.08V4.336a1 1 0 0 1 1-1h7.96a1 1 0 0 1 1 1v12.266l8.294 6.262a1 1 0 0 1-1.205 1.596l-8.69-6.562a1 1 0 0 1-.399-.798V5.336h-5.96v5.752a1 1 0 0 1-1.602.798L31.01 2.253 1.602 24.46a.998.998 0 0 1-1.205-1.596z"
                  />
                </svg>
              </span>
              {t("HomeLabel")}
            </a>
          </li>
          <li className="nav-item">
            <a
              className="nav-link"
              id="3-nav"
              data-toggle="tab"
              href="#3-content"
              role="tab"
              aria-controls="3-content"
              aria-selected="false"
              onClick={() => setOption(options[2])}
            >
              <span className="icon-holder">
                <svg
                  className="icon"
                  xmlns="http://www.w3.org/2000/svg"
                  width="57"
                  height="55"
                  viewBox="0 0 57 55"
                >
                  <path
                    fill=""
                    fillRule="evenodd"
                    d="M34.551 0a3.892 3.892 0 0 1 3.887 3.889V9.63h13.769a3.891 3.891 0 0 1 3.887 3.888v37.216a3.892 3.892 0 0 1-3.887 3.889H3.885A3.892 3.892 0 0 1 0 50.734V13.518A3.89 3.89 0 0 1 3.885 9.63h13.772V3.889A3.892 3.892 0 0 1 21.543 0zm17.656 11.63H3.885A1.889 1.889 0 0 0 2 13.518v37.216a1.89 1.89 0 0 0 1.885 1.889h48.322a1.89 1.89 0 0 0 1.887-1.889V13.518a1.89 1.89 0 0 0-1.887-1.888zm-24.16 3.661c9.283 0 16.836 7.552 16.836 16.835 0 9.283-7.553 16.835-16.836 16.835-9.283 0-16.836-7.552-16.836-16.835 0-9.283 7.553-16.835 16.836-16.835zm0 2c-8.181 0-14.836 6.655-14.836 14.835s6.655 14.835 14.836 14.835c8.181 0 14.836-6.655 14.836-14.835s-6.655-14.835-14.836-14.835zm2.695 3.979a1 1 0 0 1 1 1v6.162h6.161a1 1 0 0 1 1 1v5.39a1 1 0 0 1-1 1h-6.161v6.161a1 1 0 0 1-1 1h-5.39a1 1 0 0 1-1-1v-6.161H18.19a1 1 0 0 1-1-1v-5.39a1 1 0 0 1 1-1h6.162V22.27a1 1 0 0 1 1-1zm-1 2h-3.39v6.162a1 1 0 0 1-1 1H19.19v3.39h6.162a1 1 0 0 1 1 1v6.161h3.39v-6.161a1 1 0 0 1 1-1h6.161v-3.39h-6.161a1 1 0 0 1-1-1V23.27zM34.551 2H21.543a1.89 1.89 0 0 0-1.886 1.889V9.63h16.781V3.889A1.89 1.89 0 0 0 34.551 2z"
                  />
                </svg>
              </span>
              {t("LifeLabel")}
            </a>
          </li>
        </ul>
        <form
          onSubmit={event => {
            onSave(event);
            setSubmitted(true);
          }}
          className={submitted ? "was-validated" : ""}
          noValidate
        >
          {errors.onSave && (
            <div className="alert alert-danger mt-2">{errors.onSave}</div>
          )}
          <InputText
            name="firstName"
            label={t("FirstName")}
            value={request.firstName}
            onChange={onChange}
            error={errors.firstName}
          />
          <InputText
            name="lastName"
            label={t("LastName")}
            value={request.lastName}
            onChange={onChange}
            error={errors.lastName}
          />
          <InputText
            name="street"
            label={t("Street")}
            value={request.street}
            onChange={onChange}
            error={errors.street}
          />
          <InputText
            name="city"
            label={t("City")}
            value={request.city}
            onChange={onChange}
            error={errors.city}
          />
          <div className="row">
            <div className="col-md-6">
              <InputSelect
                name="state"
                label={t("State")}
                defaultOption={request.state || ""}
                options={states.map(state => ({
                  text: state
                }))}
                onChange={onSelect}
                error={errors.state}
              />
            </div>
            <div className="col-md-6">
              <InputText
                name="zipCode"
                label={t("ZipCode")}
                value={request.zipCode}
                onChange={onChange}
                error={errors.zipCode}
              />
            </div>
          </div>
          <InputText
            name="email"
            label={t("Email")}
            value={request.email}
            onChange={onChange}
            error={errors.email}
          />
          <div className="tab-content" id="myTabContent">
            <div
              className="tab-pane fade show active"
              id="1-content"
              role="tabpanel"
              aria-labelledby="1-nav"
            >
              <h3>{t("InsuranceDetails")}</h3>
              <div className="row">
                <div className="col-md-6">
                  <InputText
                    name="detail1"
                    label={t("CarModel")}
                    value={request.detail1}
                    onChange={onChange}
                    error={errors.insuranceDetails}
                  />
                </div>
                <div className="col-md-6">
                  <InputText
                    name="detail2"
                    label={t("Year")}
                    value={request.detail2}
                    onChange={onNumberChange}
                    error={errors.insuranceDetails}
                  />
                </div>
              </div>
            </div>
            <div
              className="tab-pane fade"
              id="2-content"
              role="tabpanel"
              aria-labelledby="2-nav"
            >
              <h3>{t("InsuranceDetails")}</h3>
              <div className="row">
                <div className="col-md-6">
                  <InputText
                    name="detail1"
                    label={t("HomeYear")}
                    value={request.detail1}
                    onChange={onNumberChange}
                    error={errors.insuranceDetails}
                  />
                </div>
                <div className="col-md-6">
                  <InputText
                    name="detail2"
                    label={t("Worth")}
                    value={request.detail2}
                    onChange={onNumberChange}
                    error={errors.insuranceDetails}
                  />
                </div>
              </div>
            </div>
            <div
              className="tab-pane fade"
              id="3-content"
              role="tabpanel"
              aria-labelledby="3-nav"
            >
              <h3>{t("InsuranceDetails")}</h3>
              <div className="row">
                <div className="col-md-6">
                  <InputText
                    name="detail1"
                    label={t("Age")}
                    value={request.detail1}
                    onChange={onNumberChange}
                    error={errors.insuranceDetails}
                  />
                </div>
                <div className="col-md-6">
                  <InputText
                    name="detail2"
                    label={t("HealthState")}
                    value={request.detail2}
                    onChange={onChange}
                    error={errors.insuranceDetails}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="text-center">
            <button
              type="submit"
              disabled={requesting}
              className="btn btn-success"
            >
              {requesting ? t("SubmitButtonClicked") : t("SubmitButton")}
            </button>
          </div>
        </form>
        <div className="text-center form-text">
          <span>{t("SubmitInfo")}</span>
        </div>
      </div>
    </div>
  );
};
RequestForm.propTypes = {
  request: PropTypes.object.isRequired,
  errors: PropTypes.object,
  states: PropTypes.array.isRequired,
  options: PropTypes.array.isRequired,
  onSave: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
  onNumberChange: PropTypes.func.isRequired,
  setOption: PropTypes.func.isRequired,
  requesting: PropTypes.bool
};