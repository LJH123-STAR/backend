from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProjectStatusEnum(str, Enum):
    draft = "draft"
    ai_generated = "ai_generated"
    under_review = "under_review"
    approved = "approved"
    published = "published"

class ReviewerRoleEnum(str, Enum):
    legal_expert = "legal_expert"
    ethnic_expert = "ethnic_expert"
    music_pro = "music_pro"

class EthnicMelodyBase(BaseModel):
    ethnic_group: str
    region: Optional[str] = None
    rhythm_pattern: Optional[str] = None
    scale_mode: Optional[str] = None
    typical_song: Optional[str] = None
    feature_description: Optional[str] = None

class EthnicMelody(EthnicMelodyBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LegalSceneBase(BaseModel):
    scene_category: str
    sub_category: Optional[str] = None
    keywords: Optional[str] = None
    legal_basis: Optional[str] = None

class LegalScene(LegalSceneBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    project_name: str
    ethnic_group: str
    legal_scene_id: Optional[int] = None

class Project(BaseModel):
    id: int
    project_name: str
    ethnic_group: str
    legal_scene_id: Optional[int]
    status: ProjectStatusEnum
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

class ProjectDetail(Project):
    legal_scene: Optional[LegalScene] = None

class SongVersionBase(BaseModel):
    version_number: int
    lyrics_text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    sheet_music_url: Optional[str] = None

class SongVersion(SongVersionBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    project_id: int
    prompt_style: Optional[str] = "standard"

class GenerateResponse(BaseModel):
    success: bool
    version_id: int
    lyrics: str
    audio_url: Optional[str] = None
    message: str

class ReviewCreate(BaseModel):
    version_id: int
    reviewer_role: ReviewerRoleEnum
    reviewer_name: Optional[str] = None
    review_comments: Optional[str] = None
    review_status: str = "pending"

class Review(ReviewCreate):
    id: int
    reviewed_at: datetime
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_projects: int
    total_lyrics_drafts: int
    legal_accuracy_rate: float
    efficiency_improvement: int
    published_works: int
    ethnic_count: int
    scene_count: int