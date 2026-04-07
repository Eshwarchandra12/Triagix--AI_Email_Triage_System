from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    tier: Literal["standard", "premium", "enterprise"] = "standard"
    sla_deadline: Optional[float] = None  # steps remaining before SLA is breached
    previous_interactions: int = 0

class Observation(BaseModel):
    current_email: dict | None 
    queue_length: int
    active_slas: int
    previous_actions: List[str] = Field(default_factory=list)

class Action(BaseModel):
    category: Literal["billing", "technical", "sales", "spam", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    assign_to: Optional[Literal["support", "engineering", "sales", "ignore"]] = "support"
    draft_reply: Optional[str] = "support"

class Reward(BaseModel):
    value: float = Field(ge=-1.0, le=1.0)
    info: dict

class Transition(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict
