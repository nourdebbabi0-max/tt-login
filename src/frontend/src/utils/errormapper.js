export function extractApiError(error) {
  if (!error) {
    return "Une erreur inattendue est survenue.";
  }

  if (typeof error === "string") {
    return error;
  }

  if (typeof error?.detail === "string") {
    return error.detail;
  }

  if (typeof error?.message === "string") {
    return error.message;
  }

  if (typeof error?.detail?.detail === "string") {
    return error.detail.detail;
  }

  if (typeof error?.detail?.code === "string") {
    switch (error.detail.code) {
      case "AUTH_FAILED":
        return "Email ou mot de passe incorrect.";
      case "ACCOUNT_TEMP_BLOCKED":
        return "Accès temporairement restreint. Veuillez réessayer plus tard.";
      case "ACCOUNT_INACTIVE":
        return "Compte désactivé.";
      case "ACCOUNT_NOT_ACTIVATED":
        return "Compte non activé.";
      default:
        return error.detail.detail || "Une erreur inattendue est survenue.";
    }
  }

  return "Une erreur inattendue est survenue.";
}