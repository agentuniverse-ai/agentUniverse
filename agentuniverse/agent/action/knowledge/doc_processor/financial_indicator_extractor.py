# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: financial_indicator_extractor.py

import re
import logging
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


@dataclass
class FinancialMetric:
    """Represents a financial metric extracted from text.

    Attributes:
        name: Metric name (e.g., 'revenue', 'profit').
        value: Numeric value.
        unit: Unit of measurement (e.g., 'USD', 'million').
        time_period: Time period (e.g., 'Q1 2024', 'FY2023').
        context: Surrounding text context.
        position: Position in document.
        confidence: Extraction confidence score.
        raw_match: Original matched text for precise currency detection.
    """
    name: str
    value: float
    unit: str
    time_period: Optional[str] = None
    context: str = ""
    position: int = 0
    confidence: float = 1.0
    raw_match: str = ""


@dataclass
class Comparison:
    """Represents a comparative metric (e.g., YoY growth).

    Attributes:
        metric_name: Name of the metric being compared.
        current_value: Current period value.
        previous_value: Previous period value.
        change: Absolute change.
        change_percent: Percentage change.
        comparison_type: Type of comparison (YoY, QoQ, etc.).
    """
    metric_name: str
    current_value: float
    previous_value: float
    change: float
    change_percent: float
    comparison_type: str


