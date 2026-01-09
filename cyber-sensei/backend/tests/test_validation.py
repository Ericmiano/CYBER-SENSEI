"""
Unit tests for validation schemas and utilities

Tests Pydantic schemas and custom exception classes
"""

import pytest
from pydantic import ValidationError as PydanticValidationError
from app.schemas import (
    UserCreate, UserLogin, UserUpdate,
    TopicCreate, TopicUpdate,
    QuizAnswer, QuizSubmission,
    DocumentCreate, DocumentUpdate,
    SearchQuery, PaginationParams
)
from app.utils.errors import (
    ValidationError, NotFoundError, ConflictError,
    UnauthorizedError, ForbiddenError, BadRequestError
)
from app.utils.pagination import paginate, PaginatedResponse


class TestUserValidation:
    """Test user creation and login validation"""
    
    def test_valid_user_creation(self):
        """Test valid user creation"""
        user = UserCreate(
            username="johndoe",
            email="john@example.com",
            password="SecurePass123!",
            full_name="John Doe"
        )
        assert user.username == "johndoe"
        assert user.email == "john@example.com"
        assert user.full_name == "John Doe"
    
    def test_user_email_validation(self):
        """Test email format validation"""
        with pytest.raises(PydanticValidationError):
            UserCreate(
                username="johndoe",
                email="invalid-email",
                password="SecurePass123!"
            )
    
    def test_user_password_min_length(self):
        """Test password minimum length"""
        with pytest.raises(PydanticValidationError):
            UserCreate(
                username="johndoe",
                email="john@example.com",
                password="short"
            )
    
    def test_user_username_validation(self):
        """Test username validation (alphanumeric/dash/underscore)"""
        with pytest.raises(PydanticValidationError):
            UserCreate(
                username="john@doe",  # @ not allowed
                email="john@example.com",
                password="SecurePass123!"
            )
    
    def test_user_username_length(self):
        """Test username length constraints"""
        with pytest.raises(PydanticValidationError):
            UserCreate(
                username="ab",  # Too short
                email="john@example.com",
                password="SecurePass123!"
            )
    
    def test_valid_login(self):
        """Test valid login credentials"""
        login = UserLogin(
            email="john@example.com",
            password="SecurePass123!"
        )
        assert login.email == "john@example.com"
        assert login.password == "SecurePass123!"
    
    def test_login_email_validation(self):
        """Test login email validation"""
        with pytest.raises(PydanticValidationError):
            UserLogin(
                email="invalid-email",
                password="SecurePass123!"
            )


class TestTopicValidation:
    """Test topic creation and update validation"""
    
    def test_valid_topic_creation(self):
        """Test valid topic creation"""
        topic = TopicCreate(
            name="Cryptography 101",
            description="Learn cryptography basics",
            difficulty_level="beginner"
        )
        assert topic.name == "Cryptography 101"
        assert topic.difficulty_level == "beginner"
    
    def test_topic_difficulty_enum(self):
        """Test difficulty level enum validation"""
        with pytest.raises(PydanticValidationError):
            TopicCreate(
                name="Topic",
                difficulty_level="expert"  # Invalid level
            )
    
    def test_topic_name_required(self):
        """Test topic name is required"""
        with pytest.raises(PydanticValidationError):
            TopicCreate(name="")
    
    def test_topic_description_optional(self):
        """Test topic description is optional"""
        topic = TopicCreate(
            name="Topic",
            difficulty_level="beginner"
        )
        assert topic.description == ""


class TestQuizValidation:
    """Test quiz submission validation"""
    
    def test_valid_quiz_answer(self):
        """Test valid quiz answer"""
        answer = QuizAnswer(
            question_id=1,
            answer="The correct answer"
        )
        assert answer.question_id == 1
        assert answer.answer == "The correct answer"
    
    def test_quiz_answer_required_fields(self):
        """Test quiz answer required fields"""
        with pytest.raises(PydanticValidationError):
            QuizAnswer(question_id=1)  # Missing answer
    
    def test_valid_quiz_submission(self):
        """Test valid quiz submission"""
        submission = QuizSubmission(
            quiz_id=1,
            answers=[
                QuizAnswer(question_id=1, answer="answer1"),
                QuizAnswer(question_id=2, answer="answer2")
            ]
        )
        assert submission.quiz_id == 1
        assert len(submission.answers) == 2


