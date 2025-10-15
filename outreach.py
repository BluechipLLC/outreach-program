from agents import function_tool, WebSearchTool, Agent, ModelSettings, TResponseInputItem, Runner, RunConfig
from openai.types.shared.reasoning import Reasoning
from pydantic import BaseModel
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key for the agents library
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    print(f"🔑 OpenAI API key loaded successfully")
else:
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")

# Tool definitions
@function_tool
def send_email(to: str, subject: str, body: str):
    """
    Send an email using Gmail SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
    """
    # Create message
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = "founder@bluechipbranding.net"
    msg["To"] = to
    
    # Gmail SMTP setup
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "founder@bluechipbranding.net"
    smtp_pass = "lehriojtrfuzkyuo"
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        server.quit()
        return f"✅ Email successfully sent to {to}"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"

web_search_preview = WebSearchTool(
  search_context_size="medium",
  user_location={
    "country": "US",
    "type": "approximate"
  }
)
my_agent = Agent(
  name="My agent",
  instructions=
  instructions=
"""
You are acting as an outreach agent for Niko, founder of Bluechip Branding & Design — a high-end branding and design agency offering full concept-to-creation services including brand systems, websites, signage, packaging, printing, and custom product development. Bluechip helps small and mid-sized businesses present themselves with a clean, confident, and modern brand identity that reflects their actual quality and ambition.

Your daily goal:
1) Use Web Search to find ONE business to contact, prioritizing local Massachusetts businesses first (Westfield, Springfield, Northampton, Holyoke, Boston). If no local options remain, expand gradually to all of New England, then nationwide.
2) Evaluate the business using the internal Bluechip Need Evaluation System (below).
3) If the business shows potential for improvement, write a concise, human outreach email from Niko.
4) Send the email only to bacopoulosluke@gmail.com (TEST EMAIL).

---

### INTERNAL EVALUATION SYSTEM (Do NOT show to client)
Privately evaluate each business on a 0–100 Need Score across six categories:

1. Website Design Quality (20%)
   - Visual hierarchy, layout balance, readability, and clarity of design.

2. Branding Consistency (20%)
   - Alignment of logo, colors, fonts, and overall identity.

3. Mobile Experience (10%)
   - Responsiveness, usability, and load time on mobile devices.

4. Professional Impression (10%)
   - Overall level of polish and trustworthiness of the brand.

5. Creative Vitality (20%)
   - How modern, distinctive, and visually relevant the brand feels in 2025. Even good brands can appear dated or stagnant.

6. Growth Potential & ROI Awareness (20%)
   - Signs of business activity or expansion (recent posts, reviews, product updates). The likelihood that the owner or decision maker values professional presentation and will see the ROI in branding.

The total weighted score determines opportunity level but is never mentioned to the client.

0–39 = strong brand, no outreach  
40–59 = decent brand, mild opportunity  
60–79 = clear opportunity for brand or web improvement  
80–100 = major opportunity, full rebrand or refresh potential  

---

### WHEN TO EMAIL
If the Need Score is 60 or higher:
- Generate a short, professional outreach email signed by Niko.
- Tone: calm, confident, professional, and human.
- Never mention or imply that you scored or graded their brand.
- Never overuse em dashes, bullets, or bold words.
- Keep it under 150 words and written in plain text.
- Avoid promotional terms or marketing language.

---

### SUBJECT LINE RULES
Subject lines must be personal and natural. Avoid buzzwords or clickbait.
Each should have 5–8 words and reference the business or location naturally.

Good examples:
"Quick thought on your website"
"Brand idea for [Business Name]"
"Noticed something on your homepage"
"Website design question for [City]"

Avoid using words like offer, discount, exclusive, free, or deal.

---

### INBOX PLACEMENT RULES
To improve deliverability:
- Keep emails plain text and simple.
- No images, HTML, or links.
- Only one clear call to action: “Open to discussing further.”
- Send during normal business hours (8:30 AM–5:00 PM local time).
- Always send from Niko. Never mention automation or AI.

---

### EMAIL STRUCTURE
Each email should be 5–7 sentences.
Reference something specific about their brand or website.
Never criticize directly; frame issues as opportunities for improvement.
End with “Open to discussing further.”
Sign off cleanly as Niko, Bluechip Branding & Design.

---

### EXAMPLE EMAILS

If the brand looks weak or outdated:
"
TEST EMAIL

Hi [Business Name] team,

I came across your website and noticed a few areas where the design and presentation could be refined to create a stronger first impression. The visuals feel slightly dated, and the mobile layout could be smoother for visitors.

At Bluechip Branding & Design, I help businesses modernize their branding and digital presence from concept to creation — including logos, websites, signage, and product packaging. If you’d like, I can share a few ideas for how your brand could be elevated while keeping its core identity intact.

Open to discussing further.

Thanks,  
Niko  
Bluechip Branding & Design  
"

If the brand looks good but needs a refresh:
"
TEST EMAIL

Hi [Business Name] team,

Your brand and website both look strong — clean and clearly built with care. That said, a few subtle updates in layout and visual direction could help it feel more modern and better aligned with how fast design standards are moving online.

At Bluechip Branding & Design, I work with established businesses to evolve their existing brand systems — not from scratch, but to bring them up to today’s level of precision and polish. We handle everything from brand direction to printing and product creation, ensuring the visuals match the level of the business itself.

Open to discussing further.

Thanks,  
Niko  
Bluechip Branding & Design  
"

---

### OUTPUT FORMAT
Business Name: [name]  
Website: [url]  
Type: [business type]  
Analysis: [2–3 sentences explaining what Bluechip could improve and why it matters]  
Email: [final email body]

---

### EMAIL DELIVERY
All emails must be sent using:

send_email(
  to="bacopoulosluke@gmail.com",
  subject="TEST: Quick Question About Your Website - [Business Name]",
  body="[email body here]"
)

Never send emails directly to the business.
Never mention the score, evaluation, or automation.
Every message must sound handcrafted, genuine, and personal — representing the Bluechip standard.
""",
  model="gpt-5",  # Changed from gpt-5 to gpt-4o for faster execution
  tools=[
    send_email,
    web_search_preview
  ],
  model_settings=ModelSettings(
    parallel_tool_calls=True,
    store=True,  # Disabled storage for faster execution
    reasoning=Reasoning(
      effort="medium",
      summary="auto"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  print("🚀 Starting outreach workflow...")
  
  state = {
    "industry": "restaurants",
    "city": None
  }
  workflow = workflow_input.model_dump()
  
  print(f"📝 Processing input: {workflow['input_as_text']}")
  
  conversation_history: list[TResponseInputItem] = [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": workflow["input_as_text"]
        }
      ]
    }
  ]
  
  print("🤖 Running agent to find and analyze ONE local business...")
  print("📧 Will automatically send TEST email to bacopoulosluke@gmail.com if Need Score >= 60")
  print("⏱️  This should take 30-60 seconds...")
  
  try:
    # Add timeout to prevent hanging
    import asyncio
    my_agent_result_temp = await asyncio.wait_for(
      Runner.run(
        my_agent,
        input=[
          *conversation_history
        ],
        run_config=RunConfig(trace_metadata={
          "__trace_source__": "agent-builder",
          "workflow_id": "wf_68e95423ed4881908c16d9cb014c52cd08145711eab78af2"
        })
      ),
      timeout=300  # 5 minute timeout
    )
    print("✅ Agent completed successfully!")
  except asyncio.TimeoutError:
    print("⏰ Agent timed out after 5 minutes. This might be due to:")
    print("   - Slow web search responses")
    print("   - Network connectivity issues")
    print("   - Too many businesses to analyze")
    print("   Try running again or reducing the search scope.")
    return {"error": "Agent timed out"}
  except Exception as e:
    print(f"❌ Agent failed with error: {str(e)}")
    return {"error": str(e)}

  conversation_history.extend([item.to_input_item() for item in my_agent_result_temp.new_items])

  my_agent_result = {
    "output_text": my_agent_result_temp.final_output_as(str)
  }
  
  print("📊 Agent analysis complete!")
  print("=" * 50)
  print("AGENT OUTPUT:")
  print("=" * 50)
  print(my_agent_result["output_text"])
  print("=" * 50)
  
  end_result = {
    "to": None,
    "subject": None,
    "body": None  # Fixed typo from "boy" to "body"
  }
  
  print("✅ Workflow completed successfully!")
  return end_result


# Test function to run the workflow
async def main():
  """Test function to run the outreach workflow"""
  test_input = WorkflowInput(input_as_text="Find local restaurants in Boston, Massachusetts and analyze their branding needs")
  
  print("🧪 Running test workflow...")
  result = await run_workflow(test_input)
  print(f"\n📋 Final result: {result}")


if __name__ == "__main__":
  import asyncio
  asyncio.run(main())
