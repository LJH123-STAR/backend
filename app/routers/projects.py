from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=schemas.Project)
@router.post("", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@router.get("/", response_model=List[schemas.Project])
@router.get("", response_model=List[schemas.Project])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db, skip, limit)

@router.get("/{project_id}", response_model=schemas.ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@router.get("/{project_id}/versions", response_model=List[schemas.SongVersion])
def get_project_versions(project_id: int, db: Session = Depends(get_db)):
    return crud.get_versions_by_project(db, project_id)

@router.patch("/{project_id}/status")
def update_status(project_id: int, status: str, db: Session = Depends(get_db)):
    project = crud.update_project_status(db, project_id, status)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"status": "updated"}