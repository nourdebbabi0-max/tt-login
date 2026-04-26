import smtplib
from email.message import EmailMessage
from app.core.config import settings


def _envoyer_email(destinataire: str, sujet: str, corps: str):
    msg = EmailMessage()
    msg["Subject"] = sujet
    msg["From"] = settings.SMTP_FROM
    msg["To"] = destinataire
    msg.set_content(corps)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email envoyé avec succès à {destinataire}")
    except Exception as e:
        print(f"❌ Erreur envoi email vers {destinataire} : {str(e)}")
        raise


def envoyer_email_activation(destinataire: str, nom_complet: str, activation_link: str):
    sujet = "Activation de votre compte - Plateforme TT"

    corps = f"""
Bonjour {nom_complet},

Votre compte a été créé sur la plateforme interne Tunisie Telecom.

Pour activer votre compte et définir votre mot de passe personnel, cliquez sur le lien ci-dessous :

{activation_link}

Ce lien expire dans 15 minutes.

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.

Cordialement,
Plateforme Interne TT
"""
    _envoyer_email(destinataire, sujet, corps)


def envoyer_email_reinitialisation(destinataire: str, nom_complet: str, reset_link: str):
    sujet = "Réinitialisation de votre mot de passe - Plateforme TT"

    corps = f"""
Bonjour {nom_complet},

Une demande de réinitialisation de mot de passe a été initiée pour votre compte.

Pour définir un nouveau mot de passe, cliquez sur le lien ci-dessous :

{reset_link}

Ce lien expire dans 15 minutes et ne peut être utilisé qu'une seule fois.

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.

Cordialement,
Plateforme Interne TT
"""
    _envoyer_email(destinataire, sujet, corps)


def envoyer_email_alerte_securite(
    destinataire: str,
    nom_complet: str,
    type_alerte: str,
    details: str = ""
):
    sujet = "Alerte sécurité - Plateforme TT"

    corps = f"""
Bonjour {nom_complet},

Une activité de sécurité inhabituelle a été détectée sur votre compte.

Type d'alerte :
{type_alerte}

Détails :
{details if details else "Plusieurs tentatives de connexion non réussies ont été détectées."}

Si vous êtes à l'origine de ces tentatives, vous pouvez ignorer ce message.
Sinon, nous vous recommandons de réinitialiser rapidement votre mot de passe.

Cordialement,
Plateforme Interne TT
"""
    _envoyer_email(destinataire, sujet, corps)


def envoyer_email_recuperation_securisee(
    destinataire: str,
    nom_complet: str,
    recovery_link: str,
    code_demande: str
):
    sujet = "Récupération sécurisée de votre mot de passe - Plateforme TT"

    corps = f"""
Bonjour {nom_complet},

Une demande de récupération sécurisée de mot de passe a été initiée pour votre compte.

Pour poursuivre la récupération, utilisez le lien sécurisé ci-dessous :

{recovery_link}

Code de demande à confirmer :
{code_demande}

Ce lien expire dans 15 minutes et ne peut être utilisé qu'une seule fois.

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.

Cordialement,
Plateforme Interne TT
"""
    _envoyer_email(destinataire, sujet, corps)