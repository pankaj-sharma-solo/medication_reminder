# Pydantic model for the expected response structure (what we send back to Agora)
from typing import List

from pydantic import BaseModel, Field


class AgoraAction(BaseModel):
    action: str = Field(..., description="Action type: 'speak' or 'listen'.")
    text: str = Field(None, description="The text for TTS if action is 'speak'.")

class AgoraTTSResponse(BaseModel):
    actions: List[AgoraAction]
    control: str = Field("continue", description="'continue' to keep the session active, 'end' to hang up.")

class AgoraWebhookPayload(BaseModel):
    text: str = Field(..., description="The transcribed text from the user's speech.")
    user_id: str = Field(None, description="The Agora User ID of the speaker.")
    channel_name: str = Field(..., description="The name of the Agora channel.")
    # Include other fields like 'timestamp', 'event_type', etc., as needed