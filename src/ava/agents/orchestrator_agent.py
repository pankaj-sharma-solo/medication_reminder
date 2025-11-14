from datetime import datetime

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from ..prompts import TODO_USAGE_INSTRUCTIONS, FILE_USAGE_INSTRUCTIONS, SUBAGENT_USAGE_INSTRUCTIONS, ORCHESTRATOR_INSTRUCTIONS
from ..states.state import DeepAgentState
from ..tools.file_tools import ls, read_file, write_file
from ..tools.task_tool import _create_task_tool
from ..tools.todo_tool import write_todo, read_todo
from ..tools.user_query_parsing_tools import think_tool, parse_and_validate_schedule, request_user_confirmation

model = init_chat_model(model="google_genai:gemini-2.5-flash-preview-09-2025", temperature=0.0)

built_in_tools = [ls, read_file, write_file, write_todo, read_todo, think_tool]

sub_agent_tools = [parse_and_validate_schedule, request_user_confirmation]

orchestrator_sub_agent = {
    "name": "medication-agent",
    "description": "Delegate research to the sub-agent medication.",
    "prompt": ORCHESTRATOR_INSTRUCTIONS.format(date=datetime.now().strftime("%a %b %-d, %Y")),
    "tools": ["parse_and_validate_schedule", "request_user_confirmation", "think_tool"],
}

task_tool = _create_task_tool(
    sub_agent_tools, [orchestrator_sub_agent], model, DeepAgentState
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