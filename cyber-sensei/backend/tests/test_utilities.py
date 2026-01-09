"""
Tests for error handling and pagination utilities

Tests custom exceptions and pagination functions
"""

import pytest
from fastapi import HTTPException
from app.utils.errors import (
    AppException, ValidationError, NotFoundError, ConflictError,
    UnauthorizedError, ForbiddenError, InternalServerError, BadRequestError,
    RateLimitError, create_error_response
)
from app.utils.pagination import paginate, PaginatedResponse, create_paginated_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


# Create test database
Base = declarative_base()

class TestModel(Base):
    """Test model for pagination tests"""
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestExceptionClasses:
    """Test custom exception classes"""
    
    def test_validation_error_structure(self):
        """Test ValidationError has correct structure"""
        error = ValidationError(
            message="Invalid email",
            field="email"
        )
        assert error.status_code == 422
        assert error.error_code == "validation_error"
        assert isinstance(error, HTTPException)
    
    def test_validation_error_detail(self):
        """Test ValidationError detail structure"""
        error = ValidationError(
            message="Email is invalid",
            field="email"
        )
        assert error.detail["error"] == "validation_error"
        assert error.detail["message"] == "Email is invalid"
        assert error.detail["field"] == "email"
    
    def test_not_found_error_with_id(self):
        """Test NotFoundError with resource ID"""
        error = NotFoundError("User", 123)
        assert error.status_code == 404
        assert error.detail["error"] == "not_found"
        assert error.detail["resource"] == "User"
        assert error.detail["resource_id"] == "123"
    
    def test_not_found_error_without_id(self):
        """Test NotFoundError without resource ID"""
        error = NotFoundError("User")
        assert error.status_code == 404
        assert "not found" in error.detail["message"].lower()
    
    def test_conflict_error(self):
        """Test ConflictError"""
        error = ConflictError("Email already exists", resource="User")
        assert error.status_code == 409
        assert error.detail["error"] == "conflict"
        assert error.detail["resource"] == "User"
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError"""
        error = UnauthorizedError("Invalid credentials")
        assert error.status_code == 401
        assert error.detail["error"] == "unauthorized"
    
    def test_forbidden_error(self):
        """Test ForbiddenError"""
        error = ForbiddenError("Access denied")
        assert error.status_code == 403
        assert error.detail["error"] == "forbidden"
    
    def test_bad_request_error(self):
        """Test BadRequestError"""
        error = BadRequestError("Invalid request", details={"field": "username"})
        assert error.status_code == 400
        assert error.detail["error"] == "bad_request"
        assert error.detail["field"] == "username"
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        error = RateLimitError()
        assert error.status_code == 429
        assert error.detail["error"] == "rate_limit"
    
    def test_internal_server_error(self):
        """Test InternalServerError"""
        error = InternalServerError()
        assert error.status_code == 500
        assert error.detail["error"] == "internal_error"
    
    def test_error_response_function(self):
        """Test create_error_response function"""
        response = create_error_response(
            status_code=400,
            error_code="bad_request",
            message="Invalid input",
            field="email"
        )
        assert response["error"] == "bad_request"
        assert response["message"] == "Invalid input"
        assert response["field"] == "email"
        assert "timestamp" in response


class TestPaginationUtility:
    """Test pagination utility function"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Add test data
        for i in range(25):
            session.add(TestModel(name=f"Item {i}"))
        session.commit()
        
        yield session
        session.close()
    
    def test_paginate_first_page(self, db_session):
        """Test pagination first page"""
        query = db_session.query(TestModel)
        result = paginate(query, page=1, limit=10)
        
        assert result["page"] == 1
        assert result["limit"] == 10
        assert result["total"] == 25
        assert result["pages"] == 3
        assert len(result["items"]) == 10
    
    def test_paginate_second_page(self, db_session):
        """Test pagination second page"""
        query = db_session.query(TestModel)
        result = paginate(query, page=2, limit=10)
        
        assert result["page"] == 2
        assert len(result["items"]) == 10
    
    def test_paginate_last_page(self, db_session):
        """Test pagination last page"""
        query = db_session.query(TestModel)
        result = paginate(query, page=3, limit=10)
        
        assert result["page"] == 3
        assert len(result["items"]) == 5
    
    def test_paginate_page_beyond_range(self, db_session):
        """Test pagination with page beyond available range"""
        query = db_session.query(TestModel)
        result = paginate(query, page=10, limit=10)
        
        assert len(result["items"]) == 0
    
    def test_paginate_custom_limit(self, db_session):
        """Test pagination with custom limit"""
        query = db_session.query(TestModel)
        result = paginate(query, page=1, limit=5)
        
        assert result["limit"] == 5
        assert result["pages"] == 5
        assert len(result["items"]) == 5
    
    def test_paginate_limit_max_100(self, db_session):
        """Test pagination limit is capped at 100"""
        query = db_session.query(TestModel)
        result = paginate(query, page=1, limit=200)
        
        assert result["limit"] == 100
    
    def test_paginate_invalid_page(self, db_session):
        """Test pagination with invalid page number"""
        query = db_session.query(TestModel)
        result = paginate(query, page=-5, limit=10)
        
        # Should default to page 1
        assert result["page"] == 1
    
    def test_paginate_invalid_limit(self, db_session):
        """Test pagination with invalid limit"""
        query = db_session.query(TestModel)
        result = paginate(query, page=1, limit=-10)
        
        # Should default to 10
        assert result["limit"] == 10
    
    def test_paginate_zero_limit(self, db_session):
        """Test pagination with zero limit"""
        query = db_session.query(TestModel)
        result = paginate(query, page=1, limit=0)
        
        # Should default to 10
        assert result["limit"] == 10
    
    def test_paginate_response_model(self, db_session):
        """Test PaginatedResponse model"""
        response = PaginatedResponse(
            items=[{"id": 1, "name": "Item"}],
            total=100,
            page=1,
            limit=10,
            pages=10
        )
        assert response.total == 100
        assert response.page == 1
        assert response.pages == 10
    
    def test_create_paginated_response(self, db_session):
        """Test create_paginated_response helper"""
        query = db_session.query(TestModel)
        data = paginate(query, page=1, limit=10)
        response = create_paginated_response(data)
        
        assert isinstance(response, PaginatedResponse)
        assert response.total == 25
        assert response.page == 1


