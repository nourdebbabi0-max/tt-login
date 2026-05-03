import { apiRequest } from "./client";

export function getFinalReportsRequest() {
  return apiRequest("/api/reports/final", {
    method: "GET"
  });
}

export function previewFinalReportRequest(filename) {
  return apiRequest(`/api/reports/final/${encodeURIComponent(filename)}/preview`, {
    method: "GET"
  });
}