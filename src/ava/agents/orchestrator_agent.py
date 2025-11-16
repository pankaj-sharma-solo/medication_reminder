from datetime import datetime

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

from ..prompts import TODO_USAGE_INSTRUCTIONS, FILE_USAGE_INSTRUCTIONS, SUBAGENT_USAGE_INSTRUCTIONS, ORCHESTRATOR_INSTRUCTIONS, AMBIENT_SUBAGENT_USAGE_INSTRUCTIONS
from ..states.state import DeepAgentState
from ..tools.file_tools import ls, read_file, write_file
from ..tools.task_tool import _create_task_tool
from ..tools.todo_tool import write_todo, read_todo
from ..tools.user_query_parsing_tools import think_tool, parse_and_validate_schedule, persist_in_db
from ..tools.reminder_tools import process_reminder_call
import os

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-09-2025", temperature=0.0, google_api_key=os.getenv("GOOGLE_API_KEY"))

built_in_tools = [ls, read_file, write_file, write_todo, read_todo, think_tool]

sub_agent_tools = [parse_and_validate_schedule, process_reminder_call, think_tool, persist_in_db]

orchestrator_sub_agent = {
    "name": "medication-agent",
    "description": "Delegate medicinal task to the sub-agent medication.",
    "prompt": ORCHESTRATOR_INSTRUCTIONS.format(date=str(datetime.now())),
    "tools": ["parse_and_validate_schedule", "think_tool", "persist_in_db"],
}

reminder_sub_agent = {
    "name": "reminder-agent",
    "description": "Delegate reminder task to the sub-agent reminder.",
    "prompt": AMBIENT_SUBAGENT_USAGE_INSTRUCTIONS,
    "tools": ["process_reminder_call", "think_tool"],
}

task_tool = _create_task_tool(
    sub_agent_tools, [orchestrator_sub_agent, reminder_sub_agent], model, DeepAgentState
)

delegation_tools = [task_tool]
all_tools = sub_agent_tools + built_in_tools + delegation_tools
SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS

INSTRUCTIONS = (
    "# TODO MANAGEMENT\n"
    + TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# FILE SYSTEM USAGE\n"
    + FILE_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# SUB-AGENT DELEGATION\n"
    + SUBAGENT_INSTRUCTIONS
)

# Create agent
agent = create_agent(
    model=model,
    tools=all_tools,
    system_prompt=INSTRUCTIONS,
    state_schema=DeepAgentState
)