class TestErrorIntegration:
    """Test error handling integration"""
    
    def test_exception_chain(self):
        """Test exception can be caught as HTTPException"""
        error = ValidationError("Invalid", field="email")
        assert isinstance(error, HTTPException)
        assert error.status_code == 422
    
    def test_error_dict_format(self):
        """Test error detail is properly formatted"""
        error = NotFoundError("User", 42)
        detail = error.detail
        
        assert isinstance(detail, dict)
        assert "error" in detail
        assert "message" in detail
        assert "resource" in detail
    
    def test_multiple_error_types(self):
        """Test different error types have correct codes"""
        errors = [
            (ValidationError("msg"), 422),
            (NotFoundError("res"), 404),
            (ConflictError("msg"), 409),
            (UnauthorizedError(), 401),
            (ForbiddenError(), 403),
            (BadRequestError("msg"), 400),
            (RateLimitError(), 429),
            (InternalServerError(), 500)
        ]
        
        for error, expected_code in errors:
            assert error.status_code == expected_code


class TestPaginationEdgeCases:
    """Test pagination edge cases"""
    
    @pytest.fixture
    def empty_db_session(self):
        """Create empty test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        session.close()
    
    def test_paginate_empty_result(self, empty_db_session):
        """Test pagination with empty results"""
        query = empty_db_session.query(TestModel)
        result = paginate(query, page=1, limit=10)
        
        assert result["total"] == 0
        assert result["pages"] == 1
        assert len(result["items"]) == 0
    
    @pytest.fixture
    def single_item_db(self):
        """Create test database with single item"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        session.add(TestModel(name="Single Item"))
        session.commit()
        
        yield session
        session.close()
    
    def test_paginate_single_item(self, single_item_db):
        """Test pagination with single item"""
        query = single_item_db.query(TestModel)
        result = paginate(query, page=1, limit=10)
        
        assert result["total"] == 1
        assert result["pages"] == 1
        assert len(result["items"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
