from openai import OpenAI
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Example lead data
lead = {
    "name": "Michael",
    "company": "Harbor Construction Co",
    "email": "michael@harborco.com"
}

# Ask your Agent to write the outreach email
response = client.responses.create(
    model="gpt-5",
    input=f"Write a confident, brand-aligned cold outreach email from Bluechip Branding & Design to {lead['company']} about improving their brand image and web presence.",
)

email_body = response.output_text

# ---- SEND THE EMAIL ---- #
msg = MIMEText(email_body, "plain")
msg["Subject"] = f"Brand Excellence for {lead['company']}"
msg["From"] = "niko@bluechipbranding.com"
msg["To"] = lead["email"]

# Replace these with your SMTP credentials
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "founder@bluechipbranding.net"
smtp_pass = "lehriojtrfuzkyuo"  # Use an App Password, not your real one

server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(smtp_user, smtp_pass)
server.sendmail(msg["From"], [msg["To"]], msg.as_string())
server.quit()

print("✅ Email sent to", lead["email"])
