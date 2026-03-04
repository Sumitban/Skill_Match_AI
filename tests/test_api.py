"""
API endpoint tests for Skill Match AI.
Tests the FastAPI endpoints with mocked dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId


@pytest.mark.unit
class TestJobEndpoints:
    """Tests for job management endpoints."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    @patch('Backened.app.jobs.job_service.JobService.create_job')
    def test_create_job_success(self, mock_create, client, job_create_request):
        """Test successful job creation."""
        mock_job = {
            "job_id": "test_job_001",
            "title": "Senior Python Developer"
        }
        mock_create.return_value = mock_job
        
        response = client.post("/jobs", json=job_create_request)
        
        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == "test_job_001"
        assert data["message"] == "Job created successfully"
    
    @patch('Backened.app.jobs.job_service.JobService.create_job')
    def test_create_job_duplicate(self, mock_create, client, job_create_request):
        """Test duplicate job creation error."""
        mock_create.side_effect = ValueError("Job with id 'test_job_001' already exists")
        
        response = client.post("/jobs", json=job_create_request)
        
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
    
    def test_create_job_invalid_request(self, client):
        """Test invalid job creation request."""
        response = client.post(
            "/jobs",
            json={"job_id": "", "title": "S", "raw_text": "short"}
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.unit
class TestCandidateEndpoints:
    """Tests for candidate processing endpoints."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    @patch('Backened.app.pipeline.candidate_service.CandidateService.process_candidate')
    def test_process_candidate_success(self, mock_process, client, candidate_create_request):
        """Test successful candidate processing."""
        test_id = ObjectId()
        mock_process.return_value = {
            "candidate_id": test_id,
            "job_id": "test_job_001"
        }
        
        response = client.post("/candidates", json=candidate_create_request)
        
        assert response.status_code == 201
        data = response.json()
        assert "candidate_id" in data
        assert data["message"] == "Candidate processed successfully"
    
    @patch('Backened.app.pipeline.candidate_service.CandidateService.process_candidate')
    def test_process_candidate_job_not_found(self, mock_process, client, candidate_create_request):
        """Test candidate processing when job not found."""
        mock_process.side_effect = ValueError("Job with id test_job_001 not found")
        
        response = client.post("/candidates", json=candidate_create_request)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @patch('Backened.app.storage.mongodb.Database.get_db')
    def test_get_candidates(self, mock_db, client, sample_candidate_document):
        """Test getting ranked candidates."""
        mock_db_instance = MagicMock()
        mock_db_instance.candidates.find.return_value.sort.return_value = [
            sample_candidate_document
        ]
        mock_db.return_value = mock_db_instance
        
        response = client.get("/candidates/test_job_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test_job_001"
        assert "count" in data
        assert isinstance(data["candidates"], list)


@pytest.mark.unit
class TestRankingEndpoints:
    """Tests for candidate ranking endpoints."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    @patch('Backened.app.ranking.baseline_ranker.BaselineRanker.rank_candidates')
    def test_rank_candidates_success(self, mock_rank, client):
        """Test successful candidate ranking."""
        mock_rank.return_value = [
            {"candidate_id": ObjectId(), "score": 0.85},
            {"candidate_id": ObjectId(), "score": 0.72}
        ]
        
        response = client.post("/rank/test_job_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test_job_001"
        assert data["count"] == 2
        assert data["message"] == "Ranking complete"
    
    @patch('Backened.app.ranking.baseline_ranker.BaselineRanker.rank_candidates')
    def test_rank_candidates_no_candidates(self, mock_rank, client):
        """Test ranking when no candidates found."""
        mock_rank.return_value = []
        
        response = client.post("/rank/test_job_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0


@pytest.mark.unit
class TestFeedbackEndpoints:
    """Tests for feedback submission endpoints."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    @patch('Backened.app.ranking.feedback_service.FeedbackService.update_hr_decision')
    def test_submit_feedback_success(self, mock_feedback, client, feedback_request):
        """Test successful feedback submission."""
        mock_feedback.return_value = True
        
        response = client.post("/feedback", json=feedback_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Feedback recorded successfully"
        assert "candidate_id" in data
    
    @patch('Backened.app.ranking.feedback_service.FeedbackService.update_hr_decision')
    def test_submit_feedback_invalid_decision(self, mock_feedback, client):
        """Test feedback with invalid decision value."""
        mock_feedback.side_effect = ValueError("Decision must be 0 or 1")
        
        response = client.post(
            "/feedback",
            json={"candidate_id": "507f1f77bcf86cd799439011", "decision": 2}
        )
        
        assert response.status_code == 422


@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling and responses."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    def test_404_not_found(self, client):
        """Test 404 endpoint not found."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_validation_error_response(self, client):
        """Test validation error response format."""
        response = client.post(
            "/jobs",
            json={"job_id": "", "title": "", "raw_text": ""}
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        from Backened.app.api.main import app
        return TestClient(app)
    
    @patch('Backened.app.jobs.job_service.JobService.create_job')
    @patch('Backened.app.pipeline.candidate_service.CandidateService.process_candidate')
    @patch('Backened.app.ranking.baseline_ranker.BaselineRanker.rank_candidates')
    @patch('Backened.app.ranking.feedback_service.FeedbackService.update_hr_decision')
    def test_complete_workflow(
        self, 
        mock_feedback,
        mock_rank,
        mock_process,
        mock_create,
        client,
        job_create_request,
        candidate_create_request,
        feedback_request
    ):
        """Test complete hiring workflow."""
        # Setup mocks
        mock_create.return_value = job_create_request
        test_id = ObjectId()
        mock_process.return_value = {
            "candidate_id": test_id,
            "job_id": job_create_request["job_id"]
        }
        mock_rank.return_value = [{"candidate_id": test_id, "score": 0.85}]
        mock_feedback.return_value = True
        
        # Create job
        job_response = client.post("/jobs", json=job_create_request)
        assert job_response.status_code == 201
        
        # Process candidate
        candidate_response = client.post("/candidates", json=candidate_create_request)
        assert candidate_response.status_code == 201
        
        # Rank candidates
        ranking_response = client.post(f"/rank/{job_create_request['job_id']}")
        assert ranking_response.status_code == 200
        
        # Submit feedback
        feedback_response = client.post("/feedback", json=feedback_request)
        assert feedback_response.status_code == 200
