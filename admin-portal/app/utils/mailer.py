import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from jinja2 import Template

# Load HTML template (only once)
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "TeamRegisteration2.html")
with open(TEMPLATE_PATH) as f:
    html_template = Template(f.read())

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def send_mail(to_email, subject, name, team_name):
    msg = MIMEMultipart("alternative")
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    html_body = html_template.render(name=name, team_name=team_name)

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
        print(f"[✓] Mail sent to {to_email}")
    except Exception as e:
        print(f"[✗] Failed to send mail to {to_email}: {e}")
