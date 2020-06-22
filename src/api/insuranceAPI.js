import axios from "./interceptors";
import { handleResponse, handleError } from "./apiHelper";

export async function buyNewInsurance(request, setShowJWTModal) {
  try {
    const response = await axios.post(
      process.env.REACT_APP_API_BASE_URL + "/requests/newinsurance",
      request,
      {
        withCredentials: true
      }
    );
    return handleResponse(response);
  } catch (error) {
    handleError(error, setShowJWTModal);
  }
}

export async function submitClaim(request) {
  try {
    const response = await axios.post(
      process.env.REACT_APP_API_BASE_URL + "/requests/claim",
      request,
      {
        withCredentials: true
      }
    );
    return handleResponse(response);
  } catch (error) {
    handleError(error);
  }
}

export async function getStatus(fromDate) {
  try {
    const response = await axios.get(
      process.env.REACT_APP_API_BASE_URL + "/requests",
      {
        params: {
          "from-date": fromDate
        },
        withCredentials: true
      }
    );
    return handleResponse(response);
  } catch (error) {
    handleError(error);
  }
}

export async function getStatusDocument(envelopId, documentId) {
  try {
    const response = await axios.get(
      process.env.REACT_APP_API_BASE_URL + "/requests/download",
      {
        params: {
          "envelope-id": envelopId,
          "document-id": documentId
        },
        withCredentials: true,
        responseType: "blob"
      }
    );
    return handleResponse(response);
  } catch (error) {
    handleError(error);
  }
}

export async function getCliwrapForRequestRenewal(request) {
  try {
    const response = await axios.post(
      process.env.REACT_APP_API_BASE_URL + "/clickwraps/renewal",
      request,
      {
        withCredentials: true
      }
    );
    return handleResponse(response);
  } catch (error) {
    handleError(error);
  }
}