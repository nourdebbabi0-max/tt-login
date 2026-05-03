const commercialMenu = [
  {
    label: "Home dashboard",
    path: "/app/powerbi/home"
  },
  {
    label: "Voir le suivi des avances",
    path: "/app/powerbi/avances"
  },
  {
    label: "Suivi par heure ADV",
    path: "/app/powerbi/avances-heure"
  },
  {
    label: "Voir le suivi des remboursements",
    path: "/app/powerbi/remboursement"
  },
  {
    label: "Suivi par heure REV",
    path: "/app/powerbi/remboursement-heure"
  },
  {
    label: "Voir les services",
    path: "/app/powerbi/service"
  },
  {
    label: "Aide à la décision",
    path: "/app/powerbi/aide-decision"
  },
  {
    label: "Voir l’évolution du parc SOS et DATA",
    path: "/app/commercial/parc-sos-data"
  },
  {
    label: "Voir le suivi des bad debts",
    path: "/app/commercial/bad-debts"
  }
];

const analyseMenu = [
  {
    label: "Voir les rapports finaux",
    path: "/app/analyse/rapports-finaux"
  }
];

const adminMenu = [
  {
    label: "Gérer les utilisateurs",
    path: "/app/admin/utilisateurs"
  },
  {
    label: "Home dashboard",
    path: "/app/powerbi/home"
  },
  {
    label: "Voir le suivi des avances",
    path: "/app/powerbi/avances"
  },
  {
    label: "Suivi par heure ADV",
    path: "/app/powerbi/avances-heure"
  },
  {
    label: "Voir le suivi des remboursements",
    path: "/app/powerbi/remboursement"
  },
  {
    label: "Suivi par heure REV",
    path: "/app/powerbi/remboursement-heure"
  },
  {
    label: "Voir les services",
    path: "/app/powerbi/service"
  },
  {
    label: "Aide à la décision",
    path: "/app/powerbi/aide-decision"
  },
  {
    label: "Voir l’évolution du parc SOS et DATA",
    path: "/app/commercial/parc-sos-data"
  },
  {
    label: "Voir le suivi des bad debts",
    path: "/app/commercial/bad-debts"
  },
  {
    label: "Voir les rapports finaux",
    path: "/app/analyse/rapports-finaux"
  }
];

export function getMenuByDepartment(departement) {
  const value = (departement || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

  if (value === "commercial") {
    return commercialMenu;
  }

  if (
    value === "analyse operationnel" ||
    value === "analyse operationnelle"
  ) {
    return analyseMenu;
  }

  if (value === "administration" || value === "admin") {
    return adminMenu;
  }

  return [];
}