#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 14:00
# @Author  : kaichuan
# @FileName: knowledge_context_synchronizer.py
"""Knowledge-Context synchronization for dynamic knowledge updates.

This module provides bidirectional synchronization between the Knowledge
system and Context system, enabling:
1. Automatic context updates when knowledge changes
2. Conflict resolution for contradicting information
3. Version tracking for knowledge evolution
4. Selective invalidation of outdated context
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field

from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
    ContextMetadata,
)
from agentuniverse.agent.context.context_manager import ContextManager


class ConflictResolutionStrategy(str, Enum):
    """Strategy for resolving conflicts between existing and new knowledge."""

    NEWEST_WINS = "newest_wins"  # Most recent knowledge takes precedence
    CRITICAL_PRESERVED = "critical_preserved"  # CRITICAL priority always kept
    MERGE = "merge"  # Attempt to merge both versions
    VERSION_BOTH = "version_both"  # Keep both as versioned segments


class KnowledgeVersion(BaseModel):
    """Version information for knowledge tracking."""

    version_id: str = Field(description="Unique version identifier")
    timestamp: datetime = Field(description="When this version was created")
    source: str = Field(description="Source of the knowledge (file, API, etc)")
    hash: Optional[str] = Field(None, description="Content hash for change detection")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SyncResult(BaseModel):
    """Result of a knowledge-context synchronization operation."""

    segments_added: int = Field(0, description="Number of new segments added")
    segments_updated: int = Field(0, description="Number of segments updated")
    segments_invalidated: int = Field(0, description="Number of segments invalidated")
    conflicts_resolved: int = Field(0, description="Number of conflicts resolved")
    version: Optional[KnowledgeVersion] = Field(None, description="New version info")
    details: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeContextSynchronizer:
    """Synchronizes Knowledge system with Context system.

    This class manages the bidirectional flow of information between the
    Knowledge and Context systems, ensuring consistency and handling conflicts.

    Key Features:
    - Automatic context updates when knowledge changes
    - Conflict resolution with multiple strategies
    - Version tracking for knowledge evolution
    - Selective invalidation of outdated context
    - Efficient change detection

    Example:
        >>> synchronizer = KnowledgeContextSynchronizer(context_manager)
        >>> result = synchronizer.sync_knowledge_to_context(
        ...     knowledge_id="doc_123",
        ...     documents=["New content..."],
        ...     session_id="session_1"
        ... )
        >>> print(f"Added {result.segments_added} segments")
    """

    def __init__(
        self,
        context_manager: ContextManager,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.NEWEST_WINS,
        enable_versioning: bool = True,
    ):
        """Initialize the synchronizer.

        Args:
            context_manager: ContextManager instance to sync with
            conflict_strategy: Strategy for resolving conflicts
            enable_versioning: Whether to track knowledge versions
        """
        self.context_manager = context_manager
        self.conflict_strategy = conflict_strategy
        self.enable_versioning = enable_versioning

        # Track successfully applied versions independently in each session.
        self._knowledge_versions: dict[tuple[str, str], KnowledgeVersion] = {}

        # Track knowledge-to-context mappings
        self._knowledge_context_map: dict[tuple[str, str], list[str]] = {}

    def sync_knowledge_to_context(
        self,
        knowledge_id: str,
        documents: List[str],
        session_id: str,
        source: str = "knowledge_base",
        priority: ContextPriority = ContextPriority.HIGH,
        **kwargs
    ) -> SyncResult:
        """Sync knowledge documents to context storage.

        This adds or updates context segments based on knowledge documents,
        handling conflicts and version tracking. Change detection and segment
        mappings are scoped to the target session. Versions are committed only
        after all writes succeed; failed attempts roll back completed writes.
        This guarantees retry cleanup for serial calls with acknowledged writes,
        not an atomic durable transaction. Unacknowledged writes, concurrent
        syncs, manager-side eviction, and partial invalidation are not rolled back.

        Args:
            knowledge_id: Unique identifier for this knowledge
            documents: List of document contents to sync
            session_id: Session to sync context for
            source: Source of the knowledge (for versioning)
            priority: Priority for the created context segments
            **kwargs: Additional parameters:
                - force_update: Force update even if no changes detected
                - invalidate_old: Invalidate old segments before adding new

        Returns:
            SyncResult with operation statistics
        """
        result = SyncResult()
        knowledge_key = (session_id, knowledge_id)
        force_update = kwargs.get("force_update", False)
        invalidate_old = kwargs.get("invalidate_old", True)

        # Create version for tracking
        if self.enable_versioning:
            version = KnowledgeVersion(
                version_id=f"{knowledge_id}_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                source=source,
                hash=self._compute_hash(documents)
            )

            # Check if content changed
            old_version = self._knowledge_versions.get(knowledge_key)
            if old_version and not force_update and old_version.hash == version.hash:
                # No changes, skip sync
                result.details["skipped"] = "No content changes detected"
                return result

        # Add new segments
        new_segment_ids = []
        try:
            for i, doc in enumerate(documents):
                segment = ContextSegment(
                    type=ContextType.BACKGROUND,
                    priority=priority,
                    content=doc,
                    tokens=len(doc.split()),  # Rough estimate
                    session_id=session_id,
                    metadata=ContextMetadata(
                        created_at=datetime.now(),
                        custom={
                            "knowledge_id": knowledge_id,
                            "version_id": version.version_id if self.enable_versioning else None,
                            "document_index": i,
                            "source": source,
                        }
                    )
                )

                stored_segment = self.context_manager.add_context(
                    session_id,
                    segment.content,
                    segment.type,
                    segment.priority,
                    metadata=segment.metadata.model_dump()
                )

                new_segment_ids.append(stored_segment.id)
                result.segments_added += 1

            # Invalidate old segments only after all new writes succeed
            if invalidate_old:
                old_segment_ids = self._knowledge_context_map.get(knowledge_key, [])
                if old_segment_ids:
                    result.segments_invalidated = self._invalidate_segments(
                        session_id, old_segment_ids
                    )
        except Exception as sync_error:
            # Delete only writes completed by this attempt. Never pass an empty
            # ID list: ContextManager interprets it as deleting the whole session.
            # A rollback error propagates with the original write error chained.
            if new_segment_ids:
                try:
                    self.context_manager.delete_context(session_id, segment_ids=new_segment_ids)
                except Exception as rollback_error:
                    raise rollback_error from sync_error
            raise

        # Update mapping
        self._knowledge_context_map[knowledge_key] = new_segment_ids
        if self.enable_versioning:
            self._knowledge_versions[knowledge_key] = version
            result.version = version

        result.details["knowledge_id"] = knowledge_id
        result.details["documents_processed"] = len(documents)

        return result

    def update_knowledge_context(
        self,
        knowledge_id: str,
        session_id: str,
        new_documents: Optional[List[str]] = None,
        **kwargs
    ) -> SyncResult:
        """Update context when knowledge base changes.

        This handles incremental updates to knowledge, resolving conflicts
        with existing context and applying the configured resolution strategy.

        Args:
            knowledge_id: Identifier for the knowledge being updated
            session_id: Session to update context for
            new_documents: New knowledge documents (if None, invalidate only)
            **kwargs: Additional parameters:
                - conflict_strategy: Override default conflict strategy

        Returns:
            SyncResult with operation statistics
        """
        result = SyncResult()
        knowledge_key = (session_id, knowledge_id)

        # Get existing segments for this knowledge
        old_segment_ids = self._knowledge_context_map.get(knowledge_key, [])
        existing_segments = self._get_segments_by_ids(session_id, old_segment_ids)

        if not new_documents:
            # Just invalidate existing segments
            result.segments_invalidated = self._invalidate_segments(
                session_id, old_segment_ids
            )
            return result

        # Resolve conflicts between old and new
        conflict_strategy = kwargs.get(
            "conflict_strategy",
            self.conflict_strategy
        )

        resolved_segments = self._resolve_conflicts(
            existing_segments,
            new_documents,
            conflict_strategy,
            knowledge_id,
            session_id
        )

        result.conflicts_resolved = len(existing_segments)
        result.segments_updated = len(resolved_segments)

        # Update context with resolved segments
        for segment in resolved_segments:
            self.context_manager.add_context(
                session_id,
                segment.content,
                segment.type,
                segment.priority,
                metadata=segment.metadata.model_dump()
            )

        return result

    def _resolve_conflicts(
        self,
        existing_segments: List[ContextSegment],
        new_documents: List[str],
        strategy: ConflictResolutionStrategy,
        knowledge_id: str,
        session_id: str
    ) -> List[ContextSegment]:
        """Resolve conflicts between existing and new knowledge.

        Args:
            existing_segments: Current context segments
            new_documents: New knowledge documents
            strategy: Conflict resolution strategy
            knowledge_id: Knowledge identifier
            session_id: Session identifier

        Returns:
            List of resolved segments
        """
        if strategy == ConflictResolutionStrategy.NEWEST_WINS:
            # Replace old with new
            return [
                ContextSegment(
                    type=ContextType.BACKGROUND,
                    priority=ContextPriority.HIGH,
                    content=doc,
                    tokens=len(doc.split()),
                    session_id=session_id,
                    metadata=ContextMetadata(
                        created_at=datetime.now(),
                        custom={
                            "knowledge_id": knowledge_id,
                            "updated_at": datetime.now().isoformat(),
                        }
                    )
                )
                for doc in new_documents
            ]

        elif strategy == ConflictResolutionStrategy.CRITICAL_PRESERVED:
            # Keep CRITICAL segments, replace others
            critical_segments = [
                seg for seg in existing_segments
                if seg.priority == ContextPriority.CRITICAL
            ]
            new_segments = [
                ContextSegment(
                    type=ContextType.BACKGROUND,
                    priority=ContextPriority.HIGH,
                    content=doc,
                    tokens=len(doc.split()),
                    session_id=session_id,
                    metadata=ContextMetadata(created_at=datetime.now())
                )
                for doc in new_documents
            ]
            return critical_segments + new_segments

        elif strategy == ConflictResolutionStrategy.VERSION_BOTH:
            # Keep both old and new as versioned segments
            versioned_old = []
            for seg in existing_segments:
                seg.metadata.custom["version"] = "old"
                seg.priority = ContextPriority.MEDIUM
                versioned_old.append(seg)

            versioned_new = []
            for doc in new_documents:
                versioned_new.append(
                    ContextSegment(
                        type=ContextType.BACKGROUND,
                        priority=ContextPriority.HIGH,
                        content=doc,
                        tokens=len(doc.split()),
                        session_id=session_id,
                        metadata=ContextMetadata(
                            created_at=datetime.now(),
                            custom={"version": "new"}
                        )
                    )
                )

            return versioned_old + versioned_new

        else:  # MERGE
            # Simple merge: combine old and new
            return existing_segments + [
                ContextSegment(
                    type=ContextType.BACKGROUND,
                    priority=ContextPriority.HIGH,
                    content=doc,
                    tokens=len(doc.split()),
                    session_id=session_id,
                    metadata=ContextMetadata(created_at=datetime.now())
                )
                for doc in new_documents
            ]

    def _invalidate_segments(
        self,
        session_id: str,
        segment_ids: List[str]
    ) -> int:
        """Mark segments as invalid/outdated.

        Args:
            session_id: Session identifier
            segment_ids: List of segment IDs to invalidate

        Returns:
            Number of segments invalidated
        """
        # Get existing segments
        all_segments = self.context_manager.get_context(session_id)

        invalidated = 0
        for segment in all_segments:
            if segment.id in segment_ids:
                # Lower priority to mark as outdated
                segment.priority = ContextPriority.LOW
                segment.metadata.custom["invalidated"] = True
                segment.metadata.custom["invalidated_at"] = datetime.now().isoformat()
                invalidated += 1

        return invalidated

    def _get_segments_by_ids(
        self,
        session_id: str,
        segment_ids: List[str]
    ) -> List[ContextSegment]:
        """Retrieve segments by their IDs.

        Args:
            session_id: Session identifier
            segment_ids: List of segment IDs

        Returns:
            List of matching segments
        """
        all_segments = self.context_manager.get_context(session_id)
        return [seg for seg in all_segments if seg.id in segment_ids]

    def _compute_hash(self, documents: List[str]) -> str:
        """Compute hash of documents for change detection.

        Args:
            documents: List of document contents

        Returns:
            Hash string
        """
        import hashlib
        content = "".join(documents)
        return hashlib.sha256(content.encode()).hexdigest()

    def get_knowledge_version(
        self, knowledge_id: str, session_id: str | None = None
    ) -> KnowledgeVersion | None:
        """Get the last successfully applied version for a knowledge ID.

        Args:
            knowledge_id: Knowledge identifier
            session_id: Restrict lookup to this session. If omitted, return the
                latest successfully applied version across sessions.

        Returns:
            KnowledgeVersion if exists, None otherwise
        """
        if session_id is not None:
            return self._knowledge_versions.get((session_id, knowledge_id))
        return self.list_knowledge_versions().get(knowledge_id)

    def list_knowledge_versions(
        self, session_id: str | None = None
    ) -> dict[str, KnowledgeVersion]:
        """List successfully applied versions, optionally restricted to a session.

        Args:
            session_id: Session to query. If omitted, preserve the knowledge-ID
                keyed view with the latest version of each knowledge ID.

        Returns:
            Dictionary mapping knowledge_id to version info
        """
        versions = {}
        for (tracked_session, knowledge_id), version in self._knowledge_versions.items():
            if session_id is not None and tracked_session != session_id:
                continue
            previous = versions.get(knowledge_id)
            if previous is None or version.timestamp >= previous.timestamp:
                versions[knowledge_id] = version
        return versions
