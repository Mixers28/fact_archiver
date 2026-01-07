import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class SourceItem(Base):
    __tablename__ = "source_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    discovered_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fetch_headers = Column(JSONB, nullable=True)
    content_type = Column(String(255), nullable=True)
    language = Column(String(32), nullable=True)
    capture_tier = Column(Integer, nullable=False, default=1)
    capture_status = Column(String(64), nullable=True)

    artifacts = relationship("Artifact", back_populates="source_item")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_item_id = Column(UUID(as_uuid=True), ForeignKey("source_items.id"), nullable=False)
    type = Column(String(32), nullable=False)
    storage_uri = Column(Text, nullable=False)
    bytes = Column(Integer, nullable=True)
    sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tool_version = Column(String(64), nullable=True)

    source_item = relationship("SourceItem", back_populates="artifacts")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    date_key = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    importance_score = Column(Float, nullable=True)
    tags = Column(JSONB, nullable=True)


class EventMembership(Base):
    __tablename__ = "event_memberships"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), primary_key=True)
    source_item_id = Column(UUID(as_uuid=True), ForeignKey("source_items.id"), primary_key=True)
    confidence = Column(Float, nullable=True)


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    normalized_text = Column(Text, nullable=False)
    claim_type = Column(String(32), nullable=False)
    entities = Column(JSONB, nullable=True)
    numeric_fields = Column(JSONB, nullable=True)


class ClaimAssertion(Base):
    __tablename__ = "claim_assertions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    source_item_id = Column(UUID(as_uuid=True), ForeignKey("source_items.id"), nullable=False)
    extracted_span = Column(String(64), nullable=True)
    excerpt = Column(Text, nullable=True)
    polarity = Column(String(16), nullable=False, default="neutral")
    assertion_time = Column(DateTime(timezone=True), nullable=True)


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    model_version = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(String(32), nullable=False)
    score = Column(Float, nullable=True)
    rationale = Column(JSONB, nullable=True)
    computed_signals = Column(JSONB, nullable=True)


class TransparencyLogEntry(Base):
    __tablename__ = "transparency_log_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    previous_root = Column(String(128), nullable=True)
    merkle_root = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class NormalizedText(Base):
    __tablename__ = "normalized_texts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_item_id = Column(UUID(as_uuid=True), ForeignKey("source_items.id"), nullable=False, unique=True)
    canonical_source_item_id = Column(UUID(as_uuid=True), ForeignKey("source_items.id"), nullable=True)
    text_hash = Column(String(64), nullable=False, index=True)
    normalized_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
