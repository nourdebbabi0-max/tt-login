import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

/* AUTH - chargés directement */
import LoginPage from "../pages/auth/login.jsx";
import ForgotPasswordPage from "../pages/auth/forgotpassword.jsx";
import ResetPasswordPage from "../pages/auth/resetpassword.jsx";
import FirstLoginPage from "../pages/auth/firstlogin.jsx";
import SecureRecoveryRequestPage from "../pages/auth/securerequest.jsx";
import SecureRecoveryValidatePage from "../pages/auth/securerevalidate.jsx";
import SecureRecoveryResetPage from "../pages/auth/securereset.jsx";

/* SYSTEM - chargés directement */
import UnauthorizedPage from "../pages/system/unauthorizedpage.jsx";
import NotFoundPage from "../pages/system/notfoundpage.jsx";
import SessionExpiredPage from "../pages/system/sessionexpiredpage.jsx";

/* APP / DASHBOARD - chargés seulement quand nécessaire */
const ProtectedRoute = lazy(() => import("../components/layout/protectedroute.jsx"));
const AppShell = lazy(() => import("../components/layout/appshell.jsx"));
const DepartmentRoute = lazy(() => import("../components/layout/departmentroute.jsx"));

const HomePage = lazy(() => import("../dashboard/homepage.jsx"));
const PowerBIDashboardPage = lazy(() => import("../dashboard/powerbidashboardpage.jsx"));
const CommercialParcSosDataPage = lazy(() =>
  import("../dashboard/commercialparcsosdatapage.jsx")
);
const CommercialBadDebtsPage = lazy(() =>
  import("../dashboard/commercialbaddebtspage.jsx")
);
const AnalyseEltPage = lazy(() => import("../dashboard/analyseeltpage.jsx"));
const AnalyseRapportsFinauxPage = lazy(() =>
  import("../dashboard/analyserapportsfinauxpage.jsx")
);
const AdminUsersPage = lazy(() => import("../dashboard/adminuserspage.jsx"));

function PageLoader() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background: "#061633",
        color: "white",
        fontSize: "20px",
        fontWeight: 700
      }}
    >
      Chargement...
    </div>
  );
}

function ProtectedAppLayout() {
  return (
    <ProtectedRoute>
      <AppShell />
    </ProtectedRoute>
  );
}

function CommercialOrAdmin({ children }) {
  return (
    <DepartmentRoute allowed={["Commercial", "Administration"]}>
      {children}
    </DepartmentRoute>
  );
}

function AnalyseOrAdmin({ children }) {
  return (
    <DepartmentRoute
      allowed={[
        "Analyse Operationnel",
        "Analyse Opérationnel",
        "Administration"
      ]}
    >
      {children}
    </DepartmentRoute>
  );
}

export default function Router() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* REDIRECTION */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* AUTH */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/mot-de-passe-oublie" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/premiere-connexion" element={<FirstLoginPage />} />

        <Route
          path="/recuperation-securisee/request"
          element={<SecureRecoveryRequestPage />}
        />

        <Route
          path="/recuperation-securisee/validate"
          element={<SecureRecoveryValidatePage />}
        />

        <Route
          path="/recuperation-securisee/reset"
          element={<SecureRecoveryResetPage />}
        />

        {/* SYSTEM */}
        <Route path="/session-expiree" element={<SessionExpiredPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* APP */}
        <Route path="/app" element={<ProtectedAppLayout />}>
          {/* HOME PLATFORM */}
          <Route index element={<HomePage />} />

          {/* ADMIN ONLY */}
          <Route
            path="admin/utilisateurs"
            element={
              <DepartmentRoute allowed={["Administration"]}>
                <AdminUsersPage />
              </DepartmentRoute>
            }
          />

          {/* POWER BI - COMMERCIAL + ADMIN */}
          <Route
            path="powerbi/home"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="home" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/avances"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="avances" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/avances-heure"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="avancesHeure" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/remboursement"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="remboursement" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/remboursement-heure"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="remboursementHeure" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/service"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="service" />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="powerbi/aide-decision"
            element={
              <CommercialOrAdmin>
                <PowerBIDashboardPage pageKey="aideDecision" />
              </CommercialOrAdmin>
            }
          />

          {/* AUTRES PAGES COMMERCIAL */}
          <Route
            path="commercial/parc-sos-data"
            element={
              <CommercialOrAdmin>
                <CommercialParcSosDataPage />
              </CommercialOrAdmin>
            }
          />

          <Route
            path="commercial/bad-debts"
            element={
              <CommercialOrAdmin>
                <CommercialBadDebtsPage />
              </CommercialOrAdmin>
            }
          />

          {/* ANALYSE + ADMIN */}
          <Route
            path="analyse/elt"
            element={
              <AnalyseOrAdmin>
                <AnalyseEltPage />
              </AnalyseOrAdmin>
            }
          />

          <Route
            path="analyse/rapports-finaux"
            element={
              <AnalyseOrAdmin>
                <AnalyseRapportsFinauxPage />
              </AnalyseOrAdmin>
            }
          />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}