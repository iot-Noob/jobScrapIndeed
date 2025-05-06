import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate  # Add this

# Configuration
smtp_server = "mail.cybertalha.com"  # Changed from IP to domain
smtp_port = 587
sender_email = "python@cybertalha.com"
sender_password = "Talha@6295"
recipient_email = "talha@talhamail.com"

# Create message
message = MIMEText("This is a test email sent from Python.")
message["Subject"] = "Test Email"
message["From"] = sender_email
message["To"] = recipient_email
message["Date"] = formatdate(localtime=True)  # Fixes 1970 date issue

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
