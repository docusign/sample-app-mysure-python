import React, { useEffect, useContext } from "react";
import { completeCallback } from "../api/auth";
import LoggedUserContext from "../contexts/logged-user/logged-user.context";

export const Callback = () => {
    const { setShowAlert, setLogged, setAuthType, setShowJWTModal } = useContext(LoggedUserContext); 
    useEffect(() => {
        completeCallback(setShowAlert, setLogged, setAuthType, setShowJWTModal);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <>
        </>
    )
} 