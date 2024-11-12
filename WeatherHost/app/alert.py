from app.database import get_all_subscribers
import smtplib
from email.message import EmailMessage
import os


def send_alert_to_users(alert_message):
        subscribers = get_all_subscribers()

        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('EMAIL_KEY')

        for subscriber in subscribers:
            recipient_email = subscriber[0]
            recipient_username = subscriber[1]
            try:
                email = EmailMessage()
                email['Subject'] = "Weather Alert Notification"
                email['From'] = sender_email
                email['To'] = recipient_email

                full_email = f"""
                Dear {recipient_username},
                
                {alert_message}
                
                Regards,
                WeatherSummarizer Team
                """
                email.set_content(full_email)

                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.starttls()
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(email)
                    # Output confirmation message
                    print(f"Email sent to {recipient_username} ({recipient_email})")

            except Exception as e:
                print(f"email error for recipient: {recipient_email}")
                raise
