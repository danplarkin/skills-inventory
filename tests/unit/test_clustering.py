"""Unit tests for clustering Lambda function."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from moto import mock_dynamodb
import boto3


@pytest.fixture
def clustering_event():
    """Create mock event for clustering."""
    return {
        "skill_categories": ["Python", "AWS", "ML"],
        "threshold": 3
    }


def test_perform_clustering():
    """Test clustering functionality."""
    with patch('boto3.client') as mock_boto:
        mock_athena = MagicMock()
        mock_athena.start_query_execution.return_value = {
            'QueryExecutionId': 'test-query-id'
        }
        mock_athena.get_query_results.return_value = {
            'ResultSet': {
                'Rows': [
                    {'Data': [{'VarCharValue': 'employee_id'}, {'VarCharValue': 'skills'}]},
                    {'Data': [{'VarCharValue': 'emp_001'}, {'VarCharValue': 'Python,AWS'}]}
                ]
            }
        }
        mock_boto.return_value = mock_athena
        
        from src.lambda_functions.clustering import lambda_handler
        
        response = lambda_handler(clustering_event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'clusters' in body or 'message' in body


def test_empty_data():
    """Test handling of empty data."""
    with patch('boto3.client') as mock_boto:
        mock_athena = MagicMock()
        mock_athena.start_query_execution.return_value = {
            'QueryExecutionId': 'test-query-id'
        }
        mock_athena.get_query_results.return_value = {
            'ResultSet': {
                'Rows': [
                    {'Data': [{'VarCharValue': 'employee_id'}, {'VarCharValue': 'skills'}]}
                ]
            }
        }
        mock_boto.return_value = mock_athena
        
        from src.lambda_functions.clustering import lambda_handler
        
        response = lambda_handler({}, None)
        
        assert response['statusCode'] in [200, 400]
