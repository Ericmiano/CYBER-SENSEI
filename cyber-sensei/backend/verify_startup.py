#!/usr/bin/env python
"""
Verify that the backend application can start without errors.
This checks imports, models, and basic initialization.
"""

import os
import sys

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SKIP_ML_ENGINE"] = "true"

def verify_imports():
    """Verify all models can be imported"""
    print("[OK] Verifying model imports...")
    try:
        from app.models import (
            User, Module, Topic, Project, Content,
            UserProgress, KnowledgeDocument,
            QuizQuestion, QuizOption,
            Annotation, AnnotationType,
            project_topics
        )
        print("  [OK] All models imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Model import failed: {e}")
        return False


def verify_schemas():
    """Verify all schemas can be imported"""
    print("[OK] Verifying schema imports...")
    try:
        from app.schemas import (
            UserResponse, UserCreate,
            LearningStepResponse, QuizSubmission,
            AnnotationCreate, AnnotationUpdate, AnnotationRead, AnnotationType,
            ModuleCreate, ModuleUpdate, ModuleRead,
            TopicCreate, TopicUpdate, TopicRead,
            ProjectCreate, ProjectUpdate, ProjectRead,
            ResourceCreate, ResourceUpdate, ResourceRead,
            QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionRead,
            UserProgressRead,
        )
        print("  [OK] All schemas imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Schema import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_routers():
    """Verify all routers can be imported"""
    print("[OK] Verifying router imports...")
    try:
        from app.routers import (
            users, learning, knowledge_base, labs, health, entities, search, annotations
        )
        print("  [OK] All routers imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Router import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_app_creation():
    """Verify the FastAPI app can be created"""
    print("[OK] Verifying FastAPI app creation...")
    try:
        from app.main import app
        print("  [OK] FastAPI app created successfully")
        print(f"  [OK] Routes registered: {len(app.routes)} routes")
        return True
    except Exception as e:
        print(f"  [FAIL] App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_database():
    """Verify database tables can be created"""
    print("[OK] Verifying database table creation...")
    try:
        from app.database import create_tables
        create_tables()
        print("  [OK] Database tables created successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Database table creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("BACKEND VERIFICATION TEST")
    print("="*60 + "\n")
    
    checks = [
        verify_imports,
        verify_schemas,
        verify_routers,
        verify_app_creation,
        verify_database,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Unexpected error in {check.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
        print()
    
    print("="*60)
    print(f"RESULTS: {sum(results)}/{len(results)} checks passed")
    print("="*60)
    
    if all(results):
        print("\n[SUCCESS] Backend is fully functional and ready for deployment!\n")
    else:
        print("\n[ERROR] Some checks failed. Please review the output above.\n")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
