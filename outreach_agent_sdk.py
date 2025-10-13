import os
import asyncio
from openai import OpenAI
from openai.agents import Agent, ModelSettings, TResponseInputItem, Runner, RunConfig
from openai.types.shared.reasoning import Reasoning
from pydantic import BaseModel
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# Load .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Initialize client ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Define your Agent ---
outreach_agent = Agent(
    name="Bluechip Outreach Agent",
    instructions="""You are the Bluechip Outreach Agent — a professional, calculated, and confident AI assistant designed to represent Bluechip Branding & Design. 
Your job is to craft cold outreach emails, follow-ups, and partnership proposals that feel sophisticated, persuasive, and aligned with Bluechip’s tone: confident, calm, collected, and slightly arrogant. 
Avoid fluff or casual language — communicate like a top-tier branding agency speaking to blue-chip companies. 
Use clean formatting, short paragraphs, and strategic pauses. When given a client profile or company info, tailor every outreach message with specific value propositions tied to branding, growth, and design excellence.""",
    model="gpt-5",
    model_settings=ModelSettings(
        store=True,
        reasoning=Reasoning(
            effort="low",
            summary="auto"
        )
    ),
)

# --- Input Schema ---
class WorkflowInput(BaseModel):
    input_as_text: str

# --- Main logic ---
async def run_workflow(workflow_input: WorkflowInput):
    conversation_history: list[TResponseInputItem] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": workflow_input.input_as_text
                }
            ]
        }
    ]

    outreach_agent_result_temp = await Runner.run(
        outreach_agent,
        input=[*conversation_history],
        run_config=RunConfig(trace_metadata={
            "__trace_source__": "agent-builder",
            "workflow_id": "wf_68ea953f401081908b577db3a1a8593a0b8e69bdcf367ce5"  # optional
        })
    )

    output_text = outreach_agent_result_temp.final_output_as(str)
    return output_text


# --- Example execution ---
async def main():
    # Example lead data
    lead = {
        "name": "Michael",
        "company": "Harbor Construction Co",
        "email": "michael@harborco.com"
    }

    print("💼 Generating email for", lead["company"], "...")
    email_body = await run_workflow(WorkflowInput(
        input_as_text=f"Write a cold outreach email to {lead['company']} ({lead['email']}). Emphasize brand transformation and web presence improvement."
    ))

    print("\n📝 Email Draft:\n", email_body)

    # ---- SEND THE EMAIL ---- #
    msg = MIMEText(email_body, "plain")
    msg["Subject"] = f"Brand Excellence for {lead['company']}"
    msg["From"] = "niko@bluechipbranding.com"
    msg["To"] = lead["email"]

    # Gmail SMTP setup
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "founder@bluechipbranding.net"
    smtp_pass = "lehriojtrfuzkyuo"  # no spaces in password

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        server.quit()
        print(f"✅ Email successfully sent to {lead['email']}")
    except Exception as e:
        print("❌ Failed to send email:", e)


if __name__ == "__main__":
    asyncio.run(main())
