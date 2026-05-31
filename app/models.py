from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey, JSON, Float, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    ai_generated = "ai_generated"
    under_review = "under_review"
    approved = "approved"
    published = "published"


class ReviewerRole(str, enum.Enum):
    legal_expert = "legal_expert"
    ethnic_expert = "ethnic_expert"
    music_pro = "music_pro"


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    need_modify = "need_modify"


class EthnicMelodyLib(Base):
    __tablename__ = "ethnic_melody_lib"
    id = Column(Integer, primary_key=True, index=True)
    ethnic_group = Column(String(50), nullable=False)
    region = Column(String(100))
    rhythm_pattern = Column(String(255))
    scale_mode = Column(String(100))
    typical_song = Column(String(200))
    feature_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class LegalSceneLib(Base):
    __tablename__ = "legal_scene_lib"
    id = Column(Integer, primary_key=True, index=True)
    scene_category = Column(String(100), nullable=False)
    sub_category = Column(String(100))
    keywords = Column(Text)
    legal_basis = Column(Text)
    example_lyrics = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class LegalTermValidator(Base):
    __tablename__ = "legal_term_validator"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(100), nullable=False, unique=True)
    is_allowed = Column(Boolean, default=True)
    correct_usage = Column(String(500))
    forbidden_context = Column(String(500))
    common_mistake = Column(String(200))


class AISongProject(Base):
    __tablename__ = "ai_song_projects"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(200), nullable=False)
    ethnic_group = Column(String(50), nullable=False)
    legal_scene_id = Column(Integer, ForeignKey("legal_scene_lib.id"))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.draft)
    created_by = Column(String(100), default="system")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    legal_scene = relationship("LegalSceneLib")
    versions = relationship("SongVersion", back_populates="project")


class SongVersion(Base):
    __tablename__ = "song_versions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("ai_song_projects.id"))
    version_number = Column(Integer, nullable=False)
    lyrics_text = Column(Text)
    melody_data = Column(JSON)
    audio_url = Column(String(500))
    video_url = Column(String(500))
    sheet_music_url = Column(String(500))
    lrc_lyrics = Column(Text)
    ai_efficiency_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("AISongProject", back_populates="versions")
    reviews = relationship("ReviewRecord", back_populates="version")


class ReviewRecord(Base):
    __tablename__ = "review_records"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("song_versions.id"))
    reviewer_role = Column(Enum(ReviewerRole), nullable=False)
    reviewer_name = Column(String(100))
    review_comments = Column(Text)
    modifications = Column(JSON)
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.pending)
    reviewed_at = Column(DateTime, server_default=func.now())

    version = relationship("SongVersion", back_populates="reviews")


class ResourceArchive(Base):
    __tablename__ = "resource_archives"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("ai_song_projects.id"))
    category_tag = Column(String(100))
    file_type = Column(Enum("audio", "video", "sheet", "package", name="file_type_enum"))
    file_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())