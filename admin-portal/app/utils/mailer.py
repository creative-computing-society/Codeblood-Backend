import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from jinja2 import Template

# Dynamically construct the absolute path
file_path = os.path.join(os.getcwd(), "app", "utils", "TEAMCOMPLETE.html")

# Load HTML template (only once)
with open(file_path, "r", encoding="utf-8") as f:
    html_template = Template(f.read())

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

def send_mail(to_email, subject, name, team_name, team_code):
    """
    Sends an email using the provided template and dynamic fields.
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    # Render the HTML body with the new team_code field
    html_body = html_template.render(name=name, team_name=team_name, team_code=team_code)

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
        print(f"[✓] Mail sent to {to_email}")
    except Exception as e:
        print(f"[✗] Failed to send mail to {to_email}: {e}")
