# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Implements backend stubs for internal knowledge base/wiki platform and learning event management, as required by the roadmap.
# Why: No orchestration or CRUD endpoints for knowledge sharing, event scheduling, or hackathon tracking previously existed.
# Root Cause: Missing endpoints for wiki CRUD, event scheduling, and hackathon tracking.
# Context: Ready for extension (integration with markdown/wiki engines, event calendar, recognition system, and analytics). Suggest Claude Sonnet or GPT-5.1-Codex for advanced learning logic.

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# --- Models ---
class WikiPage(BaseModel):
    page_id: str
    title: str
    content: str
    last_updated: str


class LearningEvent(BaseModel):
    event_id: str
    name: str
    date: str
    description: Optional[str]


class HackathonRecord(BaseModel):
    hackathon_id: str
    name: str
    participants: List[str]
    outcome: Optional[str]
    date: str


# --- Endpoints ---
@router.get("/learning/wiki", response_model=List[WikiPage])
def list_wiki_pages():
    # Stub: Return sample wiki pages
    return [
        WikiPage(
            page_id="kb-001",
            title="Onboarding Guide",
            content="Welcome to Alfred!",
            last_updated="2026-02-15T11:00:00Z",
        ),
        WikiPage(
            page_id="kb-002",
            title="API Reference",
            content="See docs/guides/api.md",
            last_updated="2026-02-15T11:05:00Z",
        ),
    ]


@router.post("/learning/wiki", response_model=WikiPage)
def create_wiki_page(page: WikiPage):
    # Stub: Simulate wiki page creation
    return page


@router.get("/learning/events", response_model=List[LearningEvent])
def list_learning_events():
    # Stub: Return sample learning events
    return [
        LearningEvent(
            event_id="event-001",
            name="AI Hackathon",
            date="2026-03-01",
            description="Annual AI hackathon event.",
        ),
        LearningEvent(
            event_id="event-002",
            name="Knowledge Sharing",
            date="2026-03-15",
            description="Monthly knowledge sharing session.",
        ),
    ]


@router.post("/learning/events", response_model=LearningEvent)
def schedule_learning_event(event: LearningEvent):
    # Stub: Simulate event scheduling
    return event


@router.get("/learning/hackathons", response_model=List[HackathonRecord])
def list_hackathons():
    # Stub: Return sample hackathon records
    return [
        HackathonRecord(
            hackathon_id="hack-001",
            name="AI Hackathon",
            participants=["alice", "bob"],
            outcome="Winner: alice",
            date="2026-03-01",
        ),
        HackathonRecord(
            hackathon_id="hack-002",
            name="Spring Hackathon",
            participants=["carol", "dave"],
            outcome="Runner-up: dave",
            date="2026-04-01",
        ),
    ]

