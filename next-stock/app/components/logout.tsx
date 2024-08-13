"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./authContext"; // Adjust the path based on your directory structure

export default function Logout() {
  const router = useRouter();
  const { token, setToken } = useAuth();

  const handleLogout = () => {
    if (token) {
      localStorage.removeItem("access_token");
      setToken(null);
      router.push("/login");
    }
  };

  if (!token) return null; // Hide button if not logged in

  return <button onClick={handleLogout}>Logout</button>;
}
