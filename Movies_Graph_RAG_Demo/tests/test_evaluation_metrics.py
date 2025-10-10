"""
Tests for evaluation metrics.

This module tests the evaluation metrics used to assess the quality
of the GraphRAG recommendation system.
"""

import pytest
from unittest.mock import Mock
from src.evaluation.metrics import (
    RecommendationResult,
    PrecisionRecall,
    NDCG,
    UserSatisfaction,
    ResponseTime,
    CostEfficiency,
    RecommendationMetrics,
)


class TestRecommendationResult:
    """Test the RecommendationResult dataclass."""
    
    def test_recommendation_result_creation(self):
        """Test creating a RecommendationResult instance."""
        recommendations = [{"id": "1", "title": "Movie 1"}]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test query",
            response_time=0.5,
            cost=0.01
        )
        
        assert result.recommendations == recommendations
        assert result.query == "test query"
        assert result.response_time == 0.5
        assert result.cost == 0.01
        assert result.metadata is None


class TestPrecisionRecall:
    """Test the PrecisionRecall metric."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metric = PrecisionRecall(k=5)
        self.ground_truth = [
            {"id": "1", "title": "Movie 1"},
            {"id": "2", "title": "Movie 2"},
            {"id": "3", "title": "Movie 3"},
        ]
    
    def test_perfect_precision_and_recall(self):
        """Test perfect precision and recall."""
        recommendations = [
            {"id": "1", "title": "Movie 1"},
            {"id": "2", "title": "Movie 2"},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        scores = self.metric.calculate(result, self.ground_truth)
        
        assert scores["precision"] == 1.0
        assert scores["recall"] == 2/3  # 2 out of 3 ground truth items
        assert scores["f1"] == 2 * (1.0 * 2/3) / (1.0 + 2/3)
    
    def test_zero_precision_and_recall(self):
        """Test zero precision and recall."""
        recommendations = [
            {"id": "4", "title": "Movie 4"},
            {"id": "5", "title": "Movie 5"},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        scores = self.metric.calculate(result, self.ground_truth)
        
        assert scores["precision"] == 0.0
        assert scores["recall"] == 0.0
        assert scores["f1"] == 0.0
    
    def test_empty_recommendations(self):
        """Test with empty recommendations."""
        result = RecommendationResult(
            recommendations=[],
            query="test",
            response_time=0.5
        )
        
        scores = self.metric.calculate(result, self.ground_truth)
        
        assert scores["precision"] == 0.0
        assert scores["recall"] == 0.0
        assert scores["f1"] == 0.0
    
    def test_partial_precision_and_recall(self):
        """Test partial precision and recall."""
        recommendations = [
            {"id": "1", "title": "Movie 1"},  # Correct
            {"id": "4", "title": "Movie 4"},  # Incorrect
            {"id": "2", "title": "Movie 2"},  # Correct
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        scores = self.metric.calculate(result, self.ground_truth)
        
        assert scores["precision"] == 2/3  # 2 out of 3 recommendations correct
        assert scores["recall"] == 2/3     # 2 out of 3 ground truth items found


class TestNDCG:
    """Test the NDCG metric."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metric = NDCG(k=5)
        self.ground_truth = [
            {"id": "1", "title": "Movie 1"},
            {"id": "2", "title": "Movie 2"},
            {"id": "3", "title": "Movie 3"},
        ]
    
    def test_perfect_ndcg(self):
        """Test perfect NDCG score."""
        recommendations = [
            {"id": "1", "title": "Movie 1"},
            {"id": "2", "title": "Movie 2"},
            {"id": "3", "title": "Movie 3"},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        ndcg = self.metric.calculate(result, self.ground_truth)
        
        assert ndcg == 1.0
    
    def test_zero_ndcg(self):
        """Test zero NDCG score."""
        recommendations = [
            {"id": "4", "title": "Movie 4"},
            {"id": "5", "title": "Movie 5"},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        ndcg = self.metric.calculate(result, self.ground_truth)
        
        assert ndcg == 0.0
    
    def test_partial_ndcg(self):
        """Test partial NDCG score."""
        recommendations = [
            {"id": "1", "title": "Movie 1"},  # Correct
            {"id": "4", "title": "Movie 4"},  # Incorrect
            {"id": "2", "title": "Movie 2"},  # Correct
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        ndcg = self.metric.calculate(result, self.ground_truth)
        
        # Should be between 0 and 1
        assert 0.0 <= ndcg <= 1.0
        assert ndcg > 0.0  # Should be positive since we have some correct items


class TestUserSatisfaction:
    """Test the UserSatisfaction metric."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metric = UserSatisfaction()
        self.ground_truth = [
            {"id": "1", "title": "Movie 1", "genres": ["Action"]},
            {"id": "2", "title": "Movie 2", "genres": ["Comedy"]},
        ]
    
    def test_high_satisfaction(self):
        """Test high satisfaction score."""
        recommendations = [
            {"id": "1", "title": "Movie 1", "genres": ["Action"]},
            {"id": "2", "title": "Movie 2", "genres": ["Comedy"]},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        satisfaction = self.metric.calculate(result, self.ground_truth)
        
        assert 0.0 <= satisfaction <= 1.0
        assert satisfaction > 0.5  # Should be high due to good overlap
    
    def test_low_satisfaction(self):
        """Test low satisfaction score."""
        recommendations = [
            {"id": "3", "title": "Movie 3", "genres": ["Drama"]},
            {"id": "4", "title": "Movie 4", "genres": ["Horror"]},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5
        )
        
        satisfaction = self.metric.calculate(result, self.ground_truth)
        
        assert 0.0 <= satisfaction <= 1.0
        assert satisfaction < 0.5  # Should be low due to poor overlap


class TestResponseTime:
    """Test the ResponseTime metric."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metric = ResponseTime()
    
    def test_fast_response(self):
        """Test fast response time."""
        result = RecommendationResult(
            recommendations=[],
            query="test",
            response_time=0.1  # 100ms
        )
        
        metrics = self.metric.calculate(result, [])
        
        assert metrics["response_time"] == 0.1
        assert metrics["is_fast"] is True
        assert metrics["is_acceptable"] is True
    
    def test_slow_response(self):
        """Test slow response time."""
        result = RecommendationResult(
            recommendations=[],
            query="test",
            response_time=2.0  # 2 seconds
        )
        
        metrics = self.metric.calculate(result, [])
        
        assert metrics["response_time"] == 2.0
        assert metrics["is_fast"] is False
        assert metrics["is_acceptable"] is False


class TestCostEfficiency:
    """Test the CostEfficiency metric."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metric = CostEfficiency()
        self.ground_truth = [{"id": "1", "title": "Movie 1"}]
    
    def test_cost_efficiency_with_cost(self):
        """Test cost efficiency calculation with cost."""
        recommendations = [{"id": "1", "title": "Movie 1"}]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5,
            cost=0.01
        )
        
        metrics = self.metric.calculate(result, self.ground_truth)
        
        assert metrics["cost_per_recommendation"] == 0.01
        assert metrics["total_cost"] == 0.01
        assert metrics["cost_efficiency"] > 0  # Should be positive
    
    def test_cost_efficiency_without_cost(self):
        """Test cost efficiency calculation without cost."""
        recommendations = [{"id": "1", "title": "Movie 1"}]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5,
            cost=None
        )
        
        metrics = self.metric.calculate(result, self.ground_truth)
        
        assert metrics["cost_per_recommendation"] == 0.0
        assert metrics["cost_efficiency"] == 0.0


class TestRecommendationMetrics:
    """Test the RecommendationMetrics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metrics = RecommendationMetrics()
        self.ground_truth = [
            {"id": "1", "title": "Movie 1"},
            {"id": "2", "title": "Movie 2"},
        ]
    
    def test_evaluate_all_metrics(self):
        """Test evaluating all metrics."""
        recommendations = [
            {"id": "1", "title": "Movie 1"},
            {"id": "3", "title": "Movie 3"},
        ]
        result = RecommendationResult(
            recommendations=recommendations,
            query="test",
            response_time=0.5,
            cost=0.01
        )
        
        evaluation = self.metrics.evaluate(result, self.ground_truth)
        
        # Check that all metrics are calculated
        assert "precision_recall" in evaluation
        assert "ndcg" in evaluation
        assert "user_satisfaction" in evaluation
        assert "response_time" in evaluation
        assert "cost_efficiency" in evaluation
        
        # Check that precision_recall returns a dict
        assert isinstance(evaluation["precision_recall"], dict)
        assert "precision" in evaluation["precision_recall"]
        assert "recall" in evaluation["precision_recall"]
        assert "f1" in evaluation["precision_recall"]
    
    def test_get_metric_descriptions(self):
        """Test getting metric descriptions."""
        descriptions = self.metrics.get_metric_descriptions()
        
        assert isinstance(descriptions, dict)
        assert "precision_recall" in descriptions
        assert "ndcg" in descriptions
        assert "user_satisfaction" in descriptions
        assert "response_time" in descriptions
        assert "cost_efficiency" in descriptions
        
        # Check that descriptions are strings
        for desc in descriptions.values():
            assert isinstance(desc, str)
            assert len(desc) > 0
    
    def test_add_custom_metric(self):
        """Test adding a custom metric."""
        class CustomMetric:
            def calculate(self, result, ground_truth):
                return 0.5
            
            def get_description(self):
                return "Custom metric"
        
        custom_metric = CustomMetric()
        self.metrics.add_custom_metric("custom", custom_metric)
        
        assert "custom" in self.metrics.metrics
        assert self.metrics.metrics["custom"] == custom_metric
    
    def test_remove_metric(self):
        """Test removing a metric."""
        initial_count = len(self.metrics.metrics)
        
        self.metrics.remove_metric("precision_recall")
        
        assert "precision_recall" not in self.metrics.metrics
        assert len(self.metrics.metrics) == initial_count - 1
    
    def test_remove_nonexistent_metric(self):
        """Test removing a non-existent metric."""
        initial_count = len(self.metrics.metrics)
        
        self.metrics.remove_metric("nonexistent")
        
        # Should not change the count
        assert len(self.metrics.metrics) == initial_count
