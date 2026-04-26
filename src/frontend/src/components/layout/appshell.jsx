import { Outlet } from "react-router-dom";
import { useEffect } from "react";
import Sidebar from "../sidebar";
import Topbar from "./topbar";
import { useAuth } from "../../hooks/useAuth";

export default function AppShell() {
  const { checkSession } = useAuth();

  useEffect(() => {
    const interval = setInterval(() => {
      checkSession();
    }, 3 * 60 * 1000);

    return () => clearInterval(interval);
  }, [checkSession]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Topbar />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}