const POWERBI_BASE_URL =
  "https://app.powerbi.com/reportEmbed?reportId=5d256c49-6f29-4373-9e4d-5e79f7ce8f2f&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730";

export const POWERBI_REPORT_URL = POWERBI_BASE_URL;

export const POWERBI_PAGE_NAMES = {
  home: "bc113abc10090200e7cc",
  avances: "566f97f9d8e1142f1b5c",
  avancesHeure: "8484c602d1e0b3ed3028",
  remboursement: "44036677b3a90310a60d",
  remboursementHeure: "52052b28c12034c84962",
  service: "e8828f907d290444390e",
  aideDecision: "f43b7eb805ad49f4dd56"
};

export function getPowerBiPageUrl(pageName) {
  const baseUrl =
    `${POWERBI_BASE_URL}&filterPaneEnabled=false&navContentPaneEnabled=false`;

  if (!pageName) {
    return baseUrl;
  }

  return `${baseUrl}&pageName=${encodeURIComponent(pageName)}`;
}