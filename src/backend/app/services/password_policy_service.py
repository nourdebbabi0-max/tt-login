from typing import List


MOTS_DE_PASSE_BLOQUES = {
    "password",
    "password123",
    "123456",
    "12345678",
    "azerty",
    "azerty123",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "tunisietelecom",
    "tunisie telecom",
    "tunisietelecom123",
    "tt123456",
    "sarra1234",
}


LONGUEUR_MIN = 12
LONGUEUR_MAX = 64


def normaliser_texte(valeur: str) -> str:
    return (valeur or "").strip().lower()


def contient_element_personnel(mot_de_passe: str, valeurs_personnelles: List[str]) -> bool:
    mot_de_passe_normalise = normaliser_texte(mot_de_passe)

    for valeur in valeurs_personnelles:
        valeur_norm = normaliser_texte(valeur)
        if valeur_norm and len(valeur_norm) >= 3 and valeur_norm in mot_de_passe_normalise:
            return True

    return False


def contient_majuscule(mot_de_passe: str) -> bool:
    return any(c.isupper() for c in mot_de_passe)


def contient_minuscule(mot_de_passe: str) -> bool:
    return any(c.islower() for c in mot_de_passe)


def contient_chiffre(mot_de_passe: str) -> bool:
    return any(c.isdigit() for c in mot_de_passe)


def contient_caractere_special(mot_de_passe: str) -> bool:
    return any(not c.isalnum() for c in mot_de_passe)


def evaluer_force_mot_de_passe(mot_de_passe: str) -> str:
    score = 0

    if len(mot_de_passe) >= 12:
        score += 1
    if len(mot_de_passe) >= 16:
        score += 1
    if contient_majuscule(mot_de_passe) and contient_minuscule(mot_de_passe):
        score += 1
    if contient_chiffre(mot_de_passe):
        score += 1
    if contient_caractere_special(mot_de_passe):
        score += 1

    if score <= 2:
        return "faible"
    if score == 3:
        return "moyen"
    if score == 4:
        return "fort"
    return "excellent"


def valider_nouveau_mot_de_passe(
    mot_de_passe: str,
    confirmation: str,
    email: str = "",
    nom_complet: str = "",
    departement: str = "",
    ancien_mot_de_passe: str = ""
):
    erreurs = []

    if mot_de_passe != confirmation:
        erreurs.append("La confirmation du mot de passe est incorrecte.")

    if len(mot_de_passe) < LONGUEUR_MIN:
        erreurs.append(f"Le mot de passe doit contenir au moins {LONGUEUR_MIN} caractères.")

    if len(mot_de_passe) > LONGUEUR_MAX:
        erreurs.append(f"Le mot de passe doit contenir au maximum {LONGUEUR_MAX} caractères.")

    mot_de_passe_normalise = normaliser_texte(mot_de_passe)

    if mot_de_passe_normalise in MOTS_DE_PASSE_BLOQUES:
        erreurs.append("Ce mot de passe est trop faible ou trop courant.")

    valeurs_personnelles = [email, nom_complet, departement]

    if contient_element_personnel(mot_de_passe, valeurs_personnelles):
        erreurs.append("Le mot de passe est trop proche de vos informations personnelles.")

    if ancien_mot_de_passe and mot_de_passe == ancien_mot_de_passe:
        erreurs.append("Le nouveau mot de passe doit être différent de l'ancien.")

    if not contient_majuscule(mot_de_passe):
        erreurs.append("Le mot de passe doit contenir au moins une majuscule.")

    if not contient_minuscule(mot_de_passe):
        erreurs.append("Le mot de passe doit contenir au moins une minuscule.")

    if not contient_chiffre(mot_de_passe):
        erreurs.append("Le mot de passe doit contenir au moins un chiffre.")

    if not contient_caractere_special(mot_de_passe):
        erreurs.append("Le mot de passe doit contenir au moins un caractère spécial.")

    force = evaluer_force_mot_de_passe(mot_de_passe)

    return {
        "valide": len(erreurs) == 0,
        "force": force,
        "erreurs": erreurs
    }