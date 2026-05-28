# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import re
import statistics

from agentuniverse_product.service.admin_service.dto import (
    AlertItemDTO,
    GuardrailDiagnosticsDTO,
    GuardrailScoreDTO,
)
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.session_service.session_service import SessionService


class AdminGuardrailService:
    """Derive lightweight LPP-style diagnostics from persisted session messages."""

    @staticmethod
    def _normalize_content(content: object | None) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content.strip()
        return str(content).strip()

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text.lower()) if token]

    @staticmethod
    def _clamp(value: float) -> float:
        return round(max(0.0, min(value, 100.0)), 2)

    @staticmethod
    def _collect_messages(session: SessionDTO | None) -> list[str]:
        if session is None:
            return []
        return [
            AdminGuardrailService._normalize_content(message.content)
            for message in (session.messages or [])
            if AdminGuardrailService._normalize_content(message.content)
        ]

    @staticmethod
    def _logic_consistency(message_count: int) -> float:
        if message_count == 0:
            return 35.0
        if message_count == 1:
            return 55.0
        if message_count >= 4:
            return 92.0
        return 75.0

    @staticmethod
    def _info_entropy(tokens: list[str]) -> float:
        if not tokens:
            return 20.0
        unique_ratio = len(set(tokens)) / len(tokens)
        return AdminGuardrailService._clamp(unique_ratio * 100)

    @staticmethod
    def _diversity_ttr(tokens: list[str]) -> float:
        if not tokens:
            return 15.0
        return AdminGuardrailService._clamp((len(set(tokens)) / len(tokens)) * 100)

    @staticmethod
    def _lpp_feature(lengths: list[int]) -> float:
        if not lengths:
            return 25.0
        if len(lengths) == 1:
            return 60.0
        try:
            stdev = statistics.pstdev(lengths)
            avg = statistics.mean(lengths)
        except statistics.StatisticsError:
            return 50.0
        if avg <= 0:
            return 40.0
        variation = stdev / avg
        return AdminGuardrailService._clamp(100 - min(variation * 120, 70))

    @staticmethod
    def _detect_warnings(
        texts: list[str],
        tokens: list[str],
        scores: GuardrailScoreDTO,
    ) -> list[AlertItemDTO]:
        warnings: list[AlertItemDTO] = []

        if not texts:
            warnings.append(
                AlertItemDTO(
                    level="info",
                    message="No message content available for guardrail diagnostics.",
                )
            )
            return warnings

        normalized = [text.lower() for text in texts]
        if len(normalized) != len(set(normalized)):
            warnings.append(
                AlertItemDTO(
                    level="warning",
                    message="Repeated message content detected in the current session.",
                )
            )

        if scores.diversity_ttr < 40:
            warnings.append(
                AlertItemDTO(
                    level="warning",
                    message="Low lexical diversity detected. Output may be homogenized.",
                )
            )

        if scores.lpp_feature < 45:
            warnings.append(
                AlertItemDTO(
                    level="warning",
                    message="High structural similarity across messages. Review for templated responses.",
                )
            )

        if scores.safety_score < 60:
            warnings.append(
                AlertItemDTO(
                    level="critical",
                    message="Composite safety score is below the recommended threshold.",
                )
            )

        return warnings

    @staticmethod
    def _risk_level(safety_score: float, warning_count: int) -> str:
        if safety_score < 60 or warning_count >= 2:
            return "high"
        if safety_score < 75 or warning_count == 1:
            return "medium"
        return "low"

    @staticmethod
    def analyze_session(session: SessionDTO | None) -> GuardrailDiagnosticsDTO:
        texts = AdminGuardrailService._collect_messages(session)
        tokens: list[str] = []
        for text in texts:
            tokens.extend(AdminGuardrailService._tokenize(text))

        lengths = [len(text) for text in texts]
        logic_consistency = AdminGuardrailService._logic_consistency(len(texts))
        info_entropy = AdminGuardrailService._info_entropy(tokens)
        diversity_ttr = AdminGuardrailService._diversity_ttr(tokens)
        lpp_feature = AdminGuardrailService._lpp_feature(lengths)
        safety_score = AdminGuardrailService._clamp(
            logic_consistency * 0.25
            + info_entropy * 0.2
            + diversity_ttr * 0.2
            + lpp_feature * 0.15
            + min(len(texts) * 8, 20)
        )

        scores = GuardrailScoreDTO(
            logic_consistency=logic_consistency,
            info_entropy=info_entropy,
            diversity_ttr=diversity_ttr,
            lpp_feature=lpp_feature,
            safety_score=safety_score,
        )
        warnings = AdminGuardrailService._detect_warnings(texts, tokens, scores)

        return GuardrailDiagnosticsDTO(
            guardrail_enabled=True,
            risk_level=AdminGuardrailService._risk_level(safety_score, len(warnings)),
            scores=scores,
            warnings=warnings,
        )

    @staticmethod
    def get_session_diagnostics(session_id: str) -> GuardrailDiagnosticsDTO:
        if not session_id:
            raise ValueError("session_id is required parameter.")

        try:
            session = SessionService.get_session_detail(session_id)
        except ValueError:
            session = None

        return AdminGuardrailService.analyze_session(session)
