import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/layout/protectedroute.jsx";
import AppShell from "../components/layout/appshell.jsx";
import DepartmentRoute from "../components/layout/departmentroute.jsx";

/* AUTH */
import LoginPage from "../pages/auth/login.jsx";
import ForgotPasswordPage from "../pages/auth/forgotpassword.jsx";
import ResetPasswordPage from "../pages/auth/resetpassword.jsx";
import FirstLoginPage from "../pages/auth/firstlogin.jsx";
import SecureRecoveryRequestPage from "../pages/auth/securerequest.jsx";
import SecureRecoveryValidatePage from "../pages/auth/securerevalidate.jsx";
import SecureRecoveryResetPage from "../pages/auth/securereset.jsx";

/* DASHBOARD */
import HomePage from "../dashboard/homepage.jsx";
import CommercialAdvancedDashboardPage from "../dashboard/commercialadvanceddashboardpage.jsx";
import CommercialRemboursementPage from "../dashboard/commercialremboursementpage.jsx";
import CommercialServicePage from "../dashboard/commercialservicepage.jsx";
import CommercialParcSosDataPage from "../dashboard/commercialparcsosdatapage.jsx";
import CommercialBadDebtsPage from "../dashboard/commercialbaddebtspage.jsx";
import AnalyseEltPage from "../dashboard/analyseeltpage.jsx";
import AnalyseRapportsFinauxPage from "../dashboard/analyserapportsfinauxpage.jsx";
import AdminUsersPage from "../dashboard/adminuserspage.jsx";

/* SYSTEM */
import UnauthorizedPage from "../pages/system/unauthorizedpage.jsx";
import NotFoundPage from "../pages/system/notfoundpage.jsx";
import SessionExpiredPage from "../pages/system/sessionexpiredpage.jsx";

function ProtectedAppLayout() {
  return (
    <ProtectedRoute>
      <AppShell />
    </ProtectedRoute>
  );
}

export default function Router() {
  return (
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

        {/* HOME */}
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

        {/* COMMERCIAL + ADMIN */}
        <Route
          path="commercial/avances"
          element={
            <DepartmentRoute allowed={["Commercial", "Administration"]}>
              <CommercialAdvancedDashboardPage />
            </DepartmentRoute>
          }
        />

        <Route
          path="commercial/remboursement"
          element={
            <DepartmentRoute allowed={["Commercial", "Administration"]}>
              <CommercialRemboursementPage />
            </DepartmentRoute>
          }
        />

        <Route
          path="commercial/service"
          element={
            <DepartmentRoute allowed={["Commercial", "Administration"]}>
              <CommercialServicePage />
            </DepartmentRoute>
          }
        />

        <Route
          path="commercial/parc-sos-data"
          element={
            <DepartmentRoute allowed={["Commercial", "Administration"]}>
              <CommercialParcSosDataPage />
            </DepartmentRoute>
          }
        />

        <Route
          path="commercial/bad-debts"
          element={
            <DepartmentRoute allowed={["Commercial", "Administration"]}>
              <CommercialBadDebtsPage />
            </DepartmentRoute>
          }
        />

        {/* ANALYSE + ADMIN */}
        <Route
          path="analyse/elt"
          element={
            <DepartmentRoute allowed={["Analyse Operationnel", "Analyse Opérationnel", "Administration"]}>
              <AnalyseEltPage />
            </DepartmentRoute>
          }
        />

        <Route
          path="analyse/rapports-finaux"
          element={
            <DepartmentRoute allowed={["Analyse Operationnel", "Analyse Opérationnel", "Administration"]}>
              <AnalyseRapportsFinauxPage />
            </DepartmentRoute>
          }
        />
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}