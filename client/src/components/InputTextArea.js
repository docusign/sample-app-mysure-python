import React from "react";
import PropTypes from "prop-types";

export const InputTextArea = ({
  name,
  label,
  onChange,
  placeholder,
  value,
  error
}) => {
  let wrapperClass = "form-group";
  if (error && error.length > 0) {
    wrapperClass += " has-error";
  }

  return (
    <div className={wrapperClass}>
      <label htmlFor={name}>{label}</label>
      <div className="field form-group">
        <textarea
          type="text"
          name={name}
          rows="4"
          className="form-control"
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          required
        >
          {placeholder}
        </textarea>
        <div className="invalid-feedback">{error}</div>
      </div>
    </div>
  );
};

InputTextArea.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  error: PropTypes.string
};