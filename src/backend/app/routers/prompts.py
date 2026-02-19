"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Prompt registry with version history, diff,
             rollback, approval workflow, and A/B testing.
Root Cause:  Sprint tasks T172-T178 — Prompt registry system.
Context:     Central prompt management for versioned prompt
             templates with governance & approval flows.
Suitability: L3 — complex state management, versioning logic.
──────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import difflib
import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/prompts", tags=["Prompt Registry"])


# ───────────────────── Enums ─────────────────────

class PromptStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


# ───────────────────── Schemas ─────────────────────

class PromptVariable(BaseModel):
    name: str
    description: str = ""
    default: Optional[str] = None
    required: bool = True


class PromptVersion(BaseModel):
    version: int
    content: str
    system_prompt: Optional[str] = None
    variables: list[PromptVariable] = []
    model_hint: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    created_by: str
    created_at: str
    content_hash: str
    change_notes: str = ""
    status: PromptStatus = PromptStatus.DRAFT


class PromptTemplate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    category: str = "general"
    tags: list[str] = []
    current_version: int = 0
    versions: list[PromptVersion] = []
    created_by: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True


class CreatePromptRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    category: str = "general"
    tags: list[str] = []
    content: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    variables: list[PromptVariable] = []
    model_hint: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    created_by: str = "system"


class UpdatePromptRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    content: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    variables: list[PromptVariable] = []
    model_hint: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    change_notes: str = ""
    updated_by: str = "system"


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    action: ApprovalAction
    reviewer: str
    comment: str = ""


class RenderRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    variables: dict[str, str] = {}
    version: Optional[int] = None


class DiffResponse(BaseModel):
    prompt_id: str
    from_version: int
    to_version: int
    diff: str
    added_lines: int
    removed_lines: int


class ApprovalRecord(BaseModel):
    id: str
    prompt_id: str
    version: int
    action: ApprovalAction
    reviewer: str
    comment: str
    timestamp: str


# ───────────────────── Prompt Registry Service ─────────────────────

