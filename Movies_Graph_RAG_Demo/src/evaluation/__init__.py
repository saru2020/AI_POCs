"""
Evaluation framework for Movies GraphRAG Demo.

This module provides comprehensive evaluation capabilities for the GraphRAG system,
including recommendation quality metrics, performance monitoring, and A/B testing.
"""

from .metrics import (
    RecommendationMetrics,
    PrecisionRecall,
    NDCG,
    UserSatisfaction,
    ResponseTime,
    CostEfficiency,
)
# from .evaluator import GraphRAGEvaluator
# from .test_data import TestDataGenerator
# from .benchmarks import BenchmarkSuite

__all__ = [
    "RecommendationMetrics",
    "PrecisionRecall", 
    "NDCG",
    "UserSatisfaction",
    "ResponseTime",
    "CostEfficiency",
    # "GraphRAGEvaluator",
    # "TestDataGenerator",
    # "BenchmarkSuite",
]
