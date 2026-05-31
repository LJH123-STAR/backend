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
    groups = crud.get_ethnic_groups(db)
    return [{"id": g.id, "name": g.ethnic_group, "region": g.region} for g in groups]


@router.get("/legal-scenes")
def list_legal_scenes(db: Session = Depends(get_db)):
    scenes = crud.get_legal_scenes(db)
    return [{"id": s.id, "category": s.scene_category, "keywords": s.keywords} for s in scenes]


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

    # 3. 获取法治场景名称
    scene = crud.get_legal_scene(db, legal_scene_id)
    scene_name = scene.scene_category if scene else "默认"

    # 4. 调用AI填词
    ai_result = ai_service.compose_lyrics_by_melody(project_id, music_features, scene_name)

    # 5. 法理校验
    legal_ok, legal_msg = ai_service.legal_calibration(ai_result["lyrics_text"])
    rhythm_ok, rhythm_msg = ai_service.rhythm_calibration(ai_result["lyrics_text"], "西南山歌")

    if not (legal_ok and rhythm_ok):
        raise HTTPException(status_code=400, detail=f"校验失败: {legal_msg} {rhythm_msg}")

    # 6. 保存版本
    version = crud.create_version(db, project_id, ai_result)

    # 7. 更新项目状态
    project = crud.get_project(db, project_id)
    if project:
        project.ethnic_group = "依曲填词"
        project.status = "ai_generated"
        db.commit()

    return schemas.GenerateResponse(
        success=True,
        version_id=version.id,
        lyrics=ai_result["lyrics_text"],
        audio_url=ai_result["audio_url"],
        message="依曲填词完成，已通过法理+韵律双重校准"
    )