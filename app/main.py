from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Task API", version="0.1.0", description="Small CRUD API for tasks/agreements.")


def get_or_404(db: Session, task_id: int) -> models.Task:
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(status: schemas.Status | None = None, overdue: bool = False,
               q: str | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
               db: Session = Depends(get_db)):
    stmt = select(models.Task).order_by(models.Task.due_date.is_(None), models.Task.due_date, models.Task.id)
    if status:
        stmt = stmt.where(models.Task.status == status)
    if overdue:
        stmt = stmt.where(models.Task.status == "open", models.Task.due_date < date.today())
    if q:
        stmt = stmt.where(models.Task.title.ilike(f"%{q}%"))
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, task_id)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = get_or_404(db, task_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, task_id))
    db.commit()
    return Response(status_code=204)
