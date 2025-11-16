from typing import Literal, Annotated
from typing_extensions import TypedDict, NotRequired
from langchain.agents import AgentState
from pydantic import BaseModel, Field, PositiveInt
from typing import Optional

class Todo(TypedDict):
    """A structured task item for tracking progress through complex workflows.

    Attributes:
        content: Short, specific description of the task
        status: Current state - pending, in_progress, or completed
    """

    content: str
    status: Literal["pending", "in_progress", "completed"]


def file_reducer(left, right):
    """Merge two file dictionaries, with right side taking precedence.

    Used as a reducer function for the files field in agent state,
    allowing incremental updates to the virtual file system.

    Args:
        left: Left side dictionary (existing files)
        right: Right side dictionary (new/updated files)

    Returns:
        Merged dictionary with right values overriding left values
    """
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return {**left, **right}


class DeepAgentState(AgentState):
    """Extended agent state that includes task tracking and virtual file system.

    Inherits from LangGraph's AgentState and adds:
    - todos: List of Todo items for task planning and progress tracking
    - files: Virtual file system stored as dict mapping filenames to content
    """

    todos: NotRequired[list[Todo]]
    files: Annotated[NotRequired[dict[str, str]], file_reducer]


# --- Pydantic Schema Definition (Not a Tool, but essential for Tool 1) ---
class MedicationSchedule(BaseModel):
    """Structured data model for a single medication schedule entry."""
    medication_name: str = Field(..., description="The name of the medication (e.g., 'Metformin').")
    dosage_mg: PositiveInt = Field(..., description="The dose strength in milligrams (e.g., 500).")
    frequency_count: PositiveInt = Field(..., description="Number of times to take the medication per unit.")
    frequency_unit: Literal["day", "week", "month"] = Field(..., description="The time unit for frequency.")
    time_of_day: str = Field(..., description="The specific time or time slot (e.g., '08:00', 'morning', or '14:30').")
    duration_days: Optional[PositiveInt] = Field(None, description="The total number of days for the regimen, if applicable.")