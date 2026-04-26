import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

function normalize(value) {
  return (value || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export default function DepartmentRoute({ allowed = [], children }) {
  const { user } = useAuth();

  const currentDepartment = normalize(user?.departement);
  const allowedDepartments = allowed.map(normalize);

  if (!allowedDepartments.includes(currentDepartment)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}