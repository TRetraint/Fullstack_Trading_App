import smtplib, ssl
import config

context = ssl.create_default_context()

def send_email(subject, message, strategy):
    if message != []:
        with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
            server.login(config.EMAIL_ADRESS,config.EMAIL_PASSWORD)
            email_message = f"Subject: {subject}\n\n"
            email_message += f"\n\nStrategy: {strategy}"
            email_message += "\n\n".join(message)
            server.sendmail(config.EMAIL_ADRESS, config.EMAIL_ADRESS, email_message)