import * as types from "./actionTypes";

export function reducer(state = { request: {} }, action) {
  switch (action.type) {
    case types.GET_CLICKWRAP_SUCCESS: {
      const { clickwrap, envelopeId, redirectUrl } = action.payload;
      return { ...state, clickwrap, envelopeId, redirectUrl };
    }
    default:
      return state;
  }
}