class PromptRegistryService:
    """Central prompt registry with versioning, diff, rollback, and approvals."""

    def __init__(self):
        self._prompts: dict[str, PromptTemplate] = {}
        self._approvals: list[ApprovalRecord] = []

    def create(self, req: CreatePromptRequest) -> PromptTemplate:
        """Create a new prompt template with initial version."""
        # Check name uniqueness
        for p in self._prompts.values():
            if p.name == req.name and p.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Prompt with name '{req.name}' already exists",
                )

        prompt_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        content_hash = hashlib.sha256(req.content.encode()).hexdigest()[:16]

        version = PromptVersion(
            version=1,
            content=req.content,
            system_prompt=req.system_prompt,
            variables=req.variables,
            model_hint=req.model_hint,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            created_by=req.created_by,
            created_at=now,
            content_hash=content_hash,
        )

        template = PromptTemplate(
            id=prompt_id,
            name=req.name,
            description=req.description,
            category=req.category,
            tags=req.tags,
            current_version=1,
            versions=[version],
            created_by=req.created_by,
            created_at=now,
            updated_at=now,
        )

        self._prompts[prompt_id] = template
        logger.info("prompt_created", id=prompt_id, name=req.name)
        return template

    def get(self, prompt_id: str) -> PromptTemplate:
        """Get a prompt template by ID."""
        prompt = self._prompts.get(prompt_id)
        if not prompt or not prompt.is_active:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt

    def list_prompts(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        status_filter: Optional[PromptStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        """List prompt templates with filtering."""
        prompts = [p for p in self._prompts.values() if p.is_active]

        if category:
            prompts = [p for p in prompts if p.category == category]

        if tag:
            prompts = [p for p in prompts if tag in p.tags]

        if status_filter:
            prompts = [
                p for p in prompts
                if p.versions and p.versions[-1].status == status_filter
            ]

        if search:
            search_lower = search.lower()
            prompts = [
                p for p in prompts
                if search_lower in p.name.lower()
                or search_lower in p.description.lower()
            ]

        total = len(prompts)
        page = prompts[skip: skip + limit]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "prompts": [p.model_dump() for p in page],
        }

    def update(self, prompt_id: str, req: UpdatePromptRequest) -> PromptTemplate:
        """Create a new version of a prompt template."""
        prompt = self.get(prompt_id)
        now = datetime.now(timezone.utc).isoformat()
        new_version_num = prompt.current_version + 1

        content_hash = hashlib.sha256(req.content.encode()).hexdigest()[:16]

        # Check if content actually changed
        if prompt.versions:
            latest = prompt.versions[-1]
            if latest.content_hash == content_hash:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content unchanged from current version",
                )

        version = PromptVersion(
            version=new_version_num,
            content=req.content,
            system_prompt=req.system_prompt,
            variables=req.variables,
            model_hint=req.model_hint,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            created_by=req.updated_by,
            created_at=now,
            content_hash=content_hash,
            change_notes=req.change_notes,
            status=PromptStatus.DRAFT,
        )

        prompt.versions.append(version)
        prompt.current_version = new_version_num
        prompt.updated_at = now

        logger.info("prompt_version_created", id=prompt_id, version=new_version_num)
        return prompt

    def diff(self, prompt_id: str, from_ver: int, to_ver: int) -> DiffResponse:
        """Compute diff between two versions."""
        prompt = self.get(prompt_id)

        from_version = self._find_version(prompt, from_ver)
        to_version = self._find_version(prompt, to_ver)

        from_lines = from_version.content.splitlines(keepends=True)
        to_lines = to_version.content.splitlines(keepends=True)

        diff_lines = list(difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=f"v{from_ver}",
            tofile=f"v{to_ver}",
            lineterm="",
        ))

        added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

        return DiffResponse(
            prompt_id=prompt_id,
            from_version=from_ver,
            to_version=to_ver,
            diff="\n".join(diff_lines),
            added_lines=added,
            removed_lines=removed,
        )

    def rollback(self, prompt_id: str, target_version: int, rolled_back_by: str = "system") -> PromptTemplate:
        """Rollback to a previous version (creates a new version with old content)."""
        prompt = self.get(prompt_id)
        target = self._find_version(prompt, target_version)
        now = datetime.now(timezone.utc).isoformat()
        new_version_num = prompt.current_version + 1

        rollback_version = PromptVersion(
            version=new_version_num,
            content=target.content,
            system_prompt=target.system_prompt,
            variables=target.variables,
            model_hint=target.model_hint,
            max_tokens=target.max_tokens,
            temperature=target.temperature,
            created_by=rolled_back_by,
            created_at=now,
            content_hash=target.content_hash,
            change_notes=f"Rollback to version {target_version}",
            status=PromptStatus.DRAFT,
        )

        prompt.versions.append(rollback_version)
        prompt.current_version = new_version_num
        prompt.updated_at = now

        logger.info("prompt_rolled_back", id=prompt_id, to_version=target_version, new_version=new_version_num)
        return prompt

    def submit_for_review(self, prompt_id: str, version: Optional[int] = None) -> PromptTemplate:
        """Submit a prompt version for approval review."""
        prompt = self.get(prompt_id)
        ver = self._find_version(prompt, version or prompt.current_version)

        if ver.status != PromptStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version {ver.version} is already in status '{ver.status}'",
            )

        ver.status = PromptStatus.PENDING_REVIEW
        logger.info("prompt_submitted_for_review", id=prompt_id, version=ver.version)
        return prompt

    def review(self, prompt_id: str, version: int, req: ApprovalRequest) -> PromptTemplate:
        """Approve, reject, or request changes on a prompt version."""
        prompt = self.get(prompt_id)
        ver = self._find_version(prompt, version)

        if ver.status != PromptStatus.PENDING_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version {version} is not pending review",
            )

        if req.action == ApprovalAction.APPROVE:
            ver.status = PromptStatus.APPROVED
        elif req.action == ApprovalAction.REJECT:
            ver.status = PromptStatus.REJECTED
        elif req.action == ApprovalAction.REQUEST_CHANGES:
            ver.status = PromptStatus.DRAFT  # Back to draft for changes

        record = ApprovalRecord(
            id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            version=version,
            action=req.action,
            reviewer=req.reviewer,
            comment=req.comment,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._approvals.append(record)

        logger.info(
            "prompt_reviewed",
            id=prompt_id,
            version=version,
            action=req.action,
            reviewer=req.reviewer,
        )
        return prompt

    def render(self, prompt_id: str, req: RenderRequest) -> dict[str, Any]:
        """Render a prompt template with variable substitution."""
        prompt = self.get(prompt_id)
        version_num = req.version or prompt.current_version
        ver = self._find_version(prompt, version_num)

        # Check required variables
        missing = []
        for var in ver.variables:
            if var.required and var.name not in req.variables and var.default is None:
                missing.append(var.name)

        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required variables: {', '.join(missing)}",
            )

        # Build variable context with defaults
        context = {}
        for var in ver.variables:
            context[var.name] = req.variables.get(var.name, var.default or "")

        # Render template (simple {{variable}} substitution)
        rendered = ver.content
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)

        result: dict[str, Any] = {
            "prompt_id": prompt_id,
            "version": version_num,
            "rendered_content": rendered,
            "variables_used": context,
        }

        if ver.system_prompt:
            system_rendered = ver.system_prompt
            for key, value in context.items():
                system_rendered = system_rendered.replace(f"{{{{{key}}}}}", value)
            result["rendered_system_prompt"] = system_rendered

        if ver.model_hint:
            result["model_hint"] = ver.model_hint
        if ver.max_tokens:
            result["max_tokens"] = ver.max_tokens
        if ver.temperature is not None:
            result["temperature"] = ver.temperature

        return result

    def delete(self, prompt_id: str) -> None:
        """Soft-delete a prompt template."""
        prompt = self.get(prompt_id)
        prompt.is_active = False
        logger.info("prompt_deleted", id=prompt_id)

    def get_approval_history(self, prompt_id: str) -> list[ApprovalRecord]:
        """Get approval history for a prompt."""
        return [a for a in self._approvals if a.prompt_id == prompt_id]

    def _find_version(self, prompt: PromptTemplate, version: int) -> PromptVersion:
        """Find a specific version of a prompt."""
        for v in prompt.versions:
            if v.version == version:
                return v
        raise HTTPException(
            status_code=404,
            detail=f"Version {version} not found",
        )


