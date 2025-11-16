from datetime import datetime, timedelta
from queue import Queue
from apscheduler.schedulers.background import BackgroundScheduler
from langchain_core.tools import tool

# --- 1. Communication Queue (The Ambient Agent's output/Orchestrator's input) ---
# This is the event bus that the Ambient Agent pushes to, and the Orchestrator listens to.
ORCHESTRATOR_QUEUE = Queue()

# --- 2. APScheduler Setup ---
# The BackgroundScheduler runs in its own thread, perfect for non-blocking ambient tasks.
SCHEDULER = BackgroundScheduler()
# Start the scheduler immediately
if not SCHEDULER.running:
    SCHEDULER.start()
    print("[Ambient:Scheduler] APScheduler started in background.")


# --- 3. Ambient Agent's Core Action (Pushes to Orchestrator) ---
@tool
def ambient_agent_trigger_action(schedule_id: str, patient_id: str) -> None:
    """
    This function is executed by APScheduler at the scheduled time.
    It pushes a command/event into the Orchestrator's queue.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    payload = {
        "event_type": "SCHEDULED_REMINDER_TRIGGER",
        "timestamp": timestamp,
        "schedule_id": schedule_id,
        "patient_id": patient_id
    }

    # PUSH the event/command back to the Orchestrator
    ORCHESTRATOR_QUEUE.put(payload)
    print(f"\n[{timestamp}] [Ambient:TRIGGER] Command pushed to Orchestrator for {schedule_id}.")


# --- 4. Ambient Agent's Tool (Called by Orchestrator/Setup) ---
# @tool
def commit_schedule_and_queue_task(schedule_id: str, patient_id: str, time_str: str) -> str:
    """
    Creates a new, scheduled job in the in-memory APScheduler.
    The job will call 'ambient_agent_trigger_action' at the specified time.
    Time format must be HH:MM (e.g., '09:00').
    """
    try:
        hour, minute = map(int, time_str.split(':'))

        # Add a test schedule that runs once, 5 seconds from now, for easy demonstration
        run_date = datetime.now() + timedelta(seconds=5)

        SCHEDULER.add_job(
            ambient_agent_trigger_action,
            'date',  # Use 'date' for one-off/immediate testing
            run_date=run_date,
            id=schedule_id,
            name=f"Med Reminder for {patient_id}",
            args=[schedule_id, patient_id]
        )

        return (
            f"COMMIT_SUCCESS: Schedule {schedule_id} saved. "
            f"Set to trigger at: {run_date.strftime('%H:%M:%S')} (5 seconds from now for demo)."
        )
    except ValueError as e:
        return f"COMMIT_FAILURE: Invalid time format '{time_str}'. Error: {e}"