import React from "react";
import { useTranslation } from "react-i18next";
import parse from "html-react-parser";

export const ApiDescription = () => {
  const { t } = useTranslation("RequestAutoRenewal");
  return (
    <div className="col-lg-6 pt-5 pb-4">
      <div id="accordion">
        <div className="card">
          <div className="card-header" id="headingOne">
            <h5 className="mb-0">
              <button
                class="btn btn-link" 
                data-bs-toggle="collapse" 
                data-bs-target="#collapseOne"
                aria-expanded="false" 
                aria-controls="collapseOne"
              >
                {t("ApiDecription.SeeMore")}
              </button>
            </h5>
          </div>
          <div
            id="collapseOne" 
            class="collapse" 
            aria-labelledby="headingOne" 
            data-bs-parent="#accordion"
          >
            <div className="card-body">
              {parse(t("ApiDecription.CodeFlow"))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};