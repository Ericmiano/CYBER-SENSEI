"""
Production-safe seed data management system.

Features:
- Separation of schema creation from test data
- Environment-aware seeding (dev/staging/prod)
- Transactional integrity
- Rollback capability
- Dry-run simulation
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from enum import Enum

from .database import SessionLocal
from .models import (
    Module, Topic, QuizQuestion, Resource, Project, User, UserProgress
)

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types."""
    development = "development"
    staging = "staging"
    production = "production"


class SeedDataManager:
    """Manage seed data safely across environments."""
    
    def __init__(self, environment: Environment = Environment.development):
        """
        Initialize seed data manager.
        
        Args:
            environment: Target environment
        """
        self.environment = environment
        self.db = SessionLocal()
        self.changes = []
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.production
    
    def seed_modules(self, dry_run: bool = False) -> List[Module]:
        """
        Seed foundational modules.
        
        Only seeds core learning modules, no test data in production.
        """
        modules_data = [
            {
                "name": "Network Security Fundamentals",
                "description": "Learn the basics of network security, protocols, and defense mechanisms",
                "icon": "🔒",
                "color": "#3498db"
            },
            {
                "name": "Ethical Hacking Basics",
                "description": "Introduction to authorized penetration testing and security auditing",
                "icon": "🔓",
                "color": "#e74c3c"
            },
            {
                "name": "Cryptography Essentials",
                "description": "Understanding encryption, hashing, and secure communication",
                "icon": "🔐",
                "color": "#9b59b6"
            },
            {
                "name": "Threat Analysis & Response",
                "description": "Identify, analyze, and respond to security threats",
                "icon": "⚠️",
                "color": "#f39c12"
            },
            {
                "name": "Defensive Security",
                "description": "Strategies for protecting systems and networks",
                "icon": "🛡️",
                "color": "#27ae60"
            }
        ]
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create {len(modules_data)} modules")
            return []
        
        created_modules = []
        
        for module_data in modules_data:
            # Check if module already exists
            existing = self.db.query(Module).filter(
                Module.name == module_data["name"]
            ).first()
            
            if not existing:
                module = Module(
                    name=module_data["name"],
                    description=module_data["description"],
                    icon=module_data.get("icon"),
                    color=module_data.get("color", "#3498db"),
                    created_by="system",
                    created_at=datetime.utcnow()
                )
                self.db.add(module)
                created_modules.append(module)
                logger.info(f"Created module: {module.name}")
        
        self.changes.append({
            "type": "modules",
            "count": len(created_modules)
        })
        
        return created_modules
    
    def seed_topics(self, module_id: int, dry_run: bool = False) -> List[Topic]:
        """
        Seed topics for a module.
        
        Args:
            module_id: Parent module ID
            dry_run: Simulate without persisting
        """
        # Get topics specific to the module
        module = self.db.query(Module).filter(Module.id == module_id).first()
        if not module:
            logger.error(f"Module {module_id} not found")
            return []
        
        topics_map = {
            "Network Security Fundamentals": [
                ("OSI Model", "Understanding the 7 layers of network communication", 1, "beginner"),
                ("TCP/IP Protocol Suite", "Deep dive into TCP/IP protocols", 2, "intermediate"),
                ("Network Threats", "Common network-based attacks", 3, "intermediate"),
                ("Firewalls & IDS", "Implementing and managing firewalls", 4, "advanced")
            ],
            "Ethical Hacking Basics": [
                ("Reconnaissance", "Information gathering techniques", 1, "beginner"),
                ("Scanning & Enumeration", "Active network scanning methods", 2, "intermediate"),
                ("Vulnerability Assessment", "Identifying system weaknesses", 3, "intermediate"),
                ("Exploitation Basics", "Understanding attack vectors", 4, "advanced")
            ],
            "Cryptography Essentials": [
                ("Symmetric Encryption", "AES and DES algorithms", 1, "intermediate"),
                ("Asymmetric Encryption", "RSA and elliptic curve cryptography", 2, "advanced"),
                ("Hashing & Integrity", "MD5, SHA, and digital signatures", 3, "intermediate"),
                ("Key Management", "Secure key generation and storage", 4, "advanced")
            ],
            "Threat Analysis & Response": [
                ("Incident Detection", "Identifying security incidents", 1, "intermediate"),
                ("Log Analysis", "Mining logs for security events", 2, "intermediate"),
                ("Forensics Basics", "Digital evidence preservation", 3, "advanced"),
                ("Response Planning", "Creating incident response plans", 4, "advanced")
            ],
            "Defensive Security": [
                ("System Hardening", "Securing operating systems", 1, "intermediate"),
                ("Application Security", "Secure coding practices", 2, "intermediate"),
                ("Access Control", "Authentication and authorization", 3, "intermediate"),
                ("Monitoring & Alerting", "Real-time security monitoring", 4, "advanced")
            ]
        }
        
        topics_data = topics_map.get(module.name, [])
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create {len(topics_data)} topics for {module.name}")
            return []
        
        created_topics = []
        
        for name, description, order, difficulty in topics_data:
            existing = self.db.query(Topic).filter(
                Topic.name == name,
                Topic.module_id == module_id
            ).first()
            
            if not existing:
                topic = Topic(
                    name=name,
                    description=description,
                    module_id=module_id,
                    order=order,
                    difficulty=difficulty,
                    created_by="system",
                    created_at=datetime.utcnow()
                )
                self.db.add(topic)
                created_topics.append(topic)
                logger.info(f"Created topic: {name}")
        
        self.changes.append({
            "type": "topics",
            "count": len(created_topics)
        })
        
        return created_topics
    
    def seed_quiz_questions(self, topic_id: int, dry_run: bool = False) -> List[QuizQuestion]:
        """
        Seed quiz questions for a topic.
        
        Args:
            topic_id: Parent topic ID
            dry_run: Simulate without persisting
        """
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            logger.error(f"Topic {topic_id} not found")
            return []
        
        # Sample questions - in production, should load from comprehensive question bank
        sample_questions = [
            {
                "prompt": f"What is a key concept in {topic.name}?",
                "explanation": "This is a fundamental concept that forms the basis of understanding",
                "options": [
                    {"option_key": "a", "label": "Foundation and core concepts", "is_correct": True},
                    {"option_key": "b", "label": "Advanced topic", "is_correct": False},
                    {"option_key": "c", "label": "Implementation detail", "is_correct": False},
                    {"option_key": "d", "label": "Historical context", "is_correct": False}
                ]
            }
        ] if not self.is_production() else []
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create {len(sample_questions)} questions")
            return []
        
        created_questions = []
        
        for q_data in sample_questions:
            question = QuizQuestion(
                prompt=q_data["prompt"],
                explanation=q_data.get("explanation"),
                topic_id=topic_id,
                created_by="system",
                created_at=datetime.utcnow()
            )
            self.db.add(question)
            created_questions.append(question)
        
        self.changes.append({
            "type": "quiz_questions",
            "count": len(created_questions)
        })
        
        return created_questions
    
    def seed_resources(self, topic_id: int, dry_run: bool = False) -> List[Resource]:
        """
        Seed learning resources for a topic.
        
        Args:
            topic_id: Parent topic ID
            dry_run: Simulate without persisting
        """
        # Sample resources - should link to real content in production
        sample_resources = [
            {
                "title": "Learning Guide",
                "description": f"Comprehensive guide for this topic",
                "resource_type": "article",
                "url": "/resources/guides/default"
            }
        ] if not self.is_production() else []
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create {len(sample_resources)} resources")
            return []
        
        created_resources = []
        
        for r_data in sample_resources:
            resource = Resource(
                title=r_data["title"],
                description=r_data.get("description"),
                resource_type=r_data.get("resource_type"),
                url=r_data.get("url"),
                topic_id=topic_id,
                uploaded_by="system",
                uploaded_at=datetime.utcnow()
            )
            self.db.add(resource)
            created_resources.append(resource)
        
        self.changes.append({
            "type": "resources",
            "count": len(created_resources)
        })
        
        return created_resources
    
    def create_user_progress(self, user_id: str, topic_id: int, 
                            dry_run: bool = False) -> Optional[UserProgress]:
        """Create user progress record."""
        if dry_run:
            logger.info(f"[DRY RUN] Would create progress record for user {user_id}")
            return None
        
        existing = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == topic_id
        ).first()
        
        if not existing:
            progress = UserProgress(
                user_id=user_id,
                topic_id=topic_id,
                completion_percentage=0,
                last_accessed=datetime.utcnow()
            )
            self.db.add(progress)
            return progress
        
        return existing
    
    def seed_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Seed all data.
        
        Args:
            dry_run: Simulate without persisting
            
        Returns:
            Summary of changes
        """
        try:
            logger.info(f"Starting seed in {self.environment} mode (dry_run={dry_run})")
            
            # Seed modules
            modules = self.seed_modules(dry_run=dry_run)
            
            # Seed topics for each module
            for module in modules:
                self.seed_topics(module.id, dry_run=dry_run)
            
            # Seed quiz questions and resources for all topics
            all_topics = self.db.query(Topic).all()
            for topic in all_topics:
                self.seed_quiz_questions(topic.id, dry_run=dry_run)
                self.seed_resources(topic.id, dry_run=dry_run)
            
            if not dry_run:
                self.db.commit()
                logger.info("Seed data committed successfully")
            
            return {
                "success": True,
                "environment": self.environment.value,
                "dry_run": dry_run,
                "changes": self.changes,
                "total_changes": sum(c.get("count", 0) for c in self.changes)
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Seed failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "changes_rolled_back": self.changes
            }
        
        finally:
            self.db.close()
    
    def rollback(self):
        """Rollback any pending changes."""
        self.db.rollback()
        logger.info("Changes rolled back")


def get_environment() -> Environment:
    """Get current environment from ENV."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    try:
        return Environment[env]
    except KeyError:
        logger.warning(f"Unknown environment: {env}, using development")
        return Environment.development


async def run_seed():
    """Run seeding with appropriate environment configuration."""
    env = get_environment()
    
    # Safety check for production
    if env == Environment.production:
        logger.warning("Production environment detected - minimal seeding only")
        response = input("Confirm seeding in PRODUCTION (type 'yes' to confirm): ")
        if response.lower() != "yes":
            logger.info("Seeding cancelled")
            return
    
    manager = SeedDataManager(environment=env)
    result = manager.seed_all(dry_run=False)
    
    logger.info(f"Seed result: {result}")
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_seed())
