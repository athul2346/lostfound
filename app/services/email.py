import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USER:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_item_verification_email(to: str, item_id, token) -> None:
    link = f"{settings.BASE_URL}/items/{item_id}/verify?token={token}"
    send_email(
        to,
        "Verify your Lost & Found post",
        f"Confirm your item post by clicking this link:\n{link}\n\n"
        f"Keep this link safe. You'll use it later to review claims.",
    )


def send_claim_verification_email(to: str, claim_id, token) -> None:
    link = f"{settings.BASE_URL}/claims/{claim_id}/verify?token={token}"
    send_email(
        to,
        "Verify your claim",
        f"Confirm your claim by clicking this link:\n{link}",
    )


def send_new_claim_notification(finder_email: str, item_id, item_token, item_title: str) -> None:
    link = f"{settings.BASE_URL}/items/{item_id}/claims?token={item_token}"
    send_email(
        finder_email,
        f"New claim on your item: {item_title}",
        f"Someone has claimed '{item_title}'. Review the claim and accept or reject it here:\n{link}",
    )