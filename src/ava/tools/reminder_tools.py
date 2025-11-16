import time
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from ..dao.db import MEDICATION_DB


def fetch_medication_data(schedule_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches specific medication schedule data from the database.
    This is the first step of the Sub-Agent's task.
    """
    print(f"[SubAgent:Data] Attempting to fetch data for schedule_id: {schedule_id}")
    time.sleep(0.1)  # Simulate network delay

    data = MEDICATION_DB.get(schedule_id)
    if data:
        print(f"[SubAgent:Data] SUCCESS. Found medication: {data['medication']}")
    else:
        print(f"[SubAgent:Data] ERROR. Schedule ID {schedule_id} not found.")
    return data


def publish_reminder_via_agora(medication_data: Dict[str, Any]) -> str:
    """
    Simulates initiating an outbound call/reminder via Agora AI.
    This is the final action of the Sub-Agent's task.
    """
    if not medication_data:
        return "AGORA_FAILED: Cannot publish reminder, no medication data provided."

    patient_id = medication_data['patient_id']
    med = medication_data['medication']
    phone = medication_data['phone_number']

    # Construct the personalized AI script/prompt
    message = (
        f"Hello {patient_id}. This is your Adherence Voice Agent. "
        f"It is time for your {med}. Please take it now. "
        f"Press 1 to confirm you have taken it."
    )

    print("=" * 60)
    print(f"[SubAgent:Agora] INITIATING CALL to {phone} for {patient_id}")
    print(f"[SubAgent:Agora] AI Script: {message[:120]}...")
    print(f"[SubAgent:Agora] Agora AI API Call Status: Simulated SUCCESS (HTTP 202)")
    print("=" * 60)
    return f"AGORA_SUCCESS: Call initiated for {med} to {phone}."


# --- 3. Sub-Agent Task Group (The single tool the Orchestrator calls) ---
@tool
def process_reminder_call(schedule_id: str, patient_id: str) -> str:
    """
    Groups data fetching and the external API call into one cohesive tool.
    This is the function the Orchestrator should delegate to.
    """
    print(f"\n[{time.strftime('%H:%M:%S')}] [Orchestrator:DELEGATE] Delegation received for {schedule_id}.")

    # Step 1: Use internal tool to fetch required data
    data = fetch_medication_data(schedule_id)

    if not data:
        return f"DELEGATION_FAILURE: Could not process {schedule_id} due to missing data."

    # Step 2: Use internal tool to publish the reminder
    result = publish_reminder_via_agora(data)

    return f"DELEGATION_COMPLETE: {result}"