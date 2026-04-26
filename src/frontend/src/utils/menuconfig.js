const commercialMenu = [
  {
    label: "Voir le suivi des avances",
    path: "/app/commercial/avances"
  },
  {
    label: "Voir le suivi des remboursements",
    path: "/app/commercial/remboursement"
  },
  {
    label: "Voir les services",
    path: "/app/commercial/service"
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
    label: "Voir ELT",
    path: "/app/analyse/elt"
  },
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
    label: "Voir le suivi des avances",
    path: "/app/commercial/avances"
  },
  {
    label: "Voir le suivi des remboursements",
    path: "/app/commercial/remboursement"
  },
  {
    label: "Voir l’évolution des services",
    path: "/app/commercial/service"
  },
  {
    label: "Voir le suivi des bad debts",
    path: "/app/commercial/bad-debts"
  },
  {
    label: "Voir le suivi du parc SOS et DATA",
    path: "/app/commercial/parc-sos-data"
  },
  {
    label: "Voir ELT",
    path: "/app/analyse/elt"
  },
  {
    label: "Voir les rapports finaux",
    path: "/app/analyse/rapports-finaux"
  }
];

export function getMenuByDepartment(departement) {
  const value = (departement || "").trim().toLowerCase();

  if (value === "commercial") {
    return commercialMenu;
  }

  if (
    value === "analyse operationnel" ||
    value === "analyse opérationnel" ||
    value === "analyse operationnelle" ||
    value === "analyse opérationnelle"
  ) {
    return analyseMenu;
  }

  if (value === "administration" || value === "admin") {
    return adminMenu;
  }

  return [];
}