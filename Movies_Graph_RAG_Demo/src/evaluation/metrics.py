"""
Evaluation metrics for GraphRAG recommendation system.

This module implements various metrics to evaluate the quality and performance
of the GraphRAG-based movie recommendation system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """Container for recommendation results and metadata."""
    recommendations: List[Dict[str, Any]]
    query: str
    response_time: float
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseMetric(ABC):
    """Base class for all evaluation metrics."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate the metric value."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what this metric measures."""
        pass


class PrecisionRecall(BaseMetric):
    """Calculate precision and recall for recommendations."""
    
    def __init__(self, k: int = 10):
        super().__init__(f"PrecisionRecall@{k}")
        self.k = k
    
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate precision and recall at k."""
        recommendations = result.recommendations[:self.k]
        ground_truth_ids = {item['id'] for item in ground_truth}
        
        if not recommendations:
            return {"precision": 0.0, "recall": 0.0}
        
        recommended_ids = {rec['id'] for rec in recommendations if 'id' in rec}
        
        # Calculate precision
        true_positives = len(recommended_ids.intersection(ground_truth_ids))
        precision = true_positives / len(recommended_ids) if recommended_ids else 0.0
        
        # Calculate recall
        recall = true_positives / len(ground_truth_ids) if ground_truth_ids else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        }
    
    def get_description(self) -> str:
        return f"Precision and recall at {self.k} recommendations"


class NDCG(BaseMetric):
    """Calculate Normalized Discounted Cumulative Gain."""
    
    def __init__(self, k: int = 10):
        super().__init__(f"NDCG@{k}")
        self.k = k
    
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate NDCG at k."""
        recommendations = result.recommendations[:self.k]
        ground_truth_ids = {item['id'] for item in ground_truth}
        
        if not recommendations:
            return 0.0
        
        # Create relevance scores (1 if in ground truth, 0 otherwise)
        relevance_scores = []
        for rec in recommendations:
            if 'id' in rec and rec['id'] in ground_truth_ids:
                relevance_scores.append(1.0)
            else:
                relevance_scores.append(0.0)
        
        # Calculate DCG
        dcg = self._dcg(relevance_scores)
        
        # Calculate IDCG (ideal DCG)
        ideal_relevance = [1.0] * min(len(ground_truth_ids), self.k)
        idcg = self._dcg(ideal_relevance)
        
        # Calculate NDCG
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        return ndcg
    
    def _dcg(self, relevance_scores: List[float]) -> float:
        """Calculate Discounted Cumulative Gain."""
        dcg = 0.0
        for i, score in enumerate(relevance_scores):
            dcg += score / np.log2(i + 2)  # i+2 because log2(1) = 0
        return dcg
    
    def get_description(self) -> str:
        return f"Normalized Discounted Cumulative Gain at {self.k}"


class UserSatisfaction(BaseMetric):
    """Calculate user satisfaction based on feedback."""
    
    def __init__(self):
        super().__init__("UserSatisfaction")
    
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate user satisfaction score."""
        # This would typically come from user feedback
        # For now, we'll use a simple heuristic based on recommendation quality
        if not result.recommendations:
            return 0.0
        
        # Simple satisfaction score based on recommendation diversity and quality
        diversity_score = self._calculate_diversity(result.recommendations)
        quality_score = self._calculate_quality(result.recommendations, ground_truth)
        
        return (diversity_score + quality_score) / 2.0
    
    def _calculate_diversity(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity of recommendations."""
        if len(recommendations) <= 1:
            return 0.0
        
        # Simple diversity based on genre variety
        genres = set()
        for rec in recommendations:
            if 'genres' in rec:
                genres.update(rec['genres'])
        
        return min(len(genres) / len(recommendations), 1.0)
    
    def _calculate_quality(self, recommendations: List[Dict[str, Any]], ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate quality score based on ground truth overlap."""
        ground_truth_ids = {item['id'] for item in ground_truth}
        recommended_ids = {rec['id'] for rec in recommendations if 'id' in rec}
        
        if not recommended_ids:
            return 0.0
        
        overlap = len(recommended_ids.intersection(ground_truth_ids))
        return overlap / len(recommended_ids)
    
    def get_description(self) -> str:
        return "User satisfaction score based on recommendation quality and diversity"


class ResponseTime(BaseMetric):
    """Calculate response time metrics."""
    
    def __init__(self):
        super().__init__("ResponseTime")
    
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate response time metrics."""
        return {
            "response_time": result.response_time,
            "is_fast": result.response_time < 0.2,  # Less than 200ms
            "is_acceptable": result.response_time < 1.0,  # Less than 1 second
        }
    
    def get_description(self) -> str:
        return "Response time metrics for query processing"


class CostEfficiency(BaseMetric):
    """Calculate cost efficiency metrics."""
    
    def __init__(self):
        super().__init__("CostEfficiency")
    
    def calculate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate cost efficiency metrics."""
        if result.cost is None:
            return {"cost_per_recommendation": 0.0, "cost_efficiency": 0.0}
        
        cost_per_rec = result.cost / len(result.recommendations) if result.recommendations else 0.0
        
        # Cost efficiency based on quality vs cost
        quality_score = self._calculate_quality_score(result.recommendations, ground_truth)
        cost_efficiency = quality_score / result.cost if result.cost > 0 else 0.0
        
        return {
            "cost_per_recommendation": cost_per_rec,
            "cost_efficiency": cost_efficiency,
            "total_cost": result.cost,
        }
    
    def _calculate_quality_score(self, recommendations: List[Dict[str, Any]], ground_truth: List[Dict[str, Any]]) -> float:
        """Calculate a simple quality score."""
        if not recommendations:
            return 0.0
        
        ground_truth_ids = {item['id'] for item in ground_truth}
        recommended_ids = {rec['id'] for rec in recommendations if 'id' in rec}
        
        overlap = len(recommended_ids.intersection(ground_truth_ids))
        return overlap / len(recommended_ids) if recommended_ids else 0.0
    
    def get_description(self) -> str:
        return "Cost efficiency metrics for LLM API usage"


class RecommendationMetrics:
    """Main class for calculating all recommendation metrics."""
    
    def __init__(self):
        self.metrics = {
            "precision_recall": PrecisionRecall(k=10),
            "ndcg": NDCG(k=10),
            "user_satisfaction": UserSatisfaction(),
            "response_time": ResponseTime(),
            "cost_efficiency": CostEfficiency(),
        }
        self.logger = logging.getLogger(__name__)
    
    def evaluate(self, result: RecommendationResult, ground_truth: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a recommendation result against ground truth."""
        evaluation_results = {}
        
        for metric_name, metric in self.metrics.items():
            try:
                score = metric.calculate(result, ground_truth)
                evaluation_results[metric_name] = score
                self.logger.debug(f"Metric {metric_name}: {score}")
            except Exception as e:
                self.logger.error(f"Error calculating metric {metric_name}: {e}")
                evaluation_results[metric_name] = None
        
        return evaluation_results
    
    def get_metric_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all metrics."""
        return {name: metric.get_description() for name, metric in self.metrics.items()}
    
    def add_custom_metric(self, name: str, metric: BaseMetric):
        """Add a custom metric to the evaluation suite."""
        self.metrics[name] = metric
        self.logger.info(f"Added custom metric: {name}")
    
    def remove_metric(self, name: str):
        """Remove a metric from the evaluation suite."""
        if name in self.metrics:
            del self.metrics[name]
            self.logger.info(f"Removed metric: {name}")
        else:
            self.logger.warning(f"Metric {name} not found")
