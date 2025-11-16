"""TODO management tools for task planning and progress tracking.

This module provides tools for creating and managing structured task lists
that enable agents to plan complex workflows and track progress through
multi-step operations.
"""

from typing import List, Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command

from ..prompts import WRITE_TODOS_DESCRIPTION
from ..states.state import Todo, DeepAgentState


@tool(description=WRITE_TODOS_DESCRIPTION)
def write_todo(
        todos: List[Todo],
        tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create or update the agent's TODO list for task planning and tracking.

    <Parameters>
    todos: List of Todo items with content and status
    tool_call_id: Tool call identifier for message response
    </Parameters>

    <Returns>
    Command to update agent state with new TODO list
    </Returns>

    **MANDATORY FORMAT EXAMPLE:**
   ```json
   {
    "todos": [
        { "content": "Parse user request for medication details (Metformin 500mg, 8 AM).", "status": "pending" },
        { "content": "Save extracted structured data to file system.", "status": "pending" },
        { "content": "Delegate validation and scheduling to the medication-agent.", "status": "pending" }
    ]
   }
   ```
    """
    return Command(
        update={
            'todos': todos,
            'messages': [
                ToolMessage(f"Updated todo list to {todos}", tool_call_id=tool_call_id)
            ]
        }
    )


@tool
def read_todo(
        state: DeepAgentState,
        tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Read the current TODO list from the agent state.
    This tool allows the agent to retrieve and review the current TODO list
    to stay focused on remaining tasks and track progress through complex workflows.
    """
    todos = state.get("todos", [])
    if not todos:
        return "No todos currently in the list."

    result = "Current TODO List:\n"
    for i, todo in enumerate(todos, 1):
        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
        emoji = status_emoji.get(todo["status"], "❓")
        result += f"{i}. {emoji} {todo['content']} ({todo['status']})\n"

    return result.strip()