class FinancialIndicatorExtractor(DocProcessor):
    """Extract financial indicators and metrics from financial reports.

    This processor extracts structured financial information including:
    1. Financial metrics (revenue, profit, margins, ratios)
    2. Temporal context (quarters, fiscal years)
    3. Comparative analysis (YoY, QoQ growth rates)
    4. Currency normalization

    Attributes:
        metrics: List of metric names to extract.
        extract_temporal: Whether to extract time period information.
        extract_comparisons: Whether to extract comparative metrics.
        currency_normalization: Whether to normalize currency values.
        use_llm: Whether to use LLM for enhanced extraction.
        llm_name: Name of the LLM to use.
        skip_on_error: Whether to skip documents that fail processing.
    """

    metrics: List[str] = None
    extract_temporal: bool = True
    extract_comparisons: bool = True
    currency_normalization: bool = True
    use_llm: bool = False
    llm_name: Optional[str] = None
    skip_on_error: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.metrics is None:
            self.metrics = [
                'revenue', 'sales', 'income',
                'profit', 'earnings', 'ebitda',
                'gross_margin', 'operating_margin', 'net_margin', 'margin',  # Specific margins before general
                'eps', 'earnings_per_share',
                'roi', 'return_on_investment', 'roe', 'roa',
                'debt', 'debt_ratio', 'leverage',
                'cash_flow', 'free_cash_flow',
                'assets', 'liabilities', 'equity',
                'growth_rate', 'market_share', 'churn_rate',  # Added percentage metrics
            ]

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Extract financial indicators from documents.

        Args:
            origin_docs: List of financial report documents.
            query: Optional query object (not used in this processor).

        Returns:
            List of documents with extracted financial metrics.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting financial indicator extraction from {len(origin_docs)} documents")

        processed_docs = []

        for doc in origin_docs:
            try:
                enhanced_doc = self._extract_from_document(doc)
                processed_docs.append(enhanced_doc)
                logger.info(f"Extracted metrics from document {doc.id}")
            except Exception as e:
                logger.error(f"Failed to extract from document {doc.id}: {e}")
                if not self.skip_on_error:
                    raise
                # Pass through original document if skip_on_error is True
                processed_docs.append(doc)

        logger.info(f"Financial extraction complete for {len(processed_docs)} documents")
        return processed_docs

    def _extract_from_document(self, doc: Document) -> Document:
        """Extract financial metrics from a single document.

        Args:
            doc: Financial report document.

        Returns:
            Document with extracted metrics in metadata.
        """
        text = doc.text

        # Step 1: Extract financial metrics
        metrics = self._extract_metrics(text)
        logger.debug(f"Extracted {len(metrics)} metrics")

        # Step 2: Extract temporal context
        time_periods = []
        if self.extract_temporal:
            time_periods = self._extract_time_periods(text)
            # Associate time periods with metrics
            for metric in metrics:
                metric.time_period = self._find_nearest_time_period(
                    metric.position, time_periods, text
                )

        # Step 3: Extract comparisons
        comparisons = []
        if self.extract_comparisons:
            comparisons = self._detect_comparisons(text, metrics)
            logger.debug(f"Detected {len(comparisons)} comparisons")

        # Step 4: Normalize currency if enabled
        if self.currency_normalization:
            self._normalize_currencies(metrics)

        # Step 5: Create enhanced document with metadata
        enhanced_doc = self._create_enhanced_document(doc, metrics, comparisons)

        return enhanced_doc

    def _extract_metrics(self, text: str) -> List[FinancialMetric]:
        """Extract financial metrics from text.

        Args:
            text: Financial report text.

        Returns:
            List of extracted FinancialMetric objects.
        """
        metrics = []

        # Define metric patterns (comprehensive)
        metric_patterns = {
            'revenue': [
                r'revenue[s]?\s*(?:of\s+|was\s+|reached\s+|totaled\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
                r'sales\s*(?:of\s+|was\s+|reached\s+|totaled\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
                r'total\s+revenue\s*(?:of\s+|:\s*|for\s+[A-Z0-9\s]+)?(?:reached\s+|was\s+|totaled\s+)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
                r'营收[达到]?(-?[0-9,.]+)\s*(万|亿)?',
                r'[\$€£¥](-?[0-9,.]+)\s*(?:million|billion|M|B)\s+(?:in\s+)?revenue',
            ],
            'sales': [
                r'sales\s*(?:of\s+|was\s+|reached\s+|totaled\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
            ],
            'income': [
                r'(?:net\s+)?income\s*(?:of\s+|was\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            'profit': [
                r'(?:net\s+|gross\s+|operating\s+)?profit\s*(?:of\s+|was\s+|reached\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
                r'(?:net\s+|operating\s+)?(?:loss|losses)\s*(?:of\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
                r'earnings\s*(?:of\s+|was\s+|reached\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
                r'净利润(?:达到)?[\$€£¥]?(-?[0-9,.]+)\s*(万|亿)?',
                r'(?:negative|loss)(?:\s+of)?\s*[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
                r'\(-?[\$€£¥]?([0-9,.]+)\s*(million|billion|M|B)?\)',  # Negative in parentheses
            ],
            'margin': [
                r'(?:gross|operating|net)?\s*margin[:]?\s+(?:of\s+|was\s+)?(-?[0-9,.]+)%',
                r'(?:gross|operating|net)?\s*margin\s+(?:reached\s+)?(-?[0-9,.]+)%',
                r'利润率(-?[0-9,.]+)%',
            ],
            'gross_margin': [
                r'gross\s+margin[:]?\s+(-?[0-9,.]+)%',
            ],
            'operating_margin': [
                r'operating\s+margin[:]?\s+(-?[0-9,.]+)%',
            ],
            'net_margin': [
                r'net\s+(?:profit\s+)?margin[:]?\s+(-?[0-9,.]+)%',
            ],
            'eps': [
                r'(?:diluted\s+)?(?:earnings|EPS)\s+per\s+share\s*(?:of\s+|was\s+|reached\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)',
                r'EPS\s*(?:of\s+|was\s+|reached\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)',
                r'diluted\s+EPS\s*(?:of\s+|was\s+|reached\s+|:\s*)?[\$€£¥]?(-?[0-9,.]+)',
                r'每股收益(-?[0-9,.]+)',
            ],
            'earnings_per_share': [
                r'earnings\s+per\s+share[:]?\s+[\$€£¥]?(-?[0-9,.]+)',
            ],
            'cash_flow': [
                r'(?:operating\s+|free\s+)?cash\s+flow\s+(?:of\s+)?[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B|千万|亿)?',
                r'现金流(-?[0-9,.]+)\s*(万|亿)?',
            ],
            'free_cash_flow': [
                r'free\s+cash\s+flow[:]?\s+[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            'roi': [
                r'(?:return\s+on\s+investment|ROI)[:]?\s+(-?[0-9,.]+)%',
            ],
            'roe': [
                r'(?:return\s+on\s+equity|ROE)[:]?\s+(-?[0-9,.]+)%',
            ],
            'roa': [
                r'(?:return\s+on\s+assets|ROA)[:]?\s+(-?[0-9,.]+)%',
            ],
            'debt': [
                r'(?:total\s+)?debt[:]?\s+[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            'debt_ratio': [
                r'debt[- ]to[- ]equity\s+ratio[:]?\s+(-?[0-9,.]+)',
                r'debt\s+ratio[:]?\s+(-?[0-9,.]+)',
            ],
            'assets': [
                r'(?:total\s+)?assets[:]?\s+[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            'liabilities': [
                r'(?:total\s+)?liabilities[:]?\s+[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            'equity': [
                r'(?:shareholders?\s+)?equity[:]?\s+[\$€£¥]?(-?[0-9,.]+)\s*(million|billion|M|B)?',
            ],
            # Generic percentage-based metrics
            'growth_rate': [
                r'growth\s+rate[:]?\s+(-?[0-9,.]+)%',
            ],
            'market_share': [
                r'market\s+share[:]?\s+(-?[0-9,.]+)%',
            ],
            'churn_rate': [
                r'churn\s+rate[:]?\s+(-?[0-9,.]+)%',
            ],
        }

        # Extract metrics using patterns
        for metric_name in self.metrics:
            patterns = metric_patterns.get(metric_name, [])

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    try:
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)

                        # Check if in parentheses (accounting negative)
                        full_match = match.group(0)
                        if full_match.startswith('(') and full_match.endswith(')'):
                            value = -abs(value)
                        # Check for explicit "loss" or "negative" keywords
                        elif 'loss' in full_match.lower() or 'negative' in full_match.lower():
                            value = -abs(value)

                        # Get unit if available
                        unit = match.group(2) if len(match.groups()) > 1 else ''

                        # Convert based on unit
                        value = self._convert_unit_to_base(value, unit)

                        # Get context
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]

                        metric = FinancialMetric(
                            name=metric_name,
                            value=value,
                            unit='USD',  # Default, will be normalized
                            context=context,
                            position=match.start(),
                            raw_match=full_match  # Store original matched text
                        )

                        metrics.append(metric)

                    except (ValueError, IndexError) as e:
                        logger.debug(f"Failed to parse metric: {e}")
                        continue

        return metrics

    def _convert_unit_to_base(self, value: float, unit: str) -> float:
        """Convert value based on unit to base unit.

        Args:
            value: Numeric value.
            unit: Unit string.

        Returns:
            Converted value in base unit.
        """
        unit_lower = unit.lower() if unit else ''

        multipliers = {
            'million': 1_000_000,
            'billion': 1_000_000_000,
            'm': 1_000_000,
            'b': 1_000_000_000,
            '千万': 10_000_000,
            '亿': 100_000_000,
            '万': 10_000,
        }

        multiplier = multipliers.get(unit_lower, 1.0)
        return value * multiplier

    def _extract_time_periods(self, text: str) -> List[Tuple[str, int]]:
        """Extract time period references from text.

        Args:
            text: Financial report text.

        Returns:
            List of (time_period, position) tuples.
        """
        time_periods = []

        # Time period patterns
        patterns = [
            r'(Q[1-4]\s+20\d{2})',  # Q1 2024
            r'(FY\s*20\d{2})',  # FY2023
            r'(fiscal\s+year\s+20\d{2})',  # fiscal year 2023
            r'(20\d{2}\s+Q[1-4])',  # 2024 Q1
            r'(第[一二三四]季度\s*20\d{2})',  # Chinese: 第一季度 2024
            r'(20\d{2}年度)',  # Chinese: 2024年度
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                time_periods.append((match.group(1), match.start()))

        return time_periods

    def _find_nearest_time_period(self, position: int,
                                  time_periods: List[Tuple[str, int]],
                                  text: str) -> Optional[str]:
        """Find the nearest time period to a given position.

        Args:
            position: Position in text.
            time_periods: List of (time_period, position) tuples.
            text: Full text.

        Returns:
            Nearest time period string or None.
        """
        if not time_periods:
            return None

        # Find nearest time period (within 200 characters)
        nearest = None
        min_distance = float('inf')

        for period, period_pos in time_periods:
            distance = abs(position - period_pos)
            if distance < min_distance and distance < 200:
                min_distance = distance
                nearest = period

        return nearest

    def _detect_comparisons(self, text: str, metrics: List[FinancialMetric]) -> List[Comparison]:
        """Detect comparative metrics (YoY, QoQ).

        Args:
            text: Financial report text.
            metrics: Extracted metrics.

        Returns:
            List of Comparison objects.
        """
        comparisons = []

        # Enhanced comparison patterns for YoY and QoQ
        comparison_patterns = [
            # YoY patterns
            (r'([0-9,.]+)%?\s+(?:YoY|year-over-year|year-on-year)', 'yoy'),
            (r'(?:YoY|year-over-year|year-on-year)\s+(?:growth|increase|up|decline|decrease|down)\s+(?:of\s+)?([0-9,.]+)%?', 'yoy'),
            (r'(?:growth|increase|up|rose)\s+([0-9,.]+)%?\s+(?:YoY|year-over-year|year-on-year)', 'yoy'),
            (r'([a-zA-Z\s]+)\s+up\s+([0-9,.]+)%\s+year-over-year', 'yoy'),
            (r'同比增长([0-9,.]+)%?', 'yoy'),

            # QoQ patterns
            (r'([0-9,.]+)%?\s+(?:QoQ|quarter-over-quarter|quarter-on-quarter)', 'qoq'),
            (r'(?:QoQ|quarter-over-quarter|quarter-on-quarter)\s+(?:growth|increase|up|decline|decrease|down)\s+(?:of\s+)?([0-9,.]+)%?', 'qoq'),
            (r'(?:growth|increase|up|rose)\s+([0-9,.]+)%?\s+(?:QoQ|quarter-over-quarter|quarter-on-quarter)', 'qoq'),
            (r'环比增长([0-9,.]+)%?', 'qoq'),

            # General comparison patterns (try to infer type from context)
            (r'([0-9,.]+)%?\s+(?:increase|growth|up|higher)\s+(?:compared to|vs\.?|versus|over)', 'unknown'),
            (r'(?:increased|grew|rose)\s+by\s+([0-9,.]+)%', 'unknown'),
        ]

        for pattern, comp_type in comparison_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    # Extract the percentage value (might be in group 1 or 2)
                    change_percent_str = None
                    for i in range(1, match.lastindex + 1 if match.lastindex else 1):
                        try:
                            val = match.group(i)
                            if val and re.match(r'^[0-9,.]+$', val):
                                change_percent_str = val
                                break
                        except:
                            continue

                    if not change_percent_str:
                        continue

                    change_percent = float(change_percent_str.replace(',', ''))

                    # Determine comparison type (use pattern's type if not unknown)
                    comparison_type = comp_type
                    if comparison_type == 'unknown':
                        # Try to infer from context
                        match_text = match.group(0).lower()
                        if 'yoy' in match_text or 'year' in match_text or '同比' in match_text:
                            comparison_type = 'yoy'
                        elif 'qoq' in match_text or 'quarter' in match_text or '环比' in match_text:
                            comparison_type = 'qoq'

                    # Find associated metric
                    metric_name = self._find_associated_metric(match.start(), metrics)

                    comparison = Comparison(
                        metric_name=metric_name or 'general',
                        current_value=0.0,  # Would need more context to extract
                        previous_value=0.0,
                        change=0.0,
                        change_percent=change_percent,
                        comparison_type=comparison_type
                    )

                    comparisons.append(comparison)

                except (ValueError, IndexError) as e:
                    logger.debug(f"Failed to parse comparison: {e}")
                    continue

        return comparisons

    def _find_associated_metric(self, position: int, metrics: List[FinancialMetric]) -> Optional[str]:
        """Find the metric associated with a comparison.

        Args:
            position: Position of comparison in text.
            metrics: List of extracted metrics.

        Returns:
            Metric name or None.
        """
        # Find nearest metric (within 100 characters)
        nearest_metric = None
        min_distance = float('inf')

        for metric in metrics:
            distance = abs(position - metric.position)
            if distance < min_distance and distance < 100:
                min_distance = distance
                nearest_metric = metric.name

        return nearest_metric

    def _normalize_currencies(self, metrics: List[FinancialMetric]) -> None:
        """Normalize currency values to a standard currency.

        Args:
            metrics: List of financial metrics.

        Note:
            Modifies metrics in place. Currently uses fixed exchange rates.
        """
        # Fixed exchange rates (simplified)
        exchange_rates = {
            'CNY': 0.14,  # CNY to USD
            'EUR': 1.09,  # EUR to USD
            'GBP': 1.27,  # GBP to USD
            'JPY': 0.0067,  # JPY to USD
        }

        for metric in metrics:
            # Check context for currency indicators
            if '¥' in metric.context or '元' in metric.context or 'CNY' in metric.context:
                metric.value *= exchange_rates.get('CNY', 1.0)
                metric.unit = 'USD'
            elif '€' in metric.context or 'EUR' in metric.context:
                metric.value *= exchange_rates.get('EUR', 1.0)
                metric.unit = 'USD'
            elif '£' in metric.context or 'GBP' in metric.context:
                metric.value *= exchange_rates.get('GBP', 1.0)
                metric.unit = 'USD'

    def _create_enhanced_document(self, original_doc: Document,
                                  metrics: List[FinancialMetric],
                                  comparisons: List[Comparison]) -> Document:
        """Create enhanced document with financial metrics in metadata.

        Args:
            original_doc: Original document.
            metrics: Extracted metrics.
            comparisons: Detected comparisons.

        Returns:
            Enhanced document with financial metadata.
        """
        # Build metadata
        metadata = original_doc.metadata.copy() if original_doc.metadata else {}

        # Save original metadata
        metadata['original_metadata'] = original_doc.metadata.copy() if original_doc.metadata else {}

        metadata.update({
            'processor_name': self.name,
            'processor_version': '1.0',
            'processing_timestamp': datetime.now().isoformat(),
            'source_document_id': original_doc.id,
        })

        # Group financial metrics by metric name
        financial_metrics = {}
        for metric in metrics:
            if metric.name not in financial_metrics:
                financial_metrics[metric.name] = []

            financial_metrics[metric.name].append({
                'value': metric.value,
                'unit': metric.unit,
                'time_period': metric.time_period,
                'confidence': metric.confidence,
                'context': metric.context[:100] if len(metric.context) > 100 else metric.context,
                'currency': self._detect_currency(metric.raw_match if metric.raw_match else metric.context),
                'scale': self._detect_scale(metric.context),
            })

        metadata['financial_metrics'] = financial_metrics
        metadata['metric_count'] = len(metrics)

        # Add comparisons
        comparative_metrics = []
        if comparisons:
            for comp in comparisons:
                comparative_metrics.append({
                    'metric': comp.metric_name,
                    'change_percent': comp.change_percent,
                    'comparison_type': comp.comparison_type,
                })

        if comparative_metrics:
            metadata['comparative_metrics'] = comparative_metrics

        # Add keywords
        keywords = original_doc.keywords.copy() if original_doc.keywords else set()
        for metric in metrics:
            keywords.add(metric.name)
        if comparisons:
            keywords.add('comparative_analysis')

        # Create enhanced document
        enhanced_doc = Document(
            id=original_doc.id,
            text=original_doc.text,
            metadata=metadata,
            embedding=original_doc.embedding,
            keywords=keywords
        )

        return enhanced_doc

    def _detect_currency(self, context: str) -> str:
        """Detect currency from context.

        Args:
            context: Text context.

        Returns:
            Currency code or empty string.
        """
        if '$' in context or 'USD' in context:
            return 'USD'
        elif '€' in context or 'EUR' in context:
            return 'EUR'
        elif '£' in context or 'GBP' in context:
            return 'GBP'
        elif '¥' in context or 'CNY' in context or '元' in context:
            return 'CNY'
        return 'USD'  # Default

    def _detect_scale(self, context: str) -> str:
        """Detect scale from context.

        Args:
            context: Text context.

        Returns:
            Scale indicator.
        """
        context_lower = context.lower()
        if 'billion' in context_lower or ' b' in context_lower or '亿' in context:
            return 'billion'
        elif 'million' in context_lower or ' m' in context_lower or '千万' in context or '百万' in context:
            return 'million'
        elif 'thousand' in context_lower or '千' in context:
            return 'thousand'
        return 'units'

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'FinancialIndicatorExtractor':
        """Initialize extractor parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing extractor parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "metrics"):
            self.metrics = doc_processor_configer.metrics
        if hasattr(doc_processor_configer, "extract_temporal"):
            self.extract_temporal = doc_processor_configer.extract_temporal
        if hasattr(doc_processor_configer, "extract_comparisons"):
            self.extract_comparisons = doc_processor_configer.extract_comparisons
        if hasattr(doc_processor_configer, "currency_normalization"):
            self.currency_normalization = doc_processor_configer.currency_normalization
        if hasattr(doc_processor_configer, "use_llm"):
            self.use_llm = doc_processor_configer.use_llm
        if hasattr(doc_processor_configer, "llm_name"):
            self.llm_name = doc_processor_configer.llm_name
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error

        return self
