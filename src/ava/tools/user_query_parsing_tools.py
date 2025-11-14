from datetime import datetime

from langchain.chat_models import init_chat_model
from langgraph.types import interrupt
from langchain_core.tools import tool
from pydantic import ValidationError

from src.ava.states.state import MedicationSchedule

model = init_chat_model(model="google_genai:gemini-2.5-flash-preview-09-2025", temperature=0.0)

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on workflow progress and decision-making within the Deep Agent Orchestrator.

    Use this tool after each critical agent/tool execution (e.g., parsing, database write, call initiation) to analyze the result and plan next steps systematically.
    This creates a deliberate pause in the workflow for quality control and sequential decision-making.

    When to use:
    - After receiving results from the **Scheduling Agent**: Was the structured data complete and valid?
    - After a **Database Write**: Was the data successfully persisted and did the write return a unique ID?
    - Before critical actions: Is the user confirmation (via **ConfirmHITL**) secured before initiating a final DB write or call?
    - Before concluding a flow: Have all steps (Parsing, Validation, Scheduling, Confirmation) been successfully executed?
    - When assessing error recovery: What crucial data is missing or invalid, and what is the plan to recover or prompt the user?

    Reflection should address:
    1. **Analysis of Tool Output**: What specific structured data or action result have I received (e.g., JSON schema, database status, unique ID)?
    2. **Data/Action Validation**: Is the output valid, complete, and does it meet the required format (e.g., are all medication fields present and correct)?
    3. **Workflow Integrity**: Is the next logical step in the sequence clear, or are there outstanding dependencies (like user confirmation)?
    4. **Strategic Decision**: Should I proceed to the next tool delegation, prompt the user for missing data, or conclude the conversation?

    Args:
        reflection: Your detailed reflection on workflow progress, tool output validation, current status, and next sequential action.

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"


@tool(args_schema=MedicationSchedule, parse_docstring=True)
def parse_and_validate_schedule(user_query: str) -> str:
    """
    Parses a natural language medication instruction from the user query into a
    structured object and validates it against the MedicationSchedule schema.

    Returns: A validated schedule data OR a string
             with an error key describing missing or invalid fields.
    """
    try:
        # Assume LLM output is a dictionary derived from user_query
        # The actual tool should contain the logic to call the LLM to get this dict
        structured_model = model.with_structured_output(MedicationSchedule)

        return f"SUCCESS_PARSED_DATA: {structured_model.invoke({"text": user_query})}"

    except ValidationError as e:
        return f"VALIDATION_ERROR: {e.errors()}"
    except Exception as e:
        return f"PARSING_ERROR: {str(e)}"


@tool(parse_docstring=True)
def request_user_confirmation(schedule_summary: str) -> str:
    """
    Triggers a Human-in-the-Loop interrupt to secure explicit user confirmation.
    Execution pauses here until the graph is resumed with the user's decision.
    """
    # This function call halts the graph. The payload is visible to the caller.
    # When the graph is resumed, 'user_decision' will be the value passed via Command(resume=...).
    user_decision = interrupt(
        {
            "action": "HITL_APPROVAL_REQUIRED",
            "summary": schedule_summary,
            "instruction": "Please respond with 'CONFIRM' or 'REJECT'."
        }
    )

    # After resume, 'user_decision' will be the user's input (e.g., "CONFIRMED")
    return user_decision