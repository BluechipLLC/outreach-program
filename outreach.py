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
  instructions="""1. Use Web Search to find ONE local business in Massachusetts.
2. Analyze this single business's website and branding.
3. Give it a "Need Score" (0–100) based on:
   - Website design quality
   - Branding consistency  
   - Mobile-friendliness
   - Overall professional appearance
4. Provide a brief analysis in this format:
   Business Name: [name]
   Website: [url]
   Type: [business type]
   Need Score: [0-100]
   Analysis: [2-3 sentences about their branding needs]

5. If the Need Score is 60 or higher, automatically send a TEST outreach email using the send_email function with:
   - to: bacopoulosluke@gmail.com (TEST EMAIL - not the business owner)
   - subject: "TEST: Quick Question About Your Website - [Business Name]"
   - body: A professional outreach message about improving their branding/website (include "TEST EMAIL" at the top)

Guidelines:
- Focus on ONE business only
- Be quick and concise
- Look for obvious branding issues
- Use fresh data from Web Search
- ALWAYS send a TEST email if Need Score >= 60
- Send ALL test emails to bacopoulosluke@gmail.com

When asked to send an email, call the send_email function with the recipient email, subject, and body.""",
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
