"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Logout() {
  const router = useRouter();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      setVisible(true);
    } else {
      setVisible(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    setVisible(false); // Hide the button immediately after logout
    router.push("/login");
  };

  return visible ? <button onClick={handleLogout}>Logout</button> : null;
}
