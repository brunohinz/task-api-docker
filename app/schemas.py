from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["open", "done", "cancelled"]


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    due_date: date | None = None
    status: Status = "open"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    due_date: date | None = None
    status: Status | None = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
