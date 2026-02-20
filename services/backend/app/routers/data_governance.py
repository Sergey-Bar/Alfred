from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

# In-memory store for demo purposes
GOVERNANCE_ASSIGNMENTS = []
GOVERNANCE_POLICIES = []


class GovernanceAssignment(BaseModel):
    id: int
    dataset: str
    owner: str
    stewards: List[str]
    assigned_at: datetime


class GovernancePolicy(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    rules: dict
    created_at: datetime


@router.post("/data-governance/assignments", status_code=status.HTTP_201_CREATED)
def register_assignment(assignment: GovernanceAssignment):
    if any(a.id == assignment.id for a in GOVERNANCE_ASSIGNMENTS):
        raise HTTPException(status_code=400, detail="Assignment ID already exists")
    GOVERNANCE_ASSIGNMENTS.append(assignment)
    return {"message": "Assignment registered", "assignment_id": assignment.id}


@router.get("/data-governance/assignments", response_model=List[GovernanceAssignment])
def list_assignments(dataset: Optional[str] = None):
    if dataset:
        return [a for a in GOVERNANCE_ASSIGNMENTS if a.dataset == dataset]
    return GOVERNANCE_ASSIGNMENTS


@router.post("/data-governance/policies", status_code=status.HTTP_201_CREATED)
def register_policy(policy: GovernancePolicy):
    if any(p.id == policy.id for p in GOVERNANCE_POLICIES):
        raise HTTPException(status_code=400, detail="Policy ID already exists")
    GOVERNANCE_POLICIES.append(policy)
    return {"message": "Policy registered", "policy_id": policy.id}


@router.get("/data-governance/policies", response_model=List[GovernancePolicy])
def list_policies():
    return GOVERNANCE_POLICIES
