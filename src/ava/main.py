import uvicorn
from fastapi import FastAPI, Request, HTTPException
import json
import time
from .agents.orchestrator_agent import agent
import dotenv

from .states.agora_states import AgoraTTSResponse, AgoraAction, AgoraWebhookPayload

dotenv.load_dotenv()

app = FastAPI()

@app.get("/call")
async def root(message: str) -> str:
    result = agent.invoke({
        "messages": [
            {"role": "user",
             "content": "Doctor gave me 500 mg metformin only for tomorrow morning 8 AM for diabetes Create a schedule for that"
             }]
    })
    return result


@app.post("/agora/webhook/convo-ai", response_model=AgoraTTSResponse, status_code=200)
async def agora_webhook_handler(payload: AgoraWebhookPayload):
    """
    Receives transcribed user input from Agora, runs the LangGraph agent,
    and sends the synthetic voice response back to Agora for playback.
    """
    transcribed_text = payload.text.strip()
    channel = payload.channel_name

    print(f"[{time.strftime('%H:%M:%S')}] Webhook received from Channel {channel}: '{transcribed_text}'")

    if not transcribed_text:
        # User was silent, respond by telling Agora to keep listening.
        print("Empty transcription. Sending 'listen' action.")
        return AgoraTTSResponse(
            actions=[AgoraAction(action="listen")],
            control="continue"
        )

    agent_response_text = agent.invoke({"messages": [{"role": "user", "content": transcribed_text}]})

    print(f"LangGraph Agent final response: '{agent_response_text}'")

    # 5. Format the structured response for Agora's TTS service
    return AgoraTTSResponse(
        actions=[
            # First action: Speak the agent's response
            AgoraAction(action="speak", text=agent_response_text),
            # Second action: Tell Agora to listen for the user's next input
            AgoraAction(action="listen")
        ],
        control="continue"
    )


# --- SECURITY NOTE ---
# In a production environment, you MUST implement robust signature verification
# (checking a request header provided by Agora) to ensure the request is legitimate.
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}")
    # Return a safe, controlled response to the Agora platform in case of error
    return json.dumps({
        "actions": [{"action": "speak",
                     "text": "I encountered a critical error while processing that request. Please try again."}],
        "control": "continue"
    }), 500


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)