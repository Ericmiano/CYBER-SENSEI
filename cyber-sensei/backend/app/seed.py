"""
Database seeding script for Cyber-Sensei.
Creates baseline curriculum data, a demo user, quiz bank, and initial progress.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Module,
    Project,
    QuizOption,
    QuizQuestion,
    Topic,
    User,
    UserProgress,
)


QUIZ_SEED_DATA = [
    {
        "topic": "The OSI Model",
        "prompt": "Which OSI layer is responsible for routing packets between different networks?",
        "options": {
            "A": "Layer 2 (Data Link)",
            "B": "Layer 3 (Network)",
            "C": "Layer 4 (Transport)",
            "D": "Layer 5 (Session)",
        },
        "answer": "B",
        "explanation": "Layer 3 handles logical addressing and routing between networks.",
    },
    {
        "topic": "The OSI Model",
        "prompt": "What is the primary purpose of the Presentation layer?",
        "options": {
            "A": "Encrypting and translating data formats",
            "B": "Establishing connections",
            "C": "Segmenting transport data",
            "D": "Managing network congestion",
        },
        "answer": "A",
        "explanation": "The Presentation layer ensures data is in a usable format and handles encryption.",
    },
    {
        "topic": "TCP/IP Basics",
        "prompt": "Which TCP/IP layer ensures reliable delivery through acknowledgments and retransmissions?",
        "options": {
            "A": "Application",
            "B": "Transport",
            "C": "Internet",
            "D": "Network Access",
        },
        "answer": "B",
        "explanation": "The Transport layer (TCP) is responsible for reliability mechanisms.",
    },
    {
        "topic": "TCP/IP Basics",
        "prompt": "What is the role of the Internet layer in the TCP/IP model?",
        "options": {
            "A": "Defines how applications access the network",
            "B": "Routes packets and handles logical addressing",
            "C": "Segments data for transport",
            "D": "Establishes wired and wireless signaling",
        },
        "answer": "B",
        "explanation": "The Internet layer (IP) handles logical addressing and routing decisions.",
    },
]


def ensure_sample_user(db: Session) -> User:
    user = db.query(User).filter_by(username="testuser").first()
    if user:
        return user

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        skill_level="beginner",
        learning_style="mixed",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()
    print("✓ Created sample user 'testuser'.")
    return user


def seed_core_content(db: Session):
    if db.query(Module).count() > 0:
        print("✓ Core modules already exist. Skipping curriculum seeding.")
        return

    print("📚 Seeding database with initial curriculum data...")

    modules_data = [
        {
            "name": "Network Fundamentals",
            "description": "Learn the basics of networking including OSI model, TCP/IP, and packet analysis",
            "difficulty": "beginner",
            "icon": "🌐",
            "color": "#1976D2",
            "order": 1,
        },
        {
            "name": "System Administration",
            "description": "Master Windows and Linux system administration, user management, and security hardening",
            "difficulty": "intermediate",
            "icon": "🖥️",
            "color": "#388E3C",
            "order": 2,
        },
        {
            "name": "Web Security",
            "description": "Understand web vulnerabilities, OWASP Top 10, and secure web application development",
            "difficulty": "intermediate",
            "icon": "🔐",
            "color": "#F57C00",
            "order": 3,
        },
        {
            "name": "Cryptography",
            "description": "Learn encryption, hashing, digital signatures, and cryptographic protocols",
            "difficulty": "advanced",
            "icon": "🔒",
            "color": "#7B1FA2",
            "order": 4,
        },
    ]

    modules: list[Module] = []
    for mod in modules_data:
        module = Module(
            name=mod["name"],
            description=mod["description"],
            difficulty=mod.get("difficulty", "beginner"),
            icon=mod.get("icon"),
            color=mod.get("color"),
            order=mod.get("order", 0),
        )
        db.add(module)
        modules.append(module)

    db.flush()

    topics_by_module = [
        [
            {"name": "The OSI Model", "content": "# The OSI Model\n\nThe Open Systems Interconnection model...", "difficulty": "beginner", "order": 1},
            {"name": "TCP/IP Basics", "content": "# TCP/IP Basics\n\nTransmission Control Protocol and Internet Protocol...", "difficulty": "beginner", "order": 2},
            {"name": "DNS and DHCP", "content": "# DNS and DHCP\n\nDomain Name System and Dynamic Host Configuration Protocol...", "difficulty": "beginner", "order": 3},
            {"name": "Network Protocols", "content": "# Network Protocols\n\nHTTP, HTTPS, FTP, SSH, and more...", "difficulty": "intermediate", "order": 4},
        ],
        [
            {"name": "Linux Fundamentals", "content": "# Linux Fundamentals\n\nLinux is a free and open-source operating system...", "difficulty": "intermediate", "order": 1},
            {"name": "Windows Administration", "content": "# Windows Administration\n\nManaging Windows systems requires understanding Active Directory...", "difficulty": "intermediate", "order": 2},
            {"name": "User and Group Management", "content": "# User and Group Management\n\nProper management is crucial for security...", "difficulty": "intermediate", "order": 3},
            {"name": "Security Hardening", "content": "# Security Hardening\n\nHardening involves reducing attack surface...", "difficulty": "advanced", "order": 4},
        ],
        [
            {"name": "OWASP Top 10", "content": "# OWASP Top 10\n\nCritical security risks to web applications...", "difficulty": "intermediate", "order": 1},
            {"name": "SQL Injection", "content": "# SQL Injection\n\nAn attack that injects malicious SQL statements...", "difficulty": "intermediate", "order": 2},
            {"name": "Cross-Site Scripting (XSS)", "content": "# Cross-Site Scripting\n\nInjection of malicious scripts into trusted websites...", "difficulty": "intermediate", "order": 3},
            {"name": "Secure Coding Practices", "content": "# Secure Coding\n\nGuidelines to build resilient applications...", "difficulty": "advanced", "order": 4},
        ],
        [
            {"name": "Symmetric Encryption", "content": "# Symmetric Encryption\n\nUses the same key for encryption and decryption...", "difficulty": "advanced", "order": 1},
            {"name": "Asymmetric Encryption", "content": "# Asymmetric Encryption\n\nUses a public and private key pair...", "difficulty": "advanced", "order": 2},
            {"name": "Hashing and Digital Signatures", "content": "# Hashing\n\nProduces fixed-size output from variable input...", "difficulty": "advanced", "order": 3},
            {"name": "Cryptographic Protocols", "content": "# Protocols\n\nSSL/TLS, SSH, and more...", "difficulty": "advanced", "order": 4},
        ],
    ]

    topics: list[Topic] = []
    for idx, module in enumerate(modules):
        for topic_data in topics_by_module[idx]:
            topic = Topic(
                module_id=module.id,
                name=topic_data["name"],
                description=f"Learn about {topic_data['name']}",
                content=topic_data["content"],
                difficulty=topic_data.get("difficulty", "beginner"),
                order=topic_data.get("order", 0),
            )
            db.add(topic)
            topics.append(topic)

    db.flush()

    projects_data = [
        {
            "title": "Network Packet Analysis",
            "objective": "Capture and analyze network packets using Wireshark",
            "difficulty_level": "beginner",
            "setup_instructions": "Install Wireshark and configure network capture...",
            "guided_steps": '["Step 1: Start packet capture", "Step 2: Filter by protocol", "Step 3: Analyze results"]',
        },
        {
            "title": "Linux System Hardening",
            "objective": "Harden a Linux system by applying security best practices",
            "difficulty_level": "intermediate",
            "setup_instructions": "Set up a Ubuntu VM and disable unnecessary services...",
            "guided_steps": '["Disable SSH root login", "Configure firewall", "Patch system"]',
        },
        {
            "title": "Web App Vulnerability Assessment",
            "objective": "Identify and fix security vulnerabilities in a sample web app",
            "difficulty_level": "intermediate",
            "setup_instructions": "Deploy the sample vulnerable app locally...",
            "guided_steps": '["Scan for SQL injection", "Test XSS vectors", "Generate report"]',
        },
        {
            "title": "Encryption and Key Management",
            "objective": "Implement encryption in a simple application",
            "difficulty_level": "advanced",
            "setup_instructions": "Set up Python development environment...",
            "guided_steps": '["Generate key pairs", "Encrypt data", "Decrypt and verify"]',
        },
    ]

    for project_data in projects_data:
        project = Project(
            title=project_data["title"],
            objective=project_data["objective"],
            difficulty_level=project_data["difficulty_level"],
            setup_instructions=project_data["setup_instructions"],
            guided_steps=project_data["guided_steps"],
        )
        if topics:
            project.topics.append(topics[0])
            if len(topics) > 1:
                project.topics.append(topics[1])
        db.add(project)

    print("✓ Seeded base modules, topics, and projects.")


def ensure_progress_entries(db: Session, user: User):
    topics = db.query(Topic).order_by(Topic.id.asc()).all()
    if not topics:
        return

    created = 0
    for i, topic in enumerate(topics[:4]):
        existing = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user.id, UserProgress.topic_id == topic.id)
            .first()
        )
        if existing:
            continue

        progress = UserProgress(
            user_id=user.id,
            topic_id=topic.id,
            mastery_probability=0.2 + (i * 0.15),
            status="in_progress" if i % 2 == 0 else "not_started",
            last_accessed_at=datetime.utcnow() - timedelta(days=i),
            next_review_date=datetime.utcnow() + timedelta(days=2),
        )
        db.add(progress)
        created += 1

    if created:
        print(f"✓ Added {created} starter progress records.")


def ensure_quiz_bank(db: Session):
    topics = db.query(Topic).all()
    if not topics:
        return

    topic_lookup = {topic.name: topic for topic in topics}
    created_questions = 0

    for quiz in QUIZ_SEED_DATA:
        topic = topic_lookup.get(quiz["topic"])
        if not topic:
            continue

        existing = (
            db.query(QuizQuestion)
            .filter(QuizQuestion.topic_id == topic.id, QuizQuestion.prompt == quiz["prompt"])
            .first()
        )
        if existing:
            continue

        question = QuizQuestion(
            topic_id=topic.id,
            prompt=quiz["prompt"],
            explanation=quiz.get("explanation"),
        )
        db.add(question)
        db.flush()

        for key, label in quiz["options"].items():
            option = QuizOption(
                question_id=question.id,
                option_key=key,
                label=label,
                is_correct=(key == quiz["answer"]),
            )
            db.add(option)
        created_questions += 1

    if created_questions:
        print(f"✓ Added {created_questions} quiz questions.")


def seed_database():
    """Populate the database with initial test data."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user = ensure_sample_user(db)
        seed_core_content(db)
        ensure_progress_entries(db, user)
        ensure_quiz_bank(db)
        db.commit()
        print("✓ Database seed check complete.")
    except Exception as exc:  # pylint: disable=broad-except
        db.rollback()
        print(f"✗ Error seeding database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
