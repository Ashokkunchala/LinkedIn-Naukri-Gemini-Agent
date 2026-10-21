from typing import Literal

from pydantic import BaseModel, Field

class JobCreate(BaseModel):
    platform: Literal["manual", "linkedin", "naukri"] = "manual"
    title: str = Field(min_length=1, max_length=200)
    company: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=200)
    url: str = Field(default="", max_length=2000)
    description: str = Field(min_length=10, max_length=50000)
    skills: list[str] = Field(default_factory=list, max_length=100)

class DraftRequest(BaseModel):
    kind: Literal["resume_summary", "cover_letter", "recruiter_message", "application_answer"]
    profile: str = Field(min_length=5, max_length=20000)
    extra_instructions: str = Field(default="", max_length=4000)

class MatchRequest(BaseModel):
    profile: str = Field(min_length=5, max_length=20000)

class ApprovalCreate(BaseModel):
    action_type: Literal["submit_application", "edit_profile", "send_message", "other"]
    target: str = Field(min_length=1, max_length=2000)
    payload: dict = Field(default_factory=dict)

class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    note: str = Field(default="", max_length=2000)

class ApplicationCreate(BaseModel):
    job_id: int
    status: Literal["interested", "drafting", "ready_for_review", "submitted", "interview", "rejected", "withdrawn"] = "interested"
    notes: str = Field(default="", max_length=5000)
