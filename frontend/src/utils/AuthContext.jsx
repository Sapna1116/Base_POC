import React, { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";
// const swal = require("sweetalert2");
import Swal from "sweetalert2";

const AuthContext = createContext();
export default AuthContext;

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(() =>
    localStorage.getItem("authTokens")
      ? JSON.parse(localStorage.getItem("authTokens"))
      : null
  );

  const [user, setUser] = useState(() =>
    localStorage.getItem("authTokens")
      ? jwtDecode(localStorage.getItem("authTokens"))
      : null
  );

  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  // Login
  const loginUser = async (email, password) => {
    const response = await fetch("http://127.0.0.1:8000/api/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
    const data = await response.json();
    console.log(data);

    if (response.status === 200) {
      console.log("Logged In");
      setAuthTokens(data);
      setUser(jwtDecode(data.access));
      localStorage.setItem("authTokens", JSON.stringify(data));
      navigate("/");
      Swal.fire({
        title: "Login Successful",
        icon: "success",
        toast: true,
        timer: 1500,
        position: "top-right",
        timerProgressBar: true,
        showConfirmButton: false,
      });
    } else {
      console.log(response.status);
      console.log("there was a server issue");
      // alert("Something went wrong" + response.status);
      Swal.fire({
        title: "Username or passowrd does not exists",
        icon: "error",
        toast: true,
        timer: 1500,
        position: "top-right",
        timerProgressBar: true,
        showConfirmButton: false,
      });
    }
  };

  // Register
  const registerUser = async (email, username, password, password2) => {
    const response = await fetch("http://127.0.0.1:8000/api/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        username,
        password,
        password2,
      }),
    });
    if (response.status === 201) {
      navigate("/login");
      Swal.fire({
        title: "Registration Successful, Login Now",
        icon: "success",
        toast: true,
        timer: 1500,
        position: "top-right",
        timerProgressBar: true,
        showConfirmButton: false,
      });
    } else {
      console.log(response.status);
      console.log("there was a server issue");
      // alert("Something went wrong" + response.status);
      Swal.fire({
        title: "An Error Occured " + response.status,
        icon: "error",
        toast: true,
        timer: 1500,
        position: "top-right",
        timerProgressBar: true,
        showConfirmButton: false,
      });
    }
  };

  // Logout
  const logoutUser = () => {
    setAuthTokens(null);
    setUser(null);
    localStorage.removeItem("authTokens");
    navigate("/login");
    Swal.fire({
      title: "Logging out!!",
      icon: "success",
      toast: true,
      timer: 1500,
      position: "top-right",
      timerProgressBar: true,
      showConfirmButton: false,
    });
  };

  const contextData = {
    user,
    setUser,
    authTokens,
    setAuthTokens,
    registerUser,
    loginUser,
    logoutUser,
  };

  useEffect(() => {
    if (authTokens) {
      setUser(jwtDecode(authTokens.access));
    }
    setLoading(false);
  }, [authTokens]);

  return (
    <AuthContext.Provider value={contextData}>
      {loading ? null : children}
    </AuthContext.Provider>
  );
};
