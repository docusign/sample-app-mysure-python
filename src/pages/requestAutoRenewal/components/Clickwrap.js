import React from "react";
import PropTypes from "prop-types";

export const ClickWrap = ({ accountId, clickwrapId, clientUserId, fullName, email, date }) => {
  return (
    <div className="form-group">
      {window.docuSignClick.Clickwrap.render(
        {
          environment: process.env.REACT_APP_DS_DEMO_SERVER,
          accountId: accountId,
          clickwrapId: clickwrapId,
          clientUserId: clientUserId,
          documentData: {
            fullName: fullName,
            email: email,
            date: date
          }
        },
        "#ds-clickwrap"
      )}
    </div>
  );
};

ClickWrap.propTypes = {
  accountId: PropTypes.string.isRequired,
  clickwrapId: PropTypes.string.isRequired,
  clientUserId: PropTypes.string.isRequired,
  fullName: PropTypes.string.isRequired,
  email: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired,
};