class TestDocumentValidation:
    """Test knowledge base document validation"""
    
    def test_valid_document_creation(self):
        """Test valid document creation"""
        doc = DocumentCreate(
            title="Introduction to Cryptography",
            content="Cryptography is the practice of secure communication...",
            category="security",
            tags=["cryptography", "security", "beginner"]
        )
        assert doc.title == "Introduction to Cryptography"
        assert len(doc.tags) == 3
    
    def test_document_title_required(self):
        """Test document title is required"""
        with pytest.raises(PydanticValidationError):
            DocumentCreate(title="", content="Content")
    
    def test_document_content_required(self):
        """Test document content is required"""
        with pytest.raises(PydanticValidationError):
            DocumentCreate(title="Title", content="")


class TestSearchValidation:
    """Test search query validation"""
    
    def test_valid_search_query(self):
        """Test valid search query"""
        query = SearchQuery(
            query="cryptography",
            search_type="all",
            limit=10,
            offset=0
        )
        assert query.query == "cryptography"
        assert query.limit == 10
    
    def test_search_type_enum(self):
        """Test search type enum validation"""
        with pytest.raises(PydanticValidationError):
            SearchQuery(
                query="test",
                search_type="invalid"
            )
    
    def test_search_limit_validation(self):
        """Test search limit validation"""
        with pytest.raises(PydanticValidationError):
            SearchQuery(
                query="test",
                limit=101  # Exceeds max
            )
    
    def test_search_offset_validation(self):
        """Test search offset must be non-negative"""
        with pytest.raises(PydanticValidationError):
            SearchQuery(
                query="test",
                offset=-1
            )


class TestPaginationValidation:
    """Test pagination parameters validation"""
    
    def test_valid_pagination_params(self):
        """Test valid pagination parameters"""
        params = PaginationParams(
            page=1,
            limit=10,
            sort_by="created_at",
            sort_order="desc"
        )
        assert params.page == 1
        assert params.limit == 10
    
    def test_page_must_be_positive(self):
        """Test page must be >= 1"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(page=0)
    
    def test_limit_must_be_positive(self):
        """Test limit must be >= 1"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(limit=0)
    
    def test_sort_order_enum(self):
        """Test sort order must be asc or desc"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(sort_order="invalid")


class TestErrorHandling:
    """Test custom exception classes"""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError(
            message="Email is invalid",
            field="email"
        )
        assert error.status_code == 422
        assert error.error_code == "validation_error"
    
    def test_not_found_error(self):
        """Test NotFoundError creation"""
        error = NotFoundError("User", 123)
        assert error.status_code == 404
        assert error.error_code == "not_found"
    
    def test_conflict_error(self):
        """Test ConflictError creation"""
        error = ConflictError("Email already exists")
        assert error.status_code == 409
        assert error.error_code == "conflict"
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError creation"""
        error = UnauthorizedError()
        assert error.status_code == 401
        assert error.error_code == "unauthorized"
    
    def test_forbidden_error(self):
        """Test ForbiddenError creation"""
        error = ForbiddenError()
        assert error.status_code == 403
        assert error.error_code == "forbidden"
    
    def test_bad_request_error(self):
        """Test BadRequestError creation"""
        error = BadRequestError("Invalid request")
        assert error.status_code == 400
        assert error.error_code == "bad_request"


class TestPaginationUtility:
    """Test pagination utility function"""
    
    def test_pagination_params_defaults(self):
        """Test pagination default values"""
        params = PaginationParams()
        assert params.page == 1
        assert params.limit == 10
        assert params.sort_order == "desc"
    
    def test_pagination_limit_max(self):
        """Test pagination limit cannot exceed 100"""
        with pytest.raises(PydanticValidationError):
            PaginationParams(limit=150)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
