from dotenv import load_dotenv
import os
from openai import OpenAI   
load_dotenv()
from src.document_pre import json_to_docx_append_vertical_tables
import re
import json
import ast

def openai_model_with_mcp_tools(selected_tables, candidate):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    user_input = f"I need full data for: {candidate} from following tables only: {', '.join(selected_tables)} as JSON, don't include duplicate records across tables."
    response = client.responses.create(
    model="gpt-5",
    input=[
        {
        "role": "developer",
        "content": [
            {
            "type": "input_text",
            "text": "\"You are a helpful assistant. Answer the user's queries. When the user asks about a candidate, retrieve the full structured data using the connected MCP tool and respond strictly in Python-compatible JSON format (not a string).\n\nPlease follow these rules exactly:\n\n1. Always include the following top-level fields in the response: \n   - \\\"Candidate Name\\\"\n   - \\\"Date of Birth\\\"\n   - \\\"Inmate Number\\\"\n\n2. Do NOT wrap section data inside a \\\"Tables\\\" key. Each table name (e.g., \\\"Adult Suicide Additional Screening\\\") should be a top-level key.\n\n3. All keys must be transformed into human-readable text:\n   - Use Title Case\n   - Replace underscores with spaces\n\n4. The output must be Python-compatible:\n   - Use unquoted `False`, `True`, and `None` (not \\\"false\\\" or \\\"null\\\")\n   - All other values should be quoted strings where appropriate\n\n5. The entire response must be a single valid JSON object, not embedded in any Markdown or explanation text.\n\nReturn only the JSON object — no comments, descriptions, or headings.\""
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "input_text",
            "text": "I need full data for: James Hernandez from following table only: adult_suicide_additional_screening, adult_suicide_risk_scale, adult_special_accommodations"
            }
        ]
        },
        {
        "role": "assistant",
        "content": [
            {
            "type": "output_text",
            "text": "{\n  \"Candidate Name\": \"James Hernandez\",\n  \"Date of Birth\": \"1990-05-12\",\n  \"Inmate Number\": \"CA0001\",\n  \"Adult Suicide Additional Screening\": [\n    {\n      \"Screening ID\": 1,\n      \"Visible Self Harm Signs\": False,\n      \"Cuts Present\": False,\n      \"Ligature Marks Present\": False,\n      \"Other Self Harm Signs\": None,\n      \"Officer Or Family Reports Risk\": False,\n      \"Reports Risk Details\": None,\n      \"Position Of Respect Or Shocking Crime\": False,\n      \"Respect Details\": None,\n      \"Responding To Voices Or Strange Behavior\": False,\n      \"Voices Details\": None,\n      \"Serious Charge Murder Kidnapping Robbery Domestic\": False,\n      \"Serious Charge Details\": None,\n      \"Emergent Referral Needed\": False,\n      \"Urgent Referral Needed\": False,\n      \"Routine Referral Needed\": False,\n      \"Additional Comments\": None\n    }\n  ],\n  \"Adult Suicide Risk Scale\": [\n    {\n      \"Screening ID\": 1,\n      \"Wish You Were Dead\": False,\n      \"Wish Dead Explanation\": None,\n      \"Thoughts Of Killing Self\": False,\n      \"Thoughts Killing Explanation\": None,\n      \"Thinking How To Kill\": False,\n      \"Thinking How Explanation\": None,\n      \"Intention To Act\": False,\n      \"Intention Explanation\": None,\n      \"Worked Out Details\": False,\n      \"Worked Out Explanation\": None,\n      \"Ever Prepared Or Done Anything\": False,\n      \"Self Harm Timeframe\": None\n    }\n  ],\n  \"Adult Special Accommodations\": [\n    {\n      \"Screening ID\": 1,\n      \"Needs Special Accommodations\": False,\n      \"Accommodation Seeing\": None,\n      \"Accommodation Hearing\": None,\n      \"Accommodation Walking\": None,\n      \"Accommodation Eating\": None,\n      \"Accommodation Sleeping\": None,\n      \"Accommodation Thinking\": None,\n      \"Accommodation Communicating\": None,\n      \"Other Accommodations\": None\n    }\n  ]\n}"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "input_text",
            "text": user_input
            }
        ]
        }
    ],
    text={
        "format": {
        "type": "text"
        },
        "verbosity": "medium"
    },
    reasoning={
        "effort": "medium",
        "summary": "auto"
    },
    tools=[
        {
        "type": "mcp",
        "server_label": "my_mcp_server_for_sarreno",
        "server_url": "https://sarrano-mcp-server-398219119144.us-central1.run.app/mcp/",
        "allowed_tools": [
            "Bigquery_tool"
        ],
        "require_approval": "never"
        }
    ],
    store=True,
    include=[
        "reasoning.encrypted_content",
        "web_search_call.action.sources"
    ]
    )
    print(f"Response: {response.output_text}")
    match = re.search(r'\{[\s\S]*\}', response.output_text)
    if match:
        json_data = match.group(0)
        try:
            input_json = ast.literal_eval(json_data)  # ✅ handles Python booleans/None
            print(f"Extracted JSON: {input_json}")
            json_to_docx_append_vertical_tables(input_json)
            return input_json
        except Exception as e:
            print(f"Error parsing assistant output: {e}")
            return response.output_text
    else:
        return response.output_text



# import anthropic
# from src.utilities import merge_response_text
# client = anthropic.Anthropic(
#     # defaults to os.environ.get("ANTHROPIC_API_KEY")
#     api_key=os.getenv("ANTHROPIC_API_KEY"),
# )
# def anthropic_model_with_mcp_tools(user_input):
#     response = client.beta.messages.create(
#     model="claude-sonnet-4-20250514",
#     max_tokens=1000,
#     messages=[{
#         "role": "user",
#         "content": user_input
#     }],
#     mcp_servers=[{
#         "type": "url",
#         "url": "https://sarrano-mcp-server-398219119144.us-central1.run.app/mcp/",
#         "name": "example-mcp",
#     }],
#     betas=["mcp-client-2025-04-04"]
#     )
#     print(f"Response: {response}")
    
#     # return response.content[0].text
#     final_res = merge_response_text(response)
    
#     return final_res