# ─── Singleton ───
_registry = PromptRegistryService()


def get_registry() -> PromptRegistryService:
    return _registry


# ───────────────────── API Routes ─────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_prompt(req: CreatePromptRequest):
    """Create a new prompt template."""
    return get_registry().create(req).model_dump()


@router.get("/")
async def list_prompts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[PromptStatus] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List prompt templates with filtering and pagination."""
    return get_registry().list_prompts(category, tag, status, search, skip, limit)


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get a prompt template by ID."""
    return get_registry().get(prompt_id).model_dump()


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str, req: UpdatePromptRequest):
    """Create a new version of a prompt template."""
    return get_registry().update(prompt_id, req).model_dump()


@router.get("/{prompt_id}/diff")
async def diff_versions(prompt_id: str, from_ver: int, to_ver: int):
    """Get diff between two versions of a prompt."""
    return get_registry().diff(prompt_id, from_ver, to_ver).model_dump()


@router.post("/{prompt_id}/rollback/{target_version}")
async def rollback_prompt(prompt_id: str, target_version: int):
    """Rollback a prompt to a previous version."""
    return get_registry().rollback(prompt_id, target_version).model_dump()


@router.post("/{prompt_id}/submit-review")
async def submit_for_review(prompt_id: str, version: Optional[int] = None):
    """Submit a prompt version for approval review."""
    return get_registry().submit_for_review(prompt_id, version).model_dump()


@router.post("/{prompt_id}/review/{version}")
async def review_prompt(prompt_id: str, version: int, req: ApprovalRequest):
    """Approve, reject, or request changes on a prompt version."""
    return get_registry().review(prompt_id, version, req).model_dump()


@router.post("/{prompt_id}/render")
async def render_prompt(prompt_id: str, req: RenderRequest):
    """Render a prompt template with variable substitution."""
    return get_registry().render(prompt_id, req)


@router.get("/{prompt_id}/approvals")
async def get_approval_history(prompt_id: str):
    """Get approval history for a prompt."""
    return [a.model_dump() for a in get_registry().get_approval_history(prompt_id)]


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str):
    """Soft-delete a prompt template."""
    get_registry().delete(prompt_id)
