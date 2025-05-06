import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from dotenv import load_dotenv

# Load environment variables
load_dotenv(interpolate=True, override=True)

def get_email_config():
    try:
        email = os.getenv("email")
        password = os.getenv("password")
        smtp_server = os.getenv("smtp_server")
        port = os.getenv("port")

        if not email:
            raise ValueError("❌ email is missing in .env")
        if not password:
            raise ValueError("❌ password is missing in .env")
        if not smtp_server:
            raise ValueError("❌ smtp_server is missing in .env")
        if not port:
            raise ValueError("❌ port is missing in .env")

        return email, password, smtp_server, int(port)

    except Exception as e:
        print(f"⚠️ Error loading config: {e}")
        exit()

def send_mail(recipient_email, subject, body):
    email, password, smtp_server, port = get_email_config()

    # Create a MIME multipart message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = email
    message["To"] = recipient_email
    message["Date"] = formatdate(localtime=True)

    # Add HTML body
    html_part = MIMEText(body, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(email, recipient_email, message.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
