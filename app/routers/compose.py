from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, ai_service
import os
import shutil

router = APIRouter(prefix="/api/compose", tags=["compose"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/ethnic-groups")
def list_ethnic_groups(db: Session = Depends(get_db)):
    groups = crud.get_ethnic_groups(db)   # 返回字典列表
    # 修改：使用字典键访问
    return [{"id": g["id"], "name": g["ethnic_group"], "region": g["region"]} for g in groups]


@router.get("/legal-scenes")
def list_legal_scenes(db: Session = Depends(get_db)):
    scenes = crud.get_legal_scenes(db)    # 返回字典列表
    # 修改：使用字典键访问
    return [{"id": s["id"], "category": s["scene_category"], "keywords": s["keywords"]} for s in scenes]


@router.post("/upload-and-generate", response_model=schemas.GenerateResponse)
async def upload_and_generate(
        project_id: int = Form(...),
        legal_scene_id: int = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # 1. 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. 分析旋律特征（模拟）
    music_features = ai_service.analyze_uploaded_song(file_path, file.filename)

    # 3. 获取法治场景名称（注意：crud.get_legal_scene 返回字典）
    scene_dict = crud.get_legal_scene(db, legal_scene_id)
    scene_name = scene_dict["scene_category"] if scene_dict else "默认"

    # 4. 调用AI填词
    ai_result = ai_service.compose_lyrics_by_melody(project_id, music_features, scene_name)

    # 5. 法理校验
    legal_ok, legal_msg = ai_service.legal_calibration(ai_result["lyrics_text"])
    rhythm_ok, rhythm_msg = ai_service.rhythm_calibration(ai_result["lyrics_text"], "西南山歌")

    if not (legal_ok and rhythm_ok):
        raise HTTPException(status_code=400, detail=f"校验失败: {legal_msg} {rhythm_msg}")

    # 6. 保存版本（crud.create_version 返回字典，但我们只需要其中的 id）
    version_dict = crud.create_version(db, project_id, ai_result)

    # 7. 更新项目状态（注意：crud.get_project 返回字典，不能直接修改属性，需要通过 ORM 对象）
    # 方案：直接使用 ORM 查询更新
    from app import models
    orm_project = db.query(models.AISongProject).filter(models.AISongProject.id == project_id).first()
    if orm_project:
        orm_project.ethnic_group = "依曲填词"
        orm_project.status = "ai_generated"
        db.commit()
        db.refresh(orm_project)

    return schemas.GenerateResponse(
        success=True,
        version_id=version_dict["id"],
        lyrics=ai_result["lyrics_text"],
        audio_url=ai_result.get("audio_url"),
        message="依曲填词完成，已通过法理+韵律双重校准"
    )
