import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter()

@router.get("", response_model=list[RuleResponse])
async def list_rules(
    camera_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Rule).order_by(Rule.created_at.desc())
    if camera_id:
        query = query.where(Rule.camera_id == camera_id)
    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_in: RuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    rule = Rule(
        camera_id=rule_in.camera_id,
        zone_id=rule_in.zone_id,
        name=rule_in.name,
        rule_type=rule_in.rule_type,
        configuration=rule_in.configuration,
        severity=rule_in.severity,
        is_enabled=rule_in.is_enabled,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    rule_in: RuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "operator"])),
):
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
