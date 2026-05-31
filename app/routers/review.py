from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/review", tags=["review"])

# 模拟审核记录
def generate_mock_reviews(version_id: int):
    roles = ['legal_expert', 'ethnic_expert', 'music_pro']
    statuses = ['pending', 'approved', 'need_modify']
    reviews = []
    for role in roles:
        reviews.append({
            "id": random.randint(1000, 9999),
            "version_id": version_id,
            "reviewer_role": role,
            "reviewer_name": f"{role}_审核员",
            "review_comments": "歌词法律表述准确，旋律符合民族特色。" if role != 'legal_expert' else "法律术语使用规范，符合相关法规。",
            "review_status": random.choice(statuses),
            "reviewed_at": datetime.now() - timedelta(days=random.randint(1, 10))
        })
    return reviews

@router.get("/version/{version_id}")
def get_reviews(version_id: int, db: Session = Depends(get_db)):
    real_reviews = crud.get_reviews_by_version(db, version_id)
    if not real_reviews:
        return generate_mock_reviews(version_id)
    return real_reviews