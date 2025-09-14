#!/usr/bin/env python3
"""
Unit tests for websocket functionality
Tests the new endpoints without requiring a full server setup
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, AsyncMock

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.routes.jobs import send_websocket_progress, analyze_job_description, match_projects_to_job
from app.routes.generate import generate_full_application
from app.models.project import JobDescription, JobDescriptionInput, GenerateFullApplicationRequest

class TestWebSocketEndpoints:
    """Test suite for websocket-enabled endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.mock_websocket_manager = Mock()
        self.mock_websocket_manager.send_progress = AsyncMock()
        
    @pytest.mark.asyncio
    async def test_send_websocket_progress(self):
        """Test the websocket progress helper function"""
        # Mock the websocket manager
        with patch('app.routes.jobs.websocket_manager', self.mock_websocket_manager):
            client_id = "test-client-123"
            message = "Test progress message"
            step = "testing"
            
            await send_websocket_progress(client_id, message, step, 1, 2)
            
            # Verify the websocket manager was called
            self.mock_websocket_manager.send_progress.assert_called_once()
            
            # Check the call arguments
            call_args = self.mock_websocket_manager.send_progress.call_args
            assert call_args[0][0] == client_id  # client_id
            
            progress_data = call_args[0][1]  # progress_data
            assert progress_data['message'] == message
            assert progress_data['step'] == step
            assert progress_data['current'] == 1
            assert progress_data['total'] == 2
            assert 'timestamp' in progress_data
    
    @pytest.mark.asyncio
    async def test_analyze_job_without_websocket(self):
        """Test job analysis without websocket (no client_id)"""
        # Mock the GeminiService
        mock_analysis = {
            "title": "Software Engineer",
            "company": "Test Company",
            "required_technologies": ["Python", "JavaScript"],
            "experience_level": "Mid-level",
            "soft_skills": ["Communication", "Problem-solving"],
            "analysis_summary": "Test job analysis"
        }
        
        with patch('app.routes.jobs.GeminiService') as mock_gemini_class:
            mock_gemini_instance = Mock()
            mock_gemini_instance.job_description_parser.return_value = mock_analysis
            mock_gemini_class.return_value = mock_gemini_instance
            
            job_desc = JobDescription(description="Test job description")
            result = await analyze_job_description(job_desc)
            
            assert result == mock_analysis
            mock_gemini_instance.job_description_parser.assert_called_once_with("Test job description")
    
    @pytest.mark.asyncio 
    async def test_analyze_job_with_websocket(self):
        """Test job analysis with websocket updates"""
        # Mock the GeminiService
        mock_analysis = {
            "title": "Software Engineer",
            "required_technologies": ["Python", "JavaScript"]
        }
        
        with patch('app.routes.jobs.GeminiService') as mock_gemini_class, \
             patch('app.routes.jobs.websocket_manager', self.mock_websocket_manager):
            
            mock_gemini_instance = Mock()
            mock_gemini_instance.job_description_parser.return_value = mock_analysis
            mock_gemini_class.return_value = mock_gemini_instance
            
            job_desc = JobDescription(description="Test job description", client_id="test-123")
            result = await analyze_job_description(job_desc)
            
            assert result == mock_analysis
            
            # Should have called websocket twice (start + completion)
            assert self.mock_websocket_manager.send_progress.call_count == 2
    
    @pytest.mark.asyncio
    async def test_analyze_job_error_handling(self):
        """Test job analysis error handling with websocket"""
        with patch('app.routes.jobs.GeminiService') as mock_gemini_class, \
             patch('app.routes.jobs.websocket_manager', self.mock_websocket_manager):
            
            mock_gemini_instance = Mock()
            mock_gemini_instance.job_description_parser.side_effect = Exception("Gemini error")
            mock_gemini_class.return_value = mock_gemini_instance
            
            job_desc = JobDescription(description="Test job description", client_id="test-123")
            
            with pytest.raises(Exception):
                await analyze_job_description(job_desc)
            
            # Should have sent error message via websocket
            self.mock_websocket_manager.send_progress.assert_called()
    
    @pytest.mark.asyncio
    async def test_match_projects_with_websocket(self):
        """Test project matching with websocket updates"""
        mock_projects = [
            Mock(project=Mock(name="Project1"), similarity_score=0.8),
            Mock(project=Mock(name="Project2"), similarity_score=0.7)
        ]
        
        with patch('app.routes.jobs.EmbeddingService') as mock_embedding_class, \
             patch('app.routes.jobs.websocket_manager', self.mock_websocket_manager):
            
            mock_embedding_instance = Mock()
            mock_embedding_instance.find_matching_projects.return_value = mock_projects
            mock_embedding_class.return_value = mock_embedding_instance
            
            job_desc_input = JobDescriptionInput(
                job_description={"title": "Software Engineer", "description": "Test description"},
                client_id="test-123"
            )
            
            result = await match_projects_to_job(job_desc_input)
            
            assert len(result) == 2
            assert result[0].similarity_score >= result[1].similarity_score  # Should be sorted
            
            # Should have sent websocket updates
            assert self.mock_websocket_manager.send_progress.call_count >= 2

class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_job_analysis_flow(self):
        """Test the complete job analysis flow"""
        # This would be a more comprehensive test that could be run 
        # against a test database and mock services
        pass
    
    def test_websocket_message_format(self):
        """Test that websocket messages follow the expected format"""
        expected_fields = ['type', 'message', 'step', 'current', 'total', 'repo_name', 'timestamp']
        
        # Mock data that would be sent via websocket
        message_data = {
            "type": "progress",
            "message": "Test message",
            "step": "testing",
            "current": 1,
            "total": 2,
            "repo_name": "",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        # Verify all expected fields are present
        for field in expected_fields:
            assert field in message_data
        
        # Verify it's JSON serializable
        json_str = json.dumps(message_data)
        parsed = json.loads(json_str)
        assert parsed == message_data

def test_websocket_url_format():
    """Test websocket URL format"""
    client_id = "test-client-123"
    expected_url = f"ws://localhost:5000/ws/{client_id}"
    
    # This would be used in frontend
    assert expected_url.startswith("ws://")
    assert client_id in expected_url

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])