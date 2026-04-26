import { apiRequest } from "./client";

export function loginRequest(payload) {
  return apiRequest("/api/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function checkSessionRequest() {
  return apiRequest("/api/session/check", {
    method: "GET"
  });
}

export function firstLoginChangePasswordRequest(payload) {
  return apiRequest("/api/change-password-first-login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function forgotPasswordRequest(payload) {
  return apiRequest("/api/password-forgot/request", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function resetPasswordRequest(payload) {
  return apiRequest("/api/password-forgot/reset", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function secureRecoveryRequest(payload) {
  return apiRequest("/api/password-recovery/secure-request", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function secureRecoveryValidateRequest(payload) {
  return apiRequest("/api/password-recovery/secure-validate", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function secureRecoveryResetRequest(payload) {
  return apiRequest("/api/password-recovery/secure-reset", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}